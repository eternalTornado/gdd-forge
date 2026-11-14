"""State of the one gdd-review report (reports/gdd-review/gdd-report.md) — picks create / update / update+add in SKILL §0.

  report_status.py --gdd <GDD> [<target file|folder> …]

Prints: exists, inSync, date, gddCommit, targets (count), sections, lenses, covers (all given targets already in the
report), missing (given GDD files not yet in it — pass to update_run.py --add), cache (data/ left by an unfinished or
uncleaned run), legacy (old dated run folders that still hold a report).
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from collect_sources import expand  # noqa: E402
from report_md import HTML, MD, REPORT_DIR, abs_path, in_sync, parse_md, read_text  # noqa: E402


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Status of reports/gdd-review/gdd-report.md and which targets it covers.")
    parser.add_argument("--gdd", required=True, help="GDD repo root (key gdd.path)")
    parser.add_argument("--dir", default=REPORT_DIR, help="report folder (default reports/gdd-review)")
    parser.add_argument("targets", nargs="*", help="GDD files or folders; folders expand to their .md files")
    args = parser.parse_args()
    gdd, run = os.path.realpath(args.gdd), args.dir
    wanted = expand(gdd, args.targets) if args.targets else []

    out = {"report": os.path.join(run, MD).replace(os.sep, "/"), "exists": os.path.exists(os.path.join(run, MD))}
    if out["exists"]:
        meta = parse_md(read_text(os.path.join(run, MD)))["block"]["meta"]
        targets = {abs_path(p, gdd, run) for p in meta.get("targets", [])}
        missing = [p for p in wanted if os.path.realpath(p) not in targets]
        out.update(inSync=in_sync(run), date=meta.get("date"), gddCommit=(meta.get("gddCommit") or "")[:7],
                   targets=len(targets), sections=meta.get("sections"), lenses=meta.get("lenses"),
                   covers=(not missing) if wanted else None, missing=missing)
    else:
        out.update(missing=wanted)
    out["cache"] = os.path.isdir(os.path.join(run, "data"))
    out["legacy"] = sorted({os.path.dirname(p).replace(os.sep, "/") for name in (MD, HTML)
                            for p in glob.glob(os.path.join(run, "*", name))})
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
