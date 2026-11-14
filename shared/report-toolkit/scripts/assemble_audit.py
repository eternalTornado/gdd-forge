import glob
import json
import os
import sys


def load(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        sys.exit(f"missing: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: assemble_audit.py <run-dir>")
    run = sys.argv[1]
    data = os.path.join(run, "data")
    meta = load(os.path.join(data, "run.json"))
    inv = load(os.path.join(data, "inventory.json"))
    qs = load(os.path.join(data, "questions.json"))
    single = meta.get("mode") != "diff"

    if not meta.get("title"):
        label = meta["new"]["label"]
        meta["title"] = f"{label} — Câu hỏi cho Backend" if single else f"{label} — Thay đổi giữa hai phiên bản và câu hỏi cho Backend"

    diff_files = {}
    for p in glob.glob(os.path.join(data, "diff-*.json")):
        d = load(p)
        diff_files[d.get("module") or os.path.basename(p)[5:-5]] = d

    modules, diffs, problems = [], [], []
    asked = {q.get("module") for q in qs.get("questions", [])}
    for m in inv["modules"]:
        if m.get("role") == "context" and m["key"] not in asked:
            continue
        d = diff_files.pop(m["key"], None) or {}
        eps = d.get("endpoints") or m.get("endpoints") or []
        eps = [{"path": e["path"], "status": "unchanged" if single else e.get("status", "unchanged")} for e in eps]
        mod = {"key": m["key"], "prefix": m["prefix"], "title": m["title"], "short": m["short"], "endpoints": eps}
        if d.get("heading"):
            mod["heading"] = d["heading"]
        if d.get("diffNote"):
            mod["diffNote"] = d["diffNote"]
        modules.append(mod)
        if not single:
            for t in d.get("diffs") or []:
                t.setdefault("module", m["key"])
                diffs.append(t)
    for k in diff_files:
        problems.append(f"diff file for unknown module: {k}")

    keys = {m["key"] for m in modules}
    questions = []
    for q in qs.get("questions", []):
        if q.get("module") not in keys:
            problems.append(f"{q.get('id')}: unknown module {q.get('module')}")
        questions.append({k: v for k, v in q.items() if k != "cid"})

    out = {"meta": meta, "modules": modules, "questions": questions, "diffs": diffs}
    scope_path = os.path.join(data, "scope.json")
    if os.path.exists(scope_path):
        out["scope"] = load(scope_path)
    with open(os.path.join(data, "audit.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"modules": len(modules), "questions": len(questions), "diffs": len(diffs), "problems": problems}, ensure_ascii=False))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
