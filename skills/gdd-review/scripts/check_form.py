import json
import os
import re
import shutil
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir, os.pardir, "shared", "report-toolkit", "scripts"))

from validate_audit import FILLER, Source, has_ellipsis  # noqa: E402

OUT_OF_SCOPE = "Out of scope: kỹ thuật/API/DB"
LOW_ONLY = {OUT_OF_SCOPE, "Lỗi trình bày"}
PRIORITIES = {"high", "mid", "low"}
TEXT_FIELDS = ("title", "issue", "ask", "api")
TARGET_LENSES = ("conflict", "scope", "missing")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fold(text):
    return unicodedata.normalize("NFC", text or "").strip().casefold()


def known_rules():
    with open(os.path.join(HERE, os.pardir, "review-standard.md"), encoding="utf-8") as handle:
        return set(re.findall(r"^#{2,4} (GR-\d+)\b", handle.read(), re.M))


def check_evidence(cand, source, flags):
    kept = []
    for ev in cand.get("evidence") or []:
        quote = ev.get("quote") if isinstance(ev, dict) else None
        if not isinstance(quote, str) or not quote.strip():
            flags.append("evidence-empty-quote")
            continue
        page = ev.get("page")
        if not isinstance(page, int) or not source.tier(quote, page):
            found = source.locate(quote)
            if found is None:
                flags.append("quote-not-verbatim: " + quote[:60])
                continue
            flags.append("page-fixed: %s -> %d" % (page, found))
            page = found
        if has_ellipsis(quote) and not has_ellipsis(source.pages.get(page, "") + source.pages.get(page + 1, "")):
            flags.append("quote-ellipsis: " + quote[:60])
            continue
        kept.append({"src": "new", "page": page, "quote": quote})
    cand["evidence"] = kept[:6]
    if len(kept) > 6:
        flags.append("evidence-trimmed-to-6")


def check_one(cand, unit, modules, categories, rules, source):
    flags, refute = [], None
    for field in TEXT_FIELDS:
        if not isinstance(cand.get(field), str) or not cand[field].strip():
            refute = refute or "thiếu field " + field
    by_fold = {fold(c): c for c in categories}
    category = by_fold.get(fold(cand.get("category")))
    if category is None:
        refute = refute or "category ngoài tập đóng: %s" % cand.get("category")
    else:
        cand["category"] = category
    check_evidence(cand, source, flags)
    if not cand["evidence"]:
        refute = refute or "không còn evidence nguyên văn"
    if category and category.startswith("Conflict") and len(cand["evidence"]) < 2:
        flags.append("conflict-one-side")
    if category in LOW_ONLY:
        cand["priority"] = "low"
    elif cand.get("priority") not in PRIORITIES:
        flags.append("priority-invalid: %s" % cand.get("priority"))
    cand_rules = [r for r in (cand.get("rules") or []) if r in rules]
    if len(cand_rules) != len(cand.get("rules") or []):
        flags.append("rules-unknown-dropped")
    cand["rules"] = cand_rules
    if not cand_rules:
        flags.append("rules-empty")
    if "`" in (cand.get("title") or ""):
        cand["title"] = cand["title"].replace("`", "")
    for field in ("issue", "ask"):
        value = cand.get(field) or ""
        if FILLER.search(value):
            flags.append("filler-word-in-" + field)
        if value.count("`") % 2 or "``" in value:
            flags.append("backtick-in-" + field)
    module = modules.get(cand.get("module"))
    key, _, lens = unit.rpartition("-")
    if lens in TARGET_LENSES or (key == "" and unit in modules):
        own = key if lens in TARGET_LENSES else unit
        own_role = modules[own].get("role") if own in modules else None
        if category == OUT_OF_SCOPE:
            cand["module"] = own
        elif own_role == "context":
            refute = refute or "Conflict/Thiếu info chỉ nằm trong GDD đối chiếu (review-standard §6)"
        elif cand.get("module") not in (own, "system"):
            flags.append("module-fixed: %s -> %s" % (cand.get("module"), own))
            cand["module"] = own
    elif module is None:
        cand["module"] = "system"
    elif module.get("role") == "context" and category != OUT_OF_SCOPE:
        refute = refute or "module đối chiếu chỉ nhận Out of scope (review-standard §6)"
    return refute, flags


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: check_form.py <run-dir> <unit>")
    run, unit = sys.argv[1], sys.argv[2]
    work = os.path.join(run, "data", "work")
    find_path = os.path.join(work, "find-%s.json" % unit)
    raw_path = os.path.join(work, "find-%s.raw.json" % unit)
    if not os.path.exists(raw_path):
        shutil.copyfile(find_path, raw_path)
    find = load(raw_path)
    modules = {m["key"]: m for m in load(os.path.join(run, "data", "inventory.json"))["modules"]}
    categories = load(os.path.join(HERE, os.pardir, "profile.json"))["categories"]
    rules = known_rules()
    source = Source(os.path.join(run, "src", "new"))
    verdicts, seen = [], set()
    for cand in find.get("candidates", []):
        cid = cand.get("cid")
        if not cid or cid in seen:
            sys.exit("check_form: missing or duplicate cid in " + find_path)
        seen.add(cid)
        refute, flags = check_one(cand, unit, modules, categories, rules, source)
        verdicts.append({"cid": cid, "verdict": "refute" if refute else "keep",
                         "reason": refute or ("; ".join(flags) if flags else "hình thức đạt"), "flags": flags})
    with open(find_path, "w", encoding="utf-8") as handle:
        json.dump(find, handle, ensure_ascii=False, indent=1)
    with open(os.path.join(work, "votes-%s-form.json" % unit), "w", encoding="utf-8") as handle:
        json.dump({"verdicts": verdicts}, handle, ensure_ascii=False, indent=1)
    refuted = sum(v["verdict"] == "refute" for v in verdicts)
    flagged = sum(bool(v["flags"]) and v["verdict"] == "keep" for v in verdicts)
    print(json.dumps({"unit": unit, "candidates": len(verdicts), "refute": refuted, "flagged": flagged}))


if __name__ == "__main__":
    main()
