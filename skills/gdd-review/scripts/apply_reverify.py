import argparse
import datetime
import json
import os

PRIORITIES = ("high", "mid", "low")
OUTCOMES = ("resolved", "obsolete")


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def outcome(reason):
    """resolve_votes.py prefixes the lens (`answer: resolved: …`); VERIFIER Mode: resolve starts its reason with an outcome."""
    tail = reason.split(":", 1)[1].strip() if reason.startswith(("answer:", "form:")) else reason
    head = tail.split(":", 1)[0].strip()
    return head if head in OUTCOMES else "refuted"


def main():
    parser = argparse.ArgumentParser(description="Apply re-verify verdicts to questions.json, keeping ids.")
    parser.add_argument("run")
    parser.add_argument("units", nargs="+")
    parser.add_argument("--verify", action="store_true",
                        help="verify mode: label drops as answered by GD and write the run note with open counts")
    args = parser.parse_args()
    data = os.path.join(args.run, "data")
    q_path = os.path.join(data, "questions.json")
    doc = load(q_path)
    kept, dropped = {}, {}
    for unit in args.units:
        verified = load(os.path.join(data, "work", "verified-%s.json" % unit))
        for cand in verified["kept"]:
            kept[cand["cid"]] = cand
        for item in verified["dropped"]:
            dropped[item["cid"]] = item
    today = datetime.date.today().isoformat()
    label = "verify %s" % today if args.verify else "cập nhật %s" % today
    out, revised, closed = [], [], {k: [] for k in OUTCOMES + ("refuted",)}
    for q in doc["questions"]:
        qid = q["id"]
        if qid in dropped:
            item = dropped[qid]
            closed[outcome(item.get("reason", ""))].append({"id": qid, "title": q.get("title", ""),
                                                            "priority": q.get("priority")})
            doc.setdefault("dropped", []).append({"cid": qid, "title": q.get("title", ""),
                                                  "reason": "%s: %s" % (label, item.get("reason", "")),
                                                  "evidence": item.get("evidence", "")})
            continue
        if qid in kept:
            new = {k: v for k, v in kept[qid].items() if k != "cid"}
            new["id"] = qid
            if any(new.get(k) != q.get(k) for k in ("title", "issue", "ask", "category", "priority", "rules", "api")):
                revised.append(qid)
            q = new
        out.append(q)
    doc["questions"] = out
    with open(q_path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)

    open_by = {p: sum(q.get("priority") == p for q in out) for p in PRIORITIES}
    result = {"dropped": sorted(dropped), "revised": len(revised), "kept": len(kept) - len(revised), "total": len(out)}
    if args.verify:
        result = {"checked": len(kept) + len(dropped), "closed": closed, "revisedIds": revised,
                  "open": len(out), "openByPriority": open_by, "unchecked": len(out) - len(kept)}
        meta_path = os.path.join(data, "run.json")
        meta = load(meta_path)
        scope_open = len(load(os.path.join(data, "scope.json"), {"rows": []}).get("rows", []))
        note = ("Verify %s theo GDD commit %s: %d/%d câu hỏi đã được GDD trả lời, %d câu không còn áp dụng; "
                "còn %d câu cần Game Design giải quyết (high %d · mid %d · low %d), %d GDD còn nội dung ngoài phạm vi. "
                "Lần verify này chỉ kiểm lại câu hỏi đã có, không tìm câu hỏi mới."
                % (today, (meta.get("gddCommit") or "")[:7], len(closed["resolved"]), result["checked"],
                   len(closed["obsolete"]), len(out), open_by["high"], open_by["mid"], open_by["low"], scope_open))
        meta["notes"] = [n for n in meta.get("notes", []) if not n.startswith("Verify ")] + [note]
        with open(meta_path, "w", encoding="utf-8") as handle:
            json.dump(meta, handle, ensure_ascii=False, indent=1)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
