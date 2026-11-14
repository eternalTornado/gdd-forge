import json
import os
import sys

LENSES = ("answer", "form")


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: resolve_votes.py <run-dir> <unit>")
    run, unit = sys.argv[1], sys.argv[2]
    data = os.path.join(run, "data")
    work = os.path.join(data, "work")
    find = load(os.path.join(work, f"find-{unit}.json"))
    if find is None:
        sys.exit(f"missing: {os.path.join(work, f'find-{unit}.json')}")
    inv = load(os.path.join(data, "inventory.json"))
    if inv is None:
        sys.exit(f"missing: {os.path.join(data, 'inventory.json')}")
    keys = {m["key"] for m in inv["modules"]}

    by_cid = {}
    for lens in LENSES:
        votes = load(os.path.join(work, f"votes-{unit}-{lens}.json")) or {}
        for v in votes.get("verdicts", []):
            by_cid.setdefault(v["cid"], []).append({**v, "lens": lens})

    kept, dropped, unverified = [], [], []
    for cand in find.get("candidates", []):
        votes = by_cid.get(cand["cid"], [])
        if len(votes) < len(LENSES):
            unverified.append(cand["cid"])
        refute = next((v for v in votes if v["verdict"] == "refute"), None)
        if refute:
            dropped.append({
                "cid": cand["cid"],
                "title": cand.get("title", ""),
                "reason": f"{refute['lens']}: {refute.get('reason', '')}",
                "evidence": refute.get("answerEvidence", ""),
            })
            continue
        merged = dict(cand)
        for v in votes:
            if v["verdict"] == "revise":
                for field, value in (v.get("rewrite") or {}).items():
                    if value not in (None, ""):
                        merged[field] = value
        if merged.get("module") not in keys:
            merged["module"] = "system"
        kept.append(merged)

    out = {"unit": unit, "kept": kept, "dropped": dropped, "unverified": unverified}
    with open(os.path.join(work, f"verified-{unit}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"unit": unit, "kept": len(kept), "dropped": len(dropped), "unverified": len(unverified)}))


if __name__ == "__main__":
    main()
