# GDD Forge

## 1. GDD Forge là gì

GDD Forge là một plugin Claude Code biến một pitch thành một Game Design Document (GDD) ngắn, chia theo
hệ thống, với ít câu hỏi nhất có thể. Mục tiêu: một GDD mà người làm game thực sự đọc hết.

Ba nguyên tắc:

- **Không bao giờ quyết ngầm.** Kit được đề xuất mọi thứ, nhưng mọi quyết định (của người dùng hay do kit
  đề xuất) đều nằm trong `decisions.md` kèm nguồn `user` / `proposal`, để người dùng sửa bất cứ lúc nào.
- **Chỉ hỏi điều vừa đắt nếu sai, vừa không suy ra được từ pitch.** Tối đa một vòng 0–4 câu trước khi
  viết.
- **GDD là tài liệu thiết kế.** Không có kiến trúc kỹ thuật, lịch, budget, copyright, index hay
  appendices.

## 2. Cài đặt

Chọn một cách:

- Thử nhanh, không cài: `claude --plugin-dir <đường dẫn tới gdd-forge>`
- Cài ở user scope: `claude plugin marketplace add <đường dẫn tới gdd-forge>` rồi
  `claude plugin install gdd-forge@birdybird-local`
- Không dùng plugin: copy `skills/*` → `~/.claude/skills/`, `agents/*` → `~/.claude/agents/`, và
  `shared/` → `~/.claude/shared/`. Skill tìm `shared/` ở `<thư mục skill>/../../shared`, nên `shared/`
  phải nằm ngang hàng `skills/`. Khi cài kiểu này, lệnh không có prefix: `/concept`, `/system`,
  `/review`, `/gdd-review`, `/name`.

Cần `python3` (3.8+, chỉ dùng thư viện chuẩn) để chạy `gdd_check.py`. `/gdd-review` cần thêm `git` (dò GDD đổi) và
`pdftotext` nếu GDD có PDF.

## 3. Cách dùng

```
/gdd-forge:concept <pitch>                      # bắt đầu GDD: decision sheet, 0–4 câu hỏi, concept.md + decisions.md
/gdd-forge:concept <path/to/pitch.md>           # pitch nằm trong file
/gdd-forge:concept --update [<GDD>] [<thay đổi>]   # sửa concept / quyết định
/gdd-forge:system --core                         # viết mọi system tier core
/gdd-forge:system <tên system>                   # viết một system (thêm system mới nếu chưa có trong concept)
/gdd-forge:system --update <tên> [<thay đổi>]    # sửa một system doc
/gdd-forge:review [<file>]                       # gdd_check.py + reviewer; không arg = cả GDD
/gdd-forge:name <pitch | GDD>                    # sinh và chọn tên game
/gdd-forge:gdd-review <GDD | thư mục | stem>      # Tech Lead review GDD bất kỳ → report câu hỏi cho Game Design
/gdd-forge:gdd-review --verify                   # đóng các câu đã được GDD mới trả lời
```

Chạy các skill trong cuộc hội thoại chính: chỉ skill nói chuyện với bạn, agent không bao giờ hỏi.

## 4. Luồng chạy

```text
pitch ─► /concept: decision sheet ─► 0–4 câu hỏi ─► gdd-concept viết concept.md + decisions.md
                                                     ─► gdd_check.py ─► ◆ bạn duyệt concept + đề xuất
      ─► /system --core ─► gdd-system viết từng system doc ─► gdd_check.py (từng file)
      ─► /review ─► gdd_check.py + gdd-reviewer ─► sửa bằng /system --update nếu cần
      ─► /system <system kế tiếp> … khi cần
```

`◆` là checkpoint thật sự duy nhất. Các bước khác không dừng giữa chừng: agent tự đề xuất, mỗi doc kết
thúc bằng tối đa 3 câu hỏi mở, bạn trả lời khi đọc doc.

**Câu hỏi trước khi viết** (chỉ khi pitch chưa trả lời; danh sách ở `shared/contracts/concept.md`):
D-04 Platforms, D-06 Business model, D-20 Multiplayer, D-09 Scope. Mọi quyết định còn lại là đề xuất.

**Duyệt concept:** skill tóm tắt pillar, core loop, danh sách system và mọi dòng `proposal`. Bạn chọn
Approve, hoặc gõ thay đổi. Khi duyệt, các dòng Core chuyển từ `proposal` sang `user`. Nếu Core còn dòng
`proposal`, `/system` sẽ nhắc rằng concept chưa được duyệt.

**Đổi quyết định bất cứ lúc nào:** sửa `decisions.md` (tay hoặc `/concept --update`), rồi `/review` liệt
kê các doc bị ảnh hưởng (dựa trên `git diff` của `decisions.md` và cột Affects).

**Tier theo giai đoạn dự án:**

| Tier | Output | Khi nào |
| --- | --- | --- |
| Concept | `concept.md` + `decisions.md` | Pitch, thử ý tưởng; hyper-casual thường dừng gần đây |
| Core | + system docs tier core | Bắt đầu prototype |
| System | thêm hoặc cập nhật từng system | Khi cần thiết kế tiếp một hệ thống |

## 5. Output

```text
deliverables/<slug>/GDD/
├── concept.md          # chương neo, ≤ ~1.000 từ
├── decisions.md        # ID · quyết định · giá trị · nguồn (user / proposal) · doc bị ảnh hưởng
└── systems/
    ├── <system>.md     # mỗi system ≤ ~1.200 từ
    └── …
```

- **`concept.md`:** Pitch, Pillars (tên · ý nghĩa · cấm gì), Core Loop, Target, Experience, References
  (tùy chọn), Out of Scope, Systems (tên · type · một dòng · pillar · tier · doc), Glossary, Open
  Questions.
- **`decisions.md`:** `## Core` (D-01…D-44, cùng ID với v1) và `## Design` (D-100+, phát sinh khi viết
  system doc).
- **System doc:** Purpose, Rules, Player-Observable Behaviors, Open Questions (bắt buộc); Tunables,
  States and Edge Cases, Content, UI Touchpoints, Interactions (tùy chọn, bỏ hẳn khi không áp dụng).
- **Type của system** quyết định guidance agent đọc: mechanics, progression, economy, level,
  enemy-behavior, ui-flow, narrative, presentation.

GDD là tài liệu sống: không có thư mục phiên bản hay `_work/`, lịch sử nằm trong git. Một GDD
hyper-casual thường khoảng 2.000–2.500 từ.

## 6. Kiểm chứng

**`shared/scripts/gdd_check.py <GDD> [--file <doc>] [--changed]`** kiểm những gì máy kiểm được:

- Heading bắt buộc, thứ tự heading, title.
- Số từ theo budget (vượt: cảnh báo; vượt quá 20%: lỗi).
- Pillars 3–5 và mỗi pillar có Forbids; bảng Systems đúng cột, type, tier, doc tồn tại; system doc nào
  cũng có trong bảng Systems.
- `decisions.md`: ID hợp lệ và không trùng, Source là `user`/`proposal`, Affects trỏ tới file có thật;
  Target trong concept khớp D-04, D-05, D-06, D-09.
- Một tunable chỉ được định nghĩa ở một system doc.
- Tham chiếu `→ <file> §<Heading>` trỏ tới heading có thật.
- Glossary viết đúng chính tả; open questions ≤ 3; 3–10 hành vi quan sát được.
- Không còn comment template, không gắn `(D-xx)` vào câu, không lọt từ ngữ nội bộ của kit.
- `--changed`: các quyết định đổi kể từ commit cuối và doc bị ảnh hưởng.

Exit code 1 khi có lỗi. Skill tự chạy script sau mỗi lần viết và cho agent sửa một lần nếu có lỗi.

**`gdd-reviewer`** có context sạch, chỉ nhận concept, decisions, doc cần review và output của script.
Nó đi theo checklist ở `shared/checklists/` (mâu thuẫn với concept hay quyết định, pillar Forbids,
monetization, rule kiểm được, độ khép kín, edge case, tỷ lệ với scope) và trả về tối đa 5 điểm mỗi doc,
có severity `high` / `medium` / `low`. Reviewer không sửa doc.

### `/gdd-review` — review GDD bất kỳ, ra câu hỏi cho Game Design

`/review` và `/gdd-review` trả lời hai câu hỏi khác nhau:

| | `/review` | `/gdd-review` |
| --- | --- | --- |
| Câu hỏi | GDD do kit viết có nhất quán với concept và decisions không? | Dev có implement được đúng một cách không? |
| Input | GDD do gdd-forge sinh (`concept.md` + `decisions.md`) | GDD bất kỳ trong repo GDD của studio (key `gdd.path`) |
| Người dùng | Người viết GDD | Technical Leader trước khi giao việc |
| Output | Finding + đề xuất `/system --update` | `reports/gdd-review/gdd-report.md` + `.html`: câu hỏi đóng cho Game Design, mục Ngoài phạm vi GDD |

Pipeline: thu nguồn → FINDER (haiku) theo ba lens (`conflict` · `scope` · `missing`) → `check_form.py` →
VERIFIER (sonnet) cố bác bỏ từng candidate → SYNTHESIZER → CRITIC (≤ `rounds` vòng) → render. Chỉ có một
report; chạy lại thì cập nhật tại chỗ theo `git diff` từ `gddCommit` của report, giữ id câu hỏi.
`--verify` chỉ kiểm câu đang mở đã được GDD mới trả lời chưa. Thu hẹp phạm vi bằng `sections=` và `lens=`.

Cấu hình đọc từ `CLAUDE.md` / `CLAUDE.local.md` của repo đang mở: `gdd.path` (bắt buộc, thiếu thì skill
hỏi), `gdd.glossary`, `gdd.filePrefix` (tuỳ chọn). Luật review ở `skills/gdd-review/review-standard.md`
(GR-NN), category ở `profile.json`; toolkit render/validate dùng chung ở `shared/report-toolkit/`.
Nhập từ repo Project-X3-GDD; flow chi tiết ở `skills/gdd-review/SKILL.md`.

## 7. Quy ước bước tiếp theo

Mọi skill kết thúc bằng một dòng đề xuất bước tiếp theo, dựa trên **kết quả thực tế** của lần chạy:

```text
**Tiếp theo:** `/gdd-forge:review systems/combat.md` — vừa viết combat.md, chưa kiểm.
```

- Một đề xuất chính, ghi đúng lệnh kèm argument; tối đa một nhánh phụ.
- Chỉ đề xuất, không tự chạy bước cần người duyệt.
- Không còn bước hợp lý thì nói "GDD xong ở tier hiện tại".

| Skill xong với kết quả | Tiếp theo |
| --- | --- |
| `/concept`, chờ pitch hoặc câu trả lời | Người trả lời |
| `/concept`, đã duyệt | `/gdd-forge:system --core` |
| `/concept`, đã duyệt và muốn đặt tên | `/gdd-forge:name <GDD>` |
| `/concept --update` đổi giá trị Core khi đã có system doc | `/gdd-forge:review` |
| `/system` xong một doc | `/gdd-forge:review systems/<slug>.md` |
| `/system --core` xong nhiều doc | `/gdd-forge:review` |
| `/review`, script báo lỗi | `/gdd-forge:system --update <tên> "<lỗi>"` → `/gdd-forge:review <file>` |
| `/review`, finding `high` | `/gdd-forge:system --update <tên> "<finding>"` → `/gdd-forge:review <file>` |
| `/review`, quyết định đổi ảnh hưởng system doc | `/gdd-forge:system --update <tên> "<D-xx đổi thành …>"` |
| `/review` sạch, còn câu hỏi mở | Người trả lời → `/gdd-forge:system --update <tên> "<trả lời>"` |
| `/review` sạch, còn system chưa có doc | `/gdd-forge:system <system kế tiếp, core trước>` |
| `/review` sạch, đủ system | GDD xong ở tier hiện tại |
| `/name` chọn xong tên | Quay lại bước đang dở |

## 8. Cấu trúc kit

```text
gdd-forge/
├── .claude-plugin/          # plugin.json, marketplace.json
├── agents/
│   ├── gdd-concept.md       # viết concept.md + decisions.md
│   ├── gdd-system.md        # viết một system doc, đọc guidance theo type
│   ├── gdd-reviewer.md      # read-only, tối đa 5 finding mỗi doc
│   ├── gdd-review.md        # worker của /gdd-review: FINDER · VERIFIER · SYNTHESIZER · CRITIC · QUOTE-FIX
│   └── gdd-namer.md         # 8 ứng viên tên, read-only
├── skills/
│   ├── concept/SKILL.md
│   ├── system/SKILL.md
│   ├── review/SKILL.md
│   ├── gdd-review/          # SKILL.md, review-standard.md, profile.json, scripts/
│   └── name/SKILL.md
└── shared/
    ├── writing-rules.md     # quyết định vs đề xuất vs thiết kế tự do; quy tắc viết; update mode; khối RESULT
    ├── contracts/           # concept.md (gồm danh sách câu hỏi bắt buộc), system.md (gồm danh sách type)
    ├── templates/           # concept.md, decisions.md, system.md
    ├── guidance/            # concept.md + 8 file theo type system
    ├── checklists/          # concept.md, system.md — checklist của reviewer
    ├── scripts/gdd_check.py
    ├── report-toolkit/      # chuẩn report, DATA.md, template HTML, prepare/resolve/assemble/validate/render
    └── data/                # kiến thức nền; _index.md chọn file theo loại doc
```

Không agent nào ghim model: mọi dispatch chạy bằng model của phiên — trừ `gdd-review`, nơi skill truyền
`model` theo vai (FINDER, QUOTE-FIX: haiku; VERIFIER, CRITIC, SYNTHESIZER: sonnet).

## 9. Thay đổi so với v1

v1 sinh GDD 13 chương (lite: 6 file) qua một workflow nhiều wave, với gate khoảng 8 lượt hỏi và luật
"không bao giờ tự quyết". Kết quả: GDD rất dài, nhiều phần thừa, hỏi lại rất nhiều và tốn token cho
kiểm chứng đối kháng nhiều tầng.

| v1 | v2 |
| --- | --- |
| 14 file theo 13 chương (lite: 6 file) | `concept.md` + `decisions.md` + `systems/*.md` |
| Gate khoảng 8 lượt, không được tự đề xuất | 0–4 câu + duyệt decision sheet một lần |
| GAP dừng hỏi cuối mỗi wave | Câu hỏi mở cuối mỗi doc, trả lời khi đọc |
| `--profile casual` theo thể loại | Tier Concept / Core / System theo giai đoạn |
| Workflow `forge-run.js` nhiều đoạn | Skill gọi agent trực tiếp |
| Finder + 3 voter + 4 lens + fix loop 2 vòng | `gdd_check.py` + một reviewer |
| 12 agent | 4 agent |
| Thư mục phiên bản + `_work/` | GDD sống trong git |

v1 vẫn nằm trong lịch sử git: commit `b9e5c6e` là trạng thái cuối cùng còn đủ file v1.

## 10. Đo lường hiệu quả

v2 chỉ đáng giữ nếu thắng v1 trên pitch thật. Chạy 3–5 pitch (ít nhất một hyper-casual và một mid-core)
qua cả hai bản, so theo:

| Chỉ số | Cách đo |
| --- | --- |
| Số lượt hỏi người | Đếm lượt hỏi từ đầu tới khi GDD xong ở tier Core |
| Tổng số từ | `wc -w` toàn bộ GDD |
| Token mỗi lần chạy | Usage của session Claude Code |
| Số lần sửa lại ý | Số lần người phải nói "không phải ý mình" |

Nếu v2 ít câu hỏi hơn nhưng số lần sửa lại ý tăng, danh sách câu hỏi bắt buộc còn thiếu: thêm câu vào
danh sách đó, không quay lại gate dài.

## 11. Nguồn

Các file trong `shared/data/` (trừ `casual/`) được scavenge (đọc lại, rút gọn, viết lại) từ **BMad
Expansion Pack — Game GDD Generator** (MIT, tác giả WangHaiSheng). Phần còn lại là thiết kế của
gdd-forge.

---

## 12. English

**What it is** — GDD Forge turns a game pitch into a short, system-based Game Design Document with as
few questions as possible. Principles: never decide silently (every decision, the user's or the kit's
proposal, is a row in `decisions.md` with its source); ask only what is costly to get wrong and cannot
be inferred from the pitch (one round of 0–4 questions); a GDD is a design document, not a technical
spec, schedule or index.

**Usage** — `/gdd-forge:concept <pitch>` writes `concept.md` and `decisions.md` after at most four
questions (platforms, business model, multiplayer, scope — only those the pitch leaves open), then asks
you to approve the concept and the kit's proposals. `/gdd-forge:system --core` or
`/gdd-forge:system <name>` writes one document per system (≤ ~1,200 words each) using guidance for its
type (mechanics, progression, economy, level, enemy-behavior, ui-flow, narrative, presentation).
`/gdd-forge:review [<file>]` runs `shared/scripts/gdd_check.py` (headings, word budgets, decision table,
single ownership of tunables, cross-references, glossary spelling, decisions changed since the last
commit) and one clean-context reviewer that returns at most five findings per document.
`/gdd-forge:name` proposes and records a title. `/gdd-forge:gdd-review <GDD>` is a Technical-Leader
review of any GDD (not only kit-made ones): find → independent verify → synthesize → critic, producing one
updatable report of closed questions for Game Design (`--verify` closes answered ones). Every skill ends
with one suggested next command.

**Install** — `claude --plugin-dir <path>` to try, or add the folder as a marketplace and install
`gdd-forge@birdybird-local`. Without the plugin system, copy `skills/`, `agents/` and `shared/` side by
side under `~/.claude/`. Requires `python3`.
