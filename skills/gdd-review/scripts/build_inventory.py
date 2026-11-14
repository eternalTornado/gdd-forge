import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gddsource import Combined, load  # noqa: E402

STOP_WORDS = {"system", "gdd", "design", "and", "the"}
SKIP_HEADINGS = re.compile(r"version history|changelog|mục lục|table of contents|tham chiếu|references?\b", re.I)
HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
FRONT_FIELD = re.compile(r"^(title|version):\s*(.+?)\s*$")
CAMEL = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")


def ascii_upper(text):
    return "".join(c for c in unicodedata.normalize("NFD", text) if c.isascii() and c.isalpha()).upper()


def words(stem):
    out = []
    for part in re.split(r"[-_\s]+", stem):
        out.extend(w for w in CAMEL.findall(part) if w.lower() not in STOP_WORDS)
    return out or [stem]


def make_prefix(stem, taken):
    ws = words(stem)
    initials = ascii_upper("".join(w[0] for w in ws))[:5]
    for cand in (ascii_upper(ws[-1])[:4], initials, ascii_upper("".join(ws))[:5]):
        if 2 <= len(cand) <= 5 and cand not in taken:
            return cand
    base = (initials or "DOC")[:4]
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        cand = (base + letter)[:5]
        if cand not in taken:
            return cand
    sys.exit("build_inventory: cannot allocate prefix for " + stem)


def strip_prefix(stem, prefix):
    return stem[len(prefix):] if prefix and stem.lower().startswith(prefix.lower()) else stem


def make_key(stem, taken):
    key = re.sub(r"[^a-z0-9]", "", ascii_upper(stem).lower()) or "doc"
    base, n = key, 2
    while key in taken or key == "system":
        key, n = "%s%d" % (base, n), n + 1
    return key


SECTION_NO = re.compile(r"^(?:§\s*)?(\d+(?:\.\d+)*)\.?(?:\s|$)")


def section_no(text):
    m = SECTION_NO.match(text)
    return m.group(1) if m else None


def parse_selectors(raw):
    out = []
    for token in (t.strip() for t in re.split(r"[;,]", raw or "") if t.strip()):
        doc, _, sel = token.rpartition(":") if ":" in token else ("", "", token)
        out.append({"token": token, "doc": doc.strip().lower(), "sel": sel.strip().lstrip("§").strip()})
    return out


def matches(selector, heading):
    sel, no = selector["sel"], section_no(heading["text"])
    if re.fullmatch(r"\d+(?:\.\d+)*", sel):
        return no is not None and (no == sel or no.startswith(sel + "."))
    return sel.lower() in heading["text"].lower()


def select(stem, heads, n_lines, selectors):
    """Selected headings + their line ranges (a heading runs until the next heading of the same or higher level)."""
    mine = [s for s in selectors if not s["doc"] or s["doc"] in stem.lower()]
    if not mine:
        return None, [], []
    picked, ranges, hit = [], [], set()
    for i, h in enumerate(heads):
        winners = [s["token"] for s in mine if matches(s, h)]
        if not winners or h["skip"]:
            continue
        hit.update(winners)
        end = next((x["line"] for x in heads[i + 1:] if x["level"] <= h["level"]), n_lines)
        ranges.append((h["line"], end))
        picked.extend(x["text"] for x in heads[i:] if x["line"] < end and not x["skip"] and x["text"] not in picked)
    return picked, ranges, [s["token"] for s in mine if s["token"] not in hit]


def scan(lines):
    meta, headings, in_front, fence = {}, [], False, False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_front = True
            continue
        if in_front:
            if line.strip() == "---":
                in_front = False
                continue
            m = FRONT_FIELD.match(line)
            if m:
                meta[m.group(1)] = m.group(2).strip().strip("\"'")
            continue
        if FENCE.match(line):
            fence = not fence
            continue
        if fence:
            continue
        if line.startswith("# ") and "h1" not in meta:
            meta["h1"] = line[2:].strip()
        m = HEADING.match(line)
        if m:
            text = m.group(2).replace("`", "").strip()
            headings.append({"text": text, "level": len(m.group(1)), "line": i, "skip": bool(SKIP_HEADINGS.search(text))})
    return meta, headings


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_inventory.py <run-dir>")
    run = sys.argv[1]
    combined = Combined(run)
    meta = load(os.path.join(run, "data", "run.json"))
    targets = [os.path.realpath(p) for p in meta["targets"]]
    selectors = parse_selectors(meta.get("sections"))
    file_prefix = meta.get("filePrefix", "")
    unmatched = []
    inv_path = os.path.join(run, "data", "inventory.json")
    old = [m for m in load(inv_path)["modules"] if m.get("file")] if os.path.exists(inv_path) else []
    previous = {m["file"]: m for m in old}
    previous_by_name = {os.path.basename(m["file"]): m for m in old}
    keys = {m["key"] for m in old}
    prefixes = {"CORE"} | {m["prefix"] for m in old}
    modules = [{"key": "system", "prefix": "CORE", "title": "Xuyên tài liệu — conflict giữa các GDD và thuật ngữ",
                "short": "Xuyên tài liệu", "pages": [], "oldPages": None, "endpoints": []}]
    files, total = [], 0
    for f in combined.files:
        real = os.path.realpath(f["path"])
        first, end = combined.body_range(f)
        body = combined.lines[first:end]
        pages = sorted({combined.page_of(i) for i in range(first, end)})
        stem = os.path.splitext(os.path.basename(real))[0]
        role = "target" if real in targets else "context"
        doc_meta, headings = scan(body)
        files.append({"path": real, "role": role, "pages": pages, "lineStart": first, "lines": len(body),
                      "version": doc_meta.get("version")})
        if role != "target" and not real.endswith(".md"):
            continue
        prior = previous.get(real) or previous_by_name.get(os.path.basename(real))
        if prior:
            key, prefix = prior["key"], prior["prefix"]
        else:
            key = make_key(strip_prefix(stem, file_prefix), keys)
            prefix = make_prefix(strip_prefix(stem, file_prefix), prefixes)
        keys.add(key)
        prefixes.add(prefix)
        title = (doc_meta.get("title") or doc_meta.get("h1") or stem).replace("`", "")
        short = strip_prefix(stem, file_prefix)
        review_pages = pages
        names = [h["text"] for h in headings if not h["skip"]]
        if role == "target" and selectors:
            picked, ranges, miss = select(stem, headings, len(body), selectors)
            if picked is None or not picked:
                unmatched.append("%s: không mục nào khớp %s" % (stem, ", ".join(miss) or "(không selector nào áp cho file này)"))
                continue
            unmatched.extend("%s: không khớp %s" % (stem, t) for t in miss)
            names = picked
            review_pages = sorted({combined.page_of(first + i) for a, b in ranges for i in range(a, b)})
        endpoints = [{"path": h, "status": "unchanged"} for h in names] if role == "target" else []
        total += len(endpoints)
        if role != "target":
            title, short = title + " (GDD đối chiếu)", short + " (đối chiếu)"
        modules.append({"key": key, "prefix": prefix, "title": title, "short": short, "pages": review_pages,
                        "filePages": pages, "oldPages": None, "endpoints": endpoints, "file": real, "role": role,
                        "version": doc_meta.get("version")})
    if unmatched:
        sys.exit("build_inventory: sections= không khớp — hỏi user rồi chạy lại:\n  " + "\n  ".join(unmatched))
    missing = [t for t in targets if t not in {m.get("file") for m in modules}]
    if missing:
        sys.exit("build_inventory: target not in prepared source: " + ", ".join(missing))
    inventory = {"modules": modules, "commonPages": [], "files": files, "totalEndpoints": total, "grepUnmatched": []}
    with open(os.path.join(run, "data", "inventory.json"), "w", encoding="utf-8") as handle:
        json.dump(inventory, handle, ensure_ascii=False, indent=1)
    module_dir = os.path.join(run, "data", "modules")
    os.makedirs(module_dir, exist_ok=True)
    for m in modules:
        with open(os.path.join(module_dir, m["key"] + ".json"), "w", encoding="utf-8") as handle:
            json.dump(m, handle, ensure_ascii=False, indent=1)
    print(json.dumps({"modules": [(m["key"], m["prefix"], m.get("role", "system"), len(m["endpoints"]), m["pages"][:1] + m["pages"][-1:]) for m in modules],
                      "sections": total, "pages": combined.page_of(len(combined.lines) - 1)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
