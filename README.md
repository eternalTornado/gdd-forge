# GDD Forge

## 1. GDD Forge là gì

GDD Forge là một plugin Claude Code biến một ý tưởng game (pitch) thành một Game Design Document (GDD) đầy đủ 13 chương. Nguyên tắc cốt lõi: một **gate** (cổng hỏi đáp) hỏi người dùng đúng những quyết định còn thiếu — kit **không bao giờ tự bịa quyết định** (nền tảng, đối tượng, mô hình kinh doanh, engine...) thay người dùng; nếu người dùng bỏ ngỏ, giá trị đó được ghi `UNDECIDED` và xuất hiện trong Open Decisions. Output cuối cùng là 13 chương GDD dạng Markdown (0_Index đến 13_Appendices) cộng với tên game được chọn.

## 2. Cài đặt

Ba cách, chọn một:

- Thử nhanh, không cài đặt: `claude --plugin-dir ~/Downloads/gdd-forge`
- Cài ở user scope: `claude plugin marketplace add ~/Downloads/gdd-forge` rồi `claude plugin install gdd-forge@birdybird-local` (`claude plugin install` chỉ nhận tên plugin từ một marketplace đã đăng ký, không nhận đường dẫn local trực tiếp)
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
/gdd-forge:forge --profile lite <pitch>          # đồng nghĩa với --profile casual
/gdd-forge:forge --profile casual --file 2   # chạy lại một file của luồng rút gọn
/gdd-forge:name <pitch>                      # chỉ sinh và chọn tên game
/gdd-forge:review <gdd folder>               # QA một GDD đã có, không sinh mới
```

Ví dụ pitch: *"Một game platformer 2D phong cách pixel art: linh hồn một chú cáo lạc trong rừng tre Việt cổ, phải thu thập ánh sáng để đánh thức các vị thần rừng đang ngủ. Nhắm tới người chơi casual trên mobile (iOS/Android), phiên bản free-to-play với IAP thẩm mỹ, không quảng cáo ép buộc, đơn (single-player), có cốt truyện nhẹ."*

## 4. Luồng chạy

```
W0 Gate ─► W1 Name ─► W2 ch3 ─► W3 ch4 → ch5 ─► W4 ch6 ‖ ch7 ─► W5 ch8 ‖ ch10 ─► W6 ch9 → ch11 ─► W7 ch12 ─► W8 Review ─► W9 Fix loop (≤1) ─► W10 (ch1→ch2) ‖ ch13 → 0_Index ─► Done
```
(`‖` = chạy song song trong một wave; `→` = tuần tự trong wave, file bên phải chỉ chạy khi file bên trái đã xong và GAP của nó đã xử lý)

Các wave chạy tuần tự vì mỗi chương chỉ đọc file đã có trên đĩa; không gộp wave để chạy nhanh hơn.

- **W0 Gate** — orchestrator hỏi các trường D-xx còn thiếu theo `brief-schema.md`, đóng băng `brief.md`.
- **W1 Name** — sinh/chốt tên game (`gdd-namer` nếu D-01 = GENERATE), tính `slug`, tạo thư mục output.
- **W2** — `gdd-concept-architect` viết chương 3 (Game Overview), chương neo cho mọi chương sau.
- **W3** — chương 4 (Mechanics) trước, rồi chương 5 (Narrative) trong cùng wave: chương 5 đọc §4.1–4.3 của chương 4 nên phải chờ chương 4 xong và GAP của nó được xử lý.
- **W4** — chương 6 (Levels) và chương 7 (Interface) viết song song, đọc chương 4 và 5.
- **W5** — chương 8 (AI) và chương 10 (Art) viết song song; chờ W4 vì chương 8 đọc encounters ở chương 6, chương 10 đọc asset needs ở chương 6 và UI ở chương 7.
- **W6** — chương 9 rồi chương 11 (cùng agent `gdd-tech-designer`, tuần tự), đọc chương 7, 8, 10.
- **W7** — chương 12 (Management); chờ W6 vì chương 12 đọc risks ở chương 9 và tool matrix ở chương 11.
- **W8 Review** — `gdd-reviewer` (opus) đọc toàn bộ 3–12 và mọi checklist, dựng `fact-ledger.md` (bảng dữ kiện) rồi chấm 12 consistency rule từ chính ledger đó, sinh `review-report.md`.
- **W9 Fix loop** — tối đa một vòng: Blockers hỏi lại người dùng, Majors patch chương liên quan (hoặc dispatch lại từ đầu nếu là lỗi structural), Minors chỉ liệt kê trong `review-report.md`, RECHECK chạy lại 12 rule trên các chương đã patch.
- **W10** — `gdd-scribe` chạy 2 dispatch song song: ch1 rồi ch2 (một dispatch, hai file) ‖ ch13 (dispatch riêng); rồi 0_Index sau cùng, do orchestrator dispatch lại `gdd-scribe`, đọc abstract (`intro`) của cả 13 chương cộng `13_Appendices.md`.

**Cắt input trước mỗi dispatch**: danh sách *Consumes* của mỗi chương chỉ tiêu thụ vài mục (§4.5, §4.8…), nhưng một agent nhận đường dẫn cả chương thì đọc cả chương. Trước mỗi dispatch W3–W7, orchestrator cắt sẵn đúng các mục đó bằng `scripts/extract-sections.sh` và chỉ truyền phần đã cắt. Riêng §3.2 (pillars) và §3.10 (Glossary) được cắt **một lần** sau W2 thành `_anchor.md` và truyền cho mọi dispatch phía sau — vì Rule 4 buộc mọi chương dùng lại Glossary, cắt thuần theo *Consumes* sẽ làm hỏng chính rule đó. Data file cũng chỉ truyền lát cần dùng: brief mobile-only nhận `data/platforms/mobile.md`, không nhận spec console/PC/VR.

**3 loại thông tin & vòng lặp GAP** (`dispatch-rules.md`): mỗi agent phân loại thứ nó viết thành DECISION (chỉ lấy từ `brief.md`), PROPOSAL (lựa chọn khả nghịch, cục bộ mà brief không nói tới — agent tự đề xuất, gắn tag `(proposal)` và liệt kê trong Open Decisions kèm 1–2 phương án thay thế, **không hỏi người dùng giữa chừng**) và ELABORATION (mọi thứ còn lại, agent thiết kế tự do). Chỉ khi thiếu một quyết định thật sự (thêm/bớt feature, mode, màn hình, giá tiền, hai nguồn mâu thuẫn nhau…) agent mới viết một placeholder `⟂ GAP` và báo cáo về, kèm lớp (`class`) `value` (chỉ điền một giá trị) hoặc `structural` (đổi bản chất một feature/luồng). Subagent không được gọi `AskUserQuestion`; GAP được gom và hỏi người dùng **vào cuối mỗi wave**, ghi câu trả lời vào `brief.md`. Xử lý theo lớp: `value` → orchestrator tự thay placeholder bằng `Edit` (chỉ PATCH lại subagent nếu hơn ~3 dòng phụ thuộc giá trị đó); `structural` → dispatch lại subagent **từ đầu** (không phải PATCH) để thay đổi thấm vào toàn file. Mã GAP có dạng `G-<chương>-<n>` để hai agent chạy song song không trùng mã. Section bị Depth rule loại bỏ vẫn giữ heading số kèm một dòng N/A — script cắt section neo theo số heading, heading biến mất sẽ dừng pipeline.

### Luồng rút gọn — `--profile casual`

Dành cho game casual / hyper-casual mobile. Luồng đầy đủ tốn khoảng 13–14 lượt dispatch trên một lượt chạy sạch (đếm theo bảng wave của `pipeline.md`; 14 nếu namer phải sinh tên; GAP re-dispatch và patch của W9 tính thêm); với casual thì phần lớn vẫn là lãng phí vì không có cốt truyện thật, không có kiến trúc AI, không multiplayer. Luồng rút gọn còn **4 wave, 6 dispatch, 6 file** trên một lượt chạy sạch — GAP re-dispatch và patch của review tính thêm:

```
W0 Gate (preset casual) ─► W1 1_Concept ─► W2 2_Core Gameplay
   ─► W3 3_UX Art and Audio ‖ 4_Business and LiveOps ‖ 5_Tech Note
   ─► W4 Review (bắt buộc) ─► 0_Index (orchestrator tự lắp) ─► Done
```

Mỗi file gộp nhiều chương của luồng đầy đủ: `1_Concept` gộp ch3 + phần setting thay cho ch5 + header bản quyền/version thay cho ch1, ch2; `2_Core Gameplay` gộp ch4 + ch6 + hành vi obstacle thay cho ch8; `3_UX Art and Audio` gộp ch7 + ch10 + phần game feel; `4_Business and LiveOps` là ch12 viết lại theo thực tế casual (vị trí rewarded video, nhịp interstitial, danh mục IAP, **định nghĩa** KPI, roadmap có bước CPI-test chỉ khi `D-48` = có chạy paid UA); `5_Tech Note` gộp ch9 + rủi ro kỹ thuật (§5.7) + danh sách SDK — không có tool matrix riêng như ch11 bản đầy đủ.

Mỗi contract lite có dòng **Owns** (file nào là chủ của sự kiện/con số nào) và **Budget** theo `wc -w` — tổng 5 file ước chừng ≤ 9.000 từ; không cắt input như luồng đầy đủ, mỗi dispatch đọc trọn các file lite phía trên nó. Review ở W4 giờ **bắt buộc**, không còn hỏi chạy hay bỏ qua.

Đặt tên trong luồng rút gọn: không có wave namer riêng — `1_Concept` §1.2 đề xuất 3 tên, orchestrator hỏi người dùng chọn ngay sau W1, ghi `game_name`/`slug` vào brief và đổi tên thư mục trước W2.

Preset casual **không phá nguyên tắc không tự bịa**: orchestrator *đề xuất* một bảng giá trị thường gặp, người dùng xác nhận hoặc sửa trong một vòng, và chỉ giá trị đã xác nhận mới được ghi vào `brief.md` (nguồn ghi là `casual preset — confirmed by user`). Giá trị chưa xác nhận không bao giờ được dùng, và D-02 (pitch) vẫn là yêu cầu bắt buộc mà preset không thể thay thế. Các trường không nằm trong preset (D-01, D-10, D-13, D-14, D-38, D-40, D-43, D-44 và các trigger Section C tương ứng) vẫn được hỏi riêng và chấp nhận `UNDECIDED`/`none`.

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

`AskUserQuestion` chỉ hiển thị tối đa 4 lựa chọn; với trường có nhiều option hơn, orchestrator liệt kê đủ trong câu hỏi, đưa 4 option khả dĩ nhất và người dùng gõ giá trị khác qua Other.

`D-09` (scope) có 2 phần trong cùng một trường: độ dài phiên chơi (`Micro`…`Large`) và tham vọng nội dung (`replay-driven`, `hours`, `~10 h`…), ví dụ `Small (5–15 min sessions) · content: replay-driven`. Section C có thêm `D-48` (`paid_ua`, chỉ hỏi ở profile casual/hyper-casual, trước `D-45`) — có chạy UA trả phí hay không, quyết định `4_Business and LiveOps.md` §4.4–§4.6 (luồng rút gọn) có nội dung CPI-test hay không.

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
├── 0_Index.md                         (gdd-scribe · sonnet)
├── 1_Copyright Information.md         (gdd-scribe · sonnet)
├── 2_Version History.md               (gdd-scribe · sonnet)
├── 3_Game Overview.md                 (gdd-concept-architect · opus)
├── 4_Gameplay and Mechanics.md        (gdd-mechanics-designer · opus)
├── 5_Story, Setting and Character.md  (gdd-narrative-designer · opus)
├── 6_Levels.md                        (gdd-level-designer · opus)
├── 7_Interface.md                     (gdd-ux-designer · sonnet)
├── 8_Artificial Intelligence.md       (gdd-ai-designer · opus)
├── 9_Technical.md                     (gdd-tech-designer · opus)
├── 10_Game Art.md                     (gdd-art-director · sonnet)
├── 11_Secondary Software.md           (gdd-tech-designer · opus)
├── 12_Management.md                   (gdd-producer · sonnet)
├── 13_Appendices.md                   (gdd-scribe · sonnet)
└── _work/
    ├── brief.md            # brief đã đóng băng
    ├── gap-log.md          # mọi câu hỏi GAP + câu trả lời + lớp (value/structural)
    ├── review-report.md    # Blockers/Majors/Minors + ma trận checklist + 12 consistency rule
    ├── fact-ledger.md      # bảng dữ kiện (key|kind|value|file §) reviewer dựng trước khi chấm rule 9–12
    ├── run-meta.md         # ngày, phiên bản kit, D-15, bảng § Waves (agent/model/status/số từ `wc -w`/self-check)
    ├── inputs/             # chỉ luồng đầy đủ: _anchor.md + lát cắt §mục cho từng dispatch (ch<N>/), cộng ch13/ và ch00/ cho W10
    └── reports/            # mỗi REPORT của agent lưu nguyên văn (<chapter>.report.md) — số từ nằm ở run-meta.md, không nằm trong REPORT
```

Luồng rút gọn (`--profile casual`) ghi ra 6 file thay vì 14, cùng thư mục `_work/` nhưng **không có `inputs/`** (không cắt input):

```
deliverables/<slug>/GDD/<version>/
├── 0_Index.md                  (orchestrator tự lắp, không tốn dispatch — §0.3 chỉ còn file|trạng thái|mục còn mở)
├── 1_Concept.md                (gdd-concept-architect · opus)
├── 2_Core Gameplay.md          (gdd-mechanics-designer · opus)
├── 3_UX Art and Audio.md       (gdd-ux-designer · sonnet)
├── 4_Business and LiveOps.md   (gdd-producer · sonnet)
├── 5_Tech Note.md              (gdd-tech-designer · opus)
└── _work/                      (như trên trừ inputs/, thêm `profile:` trong run-meta.md)
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
| gdd-tech-designer | opus | 9, 11 | kiến trúc kỹ thuật, ngân sách hiệu năng, schema lưu trữ xuyên suốt 2 chương — suy luận hệ thống sâu, không chỉ đặc tả |
| gdd-art-director | sonnet | 10 | đặc tả art direction theo pillar đã có |
| gdd-producer | sonnet | 12 | lập kế hoạch/QA, mang tính spec |
| gdd-reviewer | opus | (review) | đối chiếu chéo 10 chương, 17 checklist, 10 contract theo 12 consistency rule, dựng fact-ledger trước khi chấm — bước suy luận nặng nhất pipeline |
| gdd-scribe | sonnet | 0, 1, 2, 13 | merge glossary, dedup asset index và dựng cross-reference matrix từ 10 chương cho chương 13 — quá nặng cho haiku |

`model:` trong frontmatter mỗi agent luôn là nguồn đúng; bảng trên chỉ để tham khảo. Riêng ch5/ch8 orchestrator override xuống `model: "sonnet"` khi trigger tắt: `gdd-narrative-designer` khi `D-21 ∈ {None, Light framing}`, `gdd-ai-designer` khi `D-22 = None` — chương lúc đó gần như toàn dòng `N/A —`.

5 agent dùng chung cho cả 2 luồng (`concept-architect`, `mechanics-designer`, `ux-designer`, `producer`, `tech-designer`) là file agent tinh gọn, chỉ giữ phần đúng cho cả full lẫn lite; kinh nghiệm viết riêng theo chương nằm ở `references/guidance/<role>.full.md` / `.lite.md`, mỗi dispatch đọc đúng file guidance của profile đang chạy.

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
    │   │   ├── run-meta-template.md    # khung run-meta.md
    │   │   ├── gap-log-template.md     # khung gap-log.md
    │   │   ├── chapter-contracts.md    # index mỏng: bảng chương → agent → contract
    │   │   ├── dispatch-rules.md       # quy tắc dùng chung mọi dispatch: DECISION/PROPOSAL/ELABORATION, PATCH mode, khối REPORT
    │   │   ├── consistency-rules.md    # 12 rule cross-chapter cho reviewer
    │   │   ├── consistency-rules-lite.md  # 12 rule cho luồng rút gọn (rule 1–8 đánh số khác, 9–12 giống luồng đầy đủ)
    │   │   ├── pipeline.md             # nguồn quy trình duy nhất; SKILL.md chỉ là bản đồ
    │   │   ├── profile-casual.md       # luồng rút gọn casual/hyper-casual
    │   │   ├── contracts/              # ch00.md … ch13.md — mỗi dispatch đọc 1 file
    │   │   ├── contracts-lite/         # lite-0.md … lite-5.md — mỗi contract có dòng Owns + Budget
    │   │   └── guidance/               # <role>.full.md / <role>.lite.md — kinh nghiệm viết riêng theo chương cho 5 agent dual-profile
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

**Install** — three ways: `claude --plugin-dir ~/Downloads/gdd-forge` (quick try) · `claude plugin marketplace add ~/Downloads/gdd-forge` then `claude plugin install gdd-forge@birdybird-local` (user-scope install — `claude plugin install` only accepts a plugin name from a registered marketplace, not a local path) · copy `skills/*` to `~/.claude/skills/` and `agents/*` to `~/.claude/agents/` (no plugin — commands then have no prefix: `/forge`, `/name`, `/review`).

**Usage** — `/gdd-forge:forge <pitch>` · `/gdd-forge:forge <path/to/brief.md>` · `/gdd-forge:forge --chapter 6` · `/gdd-forge:forge --resume <out dir>` · `/gdd-forge:name <pitch>` · `/gdd-forge:review <gdd folder>`.

**Output** — `deliverables/<slug>/GDD/<version>/` holds `0_Index.md` through `13_Appendices.md` (each owned by one agent/model — see §7 above) plus `_work/` with `brief.md`, `gap-log.md`, `review-report.md`, `fact-ledger.md` (the reviewer's fact table), and `run-meta.md` (dates, kit version, and the § Waves table — word counts live only there, from `wc -w`, never in an agent's own report).

**Three kinds of information & GAPs** — every dispatch classifies what it writes as a DECISION (from `brief.md` only), a PROPOSAL (a reversible, local choice the brief doesn't make — the agent writes its own recommendation tagged `(proposal)` with 1–2 alternatives under Open Decisions, never asking the user mid-run), or an ELABORATION (everything else, designed freely). Only a genuine missing decision (a new feature/mode/screen, a real-money price, two contradicting sources…) becomes a `⟂ GAP`, tagged with a class — `value` (fills in one value) or `structural` (changes what a feature or flow *is*). Subagents can never call `AskUserQuestion`; GAPs are collected and asked to the user **at the end of every wave**, then resolved by class: `value` GAPs are patched into the file directly by the orchestrator via `Edit` (a PATCH dispatch only if more than ~3 lines depend on the value), `structural` GAPs get the owning agent re-dispatched fresh, not PATCHed.

**Casual profile** — `--profile casual` runs a 4-wave, 6-dispatch flow (on a clean run — GAP re-dispatches and review patches are extra) producing 6 files instead of 14, for casual and hyper-casual mobile titles that have no real narrative, no AI architecture and no multiplayer. Each file absorbs several full chapters; the business file covers rewarded-video placement, interstitial cadence, an IAP catalogue with real-money prices, and KPI *definitions*, with the CPI-test roadmap step and paid-UA metrics gated by the new `D-48` (`paid_ua`) field. The lite profile no longer slices its inputs — every dispatch reads the upstream lite files whole — and every lite contract now carries an `Owns` line plus a `wc -w` word budget (≈9,000 words total across the five files). The lite consistency review (W4) is now **mandatory**, never skipped. The gate proposes a preset of typical casual values which the user confirms or edits in one round — an unconfirmed preset value is never written to the brief, and the pitch (D-02) is still required. See [`profile-casual.md`](skills/forge/references/profile-casual.md).

**Input slicing (full profile only)** — a chapter contract consumes named sections, not whole files, so before each W3–W7 dispatch the orchestrator slices exactly those sections with `scripts/extract-sections.sh` and passes only the slices. Pillars (§3.2) and the Glossary (§3.10) are sliced once into `_anchor.md` and passed to every downstream dispatch, because the shared dispatch rules make every chapter reuse the Glossary and slicing strictly by contract would break that. Data files are likewise passed as topic slices selected by the brief.

**A few operational details** — every dispatch prompt, full or lite, names [`dispatch-rules.md`](skills/forge/references/dispatch-rules.md) — the single home of the writing rules, PATCH mode, and the closing `## REPORT` block, so agent files themselves no longer restate any of that. `AskUserQuestion` allows at most 4 options, so for a field with more the orchestrator lists them all in the question text and offers the 4 most likely, with anything else typed via Other; a section a Depth rule removes still keeps its numbered heading followed by a one-line reason, since downstream dispatches slice chapters by heading number and a missing heading halts the pipeline. `gdd-reviewer` runs on **opus**: it builds `fact-ledger.md` before judging anything, then checks all 12 consistency rules against it (cross-checking 10 chapters against 17 checklists and 10 contracts is the pipeline's heaviest reasoning step). `gdd-tech-designer` also runs on **opus** now (architecture and storage decisions span two full chapters or the whole lite tech note); `gdd-scribe` stays on **sonnet**, writing ch 1 then ch 2 in one run and reading pre-extracted `## Open Decisions`/`## New Terms`/abstract slices (via `extract-sections.sh`'s `@<Heading>` and `intro` spec forms) for ch 13 and `0_Index.md` instead of whole chapters. The orchestrator can also override ch 5 and ch 8 to `model: "sonnet"` when their chapter is mostly `N/A —` lines (`D-21 ∈ {None, Light framing}` / `D-22 = None`). The five dual-profile agents (`gdd-concept-architect`, `gdd-mechanics-designer`, `gdd-ux-designer`, `gdd-producer`, `gdd-tech-designer`) are kept deliberately slim and read a `references/guidance/<role>.full.md` or `.lite.md` file for chapter-specific craft advice instead of carrying it inline.
