import html
import json
import os
import re
import sys

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "templates", "audit-report.html")
STYLE = re.compile(r"<style>.*?</style>", re.S)
CODE = re.compile(r"`([^`]+)`")

PRIORITIES = [("high", "Cao", "#d93025"), ("mid", "Trung bình", "#f9ab00"), ("low", "Thấp", "#9aa0a6")]
PRIO_LABEL = {k: label for k, label, _ in PRIORITIES}
PRIO_RANK = {k: i for i, (k, _, _) in enumerate(PRIORITIES)}
DIFF_KINDS = [("added", "Thêm", "thêm", "var(--k-add)"), ("modified", "Sửa", "sửa", "var(--k-mod)"), ("removed", "Bỏ", "bỏ", "var(--k-rem)")]
DIFF_LABEL = {k: label for k, label, _, _ in DIFF_KINDS}
ROW_LABEL = {"added": "Thêm", "removed": "Bỏ", "changed": "Sửa", "unchanged": "Giữ nguyên"}
ENDPOINT_KINDS = [("new", "Mới"), ("changed", "Có thay đổi"), ("desc", "Chỉ đổi mô tả"), ("unchanged", "Giữ nguyên"), ("removed", "Bị bỏ")]
STATUS_PHRASE = {"new": "mới", "changed": "có thay đổi", "desc": "chỉ đổi mô tả", "removed": "bị bỏ"}

DEF_ENDPOINT = "Đếm theo API. 'Có thay đổi': parameter, kiểu hoặc quy tắc đổi. 'Chỉ đổi mô tả': chỉ đổi chữ, đơn vị hoặc ví dụ."
DEF_ENDPOINT_SINGLE = "Đếm theo API trong tài liệu."
DEF_ITEMS = "Đếm theo từng nội dung cụ thể trong tài liệu (một field, một dòng bảng, một quy tắc). Một endpoint có thể có nhiều điểm; chi tiết ở mục 3."
DEF_QUESTIONS = "Mức ưu tiên là đánh giá của nhóm phân tích: Cao — đổi request/response hoặc việc cấp/trừ tài nguyên; Trung bình — đổi quy tắc kiểm tra form; Thấp — lỗi trình bày tài liệu."
DEFAULT_LABELS = {
    "questions": "Câu hỏi cho Backend",
    "unit": "Endpoint",
    "unitBreakdown": "Module",
    "unitDef": DEF_ENDPOINT_SINGLE,
    "priorityDef": DEF_QUESTIONS,
    "evidence": "Tài liệu ghi",
    "figure": "Hình 1 — Câu hỏi theo module",
}

ROW_LEGEND = (
    '<div class="rowlegend"><span><span class="sw sw-added"></span>Thêm</span>'
    '<span><span class="sw sw-removed"></span>Bỏ (<span class="strike">gạch ngang</span>)</span>'
    '<span><span class="sw sw-changed"></span>Sửa</span>'
    '<span><span class="sw sw-cell"></span>Ô khác nhau giữa hai bản</span>'
    '<span><span class="sw sw-unchanged"></span>Giữ nguyên (chữ xám)</span>'
    '<span><code>—</code> không có</span></div>'
)
COLGROUP = '<colgroup><col class="c-key"><col class="c-side"><col class="c-side"><col class="c-chg"></colgroup>'
NONE = '<span class="none">—</span>'


def esc(value):
    return html.escape(value or "", quote=True)


def rich(value):
    return CODE.sub(r"<code>\1</code>", esc(value))


def load_style():
    with open(TEMPLATE, encoding="utf-8") as handle:
        match = STYLE.search(handle.read())
    if not match:
        sys.exit("render_audit: no <style> block in " + TEMPLATE)
    return match.group(0)


def width(n, top):
    return "%.1f" % (n / top * 55) if top else "0.0"


def dot(color):
    return '<span class="dot" style="background:%s"></span>' % color


def kpi(key, label, total, items, definition, dots):
    parts = ['<div class="kpi" data-kpi="%s"><div class="l">%s</div><div class="v">%d</div><div class="bd">' % (key, label, total)]
    for name, n, color in items:
        mark = dot(color) if dots else ""
        parts.append('<span class="bi" data-label="%s" data-n="%d">%s%s <b>%d</b></span>' % (esc(name), n, mark, esc(name), n))
    parts.append('</div><p class="def">%s</p></div>' % esc(definition))
    return "".join(parts)


class Report:
    def __init__(self, audit):
        self.meta = audit["meta"]
        self.single = self.meta.get("mode") == "single"
        self.labels = {**DEFAULT_LABELS, **(self.meta.get("labels") or {})}
        self.scope = audit.get("scope") if (audit.get("scope") or {}).get("rows") else None
        self.modules = audit["modules"]
        self.questions = audit.get("questions", [])
        self.diffs = [] if self.single else audit.get("diffs", [])
        self.by_module = {m["key"]: [] for m in self.modules}
        for q in self.questions:
            self.by_module.setdefault(q["module"], []).append(q)
        for key in self.by_module:
            self.by_module[key].sort(key=lambda q: (PRIO_RANK.get(q["priority"], 9), q["id"]))
        self.diff_module = {m["key"]: [] for m in self.modules}
        for d in self.diffs:
            self.diff_module.setdefault(d["module"], []).append(d)
        self.q_modules = [m for m in self.modules if self.by_module[m["key"]]]
        self.d_modules = [m for m in self.modules if self.diff_module[m["key"]]]

    def title(self):
        if self.meta.get("title"):
            return self.meta["title"]
        label = self.meta["new"]["label"]
        questions = self.labels["questions"]
        return label + (" — " + questions if self.single else " — Thay đổi giữa hai phiên bản và " + questions[:1].lower() + questions[1:])

    def subtitle(self):
        def side(doc):
            return doc["label"] + (" (%s)" % doc["note"] if doc.get("note") else "")
        head = side(self.meta["new"])
        if not self.single:
            head = side(self.meta["old"]) + " → " + head
        return head + " · " + self.meta["date"]

    def toc(self):
        parts = ['<nav class="toc" aria-label="Mục lục"><div class="toc-title">Mục lục</div><ol>',
                 '<li><a href="#tong-quan">1. Tổng quan</a></li>',
                 '<li><a href="#cau-hoi">2. %s</a> <span class="cnt">%d</span>' % (esc(self.labels["questions"]), len(self.questions))]
        if self.q_modules:
            parts.append("<ol>")
            for m in self.q_modules:
                parts.append('<li><a href="#q-%s">%s</a> <span class="cnt">%d</span></li>' % (esc(m["key"]), rich(m["short"]), len(self.by_module[m["key"]])))
            parts.append("</ol>")
        parts.append("</li>")
        if not self.single:
            parts.append('<li><a href="#khac-biet">3. Khác biệt theo module</a> <span class="cnt">%d</span>' % len(self.diffs))
            if self.d_modules:
                parts.append("<ol>")
                for m in self.d_modules:
                    parts.append('<li><a href="#m-%s">%s</a> <span class="cnt">%d</span></li>' % (esc(m["key"]), rich(m["short"]), len(self.diff_module[m["key"]])))
                parts.append("</ol>")
            parts.append("</li>")
        if self.scope:
            parts.append('<li><a href="#ngoai-pham-vi">%d. %s</a> <span class="cnt">%d</span></li>'
                         % (self.scope_number(), rich(self.scope["title"]), len(self.scope["rows"])))
        if self.meta.get("notes"):
            parts.append('<li><a href="#ghi-chu">Ghi chú</a></li>')
        parts.append("</ol></nav>")
        return "".join(parts)

    def endpoint_counts(self):
        override = self.meta.get("kpiOverride")
        if override:
            counts = {k: int(override.get(k, 0)) for k, _ in ENDPOINT_KINDS}
            return int(override.get("total", sum(counts.values()))), counts
        counts = {k: 0 for k, _ in ENDPOINT_KINDS}
        for m in self.modules:
            for ep in m.get("endpoints", []):
                counts[ep["status"]] = counts.get(ep["status"], 0) + 1
        return sum(counts.values()), counts

    def module_endpoints(self, module):
        override = (self.meta.get("kpiOverride") or {}).get("modules") or {}
        return int(override.get(module["key"], len(module.get("endpoints", []))))

    def kpis(self):
        total, counts = self.endpoint_counts()
        if self.single:
            items = [(self.labels["unitBreakdown"], len(self.modules), None)]
            parts = [kpi("endpoint", self.labels["unit"], total, items, self.labels["unitDef"], False)]
        else:
            items = [(label, counts[k], None) for k, label in ENDPOINT_KINDS if k != "removed" or counts[k] > 0]
            parts = [kpi("endpoint", self.labels["unit"], total, items, DEF_ENDPOINT, False)]
            kinds = [(label, sum(1 for d in self.diffs if d["kind"] == k), color) for k, label, _, color in DIFF_KINDS]
            parts.append(kpi("items", "Điểm khác biệt", len(self.diffs), kinds, DEF_ITEMS, True))
        prios = [(label, sum(1 for q in self.questions if q["priority"] == k), color) for k, label, color in PRIORITIES]
        parts.append(kpi("questions", self.labels["questions"], len(self.questions), prios, self.labels["priorityDef"], True))
        return '<div class="kpis">' + "".join(parts) + "</div>"

    def figure_row(self, module, n, top, segs, attrs, aria, sub):
        bar = "".join('<span class="seg %s" style="flex:%d%s" title="%s %d"></span>' % (cls, k, extra, esc(label), k) for cls, k, extra, label in segs if k)
        return ('<div class="frow" data-module="%s"%s><div class="fl">%s</div><div class="ftrack">'
                '<div class="hbar" style="width:%s%%" role="img" aria-label="%s">%s</div>'
                '<span class="fend"><span class="n">%d</span> <span class="sub">%s</span></span></div></div>'
                % (esc(module["key"]), attrs, rich(module["title"]), width(n, top), esc(aria), bar, n, esc(sub)))

    def figure(self):
        if self.single:
            return self.figure_single()
        rows = []
        top = max([len(self.diff_module[m["key"]]) for m in self.d_modules] or [0])
        for m in self.d_modules:
            ds = self.diff_module[m["key"]]
            n = len(ds)
            nq = len(self.by_module[m["key"]])
            k = {kind: sum(1 for d in ds if d["kind"] == kind) for kind, _, _, _ in DIFF_KINDS}
            words = ", ".join("%s %d" % (word, k[kind]) for kind, _, word, _ in DIFF_KINDS if k[kind])
            attrs = ' data-items="%d" data-added="%d" data-modified="%d" data-removed="%d" data-questions="%d"' % (n, k["added"], k["modified"], k["removed"], nq)
            sub = "(%s)" % words + (" · %d câu hỏi" % nq if nq else "")
            segs = [("seg-" + kind, k[kind], "", label) for kind, label, _, _ in DIFF_KINDS]
            rows.append(self.figure_row(m, n, top, segs, attrs, "%d điểm: %s" % (n, words), sub))
        rest = [m for m in self.modules if not self.diff_module[m["key"]]]
        if rest:
            items = [rich(m["title"]) + (" · %d câu hỏi" % len(self.by_module[m["key"]]) if self.by_module[m["key"]] else "") for m in rest]
            rows.append('<p class="fnone">Không thay đổi: %s</p>' % "; ".join(items))
        legend = "".join("<span>%s%s</span>" % (dot(color), label) for _, label, _, color in DIFF_KINDS)
        return ('<div class="exhibit" id="hinh-1"><p class="ex-title">Hình 1 — Điểm khác biệt theo module</p><div class="fig">%s</div>'
                '<div class="legend">%s</div></div>' % ("".join(rows), legend))

    def figure_single(self):
        rows = []
        top = max([len(self.by_module[m["key"]]) for m in self.q_modules] or [0])
        for m in self.q_modules:
            qs = self.by_module[m["key"]]
            n = len(qs)
            k = {key: sum(1 for q in qs if q["priority"] == key) for key, _, _ in PRIORITIES}
            words = ", ".join("%s %d" % (label.lower(), k[key]) for key, label, _ in PRIORITIES if k[key])
            attrs = ' data-questions="%d" data-high="%d" data-mid="%d" data-low="%d"' % (n, k["high"], k["mid"], k["low"])
            segs = [("seg-" + key, k[key], ";background:" + color, label) for key, label, color in PRIORITIES]
            rows.append(self.figure_row(m, n, top, segs, attrs, "%d câu hỏi: %s" % (n, words), "(%s)" % words))
        rest = [m for m in self.modules if not self.by_module[m["key"]]]
        if rest:
            rows.append('<p class="fnone">Không có câu hỏi: %s</p>' % "; ".join(rich(m["title"]) for m in rest))
        legend = "".join("<span>%s%s</span>" % (dot(color), label) for _, label, color in PRIORITIES)
        return ('<div class="exhibit" id="hinh-1"><p class="ex-title">%s</p><div class="fig">%s</div>'
                '<div class="legend">%s</div></div>' % (esc(self.labels["figure"]), "".join(rows), legend))

    def question(self, q):
        prio = PRIO_LABEL[q["priority"]]
        ev = []
        for e in q["evidence"]:
            chip = e.get("loc") or "tr. %s" % e["page"]
            if e.get("src", "new") != "new":
                chip += " · bản cũ"
            ev.append('<div class="evrow"><span class="pchip">%s</span><div class="qline"><span class="q" data-src="%s">%s</span></div></div>'
                      % (esc(chip), esc(e.get("src", "new")), esc(e["quote"])))
        return ('<article class="qcard" id="%s" data-priority="%s"><div class="qhead"><span class="qid">%s</span>'
                '<span class="prio p-%s">%s</span><span class="cat">%s</span><span class="api">%s</span></div>'
                '<div class="qtitle">%s</div><dl class="qbody"><dt>Vấn đề</dt><dd class="issue">%s</dd>'
                '<dt>%s</dt><dd class="ev">%s</dd><dt>Câu hỏi</dt><dd class="ask">%s</dd></dl></article>'
                % (esc(q["id"].lower()), esc(prio), esc(q["id"]), q["priority"], esc(prio), esc(q["category"]), rich(q.get("api")),
                   rich(q["title"]), rich(q["issue"]), esc(self.labels["evidence"]), "".join(ev), rich(q["ask"])))

    def questions_section(self):
        lines = ['<section id="cau-hoi"><h2>2. %s</h2>' % esc(self.labels["questions"])]
        for m in self.q_modules:
            qs = self.by_module[m["key"]]
            lines.append('<h3 id="q-%s">%s <span class="cnt">· %d câu hỏi</span></h3>' % (esc(m["key"]), rich(m["title"]), len(qs)))
            lines.extend(self.question(q) for q in qs)
        lines.append("</section>")
        return lines

    @staticmethod
    def cell(items, src):
        if items is None:
            return "<td>%s</td>" % NONE
        parts = []
        for it in items:
            label = '<span class="cl">%s:</span> ' % esc(it["label"]) if it.get("label") is not None else ""
            value = NONE if it.get("value") is None else '<span class="q" data-src="%s">%s</span>' % (src, esc(it["value"]))
            gloss = '<div class="gloss"><span class="gl">Dịch nghĩa:</span> %s</div>' % esc(it["gloss"]) if it.get("gloss") else ""
            cls = "cv cc" if it.get("changed") else "cv"
            parts.append('<div class="%s">%s<span class="cvv">%s</span>%s</div>' % (cls, label, value, gloss))
        return "<td>%s</td>" % "".join(parts)

    def pages_head(self, side, pages):
        return "Bản %s %s (%s)" % ("cũ" if side == "old" else "mới", self.meta[side]["short"], pages if pages else "không có")

    def table(self, n, d):
        tag = '<span class="tag">%s</span>' % rich(d["tag"]) if d.get("tag") else ""
        rows = []
        for r in d["rows"]:
            key_cls = "key plain" if r.get("plainKey") else "key"
            note = '<div class="rnote">%s</div>' % rich(r["note"]) if r.get("note") else ""
            rows.append('<tr class="r-%s"><td class="%s">%s</td>%s%s<td><span class="kbadge kb-%s">%s</span>%s</td></tr>'
                        % (r["kind"], key_cls, esc(r["key"]), self.cell(r.get("old"), "old"), self.cell(r.get("new"), "new"),
                           r["kind"], ROW_LABEL[r["kind"]], note))
        return ('<div class="dtable" id="t-%d" data-table="%d" data-module="%s" data-kind="%s" data-rows="%d">'
                '<div class="dhead"><span class="no">3.%d</span><span class="lbl">%s</span><span class="kbadge kb-%s">%s</span>%s</div>'
                '<div class="tablewrap"><table class="dt">%s<thead><tr><th>Thuộc tính</th><th>%s</th><th>%s</th><th>Thay đổi</th></tr></thead>'
                '<tbody>%s</tbody></table></div></div>'
                % (n, n, esc(d["module"]), d["kind"], len(d["rows"]), n, rich(d["label"]), d["kind"], DIFF_LABEL[d["kind"]], tag,
                   COLGROUP, esc(self.pages_head("old", d.get("oldPages"))), esc(self.pages_head("new", d.get("newPages"))), "".join(rows)))

    def heading(self, m):
        if m.get("heading"):
            return m["heading"]
        changed = [ep for ep in m.get("endpoints", []) if ep["status"] != "unchanged"]
        return ", ".join("`%s` %s" % (ep["path"], STATUS_PHRASE[ep["status"]]) for ep in changed)

    def diff_section(self):
        lines = ['<section id="khac-biet"><h2>3. Khác biệt theo module</h2>', ROW_LEGEND]
        n = 0
        for m in self.d_modules:
            heading = self.heading(m)
            eps = ' <span class="eps">· %s</span>' % rich(heading) if heading else ""
            lines.append('<h3 id="m-%s">%s%s</h3>' % (esc(m["key"]), rich(m["short"]), eps))
            note = '<p class="note">%s</p>' % rich(m["diffNote"]) if m.get("diffNote") else ""
            for i, d in enumerate(self.diff_module[m["key"]]):
                n += 1
                lines.append((note if i == 0 else "") + self.table(n, d))
        rest = [m for m in self.modules if not self.diff_module[m["key"]]]
        if rest:
            items = ["%s (%d%s)" % (rich(m["short"]), self.module_endpoints(m), " endpoint" if i == 0 else "") for i, m in enumerate(rest)]
            lines.append('<p class="unchanged-mods" id="khong-thay-doi">Không thay đổi: %s</p>' % ", ".join(items))
        lines.append("</section>")
        return lines

    def scope_number(self):
        return 3 if self.single else 4

    def evidence_rows(self, evidence):
        rows = []
        for e in evidence:
            chip = e.get("loc") or "tr. %s" % e["page"]
            rows.append('<div class="evrow"><span class="pchip">%s</span><div class="qline"><span class="q" data-src="new">%s</span></div></div>'
                        % (esc(chip), esc(e["quote"])))
        return "".join(rows)

    def scope_section(self):
        rows = "".join('<tr data-module="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                       % (esc(r["module"]), rich(r["doc"]), rich(", ".join(r["sections"])), esc(", ".join(r.get("kinds", []))),
                          self.evidence_rows(r["evidence"])) for r in self.scope["rows"])
        intro = '<p class="note">%s</p>' % rich(self.scope["intro"]) if self.scope.get("intro") else ""
        return ['<section id="ngoai-pham-vi"><h2>%d. %s</h2>%s' % (self.scope_number(), rich(self.scope["title"]), intro),
                '<div class="tablewrap"><table><thead><tr><th>GDD</th><th>Mục</th><th>Loại nội dung</th><th>GDD ghi</th></tr></thead>'
                '<tbody>%s</tbody></table></div></section>' % rows]

    def render(self, style):
        lines = [
            "<!doctype html>", '<html lang="vi">', "<head>", '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % esc(self.title()), style, "</head>", "<body>", '<div class="layout">',
            self.toc(), "<main>", '<header class="top">', "<h1>%s</h1>" % esc(self.title()),
            '<p class="subtitle">%s</p>' % esc(self.subtitle()), "</header>",
            '<section id="tong-quan"><h2>1. Tổng quan</h2>', self.kpis(), self.figure(), "</section>",
        ]
        lines.extend(self.questions_section())
        if not self.single:
            lines.extend(self.diff_section())
        if self.scope:
            lines.extend(self.scope_section())
        if self.meta.get("notes"):
            notes = "".join("<li>%s</li>" % rich(n) for n in self.meta["notes"])
            lines.append('<footer class="notes" id="ghi-chu"><p class="nt">Ghi chú</p><ul>%s</ul></footer>' % notes)
        lines.extend(["</main>", "</div>", "</body>", "</html>"])
        return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: render_audit.py <audit.json> <out.html>")
    with open(sys.argv[1], encoding="utf-8") as handle:
        audit = json.load(handle)
    out = Report(audit).render(load_style())
    folder = os.path.dirname(os.path.abspath(sys.argv[2]))
    os.makedirs(folder, exist_ok=True)
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as handle:
        handle.write(out)
    print(json.dumps({"out": os.path.abspath(sys.argv[2]), "bytes": len(out.encode("utf-8"))}))


if __name__ == "__main__":
    main()
