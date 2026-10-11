# GDD Forge

## 1. GDD Forge là gì

GDD Forge là một plugin Claude Code biến một ý tưởng game (pitch) thành một Game Design Document (GDD) đầy đủ 13 chương. Nguyên tắc cốt lõi: một **gate** (cổng hỏi đáp) hỏi người dùng đúng những quyết định còn thiếu — kit **không bao giờ tự bịa quyết định** (nền tảng, đối tượng, mô hình kinh doanh, engine...) thay người dùng; nếu người dùng bỏ ngỏ, giá trị đó được ghi `UNDECIDED` và xuất hiện trong Open Decisions. Output cuối cùng là 13 chương GDD dạng Markdown (0_Index đến 13_Appendices) cộng với tên game được chọn.

## 2. Cài đặt

Cần một bản Claude Code có **Workflow tool**: `/gdd-forge:forge` chạy toàn bộ phần sinh GDD trong một workflow. Plugin mang theo `workflows/forge-run.js`; khi cài dạng plugin, file này tự đăng ký thành workflow có tên `gdd-forge:forge-run`.

Ba cách, chọn một:

- Thử nhanh, không cài đặt: `claude --plugin-dir ~/Downloads/gdd-forge`
- Cài ở user scope: `claude plugin marketplace add ~/Downloads/gdd-forge` rồi `claude plugin install gdd-forge@birdybird-local` (`claude plugin install` chỉ nhận tên plugin từ một marketplace đã đăng ký, không nhận đường dẫn local trực tiếp)
- Không dùng plugin: copy `skills/*` → `~/.claude/skills/`, `agents/*` → `~/.claude/agents/` và `workflows/forge-run.js` → `~/.claude/workflows/`. Lưu ý: khi cài theo cách này, lệnh **không có prefix** `gdd-forge:` — dùng `/forge`, `/name`, `/review` thay vì `/gdd-forge:forge` v.v.

Khi cài dạng plugin (2 cách đầu), subagent xuất hiện với tên `gdd-forge:gdd-<role>` và skill gọi workflow theo tên `gdd-forge:forge-run`; khi copy thẳng, subagent tên là `gdd-<role>` và skill gọi workflow bằng `scriptPath` — đường dẫn tuyệt đối tới `${CLAUDE_SKILL_DIR}/../../workflows/forge-run.js`, nên giữ `workflows/` ngang hàng `skills/`. Skill tự nhận diện dạng nào đang có (không thấy workflow theo tên thì dùng `scriptPath`) và ghi lựa chọn vào dòng `workflow:` của `run-meta.md` — không cần cấu hình.

Kiểm tra nhanh sau khi cài: `claude plugin validate ~/Downloads/gdd-forge` (manifest) rồi `claude --plugin-dir ~/Downloads/gdd-forge -p "list skills, agents and workflows named gdd"`.

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

`/gdd-forge:forge` chạy gate (trừ `--chapter`, `--file`, `--resume`), rồi chạy một workflow duy nhất theo từng đoạn; giữa chừng nó dừng hỏi bạn ở mỗi checkpoint (§4) — cứ trả lời cho tới khi xong. Chạy skill trong cuộc hội thoại chính, vì mỗi checkpoint cần hỏi bạn. `/gdd-forge:name` và `/gdd-forge:review` không qua workflow: mỗi lệnh dispatch thẳng một agent (`gdd-namer` / `gdd-reviewer`).

## 4. Luồng chạy

Orchestrator (agent chính chạy skill) làm W0 Gate trực tiếp với bạn, rồi chạy **một workflow** — `gdd-forge:forge-run` (`workflows/forge-run.js`) — theo từng **đoạn** (segment): mỗi lần gọi, workflow chạy tiếp từ stage `from` cho tới checkpoint kế tiếp hoặc tới cuối. Workflow không hỏi được người dùng, nên mọi câu hỏi diễn ra giữa hai đoạn: orchestrator hỏi bạn, ghi câu trả lời xuống đĩa (`brief.md` § Gate additions, `gap-log.md`), rồi gọi lại với `from` = stage kế tiếp và câu trả lời trong `resolutions`. Trạng thái chỉ nằm trên đĩa (thư mục output và `_work/`), không nằm trong workflow — nên `--resume` chạy được cả ở phiên khác.

```
W0 Gate ─► workflow gdd-forge:forge-run, chạy theo đoạn:
   W1 Name ◆ ─► W2 ch3 ◆ ─► W3a ch4 ─► W3b ch5 ─► W4 ch6 ‖ ch7 ─► W5 ch8 ‖ ch10 ─► W6 ch9 → ch11 ─► W7 ch12
   ─► W8 Review ◆ ─► W9 Fix loop (tới khi sạch, ≤ 2 vòng) ◆ ─► W10 (ch1→ch2) ‖ ch13 → 0_Index → critic ─► Done
```
(`‖` = chạy song song trong một wave; `→` = tuần tự trong wave, file bên phải chỉ chạy khi file bên trái đã xong; `◆` = checkpoint. Ngoài các `◆`, mỗi wave W3a–W7 cũng dừng hỏi khi có GAP hoặc quyết định verify cần bạn.)

Các wave chạy tuần tự vì mỗi chương chỉ đọc file đã có trên đĩa; không gộp wave để chạy nhanh hơn.

| Checkpoint | Khi nào dừng | Bạn trả lời |
|---|---|---|
| Chọn tên | W1, chỉ khi cần sinh tên (luồng rút gọn: gộp vào checkpoint duyệt neo) | chọn một ứng viên của `gdd-namer` (luồng rút gọn: 3 tên ở §1.2) hoặc gõ tên khác qua Other |
| Duyệt chương neo | **luôn luôn**, sau ch3 (luồng rút gọn: sau `1_Concept`) — trước mọi chương phía sau | bảng pillar (tên · ý nghĩa · cấm gì) và feature (tên · ưu tiên · pillar) → Approve hoặc Request changes; cộng GAP của chương neo nếu có |
| GAP | cuối wave có GAP `G-…` hoặc item verify `V-…` cần bạn | trả lời từng item; câu đã trả lời trong `gap-log.md` không bị hỏi lại |
| Blocker | review (hoặc RECHECK trong fix loop) xác nhận có Blocker `R-…` | chọn phương án cho từng Blocker |
| Major tồn đọng | còn Major sau 2 vòng fix | chạy thêm một vòng, hoặc chấp nhận là known issue |

- **W0 Gate** — orchestrator hỏi các trường D-xx còn thiếu theo `brief-schema.md`, đóng băng `brief.md`. Nếu D-01 đã là tên thật, hỏi thêm một câu: giữ tên đó hay sinh tên khác. Rồi xác định cách gọi workflow (theo tên hay `scriptPath`).
- **W1 Name** — chỉ khi cần tên (D-01 ∈ {GENERATE, UNDECIDED} hoặc bạn chọn sinh tên khác): `gdd-namer` trả 8 ứng viên xếp hạng → checkpoint chọn tên; orchestrator ghi `game_name`/`slug` vào brief, đổi tên thư mục output tạm và cập nhật `slug:` trong `run-meta.md`.
- **W2** — `gdd-concept-architect` viết chương 3 (Game Overview), chương neo cho mọi chương sau; cắt `_anchor.md`, verify, rồi luôn dừng ở checkpoint duyệt neo. Request changes → ghi vào `brief.md` § Gate additions (W2 anchor review), chương 3 được viết lại từ đầu, verify lại và hỏi duyệt lại.
- **W3a / W3b** — chương 4 (Mechanics) trước, rồi chương 5 (Narrative): chương 5 đọc §4.1–4.3 của chương 4 nên phải chờ chương 4 xong và GAP của nó được xử lý.
- **W4** — chương 6 (Levels) và chương 7 (Interface) viết song song, đọc chương 4 và 5.
- **W5** — chương 8 (AI) và chương 10 (Art) viết song song; chờ W4 vì chương 8 đọc encounters ở chương 6, chương 10 đọc asset needs ở chương 6 và UI ở chương 7.
- **W6** — chương 9 rồi chương 11 (cùng agent `gdd-tech-designer`, một dispatch, tuần tự), đọc chương 7, 8, 10.
- **W7** — chương 12 (Management); chờ W6 vì chương 12 đọc risks ở chương 9 và tool matrix ở chương 11.
- **W8 Review** — `gdd-reviewer` (đọc toàn bộ chương 3–12 và mọi checklist, dựng `fact-ledger.md` rồi chấm 12 consistency rule từ chính ledger đó, sinh `review-report.md`) chạy song song với 4 lens finder: A mâu thuẫn/con số, B trung thành với brief (bịa quyết định, vi phạm loại trừ, vi phạm pillar), C độ khép kín (inventory, flow, cross-reference, glossary, asset), D vệ sinh (tỉ lệ so với scope, tuân thủ contract). Mọi finding được gộp và loại trùng, rồi được kiểm chứng: mỗi Blocker/Major qua 3 voter (evidence / rule / severity + ownership), chỉ giữ khi ≥ 2 phiếu xác nhận; Minor qua 1 voter evidence. `review-report.md` được viết lại chỉ với finding đã xác nhận, thêm `## Verification` (số đếm). Có Blocker → checkpoint.
- **W9 Fix loop** — tới khi sạch, tối đa 2 vòng. Mỗi vòng: Majors gom theo file chủ → một PATCH mỗi file, song song; Minors ≤ 2 dòng và không cần phán đoán được sửa thẳng, còn lại chỉ liệt kê; RECHECK = `gdd-reviewer` chạy lại 12 rule trên các file vừa patch ‖ một lens hồi quy → gộp → kiểm chứng như W8 → Major mới sang vòng sau. Sạch → đi tiếp; Blocker mới → checkpoint Blocker rồi vòng lặp tiếp tục; còn Major sau 2 vòng → checkpoint Major tồn đọng. Kết quả ghi vào `## Fix loop` của `review-report.md`.
- **W10** — `gdd-scribe` chạy 2 dispatch song song: ch1 rồi ch2 (một dispatch, hai file) ‖ ch13 (dispatch riêng, đọc input đã cắt sẵn); rồi 0_Index sau cùng, đọc abstract (`intro`) của cả 13 chương cộng `13_Appendices.md`. Cuối cùng một **completeness critic** hỏi "còn thiếu gì?" (file/heading, GAP chưa ghi log, `UNDECIDED` chưa vào Open Decisions, số đếm trong 0_Index lệch): lỗi ở ch 0/1/2/13 được `gdd-scribe` PATCH, lỗi khác được báo ở Done.

**Verify từng wave**: mỗi file mới (hoặc vừa viết lại từ đầu) được một finder đọc cùng contract, `dispatch-rules.md`, brief, `gap-log.md` và đúng những input writer đã nhận; mỗi Major được 3 voter với góc nhìn khác nhau (evidence / rule / severity + ownership + cần người dùng) cố bác bỏ — chỉ giữ khi ≥ 2 phiếu xác nhận. Major đã xác nhận mà không cần bạn quyết định → một PATCH cho agent chủ (Minor đi kèm); Major cần bạn quyết định hoặc phải sửa ở file upstream → item `V-…` ở checkpoint GAP. Kết quả ghi vào `_work/checks/<file>.check.md`.

**Chạy lại & resume**: `--chapter N` chạy workflow ở chế độ một chương — viết lại chương N từ đầu, verify, checkpoint GAP nếu có, rồi thêm dòng version ở ch2, dựng lại ch13 và 0_Index, kiểm tra hồi quy; Done liệt kê các chương đọc chương N có thể đã cũ (chỉ chạy lại khi bạn xác nhận). `--resume` tìm stage đầu tiên chưa xong theo STATUS trong `_work/reports/`, `run-meta.md` và `gap-log.md` (gồm cả việc bạn đã duyệt chương neo hay chưa — dòng `ANCHOR` trong gap-log; chưa duyệt thì hiện lại checkpoint neo mà không viết lại chương), hỏi nốt những câu checkpoint bị bỏ dở, rồi gọi lại workflow từ đó.

**Cắt input trước mỗi dispatch**: danh sách *Consumes* của mỗi chương chỉ tiêu thụ vài mục (§4.5, §4.8…), nhưng một agent nhận đường dẫn cả chương thì đọc cả chương. Trước mỗi dispatch W3–W7, workflow cắt sẵn đúng các mục đó bằng `scripts/extract-sections.sh` và chỉ truyền phần đã cắt (bản đồ cắt: `SLICES` trong `workflows/forge-run.js`). Riêng §3.2 (pillars) và §3.10 (Glossary) được cắt **một lần** sau W2 thành `_anchor.md` (cắt lại khi chương 3 đổi) và truyền cho mọi dispatch phía sau — vì Rule 4 buộc mọi chương dùng lại Glossary, cắt thuần theo *Consumes* sẽ làm hỏng chính rule đó. Data file cũng chỉ truyền lát cần dùng (orchestrator chọn theo brief): brief mobile-only nhận `data/platforms/mobile.md`, không nhận spec console/PC/VR.

**3 loại thông tin & vòng lặp GAP** (`dispatch-rules.md`): mỗi agent phân loại thứ nó viết thành DECISION (chỉ lấy từ `brief.md`), PROPOSAL (lựa chọn khả nghịch, cục bộ mà brief không nói tới — agent tự đề xuất, gắn tag `(proposal)` và liệt kê trong Open Decisions kèm 1–2 phương án thay thế, **không hỏi người dùng giữa chừng**) và ELABORATION (mọi thứ còn lại, agent thiết kế tự do). Chỉ khi thiếu một quyết định thật sự (thêm/bớt feature, mode, màn hình, giá tiền, hai nguồn mâu thuẫn nhau…) agent mới viết một placeholder `⟂ GAP` và báo cáo về, kèm lớp (`class`) `value` (chỉ điền một giá trị) hoặc `structural` (đổi bản chất một feature/luồng). Subagent không được gọi `AskUserQuestion`; GAP được gom và hỏi người dùng **tại checkpoint cuối mỗi wave**, ghi câu trả lời vào `brief.md`. Xử lý theo lớp: `value` → orchestrator tự thay placeholder bằng `Edit` (nếu hơn ~3 dòng phụ thuộc giá trị đó thì chọn `patch` — workflow PATCH agent chủ); `structural` → orchestrator chọn `fresh`, workflow dispatch lại agent chủ **từ đầu** (không phải PATCH) để thay đổi thấm vào toàn file, rồi verify lại. Nếu sự kiện vừa đổi đã được file phía sau trích dẫn, workflow PATCH các file trích dẫn đó sau file chủ. Mã GAP có dạng `G-<chương>-<n>` để hai agent chạy song song không trùng mã. Section bị Depth rule loại bỏ vẫn giữ heading số kèm một dòng N/A — script cắt section neo theo số heading, heading biến mất sẽ dừng pipeline.

### Luồng rút gọn — `--profile casual`

Dành cho game casual / hyper-casual mobile. Luồng đầy đủ viết 10 chương thiết kế cộng 4 chương tổng hợp; với casual thì phần lớn vẫn là lãng phí vì không có cốt truyện thật, không có kiến trúc AI, không multiplayer. Luồng rút gọn còn **3 wave viết, review, fix loop và bước lắp 0_Index — 6 file** — cùng workflow `gdd-forge:forge-run`, cùng verify từng file, review multi-lens và fix loop như luồng đầy đủ:

```
W0 Gate (preset casual) ─► workflow gdd-forge:forge-run, chạy theo đoạn:
   W1 1_Concept ◆ ─► W2 2_Core Gameplay ─► W3 3_UX Art and Audio ‖ 4_Business and LiveOps ‖ 5_Tech Note
   ─► W4 Review (bắt buộc) ◆ ─► FIX (tới khi sạch, ≤ 2 vòng) ◆ ─► INDEX: 0_Index → critic ─► Done
```

Checkpoint giống luồng đầy đủ: duyệt chương neo luôn dừng sau W1 (`1_Concept`), GAP cuối W2/W3 nếu có, Blocker sau review, Major tồn đọng sau 2 vòng fix (Major `structural` được viết lại từ đầu thay vì PATCH). `0_Index.md` do một bước lắp ráp của workflow ghép từ `contracts-lite/lite-0.md`, không bao giờ do agent thiết kế viết.

Mỗi file gộp nhiều chương của luồng đầy đủ: `1_Concept` gộp ch3 + phần setting thay cho ch5 + header bản quyền/version thay cho ch1, ch2; `2_Core Gameplay` gộp ch4 + ch6 + hành vi obstacle thay cho ch8; `3_UX Art and Audio` gộp ch7 + ch10 + phần game feel; `4_Business and LiveOps` là ch12 viết lại theo thực tế casual (vị trí rewarded video, nhịp interstitial, danh mục IAP, **định nghĩa** KPI, roadmap có bước CPI-test chỉ khi `D-48` = có chạy paid UA); `5_Tech Note` gộp ch9 + rủi ro kỹ thuật (§5.7) + danh sách SDK — không có tool matrix riêng như ch11 bản đầy đủ.

Mỗi contract lite có dòng **Owns** (file nào là chủ của sự kiện/con số nào) và **Budget** theo `wc -w` — tổng 5 file ước chừng ≤ 9.000 từ; không cắt input như luồng đầy đủ, mỗi dispatch đọc trọn các file lite phía trên nó. Review ở W4 giờ **bắt buộc**, không còn hỏi chạy hay bỏ qua.

Đặt tên trong luồng rút gọn: không có wave namer riêng — `1_Concept` §1.2 đề xuất 3 tên, bạn chọn ngay tại checkpoint duyệt neo sau W1; orchestrator ghi `game_name`/`slug` vào brief, đổi tên thư mục và điền dòng tên ở §1.1 trước W2.

`--file N` viết lại file N từ đầu, verify, checkpoint GAP nếu có, rồi thêm dòng version ở `1_Concept` §1.1, reviewer RECHECK file N, PATCH các Major và lắp lại 0_Index; Done liệt kê các file có thể đã cũ (N = 1 → file 2–5).

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
├── 0_Index.md                         (gdd-scribe)
├── 1_Copyright Information.md         (gdd-scribe)
├── 2_Version History.md               (gdd-scribe)
├── 3_Game Overview.md                 (gdd-concept-architect)
├── 4_Gameplay and Mechanics.md        (gdd-mechanics-designer)
├── 5_Story, Setting and Character.md  (gdd-narrative-designer)
├── 6_Levels.md                        (gdd-level-designer)
├── 7_Interface.md                     (gdd-ux-designer)
├── 8_Artificial Intelligence.md       (gdd-ai-designer)
├── 9_Technical.md                     (gdd-tech-designer)
├── 10_Game Art.md                     (gdd-art-director)
├── 11_Secondary Software.md           (gdd-tech-designer)
├── 12_Management.md                   (gdd-producer)
├── 13_Appendices.md                   (gdd-scribe)
└── _work/
    ├── brief.md            # brief đã đóng băng (+ § Gate additions: câu trả lời ở các checkpoint)
    ├── gap-log.md          # mọi câu hỏi GAP / verify (V-) / review (R-) + câu trả lời + lớp (value/structural)
    ├── review-report.md    # Blockers/Majors/Minors (chỉ finding đã qua verify) + ma trận checklist + 12 consistency rule + ## Verification (số đếm) + ## Fix loop (id · severity · file · status · round)
    ├── fact-ledger.md      # bảng dữ kiện (key|kind|value|file §) reviewer dựng trước khi chấm rule 9–12
    ├── run-meta.md         # ngày, phiên bản kit, D-15, dòng workflow:, bảng § Waves (agent · model của tier, `session` khi kế thừa · status · số từ `wc -w` · self-check), § Fix loop (iterations 0–N)
    ├── checks/             # kết quả verify từng file (<file>.check.md): số finding raised/refuted, finding đã xác nhận và cách xử lý (patched / hỏi người dùng)
    ├── inputs/             # chỉ luồng đầy đủ: _anchor.md + lát cắt §mục cho từng dispatch (ch<N>/), cộng ch13/ và ch00/ cho W10
    └── reports/            # mỗi REPORT của agent lưu nguyên văn (<chapter>.report.md) — số từ nằm ở run-meta.md, không nằm trong REPORT
```

Luồng rút gọn (`--profile casual`) ghi ra 6 file thay vì 14, cùng thư mục `_work/` nhưng **không có `inputs/`** (không cắt input):

```
deliverables/<slug>/GDD/<version>/
├── 0_Index.md                  (bước lắp ráp của workflow, không phải agent thiết kế — §0.3 chỉ còn file|trạng thái|mục còn mở)
├── 1_Concept.md                (gdd-concept-architect)
├── 2_Core Gameplay.md          (gdd-mechanics-designer)
├── 3_UX Art and Audio.md       (gdd-ux-designer)
├── 4_Business and LiveOps.md   (gdd-producer)
├── 5_Tech Note.md              (gdd-tech-designer)
└── _work/                      (như trên trừ inputs/, thêm `profile:` trong run-meta.md)
```

## 7. Agents & model

Không agent nào ghim model trong frontmatter. Bảng routing của workflow (`TIERS` / `ROLE_TIER` / `tierFor` trong `workflows/forge-run.js` — nguồn đúng duy nhất) chọn một tier cho từng dispatch:

| Tier | Model | Dùng cho | Vì sao |
|---|---|---|---|
| `deep` | model của phiên (không đặt `model`; hoặc `CLAUDE_CODE_SUBAGENT_MODEL`) | `gdd-concept-architect`, `gdd-mechanics-designer`, `gdd-narrative-designer`, `gdd-level-designer`, `gdd-ai-designer`, `gdd-tech-designer`, `gdd-namer`, `gdd-reviewer`; finder verify, lens finder, voter, completeness critic | phán đoán thiết kế, review và kiểm chứng đối kháng — chất lượng ở đây quyết định cả GDD, nên dùng model bạn đang chạy |
| `spec` | sonnet | `gdd-ux-designer`, `gdd-art-director`, `gdd-producer`, `gdd-scribe`; gộp finding + viết review report; lắp `0_Index.md` lite; ch5 khi `D-21 ∈ {None, Light framing}`, ch8 khi `D-22 = None` | viết đặc tả theo template và contract đã chặt, tổng hợp, gộp — neo và pillar đã có sẵn; ch5/ch8 lúc đó gần như toàn dòng `N/A —` |
| `clerk` | sonnet, effort low | bookkeeping (lưu REPORT, `wc -w`, dòng run-meta/gap-log), cắt/trích section, tìm file trích dẫn, sửa Minor ≤ 2 dòng, thêm dòng version | việc cơ học, không cần phán đoán — rẻ và nhanh |

PATCH và viết lại từ đầu dùng tier của agent chủ file. Cột Model trong `run-meta.md` § Waves ghi model của tier (`session` khi kế thừa model của phiên). Muốn mọi dispatch dùng cùng một model, nói rõ khi gọi lệnh (ví dụ "dùng opus cho mọi agent") — orchestrator truyền `model_override`, thay cho mọi tier. `/gdd-forge:name` và `/gdd-forge:review` dispatch thẳng một agent, không qua workflow — agent đó chạy model của phiên.

5 agent dùng chung cho cả 2 luồng (`concept-architect`, `mechanics-designer`, `ux-designer`, `producer`, `tech-designer`) là file agent tinh gọn, chỉ giữ phần đúng cho cả full lẫn lite; kinh nghiệm viết riêng theo chương nằm ở `references/guidance/<role>.full.md` / `.lite.md`, mỗi dispatch đọc đúng file guidance của profile đang chạy.

## 8. Cấu trúc kit

```
gdd-forge/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── gdd-*.md                    # 12 agent — không agent nào ghim model (mục 7); chủ của từng file ở mục 6
├── workflows/
│   └── forge-run.js                # workflow gdd-forge:forge-run — nơi duy nhất chứa bảng stage/chương, bản đồ cắt input, envelope dispatch, verify/review/fix loop và bảng routing model
└── skills/
    ├── forge/
    │   ├── SKILL.md                # bản đồ + hợp đồng gọi workflow (args, checkpoint, resolution)
    │   ├── references/
    │   │   ├── brief-schema.md
    │   │   ├── brief-template.md
    │   │   ├── run-meta-template.md    # khung run-meta.md
    │   │   ├── gap-log-template.md     # khung gap-log.md
    │   │   ├── chapter-contracts.md    # index mỏng: bảng chương → agent → contract
    │   │   ├── dispatch-rules.md       # quy tắc dùng chung mọi dispatch: DECISION/PROPOSAL/ELABORATION, PATCH mode, khối REPORT
    │   │   ├── consistency-rules.md    # 12 rule cross-chapter cho reviewer
    │   │   ├── consistency-rules-lite.md  # 12 rule cho luồng rút gọn (rule 1–8 đánh số khác, 9–12 giống luồng đầy đủ)
    │   │   ├── pipeline.md             # quy trình của orchestrator luồng đầy đủ: gate, vòng gọi workflow, resume, re-run, failure modes
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

**Install** — needs a Claude Code version with the **Workflow tool**. Three ways: `claude --plugin-dir ~/Downloads/gdd-forge` (quick try) · `claude plugin marketplace add ~/Downloads/gdd-forge` then `claude plugin install gdd-forge@birdybird-local` (user-scope install — `claude plugin install` only accepts a plugin name from a registered marketplace, not a local path) · copy `skills/*` to `~/.claude/skills/`, `agents/*` to `~/.claude/agents/` and `workflows/forge-run.js` to `~/.claude/workflows/` (no plugin — commands then have no prefix: `/forge`, `/name`, `/review`). As a plugin, `workflows/forge-run.js` registers as the named workflow `gdd-forge:forge-run`; a local copy is run through `scriptPath` instead (`${CLAUDE_SKILL_DIR}/../../workflows/forge-run.js`, so keep `workflows/` beside `skills/`). The skill detects which form is present and records it on the `workflow:` line of `run-meta.md`.

**Usage** — `/gdd-forge:forge <pitch>` · `/gdd-forge:forge <path/to/brief.md>` · `/gdd-forge:forge --chapter 6` · `/gdd-forge:forge --resume <out dir>` · `/gdd-forge:name <pitch>` · `/gdd-forge:review <gdd folder>`.

**How a run works** — the orchestrator (the main agent running the skill) runs the W0 gate with you, then drives one workflow, `gdd-forge:forge-run`, segment by segment: each call runs from a stage until the next checkpoint or the end. A workflow cannot ask the user, so every question happens between segments — the orchestrator asks, records the answer on disk (`brief.md` Gate additions, `gap-log.md`) and calls again; state lives only on disk (the output folder and `_work/`), so `--resume` works across sessions. Checkpoints: name choice (only when a name must be generated), anchor-chapter approval (always — ch 3, or `1_Concept` in the lite flow, before anything downstream is written), GAPs and verify decisions, review Blockers, and Majors still open after the fix loop. Every new or freshly rewritten file is verified adversarially in its own wave: one finder, then three perspective-diverse voters per Major (a finding survives with ≥ 2 upholds); confirmed Majors that need no user decision are auto-PATCHed by the owning agent, the rest become `V-` checkpoint items, and the results land in `_work/checks/`. The review (W8 full / W4 lite) runs `gdd-reviewer` in parallel with four lens finders (contradictions and numbers, brief fidelity, closure, hygiene), merges and de-duplicates their findings, and keeps only those that survive verification (three voters per Blocker/Major, ≥ 2 upholds; one evidence check per Minor). The fix loop then runs until clean, at most 2 rounds — one PATCH per owner file per round, RECHECK by `gdd-reviewer` plus a regression lens, verified the same way — after which it asks you: one more round, or accept the rest as known issues. A completeness critic checks the finished set before Done.

**Output** — `deliverables/<slug>/GDD/<version>/` holds `0_Index.md` through `13_Appendices.md` (each owned by one agent — see §6 above) plus `_work/` with `brief.md`, `gap-log.md`, `review-report.md` (verified findings only, plus `## Verification` counts and a `## Fix loop` table), `fact-ledger.md` (the reviewer's fact table), `checks/` (one verification note per file), and `run-meta.md` (dates, kit version, the `workflow:` line, and the § Waves table — word counts live only there, from `wc -w`, never in an agent's own report).

**Three kinds of information & GAPs** — every dispatch classifies what it writes as a DECISION (from `brief.md` only), a PROPOSAL (a reversible, local choice the brief doesn't make — the agent writes its own recommendation tagged `(proposal)` with 1–2 alternatives under Open Decisions, never asking the user mid-run), or an ELABORATION (everything else, designed freely). Only a genuine missing decision (a new feature/mode/screen, a real-money price, two contradicting sources…) becomes a `⟂ GAP`, tagged with a class — `value` (fills in one value) or `structural` (changes what a feature or flow *is*). Subagents can never call `AskUserQuestion`; GAPs are collected and asked to the user **at the checkpoint that closes each wave**, then resolved by class: `value` GAPs are patched into the file directly by the orchestrator via `Edit` (if more than ~3 lines depend on the value, the orchestrator picks `patch` and the workflow PATCHes the owner instead), `structural` GAPs get the owning agent re-dispatched fresh by the workflow, not PATCHed, then re-verified. When the changed fact is already cited downstream, the workflow PATCHes every citing file after the owner.

**Casual profile** — `--profile casual` runs three writing waves, a review, a fix loop and an index step on the same workflow (with the same per-file verify, multi-lens review and fix loop), producing 6 files instead of 14, for casual and hyper-casual mobile titles that have no real narrative, no AI architecture and no multiplayer. Each file absorbs several full chapters; the business file covers rewarded-video placement, interstitial cadence, an IAP catalogue with real-money prices, and KPI *definitions*, with the CPI-test roadmap step and paid-UA metrics gated by the new `D-48` (`paid_ua`) field. The lite profile no longer slices its inputs — every dispatch reads the upstream lite files whole — and every lite contract now carries an `Owns` line plus a `wc -w` word budget (≈9,000 words total across the five files). The lite consistency review (W4) is now **mandatory**, never skipped, and `0_Index.md` is assembled by a workflow step from `contracts-lite/lite-0.md`, never written by a design agent. The gate proposes a preset of typical casual values which the user confirms or edits in one round — an unconfirmed preset value is never written to the brief, and the pitch (D-02) is still required. See [`profile-casual.md`](skills/forge/references/profile-casual.md).

**Input slicing (full profile only)** — a chapter contract consumes named sections, not whole files, so before each W3–W7 dispatch the workflow slices exactly those sections with `scripts/extract-sections.sh` and passes only the slices (the slice map is `SLICES` in `workflows/forge-run.js`). Pillars (§3.2) and the Glossary (§3.10) are sliced once into `_anchor.md` and passed to every downstream dispatch, because the shared dispatch rules make every chapter reuse the Glossary and slicing strictly by contract would break that. Data files are likewise passed as topic slices the orchestrator selects from the brief.

**Models** — no agent pins a model in its frontmatter. The workflow's routing table (`TIERS` / `ROLE_TIER` / `tierFor` in `workflows/forge-run.js`) picks a tier per dispatch: `deep` = the session's model (no model set) for design judgement, review and adversarial verification — the concept, mechanics, narrative, level, AI and tech designers, the namer, the reviewer, and every verify finder, lens finder, voter and the completeness critic; `spec` = sonnet for template-driven spec writing, compiling and merging — ux, art, producer, scribe, the merge and report-writer steps, the lite `0_Index.md` assembly, and ch 5 / ch 8 when they are mostly `N/A —` lines (`D-21 ∈ {None, Light framing}` / `D-22 = None`); `clerk` = sonnet at low effort for mechanical bookkeeping, slicing and ≤ 2-line Minor fixes. PATCH and fresh re-dispatches use the owner's tier; `model_override` (only when you explicitly ask for one model everywhere) replaces every tier. `/gdd-forge:name` and `/gdd-forge:review` dispatch a single agent directly, on the session's model.

**A few operational details** — every dispatch prompt, full or lite, names [`dispatch-rules.md`](skills/forge/references/dispatch-rules.md) — the single home of the writing rules, PATCH mode, and the closing `## REPORT` block, so agent files themselves no longer restate any of that. `AskUserQuestion` allows at most 4 options, so for a field with more the orchestrator lists them all in the question text and offers the 4 most likely, with anything else typed via Other; a section a Depth rule removes still keeps its numbered heading followed by a one-line reason, since downstream dispatches slice chapters by heading number and a missing heading halts the pipeline. `gdd-reviewer` builds `fact-ledger.md` before judging anything, then checks all 12 consistency rules against it; inside `/gdd-forge:forge` it is no longer the only reviewer — its findings are merged with the four lenses' and pass the same voter check (`/gdd-forge:review` still runs it alone). `gdd-scribe` writes ch 1 then ch 2 in one run and reads pre-extracted `## Open Decisions`/`## New Terms`/abstract slices (via `extract-sections.sh`'s `@<Heading>` and `intro` spec forms) for ch 13 and `0_Index.md` instead of whole chapters. The five dual-profile agents (`gdd-concept-architect`, `gdd-mechanics-designer`, `gdd-ux-designer`, `gdd-producer`, `gdd-tech-designer`) are kept deliberately slim and read a `references/guidance/<role>.full.md` or `.lite.md` file for chapter-specific craft advice instead of carrying it inline.
