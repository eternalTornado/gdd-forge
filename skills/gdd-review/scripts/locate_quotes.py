import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gddsource import Combined, load  # noqa: E402

STRIP = dict.fromkeys(map(ord, "|*`"))
WS = re.compile(r"\s+")


def norm(text, tier):
    text = unicodedata.normalize("NFC" if tier == 1 else "NFKC", text).translate(STRIP)
    return WS.sub(" ", text).strip() if tier == 1 else WS.sub("", text)


def mapped(lines, first, tier):
    chars, owners, prev_space = [], [], False
    for offset, line in enumerate(lines):
        text = unicodedata.normalize("NFC" if tier == 1 else "NFKC", line).translate(STRIP) + "\n"
        for ch in text:
            if ch.isspace():
                if tier == 1 and chars and not prev_space:
                    chars.append(" ")
                    owners.append(first + offset)
                prev_space = True
                continue
            chars.append(ch)
            owners.append(first + offset)
            prev_space = False
    return "".join(chars), owners


def locate(combined, quote, page):
    lpp = combined.lines_per_page
    first = (page - 1) * lpp
    window = combined.lines[first:first + 2 * lpp]
    for tier in (1, 2):
        needle = norm(quote, tier)
        if not needle:
            return None
        text, owners = mapped(window, first, tier)
        at = text.find(needle)
        if at >= 0:
            return owners[at]
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: locate_quotes.py <run-dir>")
    run = sys.argv[1]
    combined = Combined(run)
    path = os.path.join(run, "data", "questions.json")
    data = load(path)
    found = missing = 0
    for q in data.get("questions", []):
        for ev in q.get("evidence", []):
            ev.pop("loc", None)
            if ev.get("src", "new") != "new":
                continue
            line = locate(combined, ev.get("quote", ""), int(ev.get("page", 0)))
            if line is None:
                missing += 1
                continue
            f, number = combined.file_line(line)
            ev["loc"] = "%s · L%d" % (os.path.basename(f["path"]), number)
            found += 1
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
    print(json.dumps({"located": found, "unlocated": missing}))


if __name__ == "__main__":
    main()
