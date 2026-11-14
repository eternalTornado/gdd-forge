import json
import os
import sys

TOOLKIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, os.pardir, "shared", "report-toolkit", "scripts")
sys.path.insert(0, os.path.realpath(TOOLKIT))

from prepare_source import clean, read_text  # noqa: E402

MARKER = "===== FILE: "


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class Combined:
    """Rebuilds the line layout prepare_source.py used, so a global line maps to a page and to a file line."""

    def __init__(self, run):
        self.run = run
        meta = load(os.path.join(run, "data", "run.json"))
        self.lines_per_page = int(meta.get("linesPerPage", 50))
        source = load(os.path.join(run, "src", "new", "source.json"))
        self.paths = source.get("paths") or [source["path"]]
        self.files = []
        if len(self.paths) == 1:
            text = clean(read_text(self.paths[0]))
            if "\f" in text:
                sys.exit("gddsource: form feed in source, page layout differs from line split")
            self.lines = text.rstrip("\n").split("\n")
            self.files.append({"path": self.paths[0], "start": 0, "offset": 1, "count": len(self.lines)})
            return
        chunks, cursor = [], 0
        for path in self.paths:
            content = clean(read_text(path))
            chunk = MARKER + os.path.relpath(path) + " =====\n" + content
            count = chunk.count("\n") + 1
            self.files.append({"path": path, "start": cursor, "offset": 0, "count": count})
            chunks.append(chunk)
            cursor += count
        self.lines = "\n".join(chunks).rstrip("\n").split("\n")
        for f in self.files:
            if not self.lines[f["start"]].startswith(MARKER):
                sys.exit("gddsource: file marker not at line %d for %s" % (f["start"], f["path"]))

    def page_of(self, line):
        return line // self.lines_per_page + 1

    def file_of(self, line):
        hit = None
        for f in self.files:
            if f["start"] <= line:
                hit = f
        return hit

    def file_line(self, line):
        f = self.file_of(line)
        return f, line - f["start"] + f["offset"]

    def body_range(self, f):
        first = f["start"] + (1 if f["offset"] == 0 else 0)
        return first, min(f["start"] + f["count"], len(self.lines))
