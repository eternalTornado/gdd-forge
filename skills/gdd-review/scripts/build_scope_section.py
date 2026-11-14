import json
import os
import re
import sys

SCOPE = "Out of scope: kỹ thuật/API/DB"
API = re.compile(r"^`([^`]+)`\s*·\s*(.+)$")
KINDS = {"GR-10": "API", "GR-11": "Database", "GR-12": "Cách implement", "GR-13": "Vận hành", "GR-14": "Code"}
MAX_QUOTES = 6
PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "profile.json")


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def split_api(api):
    m = API.match((api or "").strip())
    if not m:
        return None, []
    return m.group(1), [s.strip() for s in m.group(2).split(",") if s.strip()]


def add_unique(target, items):
    target.extend(i for i in items if i not in target)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_scope_section.py <run-dir>")
    data_dir = os.path.join(sys.argv[1], "data")
    q_path, s_path = os.path.join(data_dir, "questions.json"), os.path.join(data_dir, "scope.json")
    questions = load(q_path, None)
    if questions is None:
        sys.exit("build_scope_section: missing " + q_path)
    labels = load(PROFILE, {})["labels"]
    order = [m["key"] for m in load(os.path.join(data_dir, "inventory.json"), {"modules": []})["modules"]]
    scope = load(s_path, {"rows": []})
    rows = {r["module"]: r for r in scope.get("rows", [])}
    moved, keep = 0, []
    for q in questions["questions"]:
        if q.get("category") != SCOPE:
            keep.append(q)
            continue
        doc, secs = split_api(q.get("api"))
        row = rows.setdefault(q["module"], {"module": q["module"], "doc": "`%s`" % (doc or q["module"]),
                                            "sections": [], "kinds": [], "rules": [], "evidence": []})
        add_unique(row["sections"], secs or ["toàn tài liệu"])
        add_unique(row["rules"], q.get("rules", []))
        add_unique(row["kinds"], [KINDS[r] for r in q.get("rules", []) if r in KINDS])
        for ev in q.get("evidence", []):
            if len(row["evidence"]) < MAX_QUOTES and ev not in row["evidence"]:
                row["evidence"].append(ev)
        questions.setdefault("dropped", []).append({"cid": q.get("id"), "reason": "chuyển sang mục Ngoài phạm vi GDD"})
        moved += 1
    questions["questions"] = keep
    ranked = sorted(rows.values(), key=lambda r: order.index(r["module"]) if r["module"] in order else len(order))
    scope = {"title": labels["scopeTitle"], "intro": labels["scopeIntro"], "rows": ranked}
    with open(q_path, "w", encoding="utf-8") as handle:
        json.dump(questions, handle, ensure_ascii=False, indent=1)
    with open(s_path, "w", encoding="utf-8") as handle:
        json.dump(scope, handle, ensure_ascii=False, indent=1)
    print(json.dumps({"moved": moved, "scopeRows": len(ranked), "questions": len(keep)}))


if __name__ == "__main__":
    main()
