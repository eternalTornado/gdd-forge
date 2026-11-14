import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, os.pardir, os.pardir, "shared", "report-toolkit", "scripts"))

from validate_audit import Source  # noqa: E402

CHUNK = 25


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)


def stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def main():
    parser = argparse.ArgumentParser(description="Stage re-verify units for an updated gdd-review run.")
    parser.add_argument("run")
    parser.add_argument("--all", action="store_true", help="re-verify every question, not only those touching a changed GDD")
    parser.add_argument("--verify", action="store_true",
                        help="verify mode: stage every question and re-check scope rows against the new source instead of pruning them")
    args = parser.parse_args()
    args.all = args.all or args.verify
    data = os.path.join(args.run, "data")
    work = os.path.join(data, "work")
    update = load(os.path.join(work, "update.json"), {"changedFiles": [], "changedModules": {}})
    changed = {os.path.realpath(p) for p in update["changedFiles"]}
    changed_stems = {stem(p) for p in changed}
    inventory = load(os.path.join(data, "inventory.json"))
    page_file = {page: os.path.realpath(f["path"]) for f in inventory["files"] for page in f["pages"]}
    source = Source(os.path.join(args.run, "src", "new"))
    questions = load(os.path.join(data, "questions.json"))["questions"]

    picked = {}
    for q in questions:
        touched = args.all or any(s in (q.get("api") or "") for s in changed_stems)
        for ev in q.get("evidence", []):
            if touched:
                break
            page = source.locate(ev["quote"])
            touched = page is None or page_file.get(page) in changed
        if touched:
            cand = {k: v for k, v in q.items() if k != "id"}
            cand["cid"] = q["id"]
            cand["evidence"] = [{"src": e["src"], "page": e["page"], "quote": e["quote"]} for e in q["evidence"]]
            picked.setdefault(q["module"], []).append(cand)

    for name in os.listdir(work):
        if name.startswith(("find-rev-", "votes-rev-", "verified-rev-")):
            os.remove(os.path.join(work, name))
    units = []
    for key, cands in sorted(picked.items()):
        for n in range(0, len(cands), CHUNK):
            unit = "rev-%s-%d" % (key, n // CHUNK + 1)
            save(os.path.join(work, "find-%s.json" % unit),
                 {"candidates": cands[n:n + CHUNK], "checked": {"sections": [], "rules": []},
                  "notes": ["re-verify câu hỏi đang có trong report"]})
            units.append(unit)

    scope_path = os.path.join(data, "scope.json")
    scope = load(scope_path, {"rows": []})
    result = {"reverify": sum(len(c) for c in picked.values()), "of": len(questions), "units": units}
    if args.verify:
        result.update(recheck_scope(scope, source))
        if os.path.exists(scope_path):
            save(scope_path, scope)
    else:
        changed_keys = set(update.get("changedModules", {}))
        pruned = [r["module"] for r in scope.get("rows", []) if r["module"] in changed_keys]
        if pruned:
            scope["rows"] = [r for r in scope["rows"] if r["module"] not in changed_keys]
            save(scope_path, scope)
        result["scopeRowsPruned"] = pruned
    print(json.dumps(result, ensure_ascii=False))


def recheck_scope(scope, source):
    """Re-page each scope quote in the new source; drop quotes GD removed; drop rows with no quote left."""
    kept, cleared, partial = [], [], []
    for row in scope.get("rows", []):
        before = len(row.get("evidence", []))
        live = [dict(ev, page=page) for ev in row.get("evidence", [])
                for page in [source.locate(ev["quote"])] if page is not None]
        row["evidence"] = live
        if not live:
            cleared.append(row["module"])
            continue
        if len(live) < before:
            partial.append(row["module"])
        kept.append(row)
    scope["rows"] = kept
    return {"scopeCleared": cleared, "scopePartial": partial, "scopeOpen": len(kept)}


if __name__ == "__main__":
    main()
