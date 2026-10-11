export const meta = {
  name: 'forge-run',
  description: 'gdd-forge: write, verify, review and fix a GDD one segment at a time, stopping at each user checkpoint',
  whenToUse: 'Only when the gdd-forge forge skill calls it with args after the W0 gate. Never run it on its own.',
  phases: [
    { title: 'Resolve', detail: 'apply the answers from the previous checkpoint' },
    { title: 'Name', detail: 'gdd-namer candidates (full profile)' },
    { title: 'Write', detail: 'chapter dispatches, one wave at a time' },
    { title: 'Verify', detail: 'per-file finder → 3 adversarial voters → auto-PATCH' },
    { title: 'Review', detail: 'gdd-reviewer ‖ 4 lens finders → merge → 3 voters per Major/Blocker' },
    { title: 'Fix', detail: 'PATCH rounds + RECHECK until clean (≤ 2 rounds)' },
    { title: 'Assemble', detail: 'boilerplate, index, completeness critic' },
  ],
}

// One segment of a gdd-forge run. The forge skill (main agent) runs the W0 gate, then calls this
// workflow with `from` = the stage to start at. A segment runs forward until it needs the user
// (returns {status:'checkpoint'}), finishes ({status:'done'}) or fails ({status:'error'}). The main
// agent asks the user, records the answers on disk, and calls again with `from` = checkpoint.next and
// the answers in `resolutions`. State lives in OUT/WORK on disk, never in this script.
// Contract of args / return values: skills/forge/SKILL.md § Workflow contract.

const A = args || {}
const P = A.paths || {}
const KIT = P.kit, OUT = P.out, WORK = P.work, INPUTS = P.inputs
const FULL = A.profile === 'full'
const MODE = A.mode || 'run'
const NS = A.agent_ns || ''
const FLAGS = A.flags || {}
const DATA = A.data || {}
const GAME = A.game_name || '(working title pending — see §1.2)'

const missingArgs = ['profile', 'from', 'lang'].filter(k => !A[k])
  .concat(['kit', 'out', 'work'].filter(k => !P[k]).map(k => 'paths.' + k))
  .concat(FULL && !INPUTS ? ['paths.inputs'] : [])
  .concat(MODE !== 'run' && !A.target ? ['target'] : [])
if (missingArgs.length) {
  return { status: 'error', stage: A.from || null, message: `forge-run is missing args: ${missingArgs.join(', ')}. Start it from /gdd-forge:forge, never on its own.` }
}

// ---------------------------------------------------------------------------------------------
// Tables — the single home of file names, owners, templates, checklists, data and the slice map.

const CH = {   // full profile
  0: { file: '0_Index.md', role: 'scribe', tmpl: '00-index.md' },
  1: { file: '1_Copyright Information.md', role: 'scribe', tmpl: '01-copyright.md' },
  2: { file: '2_Version History.md', role: 'scribe', tmpl: '02-version-history.md' },
  3: { file: '3_Game Overview.md', role: 'concept-architect', tmpl: '03-game-overview.md', checks: ['ch03-overview.md', 'ch00-structure.md'], data: ['patterns', 'platforms'], guidance: true },
  4: { file: '4_Gameplay and Mechanics.md', role: 'mechanics-designer', tmpl: '04-gameplay-mechanics.md', checks: ['ch04-mechanics.md', 'ch00-structure.md'], data: ['patterns', 'monetization-if-f2p'], guidance: true },
  5: { file: '5_Story, Setting and Character.md', role: 'narrative-designer', tmpl: '05-story-setting-character.md', checks: ['ch05-narrative.md', 'ch05-character.md', 'ch05-world.md'], data: ['cultural'] },
  6: { file: '6_Levels.md', role: 'level-designer', tmpl: '06-levels.md', checks: ['ch06-levels.md'] },
  7: { file: '7_Interface.md', role: 'ux-designer', tmpl: '07-interface.md', checks: ['ch07-ui-ux.md', 'ch07-audio.md'], data: ['accessibility', 'platforms'], guidance: true },
  8: { file: '8_Artificial Intelligence.md', role: 'ai-designer', tmpl: '08-artificial-intelligence.md', checks: ['ch08-ai.md'] },
  9: { file: '9_Technical.md', role: 'tech-designer', tmpl: '09-technical.md', checks: ['ch09-technical.md', 'ch09-platform.md'], data: ['platforms'], guidance: true },
  10: { file: '10_Game Art.md', role: 'art-director', tmpl: '10-game-art.md', checks: ['ch10-art.md'] },
  11: { file: '11_Secondary Software.md', role: 'tech-designer', tmpl: '11-secondary-software.md', checks: ['ch11-tooling.md'], guidance: true },
  12: { file: '12_Management.md', role: 'producer', tmpl: '12-management.md', checks: ['ch12-management.md', 'ch12-monetization.md', 'ch12-liveops.md'], data: ['monetization'], guidance: true },
  13: { file: '13_Appendices.md', role: 'scribe', tmpl: '13-appendices.md' },
}

// Full-profile input slices: dispatch → chapters passed whole + [source chapter, ...section specs].
// Every W3–W7 dispatch also gets INPUTS/_anchor.md (ch 3 §3.2 + §3.10).
const SLICES = {
  4: { whole: [3], parts: [] },
  5: { whole: [3], parts: [[4, '4.1-4.3']] },
  6: { whole: [], parts: [[3, '3.9'], [4, '4.1-4.6'], [5, '5.3', '5.5', '5.9']] },
  7: { whole: [], parts: [[3, '3.7', '3.8'], [4, '4.4', '4.9'], [5, '5.8']] },
  8: { whole: [], parts: [[4, '4.3-4.6', '4.10'], [5, '5.6'], [6, '6.4']] },
  9: { whole: [], parts: [[4, '4.5', '4.8', '4.9', '4.11'], [6, '6.2', '6.6'], [7, '7.5', '7.11'], [8, '8.2', '8.11'], [10, '10.8', '10.9']] },
  10: { whole: [], parts: [[3, '3.8'], [5, '5.2', '5.3', '5.6', '5.9'], [6, '6.4'], [7, '7.4', '7.11']] },
  11: { whole: [9], parts: [[6, '6.6'], [8, '8.10'], [10, '10.8']] },
  12: { whole: [], parts: [[3, '3.3', '3.9'], [4, '4.2', '4.7', '4.11'], [6, '6.7'], [9, '9.10'], [10, '10.9'], [11, '11.5', '11.7']] },
}

// Sections 13_Appendices consolidates per chapter, on top of "@Open Decisions" "@New Terms".
const CH13_EXTRA = { 3: ['3.2', '3.3', '3.10'], 4: ['4.11'], 6: ['6.4'], 7: ['7.11'], 10: ['10.9'] }

const LF = {   // lite profile
  0: { file: '0_Index.md', tmpl: '0-index.md' },
  1: { file: '1_Concept.md', role: 'concept-architect', tmpl: '1-concept.md', check: 'lite-1-concept.md', data: ['patterns'], reads: [] },
  2: { file: '2_Core Gameplay.md', role: 'mechanics-designer', tmpl: '2-core-gameplay.md', check: 'lite-2-gameplay.md', data: ['patterns', 'monetization-if-f2p'], reads: [1] },
  3: { file: '3_UX Art and Audio.md', role: 'ux-designer', tmpl: '3-ux-art-audio.md', check: 'lite-3-ux-audio.md', data: ['accessibility', 'mobile'], reads: [1, 2] },
  4: { file: '4_Business and LiveOps.md', role: 'producer', tmpl: '4-business-liveops.md', check: 'lite-4-business.md', data: ['monetization', 'casual-metrics'], reads: [1, 2] },
  5: { file: '5_Tech Note.md', role: 'tech-designer', tmpl: '5-tech-note.md', check: 'lite-5-tech.md', data: ['mobile'], reads: [1, 2] },
}

// Waves: stage → dispatch units; a unit is the file numbers one dispatch writes, in order.
const UNITS = FULL
  ? { W2: [[3]], W3a: [[4]], W3b: [[5]], W4: [[6], [7]], W5: [[8], [10]], W6: [[9, 11]], W7: [[12]] }
  : { W1: [[1]], W2: [[2]], W3: [[3], [4], [5]] }
const ORDER = FULL
  ? ['W1', 'W2', 'W3a', 'W3b', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10']
  : ['W1', 'W2', 'W3', 'W4', 'FIX', 'INDEX']
const ANCHOR_STAGE = FULL ? 'W2' : 'W1'
// Write order (ch 9 reads ch 10; ch 11 reads ch 9) — used when several files change at one checkpoint.
const DEP_ORDER = FULL ? [3, 4, 5, 6, 7, 8, 10, 9, 11, 12, 0, 1, 2, 13] : [1, 2, 3, 4, 5, 0]
const CONTENT = FULL ? [3, 4, 5, 6, 7, 8, 9, 10, 11, 12] : [1, 2, 3, 4, 5]
const ALL_FILES = FULL ? [0, 1, 2, ...CONTENT, 13] : [0, ...CONTENT]

// ---------------------------------------------------------------------------------------------
// Model routing — the only place the kit picks models. No agent pins one in its frontmatter.
// deep  = no model set: the session's model (or CLAUDE_CODE_SUBAGENT_MODEL) — design judgement,
//         review, adversarial verification.
// spec  = template-driven spec writing, compiling, merging.
// clerk = mechanical bookkeeping: REPORT files, wc -w, run-meta/gap-log rows, slicing, Minor fixes.
const TIERS = { deep: {}, spec: { model: 'sonnet' }, clerk: { model: 'sonnet', effort: 'low' } }
const ROLE_TIER = {
  'concept-architect': 'deep', 'mechanics-designer': 'deep', 'narrative-designer': 'deep',
  'level-designer': 'deep', 'ai-designer': 'deep', 'tech-designer': 'deep', namer: 'deep', reviewer: 'deep',
  'ux-designer': 'spec', 'art-director': 'spec', producer: 'spec', scribe: 'spec',
}
function tierFor(role, n) {
  if (FULL && n === 5 && ['None', 'Light framing'].includes(FLAGS.d21)) return 'spec'   // mostly N/A lines
  if (FULL && n === 8 && FLAGS.d22 === 'None') return 'spec'
  return ROLE_TIER[role] || 'deep'
}
const route = tier => (A.model_override ? { model: A.model_override } : TIERS[tier])
const modelLabel = tier => A.model_override || TIERS[tier].model || 'session'

// ---------------------------------------------------------------------------------------------
// Schemas

const STR = { type: 'string' }
const STRS = { type: 'array', items: STR }
const INT = { type: 'integer' }
const SEV = { type: 'string', enum: ['blocker', 'major', 'minor'] }
const obj = (properties, required) => ({ type: 'object', properties, required: required || Object.keys(properties) })

const GAP = obj({
  id: STR, class: { type: 'string', enum: ['structural', 'value'] }, field: STR, section: STR, why: STR, options: STRS,
  kept: { type: 'boolean', description: 'true when this GAP was already open in the earlier version of the file (same id)' },
}, ['id', 'class', 'field', 'section', 'why', 'options'])
const REPORT = obj({
  status: { type: 'string', enum: ['complete', 'complete-with-gaps', 'blocked'] },
  files: STRS,
  gaps: { type: 'array', items: GAP },
  proposals: INT,
  checklist: STR,
  report: { type: 'string', description: 'your ## REPORT block (dispatch-rules.md §4), verbatim' },
}, ['status', 'files', 'gaps', 'report'])
const FINDING = obj({
  id: STR,
  severity: SEV,
  rule: { type: 'string', description: 'rule / contract clause / dispatch rule the defect breaks' },
  file: { type: 'string', description: 'name of the file that must change' },
  sections: STR,
  evidence: { type: 'string', description: 'verbatim quote(s), each with file name and §' },
  what: STR,
  fix: { type: 'string', description: 'the exact change to make' },
  needs_user: { type: 'boolean', description: 'true only when a decision is missing or two sources disagree and only the user can say which yields' },
  class: { type: 'string', enum: ['structural', 'value'] },
  options: STRS,
}, ['id', 'severity', 'file', 'sections', 'evidence', 'what', 'fix', 'needs_user'])
const FINDINGS = obj({ findings: { type: 'array', items: FINDING } })
const REVIEW = obj({ report: STR, findings: { type: 'array', items: FINDING } })
const VERDICT = obj({ real: { type: 'boolean' }, severity: SEV, owner_file: STR, needs_user: { type: 'boolean' }, reason: STR })
const WORDS = { type: 'array', items: obj({ file: STR, words: INT }) }
const BOOK = obj({ words: WORDS, missing: STRS, notes: STR }, ['words', 'missing'])
const NAMES = obj({ candidates: { type: 'array', items: obj({ name: STR, rationale: STR, pronounceability: STR, conflicts: STR }) } })
const ANCHOR = obj({
  pillars: { type: 'array', items: obj({ name: STR, meaning: STR, forbids: STR }) },
  features: { type: 'array', items: obj({ name: STR, priority: STR, pillar: STR }) },
  candidates: { type: 'array', items: obj({ name: STR, rationale: STR }) },
}, ['pillars', 'features'])
const CITERS = obj({ citers: { type: 'array', items: obj({ file: STR, cites: STR, changed: STR }) } })
const MINORFIX = obj({ applied: STRS, skipped: STRS })
const OPEN = obj({ majors: { type: 'array', items: FINDING }, minors: { type: 'array', items: FINDING }, iterations: INT })
const CRITIC = obj({ files: WORDS, open_decisions: INT, proposals: INT, minors_left: INT, findings: { type: 'array', items: FINDING } })

// ---------------------------------------------------------------------------------------------
// Helpers

let STAGE = A.from
const j = (dir, name) => String(dir).replace(/\/+$/, '') + '/' + name
const pad = n => String(n).padStart(2, '0')
const T = FULL ? CH : LF
const fileOf = n => j(OUT, T[n].file)
const numOf = p => { const m = /(?:^|\/)(\d+)_[^/]*$/.exec(String(p || '').trim()); return m ? Number(m[1]) : null }
const nextOf = s => ORDER[ORDER.indexOf(s) + 1] || null
const contractOf = n => j(KIT, FULL ? `references/contracts/ch${pad(n)}.md` : `references/contracts-lite/lite-${n}.md`)
const rulesFile = () => j(KIT, FULL ? 'references/consistency-rules.md' : 'references/consistency-rules-lite.md')
const RULES_LINE = `RULES: read ${j(KIT, 'references/dispatch-rules.md')} first and obey it in full — it is part of this prompt.`
const RETURN_LINE = 'RETURN: end by calling StructuredOutput — `report` = your `## REPORT` block (dispatch-rules.md §4) verbatim, the other fields parsed from it.'
const cp = (kind, next, items, more) => ({ status: 'checkpoint', checkpoint: { kind, stage: STAGE, next, items: items || [], ...(more || {}) } })
const json = x => JSON.stringify(x, null, 1)

function mode(values, fallback) {
  const counts = new Map()
  for (const v of values) counts.set(v, (counts.get(v) || 0) + 1)
  let best = fallback, top = 0
  for (const [v, c] of counts) if (c > top || (c === top && v === fallback)) { best = v; top = c }
  return best
}

function groupBy(items, key) {
  const m = new Map()
  for (const it of items) { const k = key(it); if (!m.has(k)) m.set(k, []); m.get(k).push(it) }
  return m
}

// Every agent call goes through here: model routing, agentType, one retry on a null result.
async function run(prompt, { label, phase: ph, schema, tier = 'deep', role } = {}) {
  const opts = { label, phase: ph, ...route(tier) }
  if (schema) opts.schema = schema
  if (role) opts.agentType = NS + 'gdd-' + role
  for (let attempt = 1; attempt <= 2; attempt++) {
    const r = await agent(prompt, opts)
    if (r) return r
    log(`${label}: no result${attempt === 1 ? ' — retrying once' : ''}`)
  }
  throw new Error(`${label} returned no result twice`)
}

function dataPaths(keys) {
  const out = []
  for (const k of keys || []) {
    if (k === 'patterns') out.push(j(KIT, 'data/game-design-patterns.md'))
    else if (k === 'mobile') out.push(j(KIT, 'data/platforms/mobile.md'))
    else if (k === 'casual-metrics') out.push(j(KIT, 'data/casual/metrics-definitions.md'))
    else if (k === 'monetization-if-f2p') { if (FLAGS.f2p_or_hybrid) out.push(...(DATA.monetization || [])) }
    else out.push(...(DATA[k] || []))
  }
  return [...new Set(out)]
}

// ---------------------------------------------------------------------------------------------
// Dispatch envelopes

const sliceFile = (n, src) => j(INPUTS, `ch${n}/ch${src}.md`)
const anchorCmd = () => `bash "${j(KIT, 'scripts/extract-sections.sh')}" "${fileOf(3)}" "${j(INPUTS, '_anchor.md')}" 3.2 3.10`

// What the writer of file n reads (absolute paths, with notes). Verification reads the same list.
function inputsOf(chs) {
  const ins = [j(WORK, 'brief.md')]
  if (FULL) {
    if (chs[0] >= 4) ins.push(`${j(INPUTS, '_anchor.md')} — ch 3 §3.2 pillars + §3.10 glossary; reuse these terms verbatim`)
    for (const n of chs) {
      const s = SLICES[n]
      if (!s) continue
      for (const w of s.whole) ins.push(chs.includes(w) ? `${fileOf(w)} — your own file from this same dispatch, written first` : fileOf(w))
      for (const [src] of s.parts) ins.push(sliceFile(n, src))
    }
    for (const n of chs) ins.push(`template: ${j(KIT, 'templates/chapters/' + CH[n].tmpl)}`)
    const checks = [...new Set(chs.flatMap(n => CH[n].checks || []))]
    if (checks.length) ins.push(`checklists: ${checks.map(c => j(KIT, 'checklists/' + c)).join(', ')}`)
    const data = dataPaths(chs.flatMap(n => CH[n].data || []))
    if (data.length) ins.push(`data: ${data.join(', ')}`)
  } else {
    const f = LF[chs[0]]
    for (const r of f.reads) ins.push(`${fileOf(r)} (whole)`)
    ins.push(`template: ${j(KIT, 'templates/lite/' + f.tmpl)}`)
    ins.push(`checklist: ${j(KIT, 'checklists/lite/' + f.check)}`)
    const data = dataPaths(f.data)
    if (data.length) ins.push(`data: ${data.join(', ')}`)
  }
  return ins
}

function writePrompt(chs, extra) {
  const n = chs[0], t = T[n], files = chs.map(fileOf)
  const lines = FULL
    ? [
      `ROLE: you are gdd-${t.role} writing ${chs.map(c => CH[c].file).join(' then ')} for the GDD of "${GAME}".`,
      `LANGUAGE: write the body in ${A.lang}. Keep heading numbers in English ("# ${n}. …").`,
      RULES_LINE,
      `CONTRACT: read ${chs.map(contractOf).join(' and ')}. Obey Sections, Depth rule, Hard rules (and Owns / Budget where the contract has them).`,
    ]
    : [
      `ROLE: you are gdd-${t.role} writing ${t.file} for the GDD of "${GAME}" (lite profile — ${A.profile}).`,
      `LANGUAGE: write the body in ${A.lang}. Keep heading numbers in English ("# ${n}. …").`,
      RULES_LINE,
      `CONTRACT: read ${contractOf(n)} in full. Obey Sections, Owns, Budget, Depth rule, Hard rules.`,
    ]
  if (FULL ? t.guidance : true) lines.push(`GUIDANCE: read ${j(KIT, `references/guidance/${t.role}.${FULL ? 'full' : 'lite'}.md`)} — craft advice for this ${FULL ? 'chapter' : 'file'}.`)
  lines.push(FULL
    ? 'INPUTS (read all of these, read nothing else — the slices already contain every upstream section your contract lets you consume, so never open the full chapter they came from):'
    : 'INPUTS (read all, read nothing else):')
  for (const p of inputsOf(chs)) lines.push(`  - ${p}`)
  lines.push(`OUTPUT: write exactly ${files.length === 1 ? 'one file' : `${files.length} files, in this order`}: ${files.join(' then ')}.`)
  if (extra) lines.push(extra)
  lines.push(RETURN_LINE)
  return lines.join('\n')
}

function patchPrompt(n, body) {
  const t = T[n]
  return [
    `ROLE: you are gdd-${t.role} revising ${t.file} for the GDD of "${GAME}"${FULL ? '' : ` (lite profile — ${A.profile})`}.`,
    `LANGUAGE: body in ${A.lang}; headings keep the English numbered prefix.`,
    RULES_LINE,
    `CONTRACT: ${contractOf(n)}.`,
    `INPUTS: ${j(WORK, 'brief.md')}; your own file. Open nothing else unless an item below names it.`,
    `PATCH MODE: ${fileOf(n)} exists. ${body} Report as usual — but GAPS lists only GAPs this PATCH newly raised (an older ⟂ GAP still in the file is not re-listed).`,
    RETURN_LINE,
  ].join('\n')
}

const itemLine = f => `- ${f.id} [${f.severity}] ${f.sections}: ${f.what} — evidence: ${f.evidence} — fix: ${f.fix}`
const reviewItemsBody = items => `Fix only these review items, and everything in your file that depends on them:\n${items.map(itemLine).join('\n')}\n`

async function writeUnit(chs, { update, items, phaseName = 'Write' } = {}) {
  const n = chs[0], role = T[n].role, tier = tierFor(role, n)
  const extra = update
    ? [
      `UPDATE: ${chs.map(fileOf).join(' and ')} already exist${chs.length > 1 ? '' : 's'} from an earlier dispatch — rewrite whole with Write.${update.length ? ` brief.md now carries new Gate additions (${update.join(', ')}); integrate them through the whole file.` : ''}`,
      `GAP ids: a GAP still open from the earlier version keeps its id (mark it kept: true); number a new GAP after the highest G-${n}-<n> already in ${j(WORK, 'gap-log.md')} (read it for that only).`,
      items && items.length ? `Also fix these review items through the whole file:\n${items.map(itemLine).join('\n')}` : '',
    ].filter(Boolean).join('\n')
    : ''
  const rep = await run(writePrompt(chs, extra), { label: `write:${T[n].file}`, phase: phaseName, schema: REPORT, tier, role })
  return { chs, role, tier, rep }
}

async function patchFile(n, body, phaseName) {
  const role = T[n].role || 'scribe', tier = tierFor(role, n)
  const rep = await run(patchPrompt(n, body), { label: `patch:${T[n].file}`, phase: phaseName, schema: REPORT, tier, role })
  return { chs: [n], role, tier, rep, patched: true }
}

// ---------------------------------------------------------------------------------------------
// Clerk steps (bookkeeping, slicing, extraction) — mechanical, cheap tier

async function clerk(task, { label, phaseName, schema = BOOK }) {
  return run([
    `You are the bookkeeping clerk of a gdd-forge run ("${GAME}"). Do exactly the steps below with Bash/Read/Edit/Write.`,
    'Never change a chapter file unless a step says so. Never invent a value — copy from what you are given or what is on disk.',
    task,
  ].join('\n'), { label, phase: phaseName, schema, tier: 'clerk' })
}

const cmdBlock = cmds => cmds.map(c => `    ${c}`).join('\n')

// Full profile: rebuild _anchor.md and the slices for these chapter numbers. A MISSING section gets
// one PATCH to its owner (restore the N/A heading or write the section), then a re-slice; a second
// MISSING is an error the main agent must look at.
async function prepareSlices(nums, phaseName = 'Write') {
  if (!FULL) return
  const cmds = nums.some(n => n >= 4 && n <= 12) ? [anchorCmd()] : []   // ch 3 itself makes the anchor
  for (const n of nums) for (const [src, ...specs] of (SLICES[n] || { parts: [] }).parts) {
    cmds.push(`bash "${j(KIT, 'scripts/extract-sections.sh')}" "${fileOf(src)}" "${sliceFile(n, src)}" ${specs.join(' ')}`)
  }
  if (!cmds.length) return
  for (let attempt = 1; attempt <= 2; attempt++) {
    const r = await clerk([
      'Run these commands in order and return every stdout line containing MISSING, prefixed with the source file name (e.g. "4_Gameplay and Mechanics.md: MISSING: §4.5"). Return words: [].',
      cmdBlock(cmds),
    ].join('\n'), { label: `slices:${nums.join('+')}`, phaseName })
    const missing = (r.missing || []).filter(l => /MISSING/.test(l))
    if (!missing.length) return
    const noFile = missing.filter(l => /MISSING FILE/.test(l))
    if (noFile.length) throw new Error(`upstream file not on disk: ${noFile.join(' | ')} — resume from the wave that writes it`)
    if (attempt === 2) throw new Error(`slice still MISSING after a PATCH: ${missing.join(' | ')} — record the contract/template discrepancy in run-meta.md, fix the source, then call again from ${STAGE}`)
    const bySrc = groupBy(missing, l => numOf(l.split(':')[0]))
    await parallel([...bySrc].map(([src, lines]) => () => {
      const secs = lines.map(l => (/§\s*([\d.]+)/.exec(l) || [])[1]).filter(Boolean)
      return patchFile(src, `These numbered sections are missing: ${secs.map(s => '§' + s).join(', ')}. For each: if a Depth rule removed it, restore the heading followed by the single line 'N/A — <reason, ≤ 12 words>.'; otherwise write the section per your contract.`, phaseName)
    }))
  }
}

// Save REPORT blocks, measure files, append run-meta and gap-log rows, write per-file check notes.
async function bookkeep(stage, entries, { verifies = [], commands = [], resolved = [], phaseName = 'Write' } = {}) {
  const data = {
    stage,
    dispatches: entries.filter(Boolean).map(e => ({
      files: e.chs.map(fileOf),
      agent: 'gdd-' + e.role,
      model: modelLabel(e.tier),
      status: e.patched ? 'patched' : e.rep.status,
      self_check: e.rep.checklist || '',
      report_paths: e.chs.map(n => j(WORK, `reports/${T[n].file}.report.md`)),
      report: e.rep.report,
      gaps: (e.rep.gaps || []).map(g => ({ ...g, raised_by: 'gdd-' + e.role })),
    })),
    checks: verifies.filter(Boolean).map(v => ({
      path: j(WORK, `checks/${T[v.n].file}.check.md`),
      raised: v.raised, refuted: v.refuted,
      confirmed: v.confirmed.map(c => ({ id: v.asked[c.id] || c.id, severity: c.severity, sections: c.sections, what: c.what, disposition: v.fixed.includes(c.id) ? 'patched' : v.asked[c.id] ? 'asked the user' : 'left for the review' })),
      minors_patched: v.minorsSent,
    })),
    resolved,
  }
  const r = await clerk([
    `DATA (JSON): ${json(data)}`,
    'Steps:',
    '1. For each dispatch, write `report` verbatim to each of its report_paths, overwriting — except status "patched": append it to the existing file after a line `<!-- patch: ' + stage + ' -->` (create the file if missing), so the first block stays the writer\'s own REPORT.',
    '2. Run `wc -w` on every file in every dispatch; return the counts as `words` (file = file name only).',
    `3. Append one row per dispatch to the \`## Waves\` table of ${j(WORK, 'run-meta.md')}: | ${stage} | <file names> | <agent> | <model> | <status> | <words> | <self_check> | <notes> | (notes: empty unless a step here failed).`,
    `4. Append one row per GAP to the table in ${j(WORK, 'gap-log.md')}: | <id> | ${stage} | <raised_by> | <field> | <class> | <section> | <why> |  |  |  | — skip an id already in the table.`,
    '5. For each `resolved` entry whose id is in the gap-log.md table, fill its `Patched files` cell with its files (append if already filled); skip ids not in the table.',
    '6. For each `checks` entry, write its path: a short Markdown note listing raised / refuted counts and one line per confirmed finding (id, severity, sections, what, disposition), then the Minors patched. Create the folder if needed.',
    `6b. Copy every line starting \`NOTE:\` in a dispatch's \`report\` to the \`## Discrepancies\` section of ${j(WORK, 'run-meta.md')} as one bullet each, prefixed with the file name (skip a bullet already there).`,
    commands.length ? `7. Run these commands in order; return every stdout line containing MISSING, prefixed with the source file name:\n${cmdBlock(commands)}` : '7. (no commands) Return missing: [].',
  ].join('\n'), { label: `book:${stage}`, phaseName })
  return r
}

// ---------------------------------------------------------------------------------------------
// Adversarial verification

const LENSES = [
  { key: 'evidence', ask: 'Open the cited file(s). Refute if the quoted evidence is not there verbatim, is misread, or is taken out of context.' },
  { key: 'rule', ask: 'Open the rule, contract clause or brief field the finding relies on. Refute if it does not actually forbid or require this — e.g. the "restatement" is an allowed pointer (→ §x.y), a tagged (proposal), a formula, a Depth-rule N/A line, or a value the brief really states.' },
  { key: 'severity', ask: 'Judge consequence and ownership. Refute if it is cosmetic and was raised as major/blocker (re-grade it), or if the named owner file is wrong (name the right one). needs_user = true only if no file can be fixed without a decision the user has not made.' },
]

function votePrompt(f, lens, scope) {
  return [
    `ROLE: skeptical verifier. Try to REFUTE one finding about the GDD "${GAME}". When you cannot confirm it from the files themselves, return real=false.`,
    `FINDING ${f.id} (claimed ${f.severity}; file to change: ${f.file}; rule: ${f.rule || 'n/a'}): ${f.what}`,
    `EVIDENCE CLAIMED: ${f.evidence}`,
    `PROPOSED FIX: ${f.fix}`,
    `YOUR LENS — ${lens.key}: ${lens.ask}`,
    `READ what you need from: ${scope.join(' · ')}. brief.md, the rules files and the contracts are the authority; chapter files are the evidence.`,
    'Severity scale: blocker = only the user can resolve it (missing decision, or sources disagree and nothing says which yields); major = another section or file must change, or a rule / Hard rule is broken; minor = wording or formatting only.',
    'Return real, your severity, owner_file (name of the file that must change), needs_user, and a one-line reason.',
  ].join('\n')
}

// Three voters with different lenses; a finding survives with ≥ 2 upholds. Severity, owner and
// needs_user follow the upholding voters' majority.
// A Minor gets one evidence check instead (wording only — a false positive costs little).
async function judge(f, scope, phaseName) {
  const minor = f.severity === 'minor'
  const lenses = minor ? LENSES.slice(0, 1) : LENSES
  const votes = await parallel(lenses.map(l => () =>
    run(votePrompt(f, l, scope), { label: `vote:${l.key}:${f.id}`, phase: phaseName, schema: VERDICT })))
  const ups = votes.filter(Boolean).filter(v => v.real)
  if (ups.length < (minor ? 1 : 2)) return { ...f, real: false }
  return {
    ...f,
    real: true,
    severity: mode(ups.map(v => v.severity), f.severity),
    file: mode(ups.map(v => v.owner_file).filter(Boolean), f.file),
    needs_user: ups.filter(v => v.needs_user).length * 2 > ups.length,
  }
}

function verifyPrompt(n) {
  return [
    `ROLE: adversarial checker for ${fileOf(n)} in the GDD "${GAME}", just written by gdd-${T[n].role}. You change nothing; you find defects with evidence.`,
    `READ: that file; its contract ${contractOf(n)}; ${j(KIT, 'references/dispatch-rules.md')}; ${j(WORK, 'gap-log.md')}; and exactly what the writer was given:`,
    ...inputsOf([n]).map(p => `  - ${p}`),
    'FIND only real defects:',
    '1. a number, count, name, rule or priority that contradicts brief.md or an upstream input;',
    '2. an invented decision — a feature, mode, screen, platform, monetisation mechanism, price or legal commitment brief.md does not make, written as fact instead of a ⟂ GAP or a tagged (proposal);',
    '3. one fact, one home broken — an upstream-owned value restated with its own value instead of → §x.y; a count that does not match its list; a derived number listed as its own tunable;',
    '4. a cited §x.y that does not hold what the file claims; a glossary term respelled or redefined;',
    `5. contract conformance — a numbered heading from the contract's Sections missing; an N/A section longer than one line; a Hard rule broken${FULL ? '' : '; over the file Budget (measure with wc -w)'};`,
    '6. kit vocabulary in the deliverable (dispatch-rules.md §2 rule 7).',
    'severity: major = changes what another section or file must say, or breaks a rule / Hard rule; minor = wording or format. Use blocker / needs_user only when a decision is missing or two sources disagree and only the user can say which yields — then give 2–3 options and a class (value | structural).',
    `file = the file that must change (normally ${T[n].file}; name the upstream file if the fault is there). Ids: F-1, F-2, … Return an empty list when the file is clean — never pad.`,
  ].join('\n')
}

// One finder → voters for every major/blocker → one PATCH for confirmed fixable items (Minors ride
// along) → items that need the user become checkpoint questions (V-ids).
async function verifyFile(n, tag, phaseName = 'Verify') {
  const found = await run(verifyPrompt(n), { label: `verify:${T[n].file}`, phase: phaseName, schema: FINDINGS })
  const raw = found.findings || []
  const majors = raw.filter(f => f.severity !== 'minor')
  const minors = raw.filter(f => f.severity === 'minor')
  const scope = [fileOf(n), contractOf(n), j(KIT, 'references/dispatch-rules.md'), j(WORK, 'gap-log.md'), ...inputsOf([n])]
  const judged = (await parallel(majors.map(f => () => judge(f, scope, phaseName)))).filter(Boolean)
  const confirmed = judged.filter(x => x.real)
  const ask = confirmed.filter(x => x.needs_user || x.severity === 'blocker' || (numOf(x.file) !== null && numOf(x.file) !== n))
  const fix = confirmed.filter(x => !ask.includes(x) && x.severity === 'major')
  const minorsSent = fix.length ? [...confirmed.filter(x => x.severity === 'minor'), ...minors] : []
  let patch = null
  if (fix.length) patch = await patchFile(n, reviewItemsBody([...fix, ...minorsSent]), phaseName)
  const asked = {}
  const items = ask.map((x, i) => {
    const id = `V-${n}-${tag}${i + 1}`
    asked[x.id] = id
    const file = absFile(x.file, n), up = numOf(file) !== n
    // An upstream fault needs no design decision, only the user's call on which file yields.
    const options = x.options && x.options.length ? x.options
      : up ? [`Fix ${T[numOf(file)].file} as proposed: ${x.fix}`, `Keep ${T[numOf(file)].file}; align ${T[n].file} instead`] : []
    return { id, file, owner: T[numOf(file)].role || 'orchestrator', class: x.class || (up ? 'value' : 'structural'), field: x.what, section: x.sections, why: x.evidence, options }
  })
  if (patch) items.push(...gapItems(patch))
  log(`verify ${T[n].file}: ${raw.length} raised, ${confirmed.length} confirmed, ${fix.length} auto-patched, ${items.length} for the user`)
  return { n, raised: raw.length, refuted: majors.length - confirmed.length, confirmed, fixed: fix.map(x => x.id), asked, minorsSent: minorsSent.map(m => m.id), items, patch }
}

// A GAP belongs to the chapter in its id (G-<ch>-<n>) — matters for the two-file ch 9 + ch 11 dispatch.
const gapItems = e => (e.rep.gaps || []).filter(g => !g.kept).map(g => {
  const ch = Number((/^G-(\d+)-/.exec(g.id || '') || [])[1])
  return { ...g, file: fileOf(e.chs.includes(ch) ? ch : e.chs[0]), owner: e.role }
})
// Absolute path of a finding's file when it names a GDD file, else the fallback chapter's file.
const absFile = (name, fallback) => (numOf(name) !== null && T[numOf(name)] ? fileOf(numOf(name)) : fileOf(fallback))

// ---------------------------------------------------------------------------------------------
// Stage: apply the answers from the previous checkpoint

const NO_DISPATCH = ['edited', 'undecided', 'approved', 'another_round', 'accept']
const RESOLVED = []   // files changed while applying answers in this segment — the fix loop rechecks them

async function applyResolutions() {
  const rs = A.resolutions || []
  if (!rs.length) return null
  STAGE = 'resolve'
  const act = rs.filter(r => r.file && !NO_DISPATCH.includes(r.action))
  const byFile = groupBy(act, r => numOf(r.file))
  const nums = [...byFile.keys()].filter(n => n !== null).sort((a, b) => a - b)
  if (!nums.length && !rs.some(r => r.cascade)) return null
  log(`applying ${act.length} answer(s) to ${nums.length} file(s)`)

  // One file at a time, upstream first, so a re-written file reads its already-corrected inputs.
  nums.sort((a, b) => DEP_ORDER.indexOf(a) - DEP_ORDER.indexOf(b))
  const fresh = nums.filter(n => byFile.get(n).some(r => r.action === 'fresh'))
  const done = []
  for (const n of nums) {
    const group = byFile.get(n)
    if (fresh.includes(n)) {
      await prepareSlices([n], 'Resolve')
      done.push(await writeUnit([n], { update: group.map(r => r.id), phaseName: 'Resolve' }))
      continue
    }
    const gaps = group.filter(r => /^G-/.test(r.id)), decisions = group.filter(r => !/^G-/.test(r.id))
    const body = [
      gaps.length ? `Replace only the placeholder(s) ${gaps.map(r => r.id).join(', ')} and everything that depends on them — answers: ${gaps.map(r => `${r.id} → ${r.answer}`).join('; ')}.` : '',
      decisions.length ? `Apply these user decisions and change everything in your file that depends on them: ${decisions.map(r => `${r.id}${r.sections ? ` (${r.sections})` : ''} → ${r.answer}`).join('; ')}.` : '',
      'The answers are also recorded in brief.md under Gate additions.',
    ].filter(Boolean).join(' ')
    done.push(await patchFile(n, body, 'Resolve'))
  }

  // Facts owned by a changed file and cited elsewhere: PATCH every citing file that already exists.
  const cascades = rs.filter(r => r.cascade)
  let cascaded = []
  if (cascades.length) {
    const found = await clerk([
      `For each changed fact below, grep every *.md directly in ${OUT} (not _work/) except the changed file itself for a reference to its sections (§x.y) or for the terms / values the answer changes. Return one entry per citing file: file (name), cites (the §/term it cites), changed (the changed file name + sections).`,
      `CHANGED (JSON): ${json(cascades.map(r => ({ file: r.file, sections: r.sections || '', answer: r.answer })))}`,
    ].join('\n'), { label: 'cascade:find-citers', phaseName: 'Resolve', schema: CITERS })
    const byCiter = groupBy(found.citers || [], c => numOf(c.file))
    cascaded = await parallel([...byCiter].filter(([n]) => n !== null && T[n]).map(([n, cs]) => () =>
      patchFile(n, `Upstream changed: ${cs.map(c => c.changed).join('; ')}. Align only what cites it (${cs.map(c => c.cites).join(', ')}).`, 'Resolve')))
  }

  const blockedNow = done.filter(d => !d.patched && d.rep.status === 'blocked').map(d => d.chs[0])
  const verifies = await parallel(fresh.filter(n => !blockedNow.includes(n)).map(n => () => verifyFile(n, `U${A.from}.`, 'Resolve')))
  const entries = [...done, ...cascaded.filter(Boolean)]
  RESOLVED.push(...entries.map(e => e.chs[0]))
  await bookkeep('resolve', entries, {
    verifies,
    commands: FULL && (nums.includes(3) || cascaded.some(c => c && c.chs[0] === 3)) ? [anchorCmd()] : [],
    resolved: act.map(r => ({ id: r.id, files: [r.file.split('/').pop()] })),
    phaseName: 'Resolve',
  })

  const items = [...entries.flatMap(gapItems), ...verifies.filter(Boolean).flatMap(v => v.items)]
  if (blockedNow.length) return cp('gaps', A.from, items, { blocked: blockedNow.map(fileOf), note: 'blocked again after a fresh re-dispatch — read its saved REPORT in WORK/reports/ for the reason before answering' })
  // Back to the anchor approval after the anchor file is re-written before it was approved.
  const anchorN = FULL ? 3 : 1
  const anchorRedo = rs.some(r => r.id === 'ANCHOR' && r.action === 'fresh') || (fresh.includes(anchorN) && A.from === nextOf(ANCHOR_STAGE))
  if (anchorRedo) return anchorCheckpoint(A.from, items)
  if (items.length) return cp('gaps', A.from, items, { note: 'raised while applying the previous answers' })
  return null
}

// ---------------------------------------------------------------------------------------------
// Stage: name (full profile W1)

async function nameStage() {
  if (!FLAGS.need_name) return null
  const r = await run([
    `ROLE: you are gdd-namer producing 8 ranked name candidates for the GDD of "${A.game_name || 'an untitled game'}".`,
    `LANGUAGE: candidate names may be any language; pronounceability notes cover ${A.lang} and English.`,
    RULES_LINE,
    'CONTRACT: none — your agent file is the whole contract.',
    `INPUTS (read all of these, read nothing else): ${j(WORK, 'brief.md')}`,
    'OUTPUT: no file — return the ranked list.',
    'RETURN: end by calling StructuredOutput with the 8 candidates in rank order; `conflicts` must say you cannot check trademarks or store listings.',
  ].join('\n'), { label: 'name:gdd-namer', phase: 'Name', schema: NAMES, tier: tierFor('namer'), role: 'namer' })
  return cp('name', 'W2', [], { candidates: r.candidates })
}

// ---------------------------------------------------------------------------------------------
// Stage: one writing wave (write → verify per unit, pipelined) → bookkeeping → checkpoint if needed

async function anchorCheckpoint(next, items) {
  const n = FULL ? 3 : 1
  const secs = FULL ? '§3.2 (pillars: name, meaning, forbids) and §3.3 (features: name, P0/P1/P2, pillar)' : '§1.4 (pillars: name, meaning, forbids) and §1.5 (features: name, P0/P1/P2, pillar)'
  const wantNames = !FULL && FLAGS.need_name
  const a = await run([
    `Read ${fileOf(n)} and return ${secs}${wantNames ? ', plus the §1.2 name candidates (name + one-line rationale)' : ''}, copied faithfully and briefly in the file's language. Change nothing.`,
  ].join('\n'), { label: 'anchor:summary', phase: 'Verify', schema: ANCHOR, tier: 'spec' })
  return cp('anchor', next, items, {
    file: fileOf(n),
    anchor: { pillars: a.pillars, features: a.features },
    candidates: wantNames ? (a.candidates || []) : undefined,
  })
}

async function waveStage(stage) {
  const units = UNITS[stage]
  await prepareSlices(units.flat())
  const results = await pipeline(units,
    u => writeUnit(u),
    w => (w.rep.status === 'blocked'
      ? { ...w, verifies: [] }
      : parallel(w.chs.map(n => () => verifyFile(n, `${stage}.`))).then(vs => ({ ...w, verifies: vs }))))
  if (results.some(r => !r)) throw new Error(`a ${stage} dispatch failed twice`)
  const verifies = results.flatMap(r => r.verifies)
  if (verifies.some(v => !v)) throw new Error(`a ${stage} verification failed twice`)
  const entries = [...results, ...verifies.map(v => v.patch).filter(Boolean)]
  await bookkeep(stage, entries, { verifies, commands: FULL && stage === 'W2' ? [anchorCmd()] : [] })

  const items = [...results.flatMap(gapItems), ...verifies.flatMap(v => v.items)]
  const blocked = results.filter(r => r.rep.status === 'blocked').map(r => r.chs.map(fileOf)).flat()
  const next = nextOf(stage)
  if (stage === ANCHOR_STAGE && !blocked.length) return anchorCheckpoint(next, items)
  if (items.length || blocked.length) {
    return cp('gaps', next, items, blocked.length ? { blocked, note: 'a blocked file always gets action "fresh"' } : undefined)
  }
  return null
}

// ---------------------------------------------------------------------------------------------
// Stage: review (W8 full / W4 lite) — reviewer ‖ lens finders → merge → adversarial verify → report

const LENS_FINDERS = [
  { key: 'contradictions', ask: 'Every number, threshold, price, cadence, count, name and yes/no rule that appears in more than one file: find each key with two different values, each count that does not equal its list, each derived value also listed as its own tunable, each upstream-owned fact restated with its own value that drifted.' },
  { key: 'fidelity', ask: 'brief.md against the deliverable: invented decisions (written as fact, not a ⟂ GAP or (proposal)), UNDECIDED brief fields missing from every Open Decisions box, D-44 exclusions violated, pillar forbid clauses violated by a mechanic / screen / monetisation / tech choice, a feature outranking a feature it depends on, external facts with no data-file or brief source.' },
  { key: 'closure', ask: 'Inventories and flows close: every named screen, term, asset, SDK, currency and persisted value has a row in the inventory that owns it; every player choice has a home screen and a flow edge reaching it; every cited §x.y holds what is claimed; glossary terms are reused verbatim; asset names follow the single naming pattern.' },
  { key: 'hygiene', ask: 'Contract conformance and proportion: every numbered heading of each contract\'s Sections present; Depth-rule N/A sections are one line; Hard rules hold; budgets respected (measure with wc -w where a contract has one); no kit vocabulary in the deliverable (dispatch-rules.md §2 rule 7); scope proportionate to D-09 / D-10; no padding or restated section purposes.' },
]

function reviewInputs() {
  const contracts = CONTENT.map(contractOf)
  return [
    ...CONTENT.map(fileOf),
    j(WORK, 'brief.md'), j(WORK, 'gap-log.md'), rulesFile(), ...contracts,
    j(KIT, 'references/dispatch-rules.md'),
  ]
}

function reviewerPrompt(recheck) {
  const checklists = FULL ? `every ${j(KIT, 'checklists')}/*.md (top level only — never checklists/lite/)` : `every ${j(KIT, 'checklists/lite')}/*.md`
  return [
    `ROLE: you are gdd-reviewer ${recheck ? 'running a RECHECK on' : 'producing the review of'} the GDD of "${GAME}"${FULL ? '' : ` (lite profile — ${A.profile})`}.`,
    `LANGUAGE: body in ${A.lang}; headings keep the English numbered prefix.`,
    RULES_LINE,
    `CONTRACT: ${rulesFile()} plus ${CONTENT.map(contractOf).join(', ')}.`,
    recheck
      ? `INPUTS (read all of these, read nothing else): ${recheck.files.map(fileOf).join(', ')} (whole); ${j(WORK, 'fact-ledger.md')}; ${j(WORK, 'brief.md')}; ${j(WORK, 'gap-log.md')}; open another chapter only to check a ledger row a patched file cites.`
      : `INPUTS (read all of these, read nothing else): ${CONTENT.map(fileOf).join(', ')} (whole); ${j(WORK, 'brief.md')}; ${j(WORK, 'gap-log.md')}; ${j(WORK, 'reports')}/*; ${checklists}; ${j(WORK, 'checks')}/* (per-file verification already done — do not re-raise a finding marked patched unless it is still present).`,
    recheck
      ? `RECHECK: only these files were just patched: ${recheck.files.map(n => T[n].file).join(', ')}${recheck.items.length ? ` — for these items:\n${recheck.items.map(itemLine).join('\n')}` : ''}\nRe-run rules 1–12 against the patched files only and update their rows in ${j(WORK, 'fact-ledger.md')}. Do not rewrite review-report.md or re-open the checklist matrix.`
      : `OUTPUT: write exactly ${j(WORK, 'review-report.md')} and ${j(WORK, 'fact-ledger.md')}.`,
    `RETURN: end by calling StructuredOutput — \`report\` = your ## REPORT block; \`findings\` = every ${recheck ? 'finding still failing or newly introduced' : 'Blocker, Major and Minor'} as an object (id, severity, rule, file = the file that must change, sections, evidence, what, fix, needs_user, options for Blockers).`,
  ].join('\n')
}

function lensPrompt(l, focus) {
  return [
    `ROLE: independent reviewer of the GDD "${GAME}"${FULL ? '' : ` (lite profile — ${A.profile})`} through one lens. You change nothing; you find defects with verbatim evidence.`,
    `READ: ${reviewInputs().join(' · ')}.`,
    focus ? `FOCUS: ${focus}` : '',
    `LENS — ${l.key}: ${l.ask}`,
    `Cite the rule number from ${rulesFile()} (or the contract / dispatch-rules clause) each finding breaks. file = the file that must change: for a contradiction, the file that does NOT own the fact (owner = the file whose contract Sections define it); if the owning file contradicts itself, the owning file; if unclear, the higher-numbered file.`,
    'severity: blocker = only the user can resolve it (give options + class); major = cross-file contradiction, contract miss or broken rule; minor = wording / formatting only. Ids: L-1, L-2, … Return an empty list when you find nothing — never pad.',
  ].filter(Boolean).join('\n')
}

async function mergeFindings(raw, phaseName) {
  if (!raw.length) return []
  const r = await run([
    `Merge these ${raw.length} raw findings from independent reviewers of the GDD "${GAME}" (JSON below). Merge only true duplicates — same defect at the same place — keeping the clearest evidence and the strictest severity. Keep every distinct finding; do not judge or drop any. Re-number ids R-1, R-2, … in file order. Keep each finding's file (the file that must change).`,
    `RAW (JSON): ${json(raw)}`,
  ].join('\n'), { label: 'merge', phase: phaseName, schema: FINDINGS, tier: 'spec' })
  return r.findings || []
}

let REVIEW_STATE = null   // set by reviewStage when W8 → W9 run in the same segment

async function reviewStage() {
  const scope = reviewInputs()
  const outs = await parallel([
    () => run(reviewerPrompt(), { label: 'review:gdd-reviewer', phase: 'Review', schema: REVIEW, tier: 'deep', role: 'reviewer' }),
    ...LENS_FINDERS.map(l => () => run(lensPrompt(l), { label: `review:lens-${l.key}`, phase: 'Review', schema: FINDINGS })),
  ])
  if (!outs[0]) throw new Error('gdd-reviewer returned no result twice')
  const raw = outs.flatMap((o, i) => (o ? o.findings || [] : []).map(f => ({ ...f, source: i === 0 ? 'reviewer' : LENS_FINDERS[i - 1].key })))
  const dropped = outs.slice(1).map((o, i) => (o ? null : LENS_FINDERS[i].key)).filter(Boolean)
  if (dropped.length) log(`lens finder(s) with no result: ${dropped.join(', ')} — review ran without them`)
  const merged = await mergeFindings(raw, 'Review')
  const judged = (await parallel(merged.map(f => () => judge(f, scope, 'Review')))).filter(Boolean)
  const confirmed = judged.filter(x => x.real)
  const blockers = confirmed.filter(x => x.severity === 'blocker' || x.needs_user)
  const majors = confirmed.filter(x => x.severity === 'major' && !blockers.includes(x))
  const minors = confirmed.filter(x => x.severity === 'minor')
  // Minors are judged too: anything that reached the report survived the same vote.
  await run([
    `Rewrite ${j(WORK, 'review-report.md')} (written by gdd-reviewer moments ago) so it reports only the verified findings below, in this exact shape:`,
    `# Review report — ${GAME} ${A.version || ''}`,
    '## Blockers   (decision missing → needs the user)          — id · chapter § · what · suggested options',
    '## Majors     (cross-chapter contradiction / contract miss) — id · chapters · what · owner agent',
    '## Minors     (wording, formatting, checklist nits)         — id · chapter · what',
    '## Checklist matrix   chapter × checklist → pass %   (keep gdd-reviewer\'s matrix as written)',
    '## Consistency rules  1–12 → PASS/FAIL + evidence   (keep gdd-reviewer\'s verdicts, but a rule is FAIL whenever a verified finding below cites it — add that evidence)',
    '## Verification — raised per source, merged, confirmed, refuted (counts below)',
    `Owner agent of a file: ${CONTENT.map(n => `${T[n].file} → gdd-${T[n].role}`).join('; ')}.`,
    `VERIFIED (JSON): ${json({ blockers, majors, minors })}`,
    `COUNTS (JSON): ${json({ raised: raw.length, by_source: Object.fromEntries([...groupBy(raw, f => f.source)].map(([k, v]) => [k, v.length])), merged: merged.length, confirmed: confirmed.length, refuted: merged.length - confirmed.length, lens_finders_missing: dropped })}`,
    `Then append one row to the \`## Waves\` table of ${j(WORK, 'run-meta.md')}: | ${STAGE} | review-report.md | gdd-reviewer + 4 lenses | ${modelLabel('deep')} | complete | — | — | ${blockers.length} blockers / ${majors.length} majors / ${minors.length} minors after verification |`,
  ].join('\n'), { label: 'review:report', phase: 'Review', tier: 'spec' })
  REVIEW_STATE = { majors, minors }
  log(`review: ${raw.length} raised → ${merged.length} merged → ${confirmed.length} confirmed (${blockers.length} blockers, ${majors.length} majors, ${minors.length} minors)`)
  if (blockers.length) return cp('blockers', nextOf(STAGE), blockers.map(toItem))
  return null
}

const toItem = f => ({
  id: f.id, file: numOf(f.file) !== null && T[numOf(f.file)] ? fileOf(numOf(f.file)) : f.file,
  owner: numOf(f.file) !== null && T[numOf(f.file)] ? T[numOf(f.file)].role || 'orchestrator' : '',
  class: f.class || 'structural', field: f.what, section: f.sections, why: f.evidence, options: f.options || [],
})

// ---------------------------------------------------------------------------------------------
// Stage: fix loop (W9 full / FIX lite) — until clean, ≤ 2 rounds per segment (1 on extra_round)

async function fixStage() {
  let state = REVIEW_STATE
  if (!state) {
    state = await run([
      `Read ${j(WORK, 'review-report.md')}. Return every Major and every Minor that is still open: listed under ## Majors / ## Minors and not marked patched, fixed, listed or accepted in a "## Fix loop" table (if that table exists, its open rows are the Majors still open). Copy each as a finding object (id, severity, file = the file that must change, sections, evidence, what, fix, needs_user=false). Also return iterations = the number on the "iterations:" line of ${j(WORK, 'run-meta.md')} § Fix loop (0 if absent). Change nothing.`,
    ].join('\n'), { label: 'fix:load-open', phase: 'Fix', schema: OPEN, tier: 'spec' })
  }
  const base = state.iterations || 0   // fix-loop rounds already run in earlier segments → unique R ids
  const routable = f => numOf(f.file) !== null && T[numOf(f.file)]
  let open = (state.majors || []).filter(routable)
  let blockers = (state.majors || []).filter(f => !routable(f)).map(f => ({ ...f, needs_user: true }))   // no GDD file to patch → the user
  const minors = state.minors || []
  const cap = A.extra_round ? 1 : 2
  const history = []
  const scope = reviewInputs()
  let recheckOnly = [...new Set(RESOLVED)].filter(n => T[n] && CONTENT.includes(n))   // answers applied at segment start
  let newGaps = []

  let minorRes = { applied: [], skipped: [] }
  if (minors.length) {
    minorRes = await clerk([
      'Apply only those Minors below whose fix is at most 2 lines and needs no design judgement, each with Edit in the named file. Skip every other one. Return applied and skipped ids.',
      `MINORS (JSON): ${json(minors.map(m => ({ id: m.id, file: m.file, sections: m.sections, what: m.what, fix: m.fix })))}`,
      `Files live in ${OUT}.`,
    ].join('\n'), { label: 'fix:minors', phaseName: 'Fix', schema: MINORFIX })
  }

  let round = 0
  while ((open.length || recheckOnly.length) && round < cap && !blockers.length) {
    round++
    const byOwner = groupBy(open, f => numOf(f.file))
    const owners = [...byOwner.keys()].sort((a, b) => a - b)
    const structural = FULL ? [] : owners.filter(n => byOwner.get(n).some(f => f.class === 'structural'))
    const patched = await parallel(owners.map(n => () => (structural.includes(n)
      ? writeUnit([n], { update: [], items: byOwner.get(n), phaseName: 'Fix' }).then(w => ({ ...w, patched: true }))
      : patchFile(n, reviewItemsBody(byOwner.get(n)), 'Fix'))))
    if (patched.some(p => !p)) throw new Error(`a fix-loop PATCH failed twice (round ${round})`)
    newGaps = patched.flatMap(gapItems)
    const files = [...new Set([...owners, ...recheckOnly])].sort((a, b) => a - b)
    const recheck = { files, items: open }
    const outs = await parallel([
      () => run(reviewerPrompt(recheck), { label: `recheck:gdd-reviewer:r${round}`, phase: 'Fix', schema: REVIEW, tier: 'deep', role: 'reviewer' }),
      () => run(lensPrompt({ key: 'regression', ask: 'Check that every listed fix landed, and that nothing a patch or an applied answer touched now contradicts a file that cites it or that it cites (counts, names, values, §-references, inventories).' },
        `just changed: ${files.map(n => T[n].file).join(', ')}${open.length ? ` — items:\n${open.map(itemLine).join('\n')}` : ' (user answers applied)'}`), { label: `recheck:regression:r${round}`, phase: 'Fix', schema: FINDINGS }),
    ])
    const raw = outs.flatMap(o => (o ? o.findings || [] : []))
    const merged = (await mergeFindings(raw, 'Fix')).map((f, k) => ({ ...f, id: `R${base + round}-${k + 1}` }))
    const confirmed = (await parallel(merged.map(f => () => judge(f, scope, 'Fix')))).filter(Boolean).filter(x => x.real)
    blockers = confirmed.filter(x => x.severity === 'blocker' || x.needs_user || !routable(x))
    const fixedIds = open.map(f => f.id)
    open = confirmed.filter(x => x.severity === 'major' && !blockers.includes(x))
    recheckOnly = []
    history.push({ round: base + round, patched_files: owners.map(n => T[n].file), rechecked: files.map(n => T[n].file), fixed: fixedIds, still_open: open.map(f => f.id), new_blockers: blockers.map(f => f.id) })
    if (patched.length) await bookkeep(STAGE, patched, { phaseName: 'Fix' })
    log(`fix round ${base + round}: patched ${owners.length}, rechecked ${files.length} file(s); ${open.length} major(s) open, ${blockers.length} blocker(s)`)
    if (newGaps.length) break
  }

  await clerk([
    `1. In ${j(WORK, 'review-report.md')}, add or refresh a final "## Fix loop" section: a table id | severity | file | status | round, covering every Major (status patched or open), every Minor (fixed or listed) and every Blocker below (open). Keep the rest of the report as is.`,
    `2. In ${j(WORK, 'run-meta.md')} § Fix loop set: iterations (add ${round} to the current number), patched_chapters (add the files below), recheck (one line per round: fixed / still open / new blockers).`,
    `HISTORY (JSON): ${json(history)}`,
    `MINORS (JSON): ${json({ fixed: minorRes.applied, listed: minorRes.skipped })}`,
    `STILL OPEN (JSON): ${json(open.map(f => ({ id: f.id, file: f.file, what: f.what })))}`,
    `BLOCKERS (JSON): ${json(blockers.map(f => ({ id: f.id, file: f.file, what: f.what })))}`,
    'Return words: [] and missing: [].',
  ].join('\n'), { label: 'fix:book', phaseName: 'Fix' })

  if (newGaps.length || blockers.length) {
    return cp(blockers.length ? 'blockers' : 'gaps', STAGE, [...blockers.map(toItem), ...newGaps], { note: 'raised inside the fix loop; it continues after the answers' })
  }
  if (open.length) return cp('residual', nextOf(STAGE), open.map(toItem), { note: `Majors still open after ${round} round(s): call again from ${STAGE} with extra_round=true for one more round, or from ${nextOf(STAGE)} to accept them as known issues.` })
  return null
}

// ---------------------------------------------------------------------------------------------
// Stage: assembly — full W10 (scribe) / lite INDEX (spec-tier assembly), then the completeness critic

function scribePrompt(nums, inputs, extra) {
  return [
    `ROLE: you are gdd-scribe producing ${nums.map(n => CH[n].file).join(' then ')} for the GDD of "${GAME}".`,
    `LANGUAGE: body in ${A.lang}; headings keep the English numbered prefix.`,
    RULES_LINE,
    `CONTRACT: ${nums.map(contractOf).join(' and ')}.`,
    'INPUTS (read all of these, read nothing else):',
    ...inputs.map(p => `  - ${p}`),
    ...nums.map(n => `  - template: ${j(KIT, 'templates/chapters/' + CH[n].tmpl)}`),
    `OUTPUT: write exactly ${nums.map(fileOf).join(' then ')}.`,
    extra || '',
    RETURN_LINE,
  ].filter(Boolean).join('\n')
}

const ext = () => `bash "${j(KIT, 'scripts/extract-sections.sh')}"`

async function ch13Extracts(nums) {
  const cmds = nums.map(n => `${ext()} "${fileOf(n)}" "${j(INPUTS, `ch13/ch${n}.md`)}" "@Open Decisions" "@New Terms" ${(CH13_EXTRA[n] || []).join(' ')}`.trim())
  const r = await clerk(`Run these commands in order; return every stdout line containing MISSING, prefixed with the source file name (ABSENT lines are normal — ignore them). Return words: [].\n${cmdBlock(cmds)}`, { label: 'extract:ch13', phaseName: 'Assemble' })
  const fallback = [...new Set((r.missing || []).map(l => numOf(l.split(':')[0])).filter(n => n !== null))]
  if (fallback.length) log(`ch13 extracts fell back to whole chapters: ${fallback.join(', ')}`)
  return nums.map(n => (fallback.includes(n) ? `${fileOf(n)} (whole — extract failed)` : j(INPUTS, `ch13/ch${n}.md`)))
}

async function abstracts() {
  const cmds = []
  for (let n = 1; n <= 13; n++) cmds.push(`${ext()} "${fileOf(n)}" "${j(INPUTS, `ch00/ch${n}.intro.md`)}" intro`)
  cmds.push(`cat ${Array.from({ length: 13 }, (_, i) => `"${j(INPUTS, `ch00/ch${i + 1}.intro.md`)}"`).join(' ')} > "${j(INPUTS, 'ch00/abstracts.md')}"`)
  await clerk(`Run these commands in order. Return words: [] and missing: [].\n${cmdBlock(cmds)}`, { label: 'extract:abstracts', phaseName: 'Assemble' })
  return j(INPUTS, 'ch00/abstracts.md')
}

async function critic() {
  const expected = ALL_FILES.map(fileOf)
  return run([
    `ROLE: completeness critic for the finished GDD "${GAME}" in ${OUT}. Change nothing. Ask "what is missing?":`,
    `- every expected file exists (${expected.map(p => p.split('/').pop()).join(', ')}) and carries every numbered heading its template defines (templates under ${j(KIT, FULL ? 'templates/chapters' : 'templates/lite')});`,
    `- every ⟂ GAP placeholder left in a file is listed in ${j(WORK, 'gap-log.md')}; every UNDECIDED field of ${j(WORK, 'brief.md')} appears in an Open Decisions box${FULL ? ' and in 13_Appendices.md §D' : ''};`,
    `- 0_Index.md's status and open-item counts match ${j(WORK, 'run-meta.md')}, ${j(WORK, 'review-report.md')}${FULL ? ' and 13_Appendices.md §D; 2_Version History.md matches run-meta.md (dates, fix loop)' : ''};`,
    '- every Blocker in review-report.md is answered in gap-log.md or still listed as open.',
    `Count: open_decisions (${FULL ? 'rows in 13_Appendices.md §D' : 'bullets in the five Open Decisions boxes of files 1–5, excluding "None."'}); proposals (occurrences of "(proposal)" across the deliverable files, via grep -o | wc -l); minors_left (Minors not marked fixed in review-report.md). Run wc -w on every expected file for files.`,
    'Return findings (file = the file that must change, severity, evidence, fix; ids C-1, C-2, …) and the counts. Empty findings when complete.',
  ].join('\n'), { label: 'critic', phase: 'Assemble', schema: CRITIC })
}

function done(fin, extra) {
  return {
    status: 'done',
    summary: {
      out: OUT,
      files: fin.files,
      open_decisions: fin.open_decisions,
      proposals: fin.proposals,
      minors_left: fin.minors_left,
      issues: (fin.findings || []).map(f => `${f.id} ${f.file} ${f.sections}: ${f.what}`),
      ...(extra || {}),
    },
  }
}

async function assembleFull() {
  const reports = j(WORK, 'reports')
  const common = [j(WORK, 'brief.md'), j(WORK, 'run-meta.md'), j(WORK, 'gap-log.md'), j(WORK, 'review-report.md')]
  const extracts = await ch13Extracts(CONTENT)
  const [r12, r13] = await parallel([
    () => run(scribePrompt([1, 2], common), { label: 'write:1+2', phase: 'Assemble', schema: REPORT, tier: tierFor('scribe'), role: 'scribe' }),
    () => run(scribePrompt([13], [...extracts, ...common, `${reports}/* (each REPORT's CROSS_REFS_CITED line builds §F)`]), { label: 'write:13', phase: 'Assemble', schema: REPORT, tier: tierFor('scribe'), role: 'scribe' }),
  ])
  if (!r12 || !r13) throw new Error('a W10a scribe dispatch failed twice')
  const abs = await abstracts()
  const r0 = await run(scribePrompt([0], [abs, fileOf(13), j(WORK, 'run-meta.md'), j(WORK, 'review-report.md')]), { label: 'write:0', phase: 'Assemble', schema: REPORT, tier: tierFor('scribe'), role: 'scribe' })
  const tier = tierFor('scribe')
  await bookkeep('W10', [{ chs: [1, 2], role: 'scribe', tier, rep: r12 }, { chs: [13], role: 'scribe', tier, rep: r13 }, { chs: [0], role: 'scribe', tier, rep: r0 }], { phaseName: 'Assemble' })
  let fin = await critic()
  const scribeFixes = groupBy((fin.findings || []).filter(f => [0, 1, 2, 13].includes(numOf(f.file))), f => numOf(f.file))
  if (scribeFixes.size) {
    const patched = await parallel([...scribeFixes].map(([n, fs]) => () => patchFile(n, reviewItemsBody(fs), 'Assemble')))
    await bookkeep('W10', patched.filter(Boolean), { phaseName: 'Assemble' })
    fin = { ...fin, findings: (fin.findings || []).filter(f => ![0, 1, 2, 13].includes(numOf(f.file))) }
  }
  return done(fin)
}

function liteIndexPrompt(fixes) {
  return [
    `Assemble ${fileOf(0)} for the GDD "${GAME}" (lite profile — ${A.profile}). This is mechanical assembly, not design.`,
    `Follow ${j(KIT, 'references/contracts-lite/lite-0.md')} and the template ${j(KIT, 'templates/lite/0-index.md')} exactly.`,
    `Read: ${CONTENT.map(fileOf).join(', ')} (whole), ${j(WORK, 'brief.md')}, ${j(WORK, 'gap-log.md')}, ${j(WORK, 'review-report.md')}, ${j(WORK, 'run-meta.md')} (Words column), ${j(WORK, 'reports')}/*.`,
    'Every value is pulled verbatim from a file or report on disk — never estimate a count. Write the file in the body language of the other files; headings keep the English numbered prefix. No ## REPORT block.',
    fixes ? `Also fix:\n${fixes.map(itemLine).join('\n')}` : '',
    `Then append one row to the \`## Waves\` table of ${j(WORK, 'run-meta.md')}: | INDEX | 0_Index.md | assembly | ${modelLabel('spec')} | complete | <wc -w> | — | |`,
  ].filter(Boolean).join('\n')
}

async function assembleLite() {
  await run(liteIndexPrompt(), { label: 'assemble:0_Index', phase: 'Assemble', tier: 'spec' })
  let fin = await critic()
  const idxFixes = (fin.findings || []).filter(f => numOf(f.file) === 0)
  if (idxFixes.length) {
    await run(liteIndexPrompt(idxFixes), { label: 'assemble:0_Index:fix', phase: 'Assemble', tier: 'spec' })
    fin = { ...fin, findings: (fin.findings || []).filter(f => numOf(f.file) !== 0) }
  }
  return done(fin)
}

// ---------------------------------------------------------------------------------------------
// Mode chapter / file — re-run one chapter (full --chapter N) or one lite file (--file N)

function staleOf(n) {
  if (!FULL) return (n === 1 ? [2, 3, 4, 5] : n === 2 ? [3, 4, 5] : []).map(c => LF[c].file)
  const out = new Set()
  for (const [c, s] of Object.entries(SLICES)) if (s.whole.includes(n) || s.parts.some(([src]) => src === n)) out.add(Number(c))
  if (n === 3) for (let c = 4; c <= 12; c++) out.add(c)
  out.delete(n)
  return [...out].sort((a, b) => a - b).map(c => T[c].file)
}

async function rerunStage() {
  const n = Number(A.target)
  if (!CONTENT.includes(n)) return { status: 'error', stage: STAGE, message: `target ${n} is not a re-runnable ${FULL ? 'chapter (3–12; for 0/1/2/13 run from W10)' : 'lite file (1–5)'}` }
  await prepareSlices([n])
  const w = await writeUnit([n], { update: [] })
  const v = w.rep.status === 'blocked' ? null : await verifyFile(n, 'RR.')
  await bookkeep('RERUN', [w, v && v.patch].filter(Boolean), { verifies: v ? [v] : [], commands: FULL && n === 3 ? [anchorCmd()] : [] })
  const items = [...gapItems(w), ...(v ? v.items : [])]
  if (items.length || w.rep.status === 'blocked') {
    return cp('gaps', 'RERUN-POST', items, w.rep.status === 'blocked' ? { blocked: [fileOf(n)], note: 'a blocked file always gets action "fresh"' } : undefined)
  }
  return null
}

async function rerunPost() {
  const n = Number(A.target)
  const date = A.date || '(date not supplied)'
  if (FULL) {
    const r2 = await patchFile(2, `Append one version row (patch bump of D-15's tag, date ${date}, "re-run of chapter ${n}") and one change-log bullet. Change nothing else.`, 'Assemble')
    const extracts = await ch13Extracts(CONTENT)
    const common = [j(WORK, 'brief.md'), j(WORK, 'run-meta.md'), j(WORK, 'gap-log.md'), j(WORK, 'review-report.md')]
    const r13 = await run(scribePrompt([13], [...extracts, ...common, `${j(WORK, 'reports')}/*`], 'UPDATE: the file exists — rewrite whole with Write.'), { label: 'write:13', phase: 'Assemble', schema: REPORT, tier: tierFor('scribe'), role: 'scribe' })
    const abs = await abstracts()
    const r0 = await run(scribePrompt([0], [abs, fileOf(13), j(WORK, 'run-meta.md'), j(WORK, 'review-report.md')], 'UPDATE: the file exists — rewrite whole with Write.'), { label: 'write:0', phase: 'Assemble', schema: REPORT, tier: tierFor('scribe'), role: 'scribe' })
    const tier = tierFor('scribe')
    await bookkeep('RERUN', [r2, { chs: [13], role: 'scribe', tier, rep: r13 }, { chs: [0], role: 'scribe', tier, rep: r0 }], { phaseName: 'Assemble' })
  } else {
    await clerk(`With one Edit, append a row to the version table in ${fileOf(1)} §1.1: version bump of the last row, date ${date}, "re-run of file ${n}". Change nothing else. Return words: [] and missing: [].`, { label: 'rerun:version-row', phaseName: 'Assemble' })
  }
  // Regression check of the re-run file against everything it cites and everything citing it.
  const outs = await parallel([
    ...(FULL ? [] : [() => run(reviewerPrompt({ files: [n], items: [] }), { label: 'recheck:gdd-reviewer', phase: 'Fix', schema: REVIEW, tier: 'deep', role: 'reviewer' })]),
    () => run(lensPrompt({ key: 'regression', ask: `${T[n].file} was just re-run. Find every contradiction between it and the files it cites or that cite it (counts, names, values, §-references, inventories, glossary).` }), { label: 'recheck:regression', phase: 'Fix', schema: FINDINGS }),
  ])
  const merged = await mergeFindings(outs.flatMap(o => (o ? o.findings || [] : [])), 'Fix')
  const confirmed = (await parallel(merged.map(f => () => judge(f, reviewInputs(), 'Fix')))).filter(Boolean).filter(x => x.real)
  let issues = confirmed
  if (!FULL) {
    const majors = confirmed.filter(x => x.severity === 'major' && !x.needs_user && numOf(x.file) === n)
    if (majors.length) await bookkeep('RERUN', [await patchFile(n, reviewItemsBody(majors), 'Fix')], { phaseName: 'Fix' })
    issues = confirmed.filter(x => !majors.includes(x))
    await run(liteIndexPrompt(), { label: 'assemble:0_Index', phase: 'Assemble', tier: 'spec' })
  }
  const fin = await critic()
  return done({ ...fin, findings: [...(fin.findings || []), ...issues] }, { stale: staleOf(n) })
}

// ---------------------------------------------------------------------------------------------
// Main

async function runStage(s) {
  STAGE = s
  if (s === 'ANCHOR') return anchorCheckpoint(nextOf(ANCHOR_STAGE), [])   // re-show for approval, no rewrite
  if (FULL && s === 'W1') return nameStage()
  if (UNITS[s]) return waveStage(s)
  if ((FULL && s === 'W8') || (!FULL && s === 'W4')) return reviewStage()
  if ((FULL && s === 'W9') || (!FULL && s === 'FIX')) return fixStage()
  if (FULL && s === 'W10') return assembleFull()
  if (!FULL && s === 'INDEX') return assembleLite()
  return { status: 'error', stage: s, message: `unknown stage "${s}" for profile ${A.profile}` }
}

try {
  const pending = await applyResolutions()
  if (pending) return pending
  if (MODE !== 'run') {
    STAGE = A.from
    if (A.from === 'RERUN') {
      const r = await rerunStage()
      if (r) return r
      STAGE = 'RERUN-POST'
    } else if (A.from !== 'RERUN-POST') {
      return { status: 'error', stage: A.from, message: 'mode chapter/file starts from RERUN or RERUN-POST' }
    }
    return await rerunPost()
  }
  if (A.from === 'ANCHOR') return await runStage('ANCHOR')
  if (!ORDER.includes(A.from)) return { status: 'error', stage: A.from, message: `unknown stage "${A.from}"; stages: ANCHOR, ${ORDER.join(', ')}` }
  for (let s = A.from; s; s = nextOf(s)) {
    const out = await runStage(s)
    if (out) return out
  }
  return { status: 'error', stage: STAGE, message: 'ran past the last stage without finishing' }
} catch (e) {
  return { status: 'error', stage: STAGE, message: String((e && e.message) || e) }
}
