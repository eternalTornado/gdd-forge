#!/usr/bin/env bash
#
# extract-sections.sh — pull numbered "## N.N ..." / "### N.N.N ..." sections
# out of a chapter Markdown file, so a subagent receives only the upstream
# sections its contract lets it consume instead of a whole chapter.
#
# The orchestrator runs this once per dispatch, before handing a subagent
# its inputs.
#
# USAGE
#   extract-sections.sh <source.md> <dest.md> <spec> [<spec> ...]
#
# SPEC FORMS (one or more, any mix, in any order)
#   4.5          one section — matches a heading whose numeric prefix is
#                exactly "4.5" (e.g. "## 4.5 ..." or, at any depth,
#                "### 4.5 ..."). Matching is on the NUMBER, never the
#                title — chapter bodies are written in the user's language
#                (D-12) so titles vary; only the numeric prefix is stable.
#   4.3-4.6      an inclusive range. Both ends must share the same "major"
#                prefix (everything but the last dotted component) — e.g.
#                4.3-4.6 or 4.1-4.11. The last component is compared
#                NUMERICALLY, so 4.1-4.11 correctly includes 4.10 and 4.11
#                (never confusing 4.1 with 4.10/4.11 — see BEHAVIOUR).
#   all          the whole file — every section, in source order.
#   intro        the chapter's opening abstract: the text after the H1
#                line up to (not including) the first level-2-or-deeper
#                heading. Leading/trailing blank lines in that span are
#                skipped; HTML comments in it are left as-is. Empty (or
#                no H1) → absent, see BEHAVIOUR.
#   @<title>     one UNNUMBERED heading, at any level, whose title equals
#                <title> case-insensitively after trimming surrounding
#                whitespace (e.g. "@Open Decisions", "@New Terms"). Matches
#                on the TITLE, never a number — a numbered heading such as
#                "## 2.1 Open Decisions" never matches "@Open Decisions".
#                <title> must be non-empty after trimming. Section extent
#                follows the same rule as a numbered section (below).
#
# BEHAVIOUR
#   - A section runs from its heading line to the line before the next
#     heading at the same or a higher level (i.e. equal or fewer leading
#     '#'), or EOF. This means a "## 4.5" section swallows any deeper
#     "### 4.5.1" subsections that follow it, and stops at the next
#     heading of any kind (numbered or not) at level <= its own. The same
#     rule applies to an "@<title>" match.
#   - Lines inside fenced code blocks (``` or ~~~) are never treated as
#     headings, so ASCII layout sketches and mermaid blocks whose lines
#     start with '#' cannot split a section, and a "## Heading" that only
#     appears inside a fence can never satisfy "@Heading" either.
#   - Output order follows the SOURCE FILE'S order (by position in the
#     file), never the order the specs were given in. Numeric specs,
#     "intro" and "@<title>" specs freely mix in one invocation. A section
#     requested twice (via overlapping specs, or the same "@<title>"/
#     "intro" spec repeated, case/whitespace-insensitively for "@<title>")
#     is only emitted once.
#   - The destination file starts with the source's H1 line (if it has
#     one), then a provenance comment naming the source path and the
#     specs extracted, then the extracted sections separated by a blank
#     line.
#   - A requested numbered section that has no matching heading in the
#     source produces a placeholder comment in the destination, in the
#     position it would have occupied:
#       <!-- MISSING: §4.5 not found in <source basename> -->
#     and a matching notice on stdout so the orchestrator notices it:
#       MISSING: §4.5
#   - A requested "intro" or "@<title>" that has no content/match in the
#     source is normal, not an error: it produces a placeholder comment
#     using the exact spec text (never "MISSING:") —
#       <!-- ABSENT: @New Terms not found in <source basename> -->
#       <!-- ABSENT: intro not found in <source basename> -->
#     and a matching notice on stdout:
#       ABSENT: @New Terms
#       ABSENT: intro
#   - A source file that does not exist writes a single placeholder line
#     to the destination, prints a matching notice on stdout, and exits 2:
#       <!-- MISSING FILE: <path> -->
#       MISSING FILE: <path>
#
# EXIT CODES
#   0   success — including when some requested sections were missing or
#       an "intro"/"@<title>" spec was absent
#   1   usage error (wrong argument count, or a spec that isn't
#       "all" / "intro" / "@<non-empty title>" / "N(.N)*" /
#       "N(.N)*-N(.N)*" with a matching major prefix)
#   2   the source file does not exist
#
# The destination's parent directory is created if it does not exist.

set -u

die_usage() {
  echo "usage: $(basename "$0") <source.md> <dest.md> <spec> [<spec> ...]" >&2
  echo "  spec: 4.5  |  4.3-4.6  |  all  |  intro  |  @<Heading title>" >&2
  [ -n "${1:-}" ] && echo "error: $1" >&2
  exit 1
}

is_number() {
  # digits and dots only, no leading/trailing/double dot
  [[ "$1" =~ ^[0-9]+(\.[0-9]+)*$ ]]
}

trim() {
  # strip leading/trailing whitespace (portable, no sed/awk dependency)
  local s="$1"
  while [[ "$s" == [[:space:]]* ]]; do s="${s#?}"; done
  while [[ "$s" == *[[:space:]] ]]; do s="${s%?}"; done
  printf '%s' "$s"
}

if [ "$#" -lt 3 ]; then
  die_usage "need a source, a destination, and at least one spec"
fi

SOURCE="$1"
DEST="$2"
shift 2
SPECS=("$@")

DEST_DIR="$(dirname -- "$DEST")"
mkdir -p -- "$DEST_DIR"

# ---------------------------------------------------------------------------
# Missing source file: write the placeholder, notify, exit 2.
# ---------------------------------------------------------------------------
if [ ! -f "$SOURCE" ]; then
  printf '<!-- MISSING FILE: %s -->\n' "$SOURCE" > "$DEST"
  echo "MISSING FILE: $SOURCE"
  exit 2
fi

DEST_BASENAME="$(basename -- "$SOURCE")"

# ---------------------------------------------------------------------------
# Parse specs: figure out ALLMODE, or expand every spec into concrete
# "wanted" section numbers (deduplicated). Range expansion walks the last
# dotted component as an integer so 4.1-4.11 yields 4.1 .. 4.11 in the
# right numeric order regardless of digit-count.
# ---------------------------------------------------------------------------
ALLMODE=0
declare -a WANTED=()
declare -a HEADINGS=()
INTRO_WANTED=0

for spec in "${SPECS[@]}"; do
  if [ "$spec" = "all" ]; then
    ALLMODE=1
    continue
  fi

  if [ "$spec" = "intro" ]; then
    INTRO_WANTED=1
    continue
  fi

  if [[ "$spec" == @* ]]; then
    title="${spec#@}"
    title="$(trim "$title")"
    [ -n "$title" ] || die_usage "malformed heading spec (empty title): $spec"
    HEADINGS+=("$spec")
    continue
  fi

  if [[ "$spec" == *-* ]]; then
    # range form: exactly one '-', both sides valid numbers
    if [ "$(grep -o '-' <<<"$spec" | wc -l | tr -d ' ')" != "1" ]; then
      die_usage "malformed range spec: $spec"
    fi
    start="${spec%-*}"
    end="${spec#*-}"
    is_number "$start" || die_usage "malformed range start: $spec"
    is_number "$end" || die_usage "malformed range end: $spec"

    IFS='.' read -r -a sa <<< "$start"
    IFS='.' read -r -a ea <<< "$end"
    if [ "${#sa[@]}" -ne "${#ea[@]}" ]; then
      die_usage "range endpoints must share the same major number: $spec"
    fi
    n="${#sa[@]}"
    for ((i = 0; i < n - 1; i++)); do
      if [ "${sa[i]}" != "${ea[i]}" ]; then
        die_usage "range endpoints must share the same major number: $spec"
      fi
    done
    startlast="${sa[$((n - 1))]}"
    endlast="${ea[$((n - 1))]}"
    if ((10#$startlast > 10#$endlast)); then
      die_usage "range start is after range end: $spec"
    fi
    prefix=""
    if [ "$n" -gt 1 ]; then
      prefix="${sa[0]}"
      for ((i = 1; i < n - 1; i++)); do prefix="${prefix}.${sa[i]}"; done
    fi
    for ((k = 10#$startlast; k <= 10#$endlast; k++)); do
      if [ -n "$prefix" ]; then
        WANTED+=("${prefix}.${k}")
      else
        WANTED+=("${k}")
      fi
    done
  else
    is_number "$spec" || die_usage "malformed spec: $spec"
    WANTED+=("$spec")
  fi
done

PROV_SPECS="$(IFS=,; echo "${SPECS[*]}")"
PROVENANCE="<!-- extracted by extract-sections.sh · source: ${SOURCE} · specs: ${PROV_SPECS} -->"

# ---------------------------------------------------------------------------
# Hand off to awk for the actual parse/select/emit. It reads the source as
# its normal input (building lines[1..NR]) and does everything else in
# END, since section boundaries can only be known once the whole file (and
# every heading in it) has been seen.
# ---------------------------------------------------------------------------
WANTED_FILE=""
HEADINGS_FILE=""
if [ "$ALLMODE" -eq 0 ]; then
  WANTED_FILE="$(mktemp)"
  HEADINGS_FILE="$(mktemp)"
  trap 'rm -f "$WANTED_FILE" "$HEADINGS_FILE"' EXIT
  if [ "${#WANTED[@]}" -gt 0 ]; then
    printf '%s\n' "${WANTED[@]}" | sort -u > "$WANTED_FILE"
  else
    : > "$WANTED_FILE"
  fi
  if [ "${#HEADINGS[@]}" -gt 0 ]; then
    printf '%s\n' "${HEADINGS[@]}" > "$HEADINGS_FILE"
  else
    : > "$HEADINGS_FILE"
  fi
fi

awk \
  -v dest="$DEST" \
  -v allmode="$ALLMODE" \
  -v wantedfile="${WANTED_FILE:-}" \
  -v headingsfile="${HEADINGS_FILE:-}" \
  -v introwanted="$INTRO_WANTED" \
  -v provenance="$PROVENANCE" \
  -v destbasename="$DEST_BASENAME" \
'
function cmpnum(a, b,    ac, bc, na, nb, i, av, bv, mx) {
  na = split(a, ac, ".")
  nb = split(b, bc, ".")
  mx = (na > nb) ? na : nb
  for (i = 1; i <= mx; i++) {
    av = (i <= na) ? ac[i] + 0 : -1
    bv = (i <= nb) ? bc[i] + 0 : -1
    if (av < bv) return -1
    if (av > bv) return 1
  }
  return 0
}

# section end for an arbitrary heading index p (into allh_line/allh_level):
# line before the next heading (any kind) at the same or a higher level,
# else EOF. Same rule as the numbered-heading extent below.
function section_end(p,    lvl, q, endl) {
  lvl = allh_level[p]
  endl = total
  for (q = p + 1; q <= nall; q++) {
    if (allh_level[q] <= lvl) { endl = allh_line[q] - 1; break }
  }
  return endl
}

# a sortable pseudo-number for an unnumbered heading at allh index p, used
# only to interleave "@<title>" matches with numbered sections in source
# order: anchor it just after the nearest PRECEDING numbered heading (by
# source position), or before everything if none precedes it.
function anchor_key(p,    kx, best) {
  best = 0
  for (kx = 1; kx <= nheads; kx++) {
    if (head_p[kx] < p) best = kx
    else break
  }
  if (best == 0) return "0.999999"
  return head_num[best] ".999999"
}

BEGIN {
  if (allmode == 0 && wantedfile != "") {
    while ((getline wline < wantedfile) > 0) {
      if (wline != "") wanted[wline] = 1
    }
    close(wantedfile)
  }
  if (allmode == 0 && headingsfile != "") {
    while ((getline hline < headingsfile) > 0) {
      if (hline == "") continue
      rawtitle = substr(hline, 2)                 # drop leading "@"
      gsub(/^[ \t]+|[ \t]+$/, "", rawtitle)        # trim whitespace
      key = tolower(rawtitle)
      if (!(key in headingwanted)) {
        headingwanted[key] = 1
        headingraw[key] = hline                   # first literal spec wins
      }
    }
    close(headingsfile)
  }
}

{ lines[NR] = $0 }

END {
  total = NR

  # ---- mark lines inside fenced code blocks (``` or ~~~) so an ASCII
  #      layout sketch or mermaid block whose lines start with "#" is
  #      never mistaken for a heading. A fence opens on a line that,
  #      after stripping up to 3 leading spaces, starts with 3+ backticks
  #      or 3+ tildes; it closes on a line starting with the same
  #      character repeated at least that many times and nothing else but
  #      trailing whitespace. An unclosed fence leaves the rest of the
  #      file in-fence. ----
  fence_state = 0
  fence_char = ""
  fence_len = 0
  for (i = 1; i <= total; i++) {
    line = lines[i]
    stripped = line
    nstrip = 0
    while (nstrip < 3 && substr(stripped, 1, 1) == " ") {
      stripped = substr(stripped, 2)
      nstrip++
    }
    if (fence_state == 0) {
      if (match(stripped, /^```+/)) {
        infence[i] = 1
        fence_state = 1
        fence_char = "`"
        k = 1
        while (substr(stripped, k, 1) == "`") k++
        fence_len = k - 1
      } else if (match(stripped, /^~~~+/)) {
        infence[i] = 1
        fence_state = 1
        fence_char = "~"
        k = 1
        while (substr(stripped, k, 1) == "~") k++
        fence_len = k - 1
      } else {
        infence[i] = 0
      }
    } else {
      infence[i] = 1
      if (substr(stripped, 1, 1) == fence_char) {
        k = 1
        while (substr(stripped, k, 1) == fence_char) k++
        run = k - 1
        rest = substr(stripped, k)
        gsub(/[ \t]+$/, "", rest)
        if (run >= fence_len && rest == "") {
          fence_state = 0
        }
      }
    }
  }

  # ---- H1 (exactly one leading "#" then a space) ----
  h1_line = 0
  for (i = 1; i <= total; i++) {
    if (infence[i]) continue
    if (lines[i] ~ /^# /) { h1_line = i; break }
  }

  if (allmode == 1) {
    if (h1_line > 0) {
      print lines[h1_line] > dest
      print "" > dest
      bodystart = h1_line + 1
    } else {
      bodystart = 1
    }
    print provenance > dest
    print "" > dest
    for (i = bodystart; i <= total; i++) print lines[i] > dest
    exit 0
  }

  # ---- every ATX heading line (any level, numbered or not) — needed to
  #      compute correct section boundaries even when the next heading
  #      (e.g. an "## Open Decisions" appendix) has no section number ----
  nall = 0
  for (i = 1; i <= total; i++) {
    if (infence[i]) continue
    line = lines[i]
    if (match(line, /^#{1,6}([ \t]|$)/)) {
      lvl = 0; j = 1
      while (substr(line, j, 1) == "#") { lvl++; j++ }
      nall++
      allh_line[nall] = i
      allh_level[nall] = lvl
    }
  }

  # ---- the subset of those headings that carry a numeric prefix ----
  nheads = 0
  for (p = 1; p <= nall; p++) {
    i = allh_line[p]
    line = lines[i]
    lvl = allh_level[p]
    j = lvl + 1
    while (substr(line, j, 1) == " " || substr(line, j, 1) == "\t") j++
    c = substr(line, j, 1)
    if (c ~ /[0-9]/) {
      tok = ""
      k = j
      while (1) {
        c2 = substr(line, k, 1)
        if (c2 ~ /[0-9]/ || c2 == ".") { tok = tok c2; k++ } else break
      }
      if (tok !~ /\.$/) {
        nheads++
        head_p[nheads] = p
        head_num[nheads] = tok
        is_numbered[p] = 1
      }
    }
  }

  # ---- section end = line before the next heading (any kind) at the
  #      same or a higher level, else EOF ----
  for (kx = 1; kx <= nheads; kx++) {
    p = head_p[kx]
    lvl = allh_level[p]
    head_line[kx] = allh_line[p]
    endl = total
    for (q = p + 1; q <= nall; q++) {
      if (allh_level[q] <= lvl) { endl = allh_line[q] - 1; break }
    }
    head_end[kx] = endl
  }

  # ---- resolve wanted numbers against the numbered headings ----
  n_items = 0
  for (w in wanted) {
    found_k = 0
    for (kx = 1; kx <= nheads; kx++) {
      if (head_num[kx] == w) { found_k = kx; break }
    }
    n_items++
    if (found_k > 0) {
      item_key[n_items] = w
      item_kind[n_items] = "F"
      item_ref[n_items] = found_k
    } else {
      item_key[n_items] = w
      item_kind[n_items] = "M"
      item_ref[n_items] = w
    }
  }

  # ---- order the requested items by section number, numerically ----
  for (a = 2; a <= n_items; a++) {
    bk = item_key[a]; bkind = item_kind[a]; bref = item_ref[a]
    b = a - 1
    while (b >= 1 && cmpnum(item_key[b], bk) > 0) {
      item_key[b + 1] = item_key[b]
      item_kind[b + 1] = item_kind[b]
      item_ref[b + 1] = item_ref[b]
      b--
    }
    item_key[b + 1] = bk
    item_kind[b + 1] = bkind
    item_ref[b + 1] = bref
  }

  # ---- resolve "intro" and "@<title>" specs (kept entirely separate from
  #      the numeric WANTED resolution above; n_extra stays 0 — and none of
  #      this code changes the numeric output — whenever neither was
  #      requested, so a pure-numeric invocation is byte-for-byte what the
  #      script produced before these two spec forms existed) ----
  n_extra = 0

  if (introwanted == 1) {
    n_extra++
    introfound = 0
    if (h1_line > 0) {
      endbound = total
      for (p = 1; p <= nall; p++) {
        if (allh_level[p] >= 2) { endbound = allh_line[p] - 1; break }
      }
      s = h1_line + 1
      e = endbound
      while (s <= e && lines[s] ~ /^[ \t]*$/) s++
      while (e >= s && lines[e] ~ /^[ \t]*$/) e--
      if (s <= e) introfound = 1
    }
    if (introfound) {
      extra_kind[n_extra] = "I"
      extra_start[n_extra] = s
      extra_end[n_extra] = e
      extra_sortkey[n_extra] = "0"
    } else {
      extra_kind[n_extra] = "IA"
      extra_sortkey[n_extra] = "999999"
      extra_label[n_extra] = "intro"
    }
  }

  # ---- resolve @<title> against every UNNUMBERED heading (any level);
  #      numbered headings are never eligible, per spec ----
  for (hk in headingwanted) {
    n_extra++
    matched_p = 0
    for (p = 1; p <= nall; p++) {
      if (is_numbered[p]) continue
      i = allh_line[p]
      line = lines[i]
      lvl = allh_level[p]
      j = lvl + 1
      while (substr(line, j, 1) == " " || substr(line, j, 1) == "\t") j++
      title = substr(line, j)
      gsub(/[ \t]+$/, "", title)
      if (tolower(title) == hk) { matched_p = p; break }
    }
    if (matched_p > 0) {
      extra_kind[n_extra] = "H"
      extra_start[n_extra] = allh_line[matched_p]
      extra_end[n_extra] = section_end(matched_p)
      extra_sortkey[n_extra] = anchor_key(matched_p)
    } else {
      extra_kind[n_extra] = "HA"
      extra_sortkey[n_extra] = "999999"
      extra_label[n_extra] = headingraw[hk]
    }
  }

  # ---- emit ----
  if (h1_line > 0) {
    print lines[h1_line] > dest
    print "" > dest
  }
  print provenance > dest

  if (n_extra == 0) {
    for (a = 1; a <= n_items; a++) {
      print "" > dest
      if (item_kind[a] == "F") {
        kx = item_ref[a]
        for (ln = head_line[kx]; ln <= head_end[kx]; ln++) print lines[ln] > dest
      } else {
        num = item_ref[a]
        print "<!-- MISSING: §" num " not found in " destbasename " -->" > dest
        print "MISSING: §" num
      }
    }
  } else {
    # merge the numeric items with the intro/@ extras into one list, sorted
    # by the same numeric-ish key (real section numbers for numeric items,
    # a synthetic source-order key — see anchor_key() — for the extras),
    # so the destination still reads in source order regardless of spec mix
    ncomb = 0
    for (a = 1; a <= n_items; a++) {
      ncomb++
      comb_key[ncomb] = item_key[a]
      comb_kind[ncomb] = item_kind[a]
      comb_ref[ncomb] = item_ref[a]
    }
    for (b = 1; b <= n_extra; b++) {
      ncomb++
      comb_key[ncomb] = extra_sortkey[b]
      comb_kind[ncomb] = extra_kind[b]
      comb_ref[ncomb] = b
    }
    for (a = 2; a <= ncomb; a++) {
      bk = comb_key[a]; bkind = comb_kind[a]; bref = comb_ref[a]
      c = a - 1
      while (c >= 1 && cmpnum(comb_key[c], bk) > 0) {
        comb_key[c + 1] = comb_key[c]
        comb_kind[c + 1] = comb_kind[c]
        comb_ref[c + 1] = comb_ref[c]
        c--
      }
      comb_key[c + 1] = bk
      comb_kind[c + 1] = bkind
      comb_ref[c + 1] = bref
    }

    for (a = 1; a <= ncomb; a++) {
      print "" > dest
      k = comb_kind[a]
      if (k == "F") {
        kx = comb_ref[a]
        for (ln = head_line[kx]; ln <= head_end[kx]; ln++) print lines[ln] > dest
      } else if (k == "M") {
        num = comb_ref[a]
        print "<!-- MISSING: §" num " not found in " destbasename " -->" > dest
        print "MISSING: §" num
      } else if (k == "H" || k == "I") {
        eidx = comb_ref[a]
        for (ln = extra_start[eidx]; ln <= extra_end[eidx]; ln++) print lines[ln] > dest
      } else {
        eidx = comb_ref[a]
        lbl = extra_label[eidx]
        print "<!-- ABSENT: " lbl " not found in " destbasename " -->" > dest
        print "ABSENT: " lbl
      }
    }
  }
}
' "$SOURCE"

exit 0
