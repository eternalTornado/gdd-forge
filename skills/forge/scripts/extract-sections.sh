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
#
# BEHAVIOUR
#   - A section runs from its heading line to the line before the next
#     heading at the same or a higher level (i.e. equal or fewer leading
#     '#'), or EOF. This means a "## 4.5" section swallows any deeper
#     "### 4.5.1" subsections that follow it, and stops at the next
#     heading of any kind (numbered or not) at level <= its own.
#   - Output order follows the SOURCE FILE'S order (by section number,
#     compared numerically), never the order the specs were given in.
#     A section requested twice (via overlapping specs) is only emitted
#     once.
#   - The destination file starts with the source's H1 line (if it has
#     one), then a provenance comment naming the source path and the
#     specs extracted, then the extracted sections separated by a blank
#     line.
#   - A requested section that has no matching heading in the source
#     produces a placeholder comment in the destination, in the position
#     it would have occupied:
#       <!-- MISSING: §4.5 not found in <source basename> -->
#     and a matching notice on stdout so the orchestrator notices it:
#       MISSING: §4.5
#   - A source file that does not exist writes a single placeholder line
#     to the destination, prints a matching notice on stdout, and exits 2:
#       <!-- MISSING FILE: <path> -->
#       MISSING FILE: <path>
#
# EXIT CODES
#   0   success — including when some requested sections were missing
#   1   usage error (wrong argument count, or a spec that isn't
#       "all" / "N(.N)*" / "N(.N)*-N(.N)*" with a matching major prefix)
#   2   the source file does not exist
#
# The destination's parent directory is created if it does not exist.

set -u

die_usage() {
  echo "usage: $(basename "$0") <source.md> <dest.md> <spec> [<spec> ...]" >&2
  echo "  spec: 4.5  |  4.3-4.6  |  all" >&2
  [ -n "${1:-}" ] && echo "error: $1" >&2
  exit 1
}

is_number() {
  # digits and dots only, no leading/trailing/double dot
  [[ "$1" =~ ^[0-9]+(\.[0-9]+)*$ ]]
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

for spec in "${SPECS[@]}"; do
  if [ "$spec" = "all" ]; then
    ALLMODE=1
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
if [ "$ALLMODE" -eq 0 ]; then
  WANTED_FILE="$(mktemp)"
  trap 'rm -f "$WANTED_FILE"' EXIT
  if [ "${#WANTED[@]}" -gt 0 ]; then
    printf '%s\n' "${WANTED[@]}" | sort -u > "$WANTED_FILE"
  else
    : > "$WANTED_FILE"
  fi
fi

awk \
  -v dest="$DEST" \
  -v allmode="$ALLMODE" \
  -v wantedfile="${WANTED_FILE:-}" \
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

BEGIN {
  if (allmode == 0 && wantedfile != "") {
    while ((getline wline < wantedfile) > 0) {
      if (wline != "") wanted[wline] = 1
    }
    close(wantedfile)
  }
}

{ lines[NR] = $0 }

END {
  total = NR

  # ---- H1 (exactly one leading "#" then a space) ----
  h1_line = 0
  for (i = 1; i <= total; i++) {
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

  # ---- emit ----
  if (h1_line > 0) {
    print lines[h1_line] > dest
    print "" > dest
  }
  print provenance > dest

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
}
' "$SOURCE"

exit 0
