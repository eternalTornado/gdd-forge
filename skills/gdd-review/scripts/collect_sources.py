import argparse
import json
import os
import re
import shutil
import sys

WIKI = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


def keep_dir(root, folder, name):
    """Skip dot dirs and the root `reports/` (gdd-review writes gdd-report.md there when the GDD repo hosts the skill)."""
    return not name.startswith(".") and not (name == "reports" and os.path.realpath(folder) == root)


def index(root):
    by_stem = {}
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if keep_dir(root, folder, d)]
        for name in files:
            if name.endswith(".md"):
                by_stem.setdefault(os.path.splitext(name)[0].lower(), []).append(os.path.realpath(os.path.join(folder, name)))
    return by_stem


def expand(root, items):
    out = []
    for item in items:
        path = os.path.realpath(item if os.path.isabs(item) or os.path.exists(item) else os.path.join(root, item))
        if os.path.isdir(path):
            for folder, dirs, files in os.walk(path):
                dirs[:] = sorted(d for d in dirs if keep_dir(root, folder, d))
                out.extend(os.path.join(folder, f) for f in sorted(files) if f.endswith(".md"))
        elif os.path.isfile(path):
            out.append(path)
        else:
            sys.exit("collect_sources: not found: " + item)
    seen, uniq = set(), []
    for p in map(os.path.realpath, out):
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def main():
    parser = argparse.ArgumentParser(description="Targets + one level of [[wiki-link]] context + glossary for a GDD review run.")
    parser.add_argument("--gdd", required=True, help="GDD repo root")
    parser.add_argument("--run", required=True, help="run dir; glossary copy goes to <run>/src/ctx/")
    parser.add_argument("--context", choices=("links", "none"), default="links")
    parser.add_argument("--extra", action="append", default=[], help="additional context file or folder")
    parser.add_argument("--glossary", help="glossary file, relative to --gdd (key gdd.glossary)")
    parser.add_argument("targets", nargs="+")
    args = parser.parse_args()

    root = os.path.realpath(os.path.expanduser(args.gdd))
    targets = expand(root, args.targets)
    if not targets:
        sys.exit("collect_sources: no .md target")
    context, unresolved = [], []
    if args.context == "links":
        by_stem = index(root)
        for target in targets:
            with open(target, encoding="utf-8") as handle:
                links = WIKI.findall(handle.read())
            for link in links:
                stem = os.path.splitext(link.strip())[0].lower()
                if stem == "glossary":
                    continue
                hits = by_stem.get(stem, [])
                if len(hits) == 1:
                    if hits[0] not in targets and hits[0] not in context:
                        context.append(hits[0])
                elif link.strip() not in unresolved:
                    unresolved.append(link.strip() + (" (ambiguous: %d files)" % len(hits) if hits else ""))
    for p in expand(root, args.extra):
        if p not in targets and p not in context:
            context.append(p)
    glossary = os.path.join(root, args.glossary) if args.glossary else None
    if args.context == "links" and glossary and os.path.isfile(glossary):
        ctx_dir = os.path.join(args.run, "src", "ctx")
        os.makedirs(ctx_dir, exist_ok=True)
        copy = os.path.join(ctx_dir, os.path.basename(glossary) + ".txt")
        shutil.copyfile(glossary, copy)
        context.append(os.path.realpath(copy))
    print(json.dumps({"targets": targets, "context": context, "unresolvedLinks": unresolved}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
