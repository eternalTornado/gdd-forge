# GDD Forge

## 1. GDD Forge là gì

GDD Forge là một plugin Claude Code biến một ý tưởng game (pitch) thành một Game Design Document (GDD) đầy đủ 13 chương. Nguyên tắc cốt lõi: một **gate** (cổng hỏi đáp) hỏi người dùng đúng những quyết định còn thiếu — kit **không bao giờ tự bịa quyết định** (nền tảng, đối tượng, mô hình kinh doanh, engine...) thay người dùng; nếu người dùng bỏ ngỏ, giá trị đó được ghi `UNDECIDED` và xuất hiện trong Open Decisions. Output cuối cùng là 13 chương GDD dạng Markdown (0_Index đến 13_Appendices) cộng với tên game được chọn.

## 2. Cài đặt

Ba cách, chọn một:

- Thử nhanh, không cài đặt: `claude --plugin-dir ~/Downloads/gdd-forge`
- Cài ở user scope: `claude plugin install ~/Downloads/gdd-forge`
- Không dùng plugin: copy `skills/*` → `~/.claude/skills/` và `agents/*` → `~/.claude/agents/`. Lưu ý: khi cài theo cách này, lệnh **không có prefix** `gdd-forge:` — dùng `/forge`, `/name`, `/review` thay vì `/gdd-forge:forge` v.v.

Khi cài dạng plugin (2 cách đầu), subagent xuất hiện với tên `gdd-forge:gdd-<role>`; khi copy thẳng, tên là `gdd-<role>`. Skill tự nhận diện dạng nào đang có — không cần cấu hình.

Kiểm tra nhanh sau khi cài: `claude plugin validate ~/Downloads/gdd-forge` (manifest) rồi `claude --plugin-dir ~/Downloads/gdd-forge -p "list skills and agents named gdd"`.

## 3. Cách dùng

```
/gdd-forge:forge <pitch>                     # bắt đầu từ một ý tưởng bằng lời
/gdd-forge:forge <path/to/brief.md>          # bắt đầu từ một brief đã có sẵn
/gdd-forge:forge --chapter 6                 # chạy lại một chương duy nhất
/gdd-forge:forge --resume <out dir>          # tiếp tục một lượt chạy dở dang
/gdd-forge:forge --profile casual <pitch>    # luồng rút gọn cho casual / hyper-casual
/gdd-forge:forge --profile casual --file 2   # chạy lại một file của luồng rút gọn
/gdd-forge:name <pitch>                      # chỉ sinh và chọn tên game
/gdd-forge:review <gdd folder>               # QA một GDD đã có, không sinh mới
```

Ví dụ pitch: *"Một game platformer 2D phong cách pixel art: linh hồn một chú cáo lạc trong rừng tre Việt cổ, phải thu thập ánh sáng để đánh thức các vị thần rừng đang ngủ. Nhắm tới người chơi casual trên mobile (iOS/Android), phiên bản free-to-play với IAP thẩm mỹ, không quảng cáo ép buộc, đơn (single-player), có cốt truyện nhẹ."*

## 4. Luồng chạy

```
W0 Gate ─► W1 Name ─► W2 ch3 ─► W3 ch4 ‖ ch5 ─► W4 ch6 ‖ ch7 ─► W5 ch8 ‖ ch10 ─► W6 ch9→ch11 ─► W7 ch12 ─► W8 Review ─► W9 Fix loop (≤1) ─► W10 ch1 ‖ ch2 ‖ ch13 ‖ 0_Index ─► Done
```
(`‖` = chạy song song trong một wave; `→` = cùng agent, chạy tuần tự)

Các wave chạy tuần tự vì mỗi chương chỉ đọc file đã có trên đĩa; không gộp wave để chạy nhanh hơn.

- **W0 Gate** — orchestrator hỏi các trường D-xx còn thiếu theo `brief-schema.md`, đóng băng `brief.md`.
- **W1 Name** — sinh/chốt tên game (`gdd-namer` nếu D-01 = GENERATE), tính `slug`, tạo thư mục output.
- **W2** — `gdd-concept-architect` viết chương 3 (Game Overview), chương neo cho mọi chương sau.
- **W3** — chương 4 (Mechanics) và chương 5 (Narrative) viết song song, cùng đọc chương 3.
- **W4** — chương 6 (Levels) và chương 7 (Interface) viết song song, đọc chương 4 và 5.
- **W5** — chương 8 (AI) và chương 10 (Art) viết song song; chờ W4 vì chương 8 đọc encounters ở chương 6, chương 10 đọc asset needs ở chương 6 và UI ở chương 7.
- **W6** — chương 9 rồi chương 11 (cùng agent `gdd-tech-designer`, tuần tự), đọc chương 7, 8, 10.
- **W7** — chương 12 (Management); chờ W6 vì chương 12 đọc risks ở chương 9 và tool matrix ở chương 11.
- **W8 Review** — `gdd-reviewer` đọc toàn bộ 3–12 và mọi checklist, sinh `review-report.md`.
- **W9 Fix loop** — tối đa một vòng: Blockers hỏi lại người dùng, Majors patch chương liên quan, Minors chỉ liệt kê.
- **W10** — `gdd-scribe` lắp chương 1, 2, 13 và 0_Index từ mọi thứ đã hoàn tất.

**Cắt input trước mỗi dispatch**: danh sách *Consumes* của mỗi chương chỉ tiêu thụ vài mục (§4.5, §4.8…), nhưng một agent nhận đường dẫn cả chương thì đọc cả chương. Trước mỗi dispatch W3–W7, orchestrator cắt sẵn đúng các mục đó bằng `scripts/extract-sections.sh` và chỉ truyền phần đã cắt. Riêng §3.2 (pillars) và §3.10 (Glossary) được cắt **một lần** sau W2 thành `_anchor.md` và truyền cho mọi dispatch phía sau — vì Rule 4 buộc mọi chương dùng lại Glossary, cắt thuần theo *Consumes* sẽ làm hỏng chính rule đó. Data file cũng chỉ truyền lát cần dùng: brief mobile-only nhận `data/platforms/mobile.md`, không nhận spec console/PC/VR.

**Vòng lặp GAP**: subagent không được phép hỏi người dùng trực tiếp (không có quyền gọi `AskUserQuestion`). Khi một chương cần một quyết định còn thiếu, subagent viết một placeholder GAP và báo cáo về; **skill (orchestrator) hỏi thay** người dùng, ghi câu trả lời vào `brief.md`, rồi dispatch lại subagent ở chế độ PATCH để thay đúng chỗ đó — không viết lại cả chương.

### Luồng rút gọn — `--profile casual`

Dành cho game casual / hyper-casual mobile. Luồng đầy đủ tốn khoảng 20 lượt dispatch; với casual thì phần lớn là lãng phí vì không có cốt truyện thật, không có kiến trúc AI, không multiplayer. Luồng rút gọn còn **4 wave, 6 dispatch, 6 file**:

```
W0 Gate (preset casual) ─► W1 1_Concept ─► W2 2_Core Gameplay
   ─► W3 3_UX Art and Audio ‖ 4_Business and LiveOps ‖ 5_Tech Note
   ─► W4 Review rút gọn ─► 0_Index (orchestrator tự lắp) ─► Done
```

Mỗi file gộp nhiều chương của luồng đầy đủ: `1_Concept` gộp ch3 + phần setting thay cho ch5 + header bản quyền/version thay cho ch1, ch2; `2_Core Gameplay` gộp ch4 + ch6 + hành vi obstacle thay cho ch8; `3_UX Art and Audio` gộp ch7 + ch10 + phần game feel; `4_Business and LiveOps` là ch12 viết lại theo thực tế casual (vị trí rewarded video, nhịp interstitial, IAP remove-ads, **định nghĩa** KPI, concept playable ad cho test CPI); `5_Tech Note` gộp ch9 + tool matrix của ch11 + danh sách SDK.

Preset casual **không phá nguyên tắc không tự bịa**: orchestrator *đề xuất* một bảng giá trị thường gặp, người dùng xác nhận hoặc sửa trong một vòng, và chỉ giá trị đã xác nhận mới được ghi vào `brief.md` (nguồn ghi là `casual preset — confirmed by user`). Giá trị chưa xác nhận không bao giờ được dùng, và D-02 (pitch) vẫn là yêu cầu bắt buộc mà preset không thể thay thế.

Quay lại luồng đầy đủ ngay khi game có cốt truyện thật, AI thật, multiplayer, hoặc nền tảng chính là console/PC. Chi tiết: [`profile-casual.md`](skills/forge/references/profile-casual.md).

## 5. Gate hỏi gì

Section A — Identity (luôn hỏi nếu thiếu):

| ID | Trường | ID | Trường |
|---|---|---|---|
| D-01 | working_title | D-09 | scope |
| D-02 | pitch (bắt buộc) | D-10 | team_budget |
| D-03 | genre | D-11 | engine |
| D-04 | platforms | D-12 | gdd_language |
| D-05 | audience | D-13 | reference_games |
| D-06 | business_model | D-14 | output_dir |
| D-07 | art_direction | D-15 | gdd_version |
| D-08 | tone_theme | | |

Section B — Structure triggers (⚡ luôn hỏi, quyết định phần nào của Section C sẽ bật):

| ID | Trường | ID | Trường |
|---|---|---|---|
| D-20 | multiplayer | D-23 | level_structure |
| D-21 | narrative_weight | D-24 | liveops |
| D-22 | ai_agents | | |

Section C (D-30…D-44) chỉ hỏi khi trigger tương ứng bật (ví dụ D-30 chỉ hỏi khi D-06 ∈ {F2P, Subscription, Hybrid}) — xem đầy đủ trong [`brief-schema.md`](skills/forge/references/brief-schema.md).

## 6. Output

```
deliverables/<slug>/GDD/<version>/
├── 0_Index.md                         (gdd-scribe · haiku)
├── 1_Copyright Information.md         (gdd-scribe · haiku)
├── 2_Version History.md               (gdd-scribe · haiku)
├── 3_Game Overview.md                 (gdd-concept-architect · opus)
├── 4_Gameplay and Mechanics.md        (gdd-mechanics-designer · opus)
├── 5_Story, Setting and Character.md  (gdd-narrative-designer · opus)
├── 6_Levels.md                        (gdd-level-designer · opus)
├── 7_Interface.md                     (gdd-ux-designer · sonnet)
├── 8_Artificial Intelligence.md       (gdd-ai-designer · opus)
├── 9_Technical.md                     (gdd-tech-designer · sonnet)
├── 10_Game Art.md                     (gdd-art-director · sonnet)
├── 11_Secondary Software.md           (gdd-tech-designer · sonnet)
├── 12_Management.md                   (gdd-producer · sonnet)
├── 13_Appendices.md                   (gdd-scribe · haiku)
└── _work/
    ├── brief.md            # brief đã đóng băng
    ├── gap-log.md          # mọi câu hỏi GAP + câu trả lời
    ├── review-report.md    # Blockers/Majors/Minors + ma trận checklist
    ├── run-meta.md         # ngày, phiên bản kit, hash brief
    └── reports/            # mỗi REPORT của agent lưu nguyên văn (<chapter>.report.md)
```

Luồng rút gọn (`--profile casual`) ghi ra 6 file thay vì 14, cùng thư mục `_work/`:

```
deliverables/<slug>/GDD/<version>/
├── 0_Index.md                  (orchestrator tự lắp, không tốn dispatch)
├── 1_Concept.md                (gdd-concept-architect · opus)
├── 2_Core Gameplay.md          (gdd-mechanics-designer · opus)
├── 3_UX Art and Audio.md       (gdd-ux-designer · sonnet)
├── 4_Business and LiveOps.md   (gdd-producer · sonnet)
├── 5_Tech Note.md              (gdd-tech-designer · sonnet)
└── _work/                      (như trên, thêm `profile:` trong run-meta.md)
```

## 7. Agents & model

| Agent | Model | Chương | Lý do chọn model |
|---|---|---|---|
| gdd-namer | opus | (đặt tên) | sáng tạo, cần nhiều phương án khác biệt |
| gdd-concept-architect | opus | 3 | thiết kế nền tảng — mọi chương khác neo vào đây |
| gdd-mechanics-designer | opus | 4 | thiết kế hệ thống, cần suy luận sâu |
| gdd-narrative-designer | opus | 5 | sáng tạo cốt truyện/nhân vật/thế giới |
| gdd-level-designer | opus | 6 | thiết kế không gian, cần suy luận sáng tạo |
| gdd-ai-designer | opus | 8 | thiết kế hành vi AI, cần lý luận kiến trúc |
| gdd-ux-designer | sonnet | 7 | đặc tả UI/UX theo khuôn mẫu đã định |
| gdd-tech-designer | sonnet | 9, 11 | đặc tả kỹ thuật, spec hoá hơn là sáng tạo |
| gdd-art-director | sonnet | 10 | đặc tả art direction theo pillar đã có |
| gdd-producer | sonnet | 12 | lập kế hoạch/QA, mang tính spec |
| gdd-reviewer | sonnet | (review) | đối chiếu checklist, không sáng tạo |
| gdd-scribe | haiku | 0, 1, 2, 13 | lắp ráp boilerplate từ nội dung đã có |

## 8. Cấu trúc kit

```
gdd-forge/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── gdd-*.md                    # 12 agent — xem bảng ở mục 7
└── skills/
    ├── forge/
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── brief-schema.md
    │   │   ├── brief-template.md
    │   │   ├── chapter-contracts.md    # index mỏng: bảng chương → agent → contract
    │   │   ├── consistency-rules.md    # 8 rule cross-chapter cho reviewer
    │   │   ├── pipeline.md             # luồng đầy đủ W0–W10
    │   │   ├── profile-casual.md       # luồng rút gọn casual/hyper-casual
    │   │   ├── contracts/              # ch00.md … ch13.md — mỗi dispatch đọc 1 file
    │   │   └── contracts-lite/         # lite-0.md … lite-5.md
    │   ├── scripts/
    │   │   └── extract-sections.sh     # cắt §mục từ chương đã viết
    │   ├── templates/
    │   │   ├── chapters/               # 00-index.md … 13-appendices.md
    │   │   └── lite/                   # 0-index.md … 5-tech-note.md
    │   ├── checklists/                 # 17 file cho luồng đầy đủ
    │   │   └── lite/                   # 5 file cho luồng rút gọn
    │   └── data/                       # kiến thức nền — nguồn ngoài duy nhất
    │       ├── game-design-patterns.md
    │       ├── platforms/              # mobile, pc, console, web, vr-ar…
    │       ├── cultural/               # east-asia, western, emerging…
    │       ├── monetization/           # primary-models, mechanics, ethics…
    │       ├── accessibility/          # standards, platform-guidelines…
    │       └── casual/                 # metrics-definitions.md (chỉ định nghĩa, không có số benchmark)
    ├── name/
    │   └── SKILL.md
    └── review/
        └── SKILL.md
```

Mỗi thư mục con trong `data/` có `_index.md` ghi **selector**: brief field nào quyết định lát nào được truyền cho dispatch. Ví dụ `platforms/mobile.md` chỉ được truyền khi D-04 có iOS hoặc Android.

## 9. Nguồn

Templates, checklists và data files được scavenge (đọc lại, rút gọn, viết lại theo hợp đồng chương mới) từ **BMad Expansion Pack — Game GDD Generator** (MIT, tác giả WangHaiSheng); phần orchestration (gate, pipeline wave, vòng lặp GAP, chống bịa đặt) là thiết kế mới hoàn toàn cho gdd-forge, không sao chép từ BMAD.

---

## 10. English

**What it is** — GDD Forge turns a game pitch into a 13-chapter Game Design Document. Its core principle: an input **gate** asks the user for missing decisions and never invents them (platform, audience, business model, engine, etc.); anything left open is recorded as `UNDECIDED` and surfaced in Open Decisions. Output: 13 Markdown chapters (0_Index … 13_Appendices) plus a chosen game name.

**Install** — three ways: `claude --plugin-dir ~/Downloads/gdd-forge` (quick try) · `claude plugin install ~/Downloads/gdd-forge` (user-scope install) · copy `skills/*` to `~/.claude/skills/` and `agents/*` to `~/.claude/agents/` (no plugin — commands then have no prefix: `/forge`, `/name`, `/review`).

**Usage** — `/gdd-forge:forge <pitch>` · `/gdd-forge:forge <path/to/brief.md>` · `/gdd-forge:forge --chapter 6` · `/gdd-forge:forge --resume <out dir>` · `/gdd-forge:name <pitch>` · `/gdd-forge:review <gdd folder>`.

**Output** — `deliverables/<slug>/GDD/<version>/` holds `0_Index.md` through `13_Appendices.md` (each owned by one agent/model — see §7 above) plus `_work/` with `brief.md`, `gap-log.md`, `review-report.md`, `run-meta.md`, and `reports/` (each agent's REPORT block, saved verbatim).

**Casual profile** — `--profile casual` runs a 4-wave, 6-dispatch flow producing 6 files instead of 14, for casual and hyper-casual mobile titles that have no real narrative, no AI architecture and no multiplayer. Each file absorbs several full chapters, and the business file is rewritten around what casual games actually live on: rewarded-video placement, interstitial cadence, remove-ads IAP, KPI *definitions*, and the playable-ad concept a CPI test needs. The gate proposes a preset of typical casual values which the user confirms or edits in one round — an unconfirmed preset value is never written to the brief, and the pitch (D-02) is still required. See [`profile-casual.md`](skills/forge/references/profile-casual.md).

**Input slicing** — a chapter contract consumes named sections, not whole files, so before each W3–W7 dispatch the orchestrator slices exactly those sections with `scripts/extract-sections.sh` and passes only the slices. Pillars (§3.2) and the Glossary (§3.10) are sliced once into `_anchor.md` and passed to every downstream dispatch, because envelope rule 4 makes every chapter reuse the Glossary and slicing strictly by contract would break that rule. Data files are likewise passed as topic slices selected by the brief.
