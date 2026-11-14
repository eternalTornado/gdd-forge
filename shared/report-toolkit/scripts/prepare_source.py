import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from xml.etree import ElementTree

FORMATS = {".pdf": "pdf", ".md": "md", ".markdown": "md", ".txt": "txt", ".html": "html", ".htm": "html", ".docx": "docx"}
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"))
TOOL_DIRS = ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin")
PAGE_FILE = re.compile(r"^p\d+\.txt$")

HTML_SKIP = {"script", "style", "noscript", "template"}
HTML_VOID_BREAK = {"br", "hr"}
HTML_BLOCK = {
    "address", "article", "aside", "blockquote", "caption", "dd", "details", "div", "dl", "dt",
    "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "header", "li", "main", "nav", "ol", "p", "section", "summary", "table", "tbody", "tfoot",
    "thead", "title", "tr", "ul",
}
HTML_CELL = {"td", "th"}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MC_FALLBACK = "{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback"
DOCX_SKIP = {W + "pPr", W + "rPr", W + "tcPr", W + "trPr", W + "tblPr", W + "tblGrid", W + "sdtPr", MC_FALLBACK}
DOCX_CONTAINERS = {W + "sdt", W + "sdtContent", W + "customXml", W + "smartTag"}
DOCX_OFF = {"0", "false", "off"}


def fail(message):
    sys.exit("prepare_source: " + message)


def tool(name):
    found = shutil.which(name)
    if found:
        return found
    for folder in TOOL_DIRS:
        candidate = os.path.join(folder, name)
        if os.access(candidate, os.X_OK):
            return candidate
    fail(name + " not found (install poppler)")


def run(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        fail(" ".join(cmd[:1]) + " failed: " + proc.stderr.decode("utf-8", "replace").strip())
    return proc.stdout


def clean(text):
    return text.translate(ZERO_WIDTH).replace("\r\n", "\n").replace("\r", "\n")


def pdf_pages(path):
    info = run([tool("pdfinfo"), path]).decode("utf-8", "replace")
    match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    if not match:
        fail("pdfinfo did not report a page count")
    pdftotext = tool("pdftotext")
    pages = []
    for n in range(1, int(match.group(1)) + 1):
        raw = run([pdftotext, "-raw", "-enc", "UTF-8", "-f", str(n), "-l", str(n), path, "-"])
        pages.append(clean(raw.decode("utf-8")).replace("\f", ""))
    return pages


def read_text(path):
    with open(path, "rb") as handle:
        data = handle.read()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        fail("input is not valid UTF-8: " + str(error))


class HtmlText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.last = "\n"
        self.skip = 0
        self.pre = 0

    def emit(self, text):
        if text:
            self.parts.append(text)
            self.last = text[-1]

    def block(self):
        if self.last != "\n":
            self.emit("\n")

    def handle_starttag(self, tag, attrs):
        if tag in HTML_SKIP:
            self.skip += 1
        elif tag == "pre":
            self.pre += 1
            self.block()
        elif tag in HTML_BLOCK:
            self.block()
        elif tag in HTML_VOID_BREAK:
            self.emit("\n")

    def handle_endtag(self, tag):
        if tag in HTML_SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag == "pre":
            self.pre = max(0, self.pre - 1)
            self.block()
        elif tag in HTML_BLOCK:
            self.block()
        elif tag in HTML_CELL:
            self.emit("\t")

    def handle_data(self, data):
        if self.skip:
            return
        if self.pre:
            self.emit(data)
            return
        text = re.sub(r"\s+", " ", data)
        self.emit(text.lstrip(" ") if self.last in "\n\t" else text)


def html_text(path):
    parser = HtmlText()
    parser.feed(clean(read_text(path)))
    parser.close()
    lines = [line.rstrip() for line in "".join(parser.parts).split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip("\n")


def docx_runs(element):
    out = []
    for child in element:
        tag = child.tag
        if tag in DOCX_SKIP:
            continue
        if tag == W + "t":
            out.append(child.text or "")
        elif tag == W + "tab":
            out.append("\t")
        elif tag == W + "br":
            out.append("\f" if child.get(W + "type") == "page" else "\n")
        elif tag == W + "cr":
            out.append("\n")
        elif tag == W + "noBreakHyphen":
            out.append("-")
        elif tag == W + "p":
            out.append("\n" + docx_paragraph(child))
        else:
            out.append(docx_runs(child))
    return "".join(out)


def docx_paragraph(paragraph):
    props = paragraph.find(W + "pPr")
    marker = props.find(W + "pageBreakBefore") if props is not None else None
    head = "\f" if marker is not None and marker.get(W + "val") not in DOCX_OFF else ""
    return head + docx_runs(paragraph)


def docx_lines(element):
    lines = []
    for child in element:
        if child.tag == W + "p":
            lines.append(docx_paragraph(child))
        elif child.tag == W + "tbl":
            for row in child.findall(W + "tr"):
                cells = [" ".join(line for line in docx_lines(cell) if line.strip()) for cell in row.findall(W + "tc")]
                lines.append("\t".join(cells))
        elif child.tag in DOCX_CONTAINERS:
            lines.extend(docx_lines(child))
    return lines


def docx_text(path):
    try:
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError) as error:
        fail("cannot read docx: " + str(error))
    body = root.find(W + "body")
    return clean("\n".join(docx_lines(body if body is not None else root)))


def split_pages(text, lines_per_page):
    if "\f" in text:
        pages = text.split("\f")
        if not pages[-1].strip():
            pages.pop()
    else:
        lines = text.rstrip("\n").split("\n")
        pages = ["\n".join(lines[i:i + lines_per_page]) for i in range(0, len(lines), lines_per_page)]
    return [page.strip("\n") for page in pages]


def extract(path, fmt, lines_per_page):
    if fmt == "pdf":
        return pdf_pages(path)
    if fmt == "html":
        text = html_text(path)
    elif fmt == "docx":
        text = docx_text(path)
    else:
        text = clean(read_text(path))
    if not text.strip():
        fail("no text extracted from " + path)
    return split_pages(text, lines_per_page)


def with_newline(text):
    return text if not text or text.endswith("\n") else text + "\n"


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main():
    parser = argparse.ArgumentParser(description="Normalize a requirement document into per-page UTF-8 text.")
    parser.add_argument("--in", dest="sources", action="append", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--short")
    parser.add_argument("--lines-per-page", type=int, default=50)
    args = parser.parse_args()

    sources = [os.path.realpath(path) for path in args.sources]
    for path in sources:
        if not os.path.isfile(path):
            fail("input not found: " + path)
    if not args.label.strip():
        fail("--label must not be empty")
    if args.lines_per_page < 1:
        fail("--lines-per-page must be >= 1")
    formats = [FORMATS.get(os.path.splitext(path)[1].lower()) for path in sources]
    for path, fmt in zip(sources, formats):
        if fmt is None:
            fail("unsupported format: " + path + " (expected " + ", ".join(sorted(FORMATS)) + ")")

    if len(sources) == 1:
        fmt = formats[0]
        pages = [with_newline(page) for page in extract(sources[0], fmt, args.lines_per_page)]
    else:
        if any(fmt not in ("md", "txt") for fmt in formats):
            fail("several inputs must all be .md/.markdown/.txt")
        fmt = "md"
        text = "\n".join("===== FILE: %s =====\n%s" % (os.path.relpath(path), clean(read_text(path))) for path in sources)
        pages = [with_newline(page) for page in split_pages(text, args.lines_per_page)]
    if not pages:
        fail("no pages extracted from " + ", ".join(sources))
    if not any(page.strip() for page in pages):
        print("prepare_source: warning: every page is empty (scanned document?)", file=sys.stderr)

    out = os.path.realpath(args.out)
    pages_dir = os.path.join(out, "pages")
    os.makedirs(pages_dir, exist_ok=True)
    for name in os.listdir(pages_dir):
        if PAGE_FILE.match(name):
            os.remove(os.path.join(pages_dir, name))
    width = max(3, len(str(len(pages))))
    for n, page in enumerate(pages, 1):
        write(os.path.join(pages_dir, "p%0*d.txt" % (width, n)), page)
    write(os.path.join(out, "full.txt"), "".join("===== PAGE %d =====\n%s" % (n, page) for n, page in enumerate(pages, 1)))

    hasher = hashlib.sha256()
    for path in sources:
        with open(path, "rb") as handle:
            hasher.update(handle.read())
    digest = hasher.hexdigest()
    short = args.short if args.short else args.label
    meta = {"label": args.label, "short": short, "path": sources[0], "format": fmt, "sha256": digest, "pages": len(pages), "unit": "page"}
    if len(sources) > 1:
        meta["paths"] = sources
    write(os.path.join(out, "source.json"), json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"label": args.label, "pages": len(pages), "out": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
