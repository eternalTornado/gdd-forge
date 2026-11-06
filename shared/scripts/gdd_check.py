#!/usr/bin/env python3
"""gdd_check.py — deterministic checks for a gdd-forge v2 GDD folder.

Usage:
  python3 gdd_check.py <GDD dir> [--file <path>] [--changed]

  <GDD dir>   folder holding concept.md, decisions.md and systems/
  --file      report only findings for this document (path relative to the GDD dir or absolute)
  --changed   list decisions changed since the last git commit and the documents they affect

Exit codes: 0 = no errors, 1 = errors found, 2 = usage or missing folder.
Python 3.8+, stdlib only. Rules: shared/contracts/*.md and shared/writing-rules.md.
"""
import argparse
import os
import re
import subprocess
import sys

CONCEPT_BUDGET = 1000
SYSTEM_BUDGET = 1200
HARD_OVER = 1.2

CONCEPT_ORDER = ["Pitch", "Pillars", "Core Loop", "Target", "Experience", "References",
                 "Out of Scope", "Systems", "Glossary", "Open Questions"]
CONCEPT_REQUIRED = [h for h in CONCEPT_ORDER if h != "References"]
SYSTEM_ORDER = ["Purpose", "Rules", "Tunables", "States and Edge Cases", "Content",
                "UI Touchpoints", "Interactions", "Player-Observable Behaviors", "Open Questions"]
SYSTEM_REQUIRED = ["Purpose", "Rules", "Player-Observable Behaviors", "Open Questions"]
TYPES = {"mechanics", "progression", "economy", "level", "enemy-behavior", "ui-flow",
         "narrative", "presentation"}
TARGET_IDS = ["D-04", "D-05", "D-06", "D-09"]
KIT_WORDS = ["gdd-forge", "writing-rules", "writing rules", "dispatch", "checklist",
             "word budget", "(proposal)"]
NONE_CELLS = {"", "—", "-", "–", "none", "n/a"}

REF_RE = re.compile(r"→\s*([\w./-]+\.md)\s*§\s*(.+)")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+\S")
DTAG_RE = re.compile(r"\(D-\d+\)")


class Report:
    def __init__(self, only=None):
        self.items = []
        self.only = only

    def add(self, level, path, where, msg):
        if self.only and path != self.only:
            return
        self.items.append((level, path, where, msg))

    def errors(self):
        return sum(1 for i in self.items if i[0] == "ERROR")

    def warnings(self):
        return sum(1 for i in self.items if i[0] == "WARN")


class Doc:
    """A markdown document split into level-2 sections (code fences ignored)."""

    def __init__(self, root, rel):
        self.rel = rel
        self.path = os.path.join(root, rel)
        with open(self.path, encoding="utf-8") as f:
            self.text = f.read()
        self.title = None
        self.headings = []
        self.sections = {}
        current = None
        fence = False
        for line in self.text.splitlines():
            if line.strip().startswith("```"):
                fence = not fence
            if not fence and line.startswith("# ") and self.title is None:
                self.title = line[2:].strip()
                continue
            if not fence and line.startswith("## "):
                current = line[3:].strip()
                self.headings.append(current)
                self.sections.setdefault(current, [])
                continue
            if current is not None:
                self.sections[current].append(line)

    def words(self):
        return len(self.text.split())

    def section_text(self, name):
        return "\n".join(self.sections.get(name, []))

    def table(self, name):
        """First markdown table in a section → (header, rows); cells stripped."""
        lines = [l.strip() for l in self.sections.get(name, []) if l.strip().startswith("|")]
        if len(lines) < 2:
            return [], []
        split = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
        header = split(lines[0])
        rows = [split(l) for l in lines[2:]]
        return header, rows

    def list_items(self, name):
        return [l for l in self.sections.get(name, []) if LIST_ITEM_RE.match(l)]


def col(header, row, name):
    for i, h in enumerate(header):
        if h.lower().startswith(name.lower()):
            return row[i] if i < len(row) else ""
    return None


def check_headings(rep, doc, order, required):
    for h in required:
        if h not in doc.sections:
            rep.add("ERROR", doc.rel, "", 'missing required heading "## %s"' % h)
    for h in doc.headings:
        if h not in order:
            rep.add("WARN", doc.rel, h, "heading not in the template")
    present = [h for h in doc.headings if h in order]
    if present != sorted(present, key=order.index):
        rep.add("ERROR", doc.rel, "", "headings out of template order: " + ", ".join(present))
    for h in set(doc.headings):
        if doc.headings.count(h) > 1:
            rep.add("ERROR", doc.rel, h, "heading appears more than once")
    if not doc.title:
        rep.add("ERROR", doc.rel, "", 'missing "# " title line')


def check_budget(rep, doc, budget, words_log):
    n = doc.words()
    words_log.append((doc.rel, n, budget))
    if n > budget * HARD_OVER:
        rep.add("ERROR", doc.rel, "", "%d words, more than 20%% over the %d budget" % (n, budget))
    elif n > budget:
        rep.add("WARN", doc.rel, "", "%d words, over the %d budget" % (n, budget))


def check_open_questions(rep, doc):
    n = len(doc.list_items("Open Questions"))
    if n > 3:
        rep.add("ERROR", doc.rel, "Open Questions", "%d open questions, at most 3 allowed" % n)
    if n == 0 and "Open Questions" in doc.sections and "none" not in doc.section_text("Open Questions").lower():
        rep.add("WARN", doc.rel, "Open Questions", 'empty; write "None." when nothing is open')


def check_common(rep, doc):
    if "<!--" in doc.text:
        rep.add("ERROR", doc.rel, "", "template comment left in the document")
    if DTAG_RE.search(doc.text):
        rep.add("WARN", doc.rel, "", "(D-xx) tag on prose; keep traceability in tables or decisions.md")
    low = doc.text.lower()
    for w in KIT_WORDS:
        if w in low:
            rep.add("WARN", doc.rel, "", 'kit vocabulary in the deliverable: "%s"' % w)


def resolve_ref(root, name):
    name = name.strip()
    for cand in (name, os.path.join("systems", os.path.basename(name))):
        if os.path.isfile(os.path.join(root, cand)):
            return cand.replace(os.sep, "/")
    return None


def check_refs(rep, root, doc, docs):
    for line in doc.text.splitlines():
        for m in REF_RE.finditer(line):
            target = resolve_ref(root, m.group(1))
            if not target:
                rep.add("ERROR", doc.rel, "", 'reference to missing file "%s"' % m.group(1))
                continue
            tdoc = docs.get(target)
            if tdoc is None:
                continue
            rest = m.group(2).lower()
            if not any(rest.startswith(h.lower()) for h in tdoc.headings):
                rep.add("ERROR", doc.rel, "", 'reference "→ %s §%s" points to no heading in %s'
                        % (m.group(1), m.group(2).strip()[:40], target))


def check_glossary(rep, terms, docs):
    for term in terms:
        if len(term) < 3:
            continue
        pat = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        for doc in docs.values():
            if doc.rel == "decisions.md":
                continue
            bad = set()
            for m in pat.finditer(doc.text):
                found = m.group(0)
                if found == term or found[1:] == term[1:]:
                    continue
                bad.add(found)
            for b in sorted(bad):
                rep.add("WARN", doc.rel, "", 'glossary term "%s" written as "%s"' % (term, b))


def load_decisions(rep, doc):
    decisions = {}
    if "Core" not in doc.sections:
        rep.add("ERROR", doc.rel, "", 'missing "## Core"')
    if "Design" not in doc.sections:
        rep.add("ERROR", doc.rel, "", 'missing "## Design"')
    for sec in ("Core", "Design"):
        header, rows = doc.table(sec)
        if sec == "Core" and not rows:
            rep.add("ERROR", doc.rel, sec, "no decision rows")
        for row in rows:
            did = col(header, row, "ID") or ""
            if not re.fullmatch(r"D-\d+", did):
                rep.add("ERROR", doc.rel, sec, 'bad decision id "%s"' % did)
                continue
            num = int(did[2:])
            if sec == "Core" and num >= 100:
                rep.add("ERROR", doc.rel, sec, "%s belongs in ## Design (D-100+)" % did)
            if sec == "Design" and num < 100:
                rep.add("ERROR", doc.rel, sec, "%s in ## Design must be D-100 or higher" % did)
            if did in decisions:
                rep.add("ERROR", doc.rel, sec, "duplicate id %s" % did)
            value = col(header, row, "Value") or ""
            source = (col(header, row, "Source") or "").lower()
            if not value:
                rep.add("ERROR", doc.rel, sec, "%s has no value" % did)
            if source not in ("user", "proposal"):
                rep.add("ERROR", doc.rel, sec, '%s source "%s" must be user or proposal' % (did, source))
            decisions[did] = {"value": value, "source": source,
                              "affects": col(header, row, "Affects") or "", "section": sec}
    return decisions


def check_affects(rep, root, doc, decisions):
    for did, d in decisions.items():
        for part in re.split(r"[,;]", d["affects"]):
            part = part.strip()
            if not part or part.lower() in NONE_CELLS:
                continue
            fname = part.split("§")[0].strip().split()[0] if part.split("§")[0].strip() else ""
            if fname.endswith(".md") and not resolve_ref(root, fname):
                rep.add("WARN", doc.rel, did, 'Affects names missing file "%s"' % fname)


def check_concept(rep, root, doc, decisions):
    check_headings(rep, doc, CONCEPT_ORDER, CONCEPT_REQUIRED)
    header, rows = doc.table("Pillars")
    pillars = []
    if not 3 <= len(rows) <= 5:
        rep.add("ERROR", doc.rel, "Pillars", "%d pillars, need 3–5" % len(rows))
    for row in rows:
        name = col(header, row, "Pillar") or ""
        pillars.append(name.lower())
        if (col(header, row, "Forbids") or "").lower() in NONE_CELLS:
            rep.add("ERROR", doc.rel, "Pillars", 'pillar "%s" forbids nothing' % name)
    target = doc.section_text("Target").lower()
    for did in TARGET_IDS:
        d = decisions.get(did)
        if d and d["value"].upper() != "UNDECIDED" and d["value"].lower() not in target:
            rep.add("WARN", doc.rel, "Target", '%s value "%s" not found verbatim' % (did, d["value"]))
    header, rows = doc.table("Systems")
    systems = []
    for need in ("System", "Type", "One line", "Pillar", "Tier", "Doc"):
        if col(header, header, need) is None:
            rep.add("ERROR", doc.rel, "Systems", 'table has no "%s" column' % need)
            return pillars, systems
    for row in rows:
        name = col(header, row, "System")
        stype = (col(header, row, "Type") or "").lower()
        tier = (col(header, row, "Tier") or "").lower()
        pillar = (col(header, row, "Pillar") or "").lower()
        docref = (col(header, row, "Doc") or "").strip("` ")
        if stype not in TYPES:
            rep.add("ERROR", doc.rel, "Systems", '%s: type "%s" is not one of %s' % (name, stype, ", ".join(sorted(TYPES))))
        if tier not in ("core", "later"):
            rep.add("ERROR", doc.rel, "Systems", '%s: tier "%s" must be core or later' % (name, tier))
        if pillars and pillar and not any(p and (p in pillar or pillar in p) for p in pillars):
            rep.add("WARN", doc.rel, "Systems", '%s: pillar "%s" is not in ## Pillars' % (name, pillar))
        if docref.lower() not in NONE_CELLS:
            if not os.path.isfile(os.path.join(root, docref)):
                rep.add("ERROR", doc.rel, "Systems", '%s: doc "%s" does not exist' % (name, docref))
            systems.append(docref.replace(os.sep, "/"))
    if not rows:
        rep.add("ERROR", doc.rel, "Systems", "no systems listed")
    terms = []
    gh, grows = doc.table("Glossary")
    for row in grows:
        t = col(gh, row, "Term")
        if t:
            terms.append(t.strip("* "))
    return pillars, systems, terms


def check_system(rep, doc, listed):
    check_headings(rep, doc, SYSTEM_ORDER, SYSTEM_REQUIRED)
    n = len(doc.list_items("Player-Observable Behaviors"))
    if not 3 <= n <= 10:
        rep.add("WARN", doc.rel, "Player-Observable Behaviors", "%d behaviors, aim for 3–10" % n)
    if doc.rel not in listed:
        rep.add("ERROR", doc.rel, "", "not listed in concept.md ## Systems (Doc column)")
    tunables = []
    header, rows = doc.table("Tunables")
    for row in rows:
        if row and row[0]:
            tunables.append(row[0].strip("*` ").lower())
    return tunables


def changed_decisions(root, decisions):
    try:
        out = subprocess.run(["git", "-C", root, "diff", "--unified=0", "HEAD", "--", "decisions.md"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    ids = set()
    for line in out.splitlines():
        if line[:1] in "+-" and not line.startswith(("+++", "---")):
            m = re.search(r"\|\s*(D-\d+)\s*\|", line)
            if m:
                ids.add(m.group(1))
    return {i: decisions.get(i, {}).get("affects", "(row removed)") for i in sorted(ids)}


def main():
    ap = argparse.ArgumentParser(description="Check a gdd-forge v2 GDD folder.")
    ap.add_argument("gdd")
    ap.add_argument("--file")
    ap.add_argument("--changed", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.gdd)
    if not os.path.isdir(root):
        print("gdd_check: no such folder: %s" % root)
        return 2
    only = None
    if a.file:
        only = os.path.relpath(os.path.abspath(a.file) if os.path.isabs(a.file) else os.path.join(root, a.file), root).replace(os.sep, "/")
    rep = Report(only)
    words = []
    docs = {}
    for rel in ("concept.md", "decisions.md"):
        if not os.path.isfile(os.path.join(root, rel)):
            rep.add("ERROR", rel, "", "file missing")
        else:
            docs[rel] = Doc(root, rel)
    sysdir = os.path.join(root, "systems")
    if os.path.isdir(sysdir):
        for name in sorted(os.listdir(sysdir)):
            if name.endswith(".md"):
                docs["systems/" + name] = Doc(root, "systems/" + name)

    decisions = {}
    if "decisions.md" in docs:
        decisions = load_decisions(rep, docs["decisions.md"])
        check_affects(rep, root, docs["decisions.md"], decisions)
        if "<!--" in docs["decisions.md"].text:
            rep.add("ERROR", "decisions.md", "", "template comment left in the document")
    listed, terms = [], []
    if "concept.md" in docs:
        res = check_concept(rep, root, docs["concept.md"], decisions)
        if len(res) == 3:
            _, listed, terms = res
        check_budget(rep, docs["concept.md"], CONCEPT_BUDGET, words)
        check_open_questions(rep, docs["concept.md"])
    owners = {}
    for rel, doc in docs.items():
        if not rel.startswith("systems/"):
            continue
        for t in check_system(rep, doc, listed):
            owners.setdefault(t, []).append(rel)
        check_budget(rep, doc, SYSTEM_BUDGET, words)
        check_open_questions(rep, doc)
    for t, files in owners.items():
        if len(files) > 1:
            for f in files:
                rep.add("ERROR", f, "Tunables", 'tunable "%s" defined in %s' % (t, ", ".join(files)))
    for rel, doc in docs.items():
        if rel != "decisions.md":
            check_common(rep, doc)
            check_refs(rep, root, doc, docs)
    check_glossary(rep, terms, docs)

    print("gdd_check: %s" % root)
    for level, path, where, msg in rep.items:
        loc = path + (" §" + where if where else "")
        print("%-5s %s: %s" % (level, loc, msg))
    if words:
        print("words: " + " · ".join("%s %d/%d" % (p, n, b) for p, n, b in words
                                     if not only or p == only))
    if a.changed:
        ch = changed_decisions(root, decisions)
        if ch is None:
            print("changed: not a git repository or git unavailable; cannot list changed decisions")
        elif not ch:
            print("changed: no decision changed since the last commit")
        else:
            for did, aff in ch.items():
                print("changed: %s → affects: %s" % (did, aff or "(Affects empty)"))
    print("RESULT: %d errors, %d warnings" % (rep.errors(), rep.warnings()))
    return 1 if rep.errors() else 0


if __name__ == "__main__":
    sys.exit(main())
