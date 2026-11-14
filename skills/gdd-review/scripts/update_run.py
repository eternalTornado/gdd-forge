import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_inventory import scan  # noqa: E402

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def git(gdd, *args):
    out = subprocess.run(["git", "-C", gdd] + list(args), capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    if out.returncode:
        sys.exit("update_run: git %s failed: %s" % (" ".join(args), out.stderr.strip()))
    return out.stdout


def base_commit(gdd, run, meta):
    if meta.get("gddCommit"):
        return meta["gddCommit"]
    sources = os.path.join(run, "data", "sources.json")
    if not os.path.exists(sources):
        return None
    stamp = datetime.datetime.fromtimestamp(os.path.getmtime(sources))
    return git(gdd, "rev-list", "-1", "--before=" + stamp.isoformat(timespec="seconds"), "HEAD").strip() or None


def changed_headings(gdd, base, path):
    """Level 2-3 headings (outside Version History/Changelog) whose body a diff hunk touches; None = whole file is new."""
    rel = os.path.relpath(path, gdd)
    if base is None or not git(gdd, "ls-tree", base, "--", rel).strip():
        return None
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    _, heads = scan(lines)
    out = []
    for line in git(gdd, "diff", "-U0", base, "--", rel).split("\n"):
        m = HUNK.match(line)
        if not m:
            continue
        start, count = int(m.group(1)) - 1, int(m.group(2) if m.group(2) is not None else 1)
        last = start + max(count, 1) - 1
        owner = [h for h in heads if h["line"] <= start][-1:]
        inside = [h for h in heads if start < h["line"] <= last]
        for h in owner + inside:
            if not h["skip"] and h["text"] not in out:
                out.append(h["text"])
    return out


def archive_work(run):
    work = os.path.join(run, "data", "work")
    if not os.path.isdir(work):
        return None
    dest = os.path.join(work, "archive", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(dest)
    for name in os.listdir(work):
        if name != "archive":
            shutil.move(os.path.join(work, name), os.path.join(dest, name))
    return dest


def step(*cmd):
    out = subprocess.run([sys.executable, "-I", "-X", "utf8"] + list(cmd), capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    if out.returncode:
        sys.exit("update_run: %s failed:\n%s%s" % (os.path.basename(cmd[0]), out.stdout, out.stderr))
    return out.stdout


def main():
    parser = argparse.ArgumentParser(description="Refresh the gdd-review report against the current GDD repo (optionally adding GDD files).")
    parser.add_argument("run")
    parser.add_argument("--gdd", required=True)
    parser.add_argument("--force", action="store_true", help="refresh sources even when no GDD file changed")
    parser.add_argument("--verify", action="store_true",
                        help="verify mode: only existing questions are re-checked; apply_reverify.py --verify writes the run note")
    parser.add_argument("--add", nargs="+", default=[], metavar="GDD",
                        help="GDD files not yet in the report: become targets, whole file reviewed as new (changedModules = \"*\")")
    args = parser.parse_args()
    if args.add and args.verify:
        sys.exit("update_run: --verify chỉ kiểm câu hỏi đang có, không thêm GDD (--add)")
    run, gdd = args.run, os.path.realpath(args.gdd)
    meta_path = os.path.join(run, "data", "run.json")
    meta = load(meta_path)
    known = {os.path.realpath(p) for p in meta["targets"]}
    added = []
    for p in args.add:
        real = os.path.realpath(p)
        if not os.path.isfile(real):
            sys.exit("update_run: --add không phải file: " + p)
        if real not in known and real not in added:
            added.append(real)
    meta["targets"] = list(meta["targets"]) + added
    run_dir = os.path.realpath(run) + os.sep  # the glossary copy in src/ctx/ is a cache, even when reports/ sits inside the GDD repo
    tracked = [os.path.realpath(p) for p in meta["targets"]] + [
        os.path.realpath(p) for p in meta.get("context", [])
        if os.path.realpath(p).startswith(gdd) and not os.path.realpath(p).startswith(run_dir)]
    missing = [p for p in tracked if not os.path.exists(p)]
    if missing:
        sys.exit("update_run: GDD không còn ở path cũ (đổi tên/xoá) — hỏi user:\n  " + "\n  ".join(missing))

    if any(os.sep + "ctx" + os.sep in os.path.realpath(p) for p in meta.get("context", [])) and not meta.get("glossary"):
        sys.exit("update_run: run.json thiếu \"glossary\" (run cũ) — điền key gdd.glossary của CLAUDE.md vào run.json rồi chạy lại")
    base, head = base_commit(gdd, run, meta), git(gdd, "rev-parse", "HEAD").strip()
    diff_names = {os.path.realpath(os.path.join(gdd, n)) for n in git(gdd, "diff", "--name-only", base, "--").split("\n") if n} if base else set(tracked)
    changed = {}
    reviewed = meta.get("sourceHashes", {})
    for path in tracked:
        if path in diff_names and reviewed.get(path) != sha(path):
            heads = changed_headings(gdd, base, path)
            if heads is None or heads:
                changed[path] = heads
    for path in added:
        changed[path] = None
    if meta.get("glossary"):
        glossary = os.path.realpath(os.path.join(gdd, meta["glossary"]))
        copy = os.path.realpath(os.path.join(run, "src", "ctx", os.path.basename(glossary) + ".txt"))
        if glossary in diff_names and copy in [os.path.realpath(p) for p in meta.get("context", [])]:
            changed[copy] = None
    targets = {os.path.realpath(p) for p in meta["targets"]}
    report = {"base": base, "head": head, "changedFiles": sorted(changed), "addedFiles": added,
              "unchangedTargets": len(targets - set(changed))}
    if not changed and not args.force:
        print(json.dumps(dict(report, refreshed=False), ensure_ascii=False, indent=1))
        return

    archived = archive_work(run)
    os.makedirs(os.path.join(run, "data", "work"), exist_ok=True)
    if os.path.exists(os.path.join(run, "data", "questions.json")):
        shutil.copyfile(os.path.join(run, "data", "questions.json"), os.path.join(run, "data", "work", "questions.prev.json"))
    prev_src = os.path.join(run, "src", "prev")
    if os.path.isdir(prev_src):
        shutil.rmtree(prev_src)
    new_src = os.path.join(run, "src", "new")
    if os.path.isdir(new_src):  # src/ is a cache rebuilt below; a run restored from gdd-report.md has none
        shutil.move(new_src, prev_src)

    mode = meta.get("contextMode") or ("links" if meta.get("context") else "none")
    cmd = [os.path.join(HERE, "collect_sources.py"), "--gdd", gdd, "--run", run, "--context", mode]
    for extra in meta.get("extra", []):
        cmd += ["--extra", extra]
    if meta.get("glossary"):
        cmd += ["--glossary", meta["glossary"]]
    sources = json.loads(step(*(cmd + meta["targets"])))
    save(os.path.join(run, "data", "sources.json"), sources)
    today = datetime.date.today().isoformat()
    meta.update(targets=sources["targets"], context=sources["context"], contextMode=mode, gddCommit=head, date=today,
                sourceHashes={os.path.realpath(p): sha(p) for p in sources["targets"] + sources["context"]})
    if added and len(meta["targets"]) > 1:
        meta.setdefault("new", {})["note"] = "%d GDD" % len(meta["targets"])
    if not args.verify:
        note = "Cập nhật %s theo GDD commit %s: %d GDD có thay đổi được review lại" % (today, head[:7], len(changed) - len(added))
        note += ("; thêm %d GDD mới vào report." % len(added)) if added else "."
        meta["notes"] = [n for n in meta.get("notes", []) if not n.startswith("Cập nhật ")] + [note]
    save(meta_path, meta)
    step(os.path.join(HERE, "prepare.py"), run)
    step(os.path.join(HERE, "build_inventory.py"), run)

    modules = {m["file"]: m for m in load(os.path.join(run, "data", "inventory.json"))["modules"] if m.get("file")}
    report["changedModules"] = {modules[p]["key"]: (heads if heads is not None else "*")
                                for p, heads in changed.items() if p in modules}
    report.update(refreshed=True, archived=archived, mode="verify" if args.verify else "update")
    save(os.path.join(run, "data", "work", "update.json"), report)
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
