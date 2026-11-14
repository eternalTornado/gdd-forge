"""reports/gdd-review/gdd-report.md is the canonical report; gdd-report.html beside it is always rendered from it.
<run> defaults to reports/gdd-review.

  write [<run>] --gdd <GDD>          data/ (after assemble) -> gdd-report.md, parsed back and compared, then gdd-report.html
  load  [<run>] --gdd <GDD> [--force] gdd-report.md -> data/{run,questions,scope,inventory,audit}.json, then gdd-report.html
  check [<run>]                       exit 1 when gdd-report.html was not rendered from the current gdd-report.md
  clean [<run>] [--force]             delete the data/ and src/ caches; refuses while html is stale or the run is unfinished

The md holds the questions and the out-of-scope rows as readable text (hand edits are picked up by `load`);
run meta, module list and closed questions sit in a hidden `<!-- gdd-review:data ... -->` block at the end.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLKIT = os.path.realpath(os.path.join(HERE, os.pardir, os.pardir, os.pardir, "shared", "report-toolkit", "scripts"))
sys.path.insert(0, TOOLKIT)

from render_audit import Report, load_style  # noqa: E402

REPORT_DIR = os.path.join("reports", "gdd-review")  # the one report: <REPORT_DIR>/gdd-report.{md,html}; data/ + src/ beside them are run caches
MD, HTML = "gdd-report.md", "gdd-report.html"
DATA_OPEN, DATA_CLOSE = "<!-- gdd-review:data", "-->"
HASH_RE = re.compile(r'<meta name="gdd-report-md" content="sha256:([0-9a-f]{64})">')
RUN_TOKEN = "$RUN"
FORMAT = 1

PRIORITIES = [("high", "Cao"), ("mid", "Trung bình"), ("low", "Thấp")]
PRIO_LABEL = dict(PRIORITIES)
PRIO_KEY = {label: key for key, label in PRIORITIES}

F_PRIO, F_CAT, F_RULES, F_API = "- **Ưu tiên:** ", "- **Loại:** ", "- **Luật:** ", "- **Mục GDD:** "
F_ISSUE, F_EV, F_ASK = "**Vấn đề:** ", "**GDD ghi:**", "**Câu hỏi:** "
F_SECTIONS, F_KINDS = "- **Mục:** ", "- **Loại nội dung:** "
EV_LINE = re.compile(r"^- (?:(?P<loc>.+?) · )?tr\. (?P<page>\d+)(?P<old> · bản cũ)? — (?P<q>(`+) .* \5)$")
CODE = re.compile(r"(`+) (.*) \1", re.S)


# ---------- io ----------

def load_json(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        sys.exit("report_md: missing " + path)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().replace("\r\n", "\n")


def digest(text):
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ---------- paths: absolute in data/, portable in the md ----------

def rel_path(path, gdd):
    real = os.path.realpath(path)
    if os.sep + "src" + os.sep + "ctx" + os.sep in real:
        return RUN_TOKEN + "/src/ctx/" + os.path.basename(real)
    try:
        rel = os.path.relpath(real, gdd)
    except ValueError:
        rel = ".."
    return (real if rel.startswith("..") else rel).replace(os.sep, "/")


def abs_path(path, gdd, run):
    if path.startswith(RUN_TOKEN + "/"):
        return os.path.realpath(os.path.join(run, path[len(RUN_TOKEN) + 1:]))
    return os.path.realpath(path if os.path.isabs(path) else os.path.join(gdd, path))


def encode_meta(meta, gdd):
    out = {k: v for k, v in meta.items() if k not in ("title", "notes")}
    for key in ("targets", "context"):
        out[key] = [rel_path(p, gdd) for p in meta.get(key, [])]
    if meta.get("sourceHashes"):
        out["sourceHashes"] = {rel_path(p, gdd): h for p, h in meta["sourceHashes"].items()}
    return out


def decode_meta(meta, gdd, run):
    out = dict(meta)
    for key in ("targets", "context"):
        out[key] = [abs_path(p, gdd, run) for p in meta.get(key, [])]
    if meta.get("sourceHashes"):
        out["sourceHashes"] = {abs_path(p, gdd, run): h for p, h in meta["sourceHashes"].items()}
    return out


def encode_modules(inventory, gdd):
    out = []
    for m in inventory["modules"]:
        eps = [e["path"] if e.get("status", "unchanged") == "unchanged" else {"path": e["path"], "status": e["status"]}
               for e in m.get("endpoints", [])]
        item = {"key": m["key"], "prefix": m["prefix"], "title": m["title"], "short": m["short"]}
        if m.get("file"):
            item.update(file=rel_path(m["file"], gdd), role=m.get("role"), version=m.get("version"))
        item["endpoints"] = eps
        out.append(item)
    return out


def decode_modules(modules, gdd, run):
    out = []
    for m in modules:
        item = {"key": m["key"], "prefix": m["prefix"], "title": m["title"], "short": m["short"],
                "pages": [], "oldPages": None,
                "endpoints": [{"path": e, "status": "unchanged"} if isinstance(e, str) else e for e in m["endpoints"]]}
        if m.get("file"):
            item.update(file=abs_path(m["file"], gdd, run), role=m.get("role"), version=m.get("version"))
        out.append(item)
    return out


# ---------- md writer ----------

def code(text):
    fence = "`" * (max([len(r) for r in re.findall(r"`+", text)] or [0]) + 1)
    return "%s %s %s" % (fence, text, fence)


def uncode(text):
    m = CODE.fullmatch(text)
    if not m:
        raise ValueError("not a code span: " + text)
    return m.group(2)


def one_line(value, what):
    value = value or ""
    if "\n" in value or "\r" in value or value != value.strip():
        sys.exit("report_md: %s has a line break or edge whitespace, the md cannot hold it verbatim: %r" % (what, value[:80]))
    return value


def cell(text):
    return (text or "").replace("|", "\\|")


def evidence_lines(evidence, where):
    out = []
    for e in evidence:
        loc = one_line(e.get("loc"), where + " loc")
        head = ("%s · " % loc if loc else "") + "tr. %d" % int(e["page"]) + (" · bản cũ" if e.get("src", "new") == "old" else "")
        out.append("- %s — %s" % (head, code(one_line(e["quote"], where + " quote"))))
    return out


def overview(report, labels):
    total = sum(len(m.get("endpoints", [])) for m in report.modules)
    qs = report.questions
    prio = " · ".join("%s %d" % (label, sum(q["priority"] == key for q in qs)) for key, label in PRIORITIES)
    lines = ["## 1. Tổng quan", "",
             "| Chỉ số | Tổng | Chi tiết |", "|---|---:|---|",
             "| %s | %d | %s %d |" % (cell(labels["unit"]), total, cell(labels["unitBreakdown"]), len(report.modules)),
             "| %s | %d | %s |" % (cell(labels["questions"]), len(qs), prio), "",
             "- **%s:** %s" % (labels["unit"], labels["unitDef"]),
             "- **Mức ưu tiên:** %s" % labels["priorityDef"], "",
             "**%s**" % labels["figure"], "",
             "| %s | Câu hỏi | %s |" % (cell(labels["unitBreakdown"]), " | ".join(label for _, label in PRIORITIES)),
             "|---|---:|" + "---:|" * len(PRIORITIES)]
    for m in report.q_modules:
        mq = report.by_module[m["key"]]
        counts = " | ".join(str(sum(q["priority"] == key for q in mq)) for key, _ in PRIORITIES)
        lines.append("| %s | %d | %s |" % (cell(m["title"]), len(mq), counts))
    rest = [m["title"] for m in report.modules if not report.by_module[m["key"]]]
    if rest:
        lines += ["", "Không có câu hỏi: " + "; ".join(rest)]
    return lines + [""]


def question_lines(q):
    where = q["id"]
    return ["#### %s · %s" % (q["id"], one_line(q["title"], where + " title")), "",
            F_PRIO + PRIO_LABEL[q["priority"]],
            F_CAT + one_line(q["category"], where + " category"),
            (F_RULES + ", ".join(q.get("rules", []))).rstrip(),
            (F_API + one_line(q.get("api"), where + " api")).rstrip(), "",
            F_ISSUE + one_line(q["issue"], where + " issue"), "",
            F_EV, ""] + evidence_lines(q["evidence"], where) + ["",
            F_ASK + one_line(q["ask"], where + " ask"), ""]


def scope_lines(scope):
    lines = ["## 3. " + scope["title"], ""]
    if scope.get("intro"):
        lines += [one_line(scope["intro"], "scope intro"), ""]
    for r in scope.get("rows", []):
        where = "scope " + r["doc"]
        lines += ["### " + one_line(r["doc"], where), "",
                  (F_SECTIONS + ", ".join(r.get("sections", []))).rstrip(),
                  (F_KINDS + ", ".join(r.get("kinds", []))).rstrip(),
                  (F_RULES + ", ".join(r.get("rules", []))).rstrip(), "",
                  F_EV, ""] + evidence_lines(r["evidence"], where) + [""]
    return lines


def render_md(audit, block):
    report = Report(audit)
    labels = report.labels
    lines = ["# " + one_line(report.title(), "title"), "", report.subtitle(), "",
             "> Report có hai bản cùng nội dung: `gdd-report.md` (file này) và `gdd-report.html`, do skill `gdd-review` ghi cùng lúc. "
             "Lần chạy `/gdd-review` sau (cập nhật hoặc `--verify`) đọc câu hỏi từ file này. Sửa tay được câu hỏi và mục ngoài phạm vi "
             "nếu giữ đúng định dạng; không sửa khối dữ liệu ẩn cuối file. Sửa tay xong muốn HTML khớp ngay: "
             "`python3 -I <skill gdd-review>/scripts/report_md.py load --gdd <GDD>` rồi `report_md.py clean`.", ""]
    lines += overview(report, labels)
    lines += ["## 2. " + labels["questions"], ""]
    for m in report.q_modules:
        mq = report.by_module[m["key"]]
        lines += ["### %s · %d câu hỏi" % (m["title"], len(mq)), ""]
        for q in mq:
            lines += question_lines(q)
    if audit.get("scope") is not None:
        lines += scope_lines(audit["scope"])
    notes = audit["meta"].get("notes") or []
    if notes:
        lines += ["## Ghi chú", ""] + ["- " + one_line(n, "note") for n in notes] + [""]
    payload = json.dumps(block, ensure_ascii=False, indent=1).replace("-->", "--\\u003e")
    lines += [DATA_OPEN, payload, DATA_CLOSE]
    return "\n".join(lines) + "\n"


# ---------- md parser ----------

def parse_md(text):
    lines = text.replace("\r\n", "\n").split("\n")
    try:
        start = lines.index(DATA_OPEN)
        end = lines.index(DATA_CLOSE, start)
    except ValueError:
        sys.exit("report_md: %s has no `%s` block" % (MD, DATA_OPEN))
    block = json.loads("\n".join(lines[start + 1:end]))
    if block.get("format") != FORMAT:
        sys.exit("report_md: unknown md format %r" % block.get("format"))
    title, section, cur = None, None, None
    questions, rows, notes, intro = [], [], [], []
    scope_title = None
    errors = []

    def field(line, prefix):
        return line[len(prefix):].strip() if line.startswith(prefix) else None

    for n, line in enumerate(lines[:start], 1):
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            head = line[3:].strip()
            section = "q" if head.startswith("2. ") else "s" if head.startswith("3. ") else "n" if head == "Ghi chú" else "o"
            if section == "s":
                scope_title = head[3:]
            cur = None
            continue
        if section == "q":
            if line.startswith("#### "):
                qid, _, qtitle = line[5:].partition(" · ")
                cur = {"id": qid.strip(), "title": qtitle.strip(), "evidence": []}
                questions.append(cur)
            elif line.startswith("### "):
                cur = None
            elif cur is not None:
                parse_body(line, n, cur, field, errors, question=True)
        elif section == "s":
            if line.startswith("### "):
                cur = {"doc": line[4:].strip(), "evidence": []}
                rows.append(cur)
            elif cur is None:
                if line.strip():
                    intro.append(line.strip())
            else:
                parse_body(line, n, cur, field, errors, question=False)
        elif section == "n" and line.startswith("- "):
            notes.append(line[2:].strip())
    if errors:
        sys.exit("report_md: %s không đúng định dạng:\n  " % MD + "\n  ".join(errors))
    scope = None
    if scope_title is not None:
        scope = {"title": scope_title, "intro": " ".join(intro), "rows": rows}
    return {"title": title, "questions": questions, "scope": scope, "notes": notes, "block": block}


def parse_body(line, n, cur, field, errors, question):
    if not line.strip():
        return
    if line.startswith("- ") and EV_LINE.match(line):
        m = EV_LINE.match(line)
        ev = {"src": "old" if m.group("old") else "new", "page": int(m.group("page")), "quote": uncode(m.group("q"))}
        if m.group("loc"):
            ev["loc"] = m.group("loc")
        cur["evidence"].append(ev)
        return
    if line.strip() == F_EV:
        return
    split = lambda v: [x.strip() for x in v.split(",") if x.strip()]  # noqa: E731
    if field(line, F_RULES.rstrip()) is not None:
        cur["rules"] = split(field(line, F_RULES.rstrip()))
        return
    if question:
        for prefix, key in ((F_CAT, "category"), (F_ISSUE, "issue"), (F_ASK, "ask")):
            if field(line, prefix.rstrip()) is not None:
                cur[key] = field(line, prefix.rstrip())
                return
        if field(line, F_API.rstrip()) is not None:
            cur["api"] = field(line, F_API.rstrip())
            return
        if field(line, F_PRIO.rstrip()) is not None:
            label = field(line, F_PRIO.rstrip())
            if label not in PRIO_KEY:
                errors.append("dòng %d: ưu tiên %r không thuộc %s" % (n, label, "/".join(PRIO_KEY)))
            cur["priority"] = PRIO_KEY.get(label, label)
            return
    else:
        if field(line, F_SECTIONS.rstrip()) is not None:
            cur["sections"] = split(field(line, F_SECTIONS.rstrip()))
            return
        if field(line, F_KINDS.rstrip()) is not None:
            cur["kinds"] = split(field(line, F_KINDS.rstrip()))
            return
    errors.append("dòng %d: không hiểu %r" % (n, line[:100]))


def to_data(parsed, gdd, run):
    """Parsed md -> the dicts data/ holds (absolute paths, module keys resolved)."""
    block = parsed["block"]
    meta = decode_meta(block["meta"], gdd, run)
    meta["title"] = parsed["title"]
    meta["notes"] = parsed["notes"]
    modules = decode_modules(block["modules"], gdd, run)
    by_prefix = {m["prefix"]: m["key"] for m in modules}
    by_stem = {os.path.splitext(os.path.basename(m["file"]))[0]: m["key"] for m in modules if m.get("file")}
    problems, questions = [], []
    for q in parsed["questions"]:
        key = by_prefix.get(q["id"].rsplit("-", 1)[0])
        if key is None:
            problems.append("%s: tiền tố id không thuộc module nào" % q["id"])
        missing = [f for f in ("priority", "category", "issue", "ask") if f not in q]
        if missing or not q["evidence"]:
            problems.append("%s: thiếu %s" % (q["id"], ", ".join(missing + ([] if q["evidence"] else ["evidence"]))))
        questions.append({"id": q["id"], "module": key, "priority": q.get("priority"), "category": q.get("category"),
                          "rules": q.get("rules", []), "api": q.get("api", ""), "title": q["title"], "issue": q.get("issue"),
                          "evidence": q["evidence"], "ask": q.get("ask")})
    ids = [q["id"] for q in questions]
    problems += ["%s: id trùng" % i for i in sorted({i for i in ids if ids.count(i) > 1})]
    scope = parsed["scope"]
    if scope is not None:
        rows = []
        for r in scope["rows"]:
            key = by_stem.get(r["doc"].strip("`"))
            if key is None:
                problems.append("ngoài phạm vi %s: không khớp GDD nào trong run" % r["doc"])
            rows.append({"module": key, "doc": r["doc"], "sections": r.get("sections", []), "kinds": r.get("kinds", []),
                         "rules": r.get("rules", []), "evidence": r["evidence"]})
        scope = {"title": scope["title"], "intro": scope["intro"], "rows": rows}
    if problems:
        sys.exit("report_md: %s:\n  " % MD + "\n  ".join(problems))
    inventory = {"modules": modules, "commonPages": [], "files": [],
                 "totalEndpoints": sum(len(m["endpoints"]) for m in modules if m.get("role") == "target"), "grepUnmatched": []}
    return {"meta": meta, "questions": {"questions": questions, "dropped": block.get("dropped", [])},
            "scope": scope, "inventory": inventory}


# ---------- steps ----------

def assemble(run):
    out = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(TOOLKIT, "assemble_audit.py"), run],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        sys.exit("report_md: assemble_audit.py failed:\n" + out.stdout + out.stderr)


def render_html(run, md_text):
    audit = load_json(os.path.join(run, "data", "audit.json"))
    html = Report(audit).render(load_style())
    anchor = '<meta charset="utf-8">'
    if anchor not in html:
        sys.exit("report_md: render_audit output has no charset meta")
    html = html.replace(anchor, anchor + '\n<meta name="gdd-report-md" content="sha256:%s">' % digest(md_text), 1)
    with open(os.path.join(run, HTML), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(html)
    return len(html.encode("utf-8"))


def html_digest(run):
    path = os.path.join(run, HTML)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        m = HASH_RE.search(handle.read(4096))
    return m.group(1) if m else None


def in_sync(run):
    md = os.path.join(run, MD)
    return os.path.exists(md) and html_digest(run) == digest(read_text(md))


def norm_questions(qs):
    return {q["id"]: {k: v for k, v in q.items() if k != "cid"} for q in qs}


def write_data(run, data):
    d = os.path.join(run, "data")
    save_json(os.path.join(d, "run.json"), data["meta"])
    save_json(os.path.join(d, "questions.json"), data["questions"])
    save_json(os.path.join(d, "inventory.json"), data["inventory"])
    scope_path = os.path.join(d, "scope.json")
    if data["scope"] is not None:
        save_json(scope_path, data["scope"])
    elif os.path.exists(scope_path):
        os.remove(scope_path)


def cmd_write(args):
    run, gdd = args.run, os.path.realpath(args.gdd)
    d = os.path.join(run, "data")
    assemble(run)
    audit = load_json(os.path.join(d, "audit.json"))
    qdoc = load_json(os.path.join(d, "questions.json"))
    inventory = load_json(os.path.join(d, "inventory.json"))
    meta = audit["meta"]
    block = {"format": FORMAT, "meta": encode_meta(meta, gdd), "modules": encode_modules(inventory, gdd),
             "dropped": qdoc.get("dropped", [])}
    text = render_md(audit, block)

    back = to_data(parse_md(text), gdd, run)
    diffs = []
    if back["meta"]["title"] != meta.get("title"):
        diffs.append("title")
    if back["meta"]["notes"] != (meta.get("notes") or []):
        diffs.append("notes")
    want, got = norm_questions(audit["questions"]), norm_questions(back["questions"]["questions"])
    diffs += ["question %s" % i for i in sorted(set(want) | set(got)) if want.get(i) != got.get(i)]
    if (audit.get("scope") or None) != back["scope"]:
        diffs.append("scope")
    if diffs:
        sys.exit("report_md: md không giữ nguyên dữ liệu (round-trip lệch), chưa ghi gì: " + ", ".join(diffs[:20]))

    with open(os.path.join(run, MD), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    size = render_html(run, text)
    print(json.dumps({"md": os.path.join(run, MD).replace(os.sep, "/"), "html": os.path.join(run, HTML).replace(os.sep, "/"),
                      "questions": len(audit["questions"]), "scopeRows": len((audit.get("scope") or {}).get("rows", [])),
                      "htmlBytes": size, "inSync": True}, ensure_ascii=False))


def cmd_load(args):
    run, gdd = args.run, os.path.realpath(args.gdd)
    md_path = os.path.join(run, MD)
    if not os.path.exists(md_path):
        sys.exit("report_md: no %s in %s" % (MD, run))
    text = read_text(md_path)
    data = to_data(parse_md(text), gdd, run)
    q_path = os.path.join(run, "data", "questions.json")
    if not args.force and os.path.exists(q_path) and os.path.getmtime(q_path) > os.path.getmtime(md_path):
        current = load_json(q_path)
        if norm_questions(current.get("questions", [])) != norm_questions(data["questions"]["questions"]):
            sys.exit("report_md: data/questions.json mới hơn %s và khác nội dung — có thể là run dở chưa render. "
                     "Chạy tiếp run rồi `write`, hoặc `load --force` để lấy theo md." % MD)
    write_data(run, data)
    assemble(run)
    render_html(run, text)
    print(json.dumps({"loaded": md_path.replace(os.sep, "/"), "questions": len(data["questions"]["questions"]),
                      "dropped": len(data["questions"]["dropped"]),
                      "scopeRows": len((data["scope"] or {}).get("rows", [])), "inSync": True}, ensure_ascii=False))


def cmd_check(args):
    ok = in_sync(args.run)
    print(json.dumps({"run": args.run, "inSync": ok}))
    sys.exit(0 if ok else 1)


def pending_units(work):
    """Units staged (find-<u>.json) but not resolved (verified-<u>.json): a run stopped midway."""
    if not os.path.isdir(work):
        return []
    names = set(os.listdir(work))
    return sorted(n[5:-5] for n in names
                  if n.startswith("find-") and n.endswith(".json") and not n.endswith(".raw.json")
                  and "verified-%s.json" % n[5:-5] not in names)


def cmd_clean(args):
    """Drop the data/ and src/ caches once md + html hold the finished run."""
    run = args.run
    if not in_sync(run):
        sys.exit("report_md: html không khớp md (hoặc thiếu md) — chạy `write` trước, không xoá gì")
    problems = []
    q_path = os.path.join(run, "data", "questions.json")
    if os.path.exists(q_path):
        md_qs = to_data(parse_md(read_text(os.path.join(run, MD))), os.getcwd(), run)["questions"]["questions"]
        if norm_questions(load_json(q_path).get("questions", [])) != norm_questions(md_qs):
            problems.append("data/questions.json khác md (kết quả chưa `write`)")
    pending = pending_units(os.path.join(run, "data", "work"))
    if pending:
        problems.append("unit chưa xong: " + ", ".join(pending[:10]) + (" …" if len(pending) > 10 else ""))
    if problems and not args.force:
        sys.exit("report_md: run còn dở, không xoá cache (`--force` để vẫn xoá):\n  " + "\n  ".join(problems))
    removed = []
    for name in ("data", "src"):
        path = os.path.join(run, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
            removed.append(name)
    print(json.dumps({"run": run, "removed": removed, "kept": [MD, HTML]}, ensure_ascii=False))


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Keep gdd-report.md (canonical) and gdd-report.html in sync.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write", help="data/ -> md -> html")
    w.add_argument("run", nargs="?", default=REPORT_DIR)
    w.add_argument("--gdd", required=True)
    ld = sub.add_parser("load", help="md -> data/ -> html")
    ld.add_argument("run", nargs="?", default=REPORT_DIR)
    ld.add_argument("--gdd", required=True)
    ld.add_argument("--force", action="store_true", help="overwrite data/ even when it holds newer unrendered questions")
    c = sub.add_parser("check", help="exit 1 when html was not rendered from the current md")
    c.add_argument("run", nargs="?", default=REPORT_DIR)
    cl = sub.add_parser("clean", help="delete data/ and src/ once md + html hold the finished run")
    cl.add_argument("run", nargs="?", default=REPORT_DIR)
    cl.add_argument("--force", action="store_true", help="delete even when the run looks unfinished")
    args = parser.parse_args()
    {"write": cmd_write, "load": cmd_load, "check": cmd_check, "clean": cmd_clean}[args.cmd](args)


if __name__ == "__main__":
    main()
