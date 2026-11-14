import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gddsource import TOOLKIT, load  # noqa: E402

PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "profile.json")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: prepare.py <run-dir>")
    run = sys.argv[1]
    meta_path = os.path.join(run, "data", "run.json")
    meta = load(meta_path)
    meta["labels"] = load(PROFILE)["labels"]
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, ensure_ascii=False, indent=1)
    cmd = [sys.executable, "-I", os.path.join(os.path.realpath(TOOLKIT), "prepare_source.py")]
    for path in meta["targets"] + meta.get("context", []):
        cmd += ["--in", path]
    cmd += ["--out", os.path.join(run, "src", "new"), "--label", meta["new"]["label"],
            "--short", meta["new"]["short"], "--lines-per-page", str(meta.get("linesPerPage", 50))]
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
