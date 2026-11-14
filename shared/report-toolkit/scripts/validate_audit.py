import argparse
import json
import os
import re
import sys
import unicodedata

CONSTITUTION = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "constitution.md")
CATEGORIES = {
    "Chưa định nghĩa hành vi/ràng buộc",
    "Mâu thuẫn trong tài liệu",
    "Không nhất quán giữa các API",
    "Không nhất quán kiểu/định dạng",
    "Thiếu sót bảo mật",
    "Lỗi đặt tên/chính tả",
}
PRIORITIES = {"high", "mid", "low"}
SOURCES = {"new", "old"}
STATUSES = {"new", "changed", "desc", "unchanged", "removed"}
DIFF_KINDS = {"added", "modified", "removed"}
ROW_KINDS = {"added", "removed", "changed", "unchanged"}
OVERRIDE_KEYS = ("new", "changed", "desc", "unchanged", "removed")
KEY_RE = re.compile(r"^[a-z0-9]+$")
PREFIX_RE = re.compile(r"^[A-Z]{2,5}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PAGES_RE = re.compile(r"^tr\. (\d+)(?:[–-](\d+))?$")
RULE_HEAD = re.compile(r"^#{2,4} (AC-\d+)\b", re.M)
FILLER = re.compile(r"\b(tbd|todo|lorem)\b", re.I)
STRIP1 = dict.fromkeys(map(ord, "|*`"))
WS = re.compile(r"\s+")
PAGE_FILE = re.compile(r"^p(\d+)\.txt$")
LINE_HYPHEN = re.compile(r"(?<=[^\W\d_])-[ \t]*\n\s*(?=[^\W\d_])")
SOFT = "\x00"
ELLIPSIS = re.compile(r"\.\.\.")
EDGE_LINES = 3


def norm1(value):
    return WS.sub(" ", unicodedata.normalize("NFC", value).translate(STRIP1)).strip()


def norm2(value, source=False):
    text = unicodedata.normalize("NFKC", value).translate(STRIP1)
    if source:
        text = LINE_HYPHEN.sub(SOFT, text)
    return WS.sub("", text)


def pattern2(quote):
    q = norm2(quote)
    if not q:
        return None
    soft = re.escape(SOFT)
    return re.compile((soft + "?").join("[-%s]" % soft if ch == "-" else re.escape(ch) for ch in q))


def has_ellipsis(value):
    return bool(ELLIPSIS.search(unicodedata.normalize("NFKC", value)))


class Source:
    def __init__(self, folder):
        meta_path = os.path.join(folder, "source.json")
        pages_dir = os.path.join(folder, "pages")
        if not os.path.isfile(meta_path) or not os.path.isdir(pages_dir):
            raise SystemExit("validate_audit: not a prepared source dir: " + folder)
        with open(meta_path, encoding="utf-8") as handle:
            self.meta = json.load(handle)
        texts = {}
        for name in os.listdir(pages_dir):
            m = PAGE_FILE.match(name)
            if m:
                with open(os.path.join(pages_dir, name), encoding="utf-8") as handle:
                    texts[int(m.group(1))] = handle.read()
        self.count = max(texts) if texts else 0
        self.pages = {n: texts.get(n, "") for n in range(1, self.count + 1)}
        self.cache = {}
        self.patterns = {}

    def pattern(self, quote):
        if quote not in self.patterns:
            self.patterns[quote] = pattern2(quote)
        return self.patterns[quote]

    def ellipsis_missing(self, quote, page):
        texts = self.pages.get(page, "") + self.pages.get(page + 1, "")
        return has_ellipsis(quote) and not has_ellipsis(texts)

    def forms(self, page):
        if page in self.cache:
            return self.cache[page]
        text = self.pages.get(page, "")
        joins = []
        nxt = self.pages.get(page + 1)
        if nxt is not None:
            head = text.rstrip("\n").split("\n")
            tail = nxt.split("\n")
            for k in range(EDGE_LINES + 1):
                for j in range(EDGE_LINES):
                    if k < len(head) and j < len(tail):
                        joins.append("\n".join(head[:len(head) - k]) + "\n" + "\n".join(tail[j:]))
        forms = ((norm1(text), norm2(text, True)), ([norm1(v) for v in joins], [norm2(v, True) for v in joins]))
        self.cache[page] = forms
        return forms

    def on_page(self, quote, page):
        (p1, p2), _ = self.forms(page)
        n1, n2 = norm1(quote), self.pattern(quote)
        if n1 and n1 in p1:
            return 1
        if n2 and n2.search(p2):
            return 2
        return 0

    def tier(self, quote, page):
        if page not in self.pages:
            return 0
        found = self.on_page(quote, page)
        if found or page + 1 not in self.pages or self.on_page(quote, page + 1):
            return found
        _, (j1, j2) = self.forms(page)
        n1, n2 = norm1(quote), self.pattern(quote)
        if n1 and any(n1 in v for v in j1):
            return 1
        if n2 and any(n2.search(v) for v in j2):
            return 2
        return 0

    def locate(self, quote, pages=None):
        for page in pages or range(1, self.count + 1):
            if self.tier(quote, page):
                return page
        return None


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, message):
        self.errors.append({"path": path, "message": message})

    def warn(self, path, message):
        self.warnings.append({"path": path, "message": message})


def is_text(value, allow_empty=False):
    return isinstance(value, str) and (allow_empty or value.strip() != "")


def need_text(rep, obj, field, path, allow_empty=False):
    value = obj.get(field) if isinstance(obj, dict) else None
    if not is_text(value, allow_empty):
        rep.error(path + "." + field, "required non-empty string")
        return None
    return value


def filler(rep, path, value):
    if isinstance(value, str) and FILLER.search(value):
        rep.error(path, "placeholder word: " + FILLER.search(value).group(0))


def prose(rep, path, value):
    filler(rep, path, value)
    if not isinstance(value, str):
        return
    if "``" in value:
        rep.error(path, "double backtick: a code span cannot contain or be made of backticks (DATA.md §3)")
    elif value.count("`") % 2:
        rep.error(path, "unbalanced backtick (DATA.md §3)")


def known_rules():
    if not os.path.isfile(CONSTITUTION):
        return None
    with open(CONSTITUTION, encoding="utf-8") as handle:
        return set(RULE_HEAD.findall(handle.read()))


def check_meta(rep, meta, module_keys):
    if not isinstance(meta, dict):
        rep.error("meta", "required object")
        return "diff"
    if not isinstance(meta.get("title", ""), str):
        rep.error("meta.title", "must be a string")
    filler(rep, "meta.title", meta.get("title"))
    date = need_text(rep, meta, "date", "meta")
    if date and not DATE_RE.match(date):
        rep.error("meta.date", "expected YYYY-MM-DD")
    mode = meta.get("mode")
    if mode not in ("diff", "single"):
        rep.error("meta.mode", "must be diff or single")
        mode = "diff"
    for side in ("new", "old"):
        doc = meta.get(side)
        if side == "old" and mode == "single":
            if doc is not None:
                rep.error("meta.old", "must be null when mode=single")
            continue
        if not isinstance(doc, dict):
            rep.error("meta." + side, "required object")
            continue
        need_text(rep, doc, "label", "meta." + side)
        need_text(rep, doc, "short", "meta." + side)
        if "note" in doc and not isinstance(doc["note"], (str, type(None))):
            rep.error("meta.%s.note" % side, "must be a string")
    notes = meta.get("notes", [])
    if not isinstance(notes, list) or not all(is_text(n) for n in notes):
        rep.error("meta.notes", "must be a list of non-empty strings")
    else:
        for i, n in enumerate(notes):
            prose(rep, "meta.notes[%d]" % i, n)
    override = meta.get("kpiOverride")
    if override is not None:
        check_override(rep, override, module_keys)
    labels = meta.get("labels")
    if labels is not None and (not isinstance(labels, dict) or not all(is_text(v) for v in labels.values())):
        rep.error("meta.labels", "must be an object of non-empty strings")
    return mode


def check_override(rep, override, module_keys):
    if not isinstance(override, dict):
        rep.error("meta.kpiOverride", "must be an object")
        return
    for key in ("total",) + OVERRIDE_KEYS:
        if key in override and (not isinstance(override[key], int) or override[key] < 0):
            rep.error("meta.kpiOverride." + key, "must be a non-negative integer")
    if not isinstance(override.get("total"), int):
        rep.error("meta.kpiOverride.total", "required integer")
    parts = [override.get(k) for k in OVERRIDE_KEYS if isinstance(override.get(k), int)]
    if parts and isinstance(override.get("total"), int) and sum(parts) != override["total"]:
        rep.error("meta.kpiOverride", "breakdown sums to %d, total is %d" % (sum(parts), override["total"]))
    per = override.get("modules", {})
    if not isinstance(per, dict):
        rep.error("meta.kpiOverride.modules", "must be an object")
        return
    for key, n in per.items():
        if key not in module_keys:
            rep.error("meta.kpiOverride.modules." + key, "unknown module")
        if not isinstance(n, int) or n < 0:
            rep.error("meta.kpiOverride.modules." + key, "must be a non-negative integer")


def check_modules(rep, modules, mode):
    keys, prefixes = {}, set()
    if not isinstance(modules, list) or not modules:
        rep.error("modules", "required non-empty list")
        return keys
    paths = {}
    for i, m in enumerate(modules):
        path = "modules[%d]" % i
        if not isinstance(m, dict):
            rep.error(path, "must be an object")
            continue
        key = m.get("key")
        if not isinstance(key, str) or not KEY_RE.match(key):
            rep.error(path + ".key", "must match [a-z0-9]+")
        elif key in keys:
            rep.error(path + ".key", "duplicate key " + key)
        else:
            keys[key] = m
        prefix = m.get("prefix")
        if not isinstance(prefix, str) or not PREFIX_RE.match(prefix):
            rep.error(path + ".prefix", "must be 2–5 uppercase letters")
        elif prefix in prefixes:
            rep.error(path + ".prefix", "duplicate prefix " + prefix)
        else:
            prefixes.add(prefix)
        for field in ("title", "short"):
            prose(rep, path + "." + field, need_text(rep, m, field, path))
        for field in ("heading", "diffNote"):
            if field in m and not isinstance(m[field], (str, type(None))):
                rep.error(path + "." + field, "must be a string")
            prose(rep, path + "." + field, m.get(field))
        endpoints = m.get("endpoints")
        if not isinstance(endpoints, list):
            rep.error(path + ".endpoints", "required list (may be empty)")
            continue
        for j, ep in enumerate(endpoints):
            epath = "%s.endpoints[%d]" % (path, j)
            if not isinstance(ep, dict):
                rep.error(epath, "must be an object")
                continue
            ep_path = need_text(rep, ep, "path", epath)
            status = ep.get("status")
            if status not in STATUSES:
                rep.error(epath + ".status", "must be one of " + ", ".join(sorted(STATUSES)))
            elif mode == "single" and status != "unchanged":
                rep.error(epath + ".status", "mode=single requires unchanged")
            if ep_path:
                if ep_path in paths:
                    rep.warn(epath + ".path", "duplicate of " + paths[ep_path])
                paths.setdefault(ep_path, epath)
    return keys


def check_questions(rep, questions, modules, rules, sources, stats, mode):
    if not isinstance(questions, list):
        rep.error("questions", "required list")
        return
    ids = set()
    no_rules = 0
    for i, q in enumerate(questions):
        path = "questions[%d]" % i
        if not isinstance(q, dict):
            rep.error(path, "must be an object")
            continue
        qid = q.get("id") if isinstance(q.get("id"), str) else None
        if qid:
            path += " " + qid
        module = modules.get(q.get("module"))
        if module is None:
            rep.error(path + ".module", "unknown module %r" % q.get("module"))
        if qid is None:
            rep.error(path + ".id", "required string")
        elif qid in ids:
            rep.error(path + ".id", "duplicate id")
        else:
            ids.add(qid)
            m = re.match(r"^([A-Z]{2,5})-(\d{3})$", qid)
            if not m:
                rep.error(path + ".id", "must be <PREFIX>-NNN")
            elif module is not None and m.group(1) != module.get("prefix"):
                rep.error(path + ".id", "prefix %s does not match module prefix %s" % (m.group(1), module.get("prefix")))
        if q.get("priority") not in PRIORITIES:
            rep.error(path + ".priority", "must be high, mid or low")
        if q.get("category") not in CATEGORIES:
            rep.error(path + ".category", "not in the closed category set: %r" % q.get("category"))
        qrules = q.get("rules", [])
        if not isinstance(qrules, list) or not all(isinstance(r, str) for r in qrules):
            rep.error(path + ".rules", "must be a list of strings")
        elif not qrules:
            no_rules += 1
        elif rules is not None:
            for r in qrules:
                if r not in rules:
                    rep.error(path + ".rules", "unknown rule %s (not a heading in %s)" % (r, os.path.basename(CONSTITUTION)))
        for field in ("api", "title", "issue", "ask"):
            prose(rep, path + "." + field, need_text(rep, q, field, path))
        ask = q.get("ask")
        if is_text(ask) and not ask.rstrip().endswith("?"):
            rep.error(path + ".ask", "must end with '?'")
        evidence = q.get("evidence")
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 6:
            rep.error(path + ".evidence", "must hold 1–6 quotes")
            continue
        for j, ev in enumerate(evidence):
            check_evidence(rep, "%s.evidence[%d]" % (path, j), ev, sources, stats, mode)
    if no_rules:
        rep.warn("questions", "%d question(s) have empty rules (rule ids of %s expected)" % (no_rules, os.path.basename(CONSTITUTION)))


def check_evidence(rep, path, ev, sources, stats, mode):
    if not isinstance(ev, dict):
        rep.error(path, "must be an object")
        return
    src = ev.get("src")
    page = ev.get("page")
    quote = ev.get("quote")
    if src not in SOURCES:
        rep.error(path + ".src", "must be new or old")
        return
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        rep.error(path + ".page", "must be a positive integer")
        return
    if not is_text(quote):
        rep.error(path + ".quote", "required non-empty string")
        return
    if "loc" in ev and not is_text(ev["loc"]):
        rep.error(path + ".loc", "must be a non-empty string")
    bucket = stats["evidence"][src]
    if src == "old" and mode == "single":
        bucket["fail"] += 1
        rep.error(path + ".src", "src=old but mode=single: there is no old document")
        return
    source = sources.get(src)
    if source is None:
        bucket["unchecked"] += 1
        rep.warn(path, "src=old but no --old given; quote not checked")
        return
    if page > source.count:
        bucket["fail"] += 1
        rep.error(path + ".page", "page %d beyond source (%d pages)" % (page, source.count))
        return
    if source.ellipsis_missing(quote, page):
        bucket["fail"] += 1
        rep.error(path + ".quote", "ellipsis not in source page %d: quotes are verbatim and never shortened (DATA.md §2): %s" % (page, quote[:80]))
        return
    tier = source.tier(quote, page)
    if tier:
        bucket["pass"] += 1
        bucket["tier%d" % tier] += 1
        return
    bucket["fail"] += 1
    found = source.locate(quote)
    if found:
        rep.error(path, "quote is on page %d, not page %d: %s" % (found, page, quote[:80]))
    else:
        rep.error(path, "quote not found verbatim (page %d): %s" % (page, quote[:80]))


def page_range(value):
    m = PAGES_RE.match(value) if isinstance(value, str) else None
    if not m:
        return None
    first = int(m.group(1))
    last = int(m.group(2)) if m.group(2) else first
    return list(range(first, last + 1)) if last >= first else None


def check_cell(rep, path, cell):
    if cell is None:
        return []
    if not isinstance(cell, list):
        rep.error(path, "must be null or a list of items")
        return []
    out = []
    for k, item in enumerate(cell):
        ipath = "%s[%d]" % (path, k)
        if not isinstance(item, dict):
            rep.error(ipath, "must be an object")
            continue
        for field in ("label", "value", "gloss"):
            if field in item and not isinstance(item[field], (str, type(None))):
                rep.error(ipath + "." + field, "must be a string or null")
        if "changed" in item and not isinstance(item["changed"], bool):
            rep.error(ipath + ".changed", "must be a boolean")
        filler(rep, ipath + ".gloss", item.get("gloss"))
        if is_text(item.get("value")):
            out.append((ipath + ".value", item["value"]))
    return out


def check_diffs(rep, diffs, modules, mode, sources, stats):
    if not isinstance(diffs, list):
        rep.error("diffs", "required list")
        return
    if mode == "single" and diffs:
        rep.error("diffs", "must be empty when mode=single")
    with_diffs = set()
    unchecked_old = 0
    for i, d in enumerate(diffs):
        path = "diffs[%d]" % i
        if not isinstance(d, dict):
            rep.error(path, "must be an object")
            continue
        if d.get("module") not in modules:
            rep.error(path + ".module", "unknown module %r" % d.get("module"))
        else:
            with_diffs.add(d["module"])
        if d.get("kind") not in DIFF_KINDS:
            rep.error(path + ".kind", "must be added, modified or removed")
        prose(rep, path + ".label", need_text(rep, d, "label", path))
        if "tag" in d and not isinstance(d["tag"], (str, type(None))):
            rep.error(path + ".tag", "must be a string")
        prose(rep, path + ".tag", d.get("tag"))
        ranges = {}
        for side, field in (("old", "oldPages"), ("new", "newPages")):
            value = d.get(field)
            if value is None:
                ranges[side] = None
            elif page_range(value) is None:
                rep.error(path + "." + field, "expected null, 'tr. N' or 'tr. N–M'")
                ranges[side] = None
            else:
                ranges[side] = page_range(value)
                source = sources.get(side)
                if source is not None and ranges[side][-1] > source.count:
                    rep.error(path + "." + field, "%s beyond source (%d pages)" % (value, source.count))
        rows = d.get("rows")
        if not isinstance(rows, list) or not rows:
            rep.error(path + ".rows", "required non-empty list")
            continue
        for j, r in enumerate(rows):
            rpath = "%s.rows[%d]" % (path, j)
            if not isinstance(r, dict):
                rep.error(rpath, "must be an object")
                continue
            kind = r.get("kind")
            if kind not in ROW_KINDS:
                rep.error(rpath + ".kind", "must be added, removed, changed or unchanged")
            need_text(rep, r, "key", rpath)
            if "plainKey" in r and not isinstance(r["plainKey"], bool):
                rep.error(rpath + ".plainKey", "must be a boolean")
            if "note" in r and not isinstance(r["note"], (str, type(None))):
                rep.error(rpath + ".note", "must be a string")
            prose(rep, rpath + ".note", r.get("note"))
            if kind == "added" and r.get("old") is not None:
                rep.warn(rpath, "row kind added but old cell is not null")
            if kind == "removed" and r.get("new") is not None:
                rep.warn(rpath, "row kind removed but new cell is not null")
            for side in ("old", "new"):
                values = check_cell(rep, "%s.%s" % (rpath, side), r.get(side))
                if values and ranges[side] is None:
                    rep.warn("%s.%s" % (rpath, side), "cell has values but %sPages is null" % side)
                    continue
                for vpath, value in values:
                    source = sources.get(side)
                    bucket = stats["diffValues"][side]
                    if source is None:
                        unchecked_old += 1
                        bucket["unchecked"] += 1
                        continue
                    pages = [p for p in ranges[side] if p <= source.count]
                    if any(source.tier(value, p) for p in pages):
                        bucket["pass"] += 1
                        continue
                    found = source.locate(value)
                    if found:
                        bucket["warn"] += 1
                        rep.warn(vpath, "value not in %s pages %s (found on page %d): %s" % (side, ranges[side], found, value[:80]))
                        continue
                    bucket["fail"] += 1
                    why = "ellipsis is not in the source; values are verbatim" if has_ellipsis(value) else "not found verbatim in the source"
                    rep.error(vpath, "%s value %s (DATA.md §2): %s" % (side, why, value[:80]))
    if unchecked_old:
        rep.warn("diffs", "%d old-side value(s) not checked (no --old)" % unchecked_old)
    for key, m in modules.items():
        if key in with_diffs and not m.get("heading"):
            changed = [ep for ep in m.get("endpoints", []) if isinstance(ep, dict) and ep.get("status") != "unchanged"]
            if not changed:
                rep.warn("modules." + key, "has diffs but no heading and no changed endpoint: section 3 heading will be empty")


def check_scope(rep, scope, modules, sources, stats, mode):
    if scope is None:
        return
    if not isinstance(scope, dict) or not isinstance(scope.get("rows"), list):
        rep.error("scope", "must be an object with a rows list")
        return
    prose(rep, "scope.title", need_text(rep, scope, "title", "scope"))
    prose(rep, "scope.intro", scope.get("intro"))
    for i, row in enumerate(scope["rows"]):
        path = "scope.rows[%d]" % i
        if not isinstance(row, dict):
            rep.error(path, "must be an object")
            continue
        need_text(rep, row, "module", path)
        prose(rep, path + ".doc", need_text(rep, row, "doc", path))
        secs = row.get("sections")
        if not isinstance(secs, list) or not secs or not all(is_text(s) for s in secs):
            rep.error(path + ".sections", "must be a non-empty list of strings")
        evidence = row.get("evidence")
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 6:
            rep.error(path + ".evidence", "must hold 1–6 quotes")
            continue
        for j, ev in enumerate(evidence):
            check_evidence(rep, "%s.evidence[%d]" % (path, j), ev, sources, stats, mode)


def run(audit, sources):
    rep = Report()
    stats = {
        "evidence": {s: {"pass": 0, "fail": 0, "tier1": 0, "tier2": 0, "unchecked": 0} for s in ("new", "old")},
        "diffValues": {s: {"pass": 0, "warn": 0, "fail": 0, "unchecked": 0} for s in ("new", "old")},
    }
    if not isinstance(audit, dict):
        rep.error("$", "audit.json must be an object")
        return rep, stats
    modules_raw = audit.get("modules")
    keys = {m.get("key") for m in modules_raw if isinstance(m, dict)} if isinstance(modules_raw, list) else set()
    mode = check_meta(rep, audit.get("meta"), keys)
    modules = check_modules(rep, modules_raw, mode)
    check_questions(rep, audit.get("questions"), modules, known_rules(), sources, stats, mode)
    check_diffs(rep, audit.get("diffs", []), modules, mode, sources, stats)
    check_scope(rep, audit.get("scope"), modules, sources, stats, mode)
    if mode == "diff" and "old" not in sources:
        rep.warn("--old", "mode=diff without --old: old-side quotes and values are not checked")
    stats["questions"] = len(audit.get("questions") or [])
    stats["diffs"] = len(audit.get("diffs") or [])
    return rep, stats


def apply_profile(path):
    global CATEGORIES, CONSTITUTION, RULE_HEAD
    with open(path, encoding="utf-8") as handle:
        profile = json.load(handle)
    if profile.get("categories"):
        CATEGORIES = set(profile["categories"])
    if profile.get("rules"):
        CONSTITUTION = os.path.join(os.path.dirname(os.path.abspath(path)), profile["rules"])
    if profile.get("ruleId"):
        RULE_HEAD = re.compile(r"^#{2,4} (%s)\b" % profile["ruleId"], re.M)


def main():
    parser = argparse.ArgumentParser(description="Validate audit.json against DATA.md §3 and the prepared sources.")
    parser.add_argument("audit")
    parser.add_argument("--new", required=True, dest="new_dir")
    parser.add_argument("--old", dest="old_dir")
    parser.add_argument("--profile", help="JSON {categories, rules, ruleId} replacing the closed category set and the rule source")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.profile:
        apply_profile(args.profile)
    with open(args.audit, encoding="utf-8") as handle:
        try:
            audit = json.load(handle)
        except UnicodeDecodeError:
            sys.exit("validate_audit: input is not valid UTF-8")
        except json.JSONDecodeError as error:
            sys.exit("validate_audit: invalid JSON: " + str(error))
    sources = {"new": Source(args.new_dir)}
    if args.old_dir:
        sources["old"] = Source(args.old_dir)
    rep, stats = run(audit, sources)
    if args.json:
        print(json.dumps({"ok": not rep.errors, "errors": rep.errors, "warnings": rep.warnings, "stats": stats}, ensure_ascii=False, indent=2))
    else:
        print("validate_audit: %d error(s), %d warning(s)" % (len(rep.errors), len(rep.warnings)))
        for src in ("new", "old"):
            e = stats["evidence"][src]
            print("evidence %s: %d pass (tier1 %d, tier2 %d), %d fail, %d unchecked" % (src, e["pass"], e["tier1"], e["tier2"], e["fail"], e["unchecked"]))
            v = stats["diffValues"][src]
            print("diff values %s: %d pass, %d warn, %d fail, %d unchecked" % (src, v["pass"], v["warn"], v["fail"], v["unchecked"]))
        for item in rep.errors:
            print("ERROR   %s: %s" % (item["path"], item["message"]))
        for item in rep.warnings:
            print("WARNING %s: %s" % (item["path"], item["message"]))
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
