---
name: gdd-review
description: Technical Leader review một GDD bất kỳ (repo GDD của studio khai ở key `gdd.path` của CLAUDE.md / CLAUDE.local.md — không cần do gdd-forge sinh) trước khi giao việc — tìm (1) conflict trong feature và giữa các GDD/glossary, (2) nội dung out of scope vì quá kỹ thuật (API, database, cơ chế server, vận hành) — không phân tích, chỉ liệt kê ở mục riêng "Nội dung ngoài phạm vi GDD" để Game Design chủ động xoá, (3) thiếu info để implement (trigger, số liệu, công thức, edge case, reset, UI state, asset) — rồi xuất report câu hỏi cho Game Design thành hai file cùng nội dung, luôn đồng bộ: `gdd-report.md` (bản gốc — cập nhật và `--verify` đọc câu hỏi từ đây) và `gdd-report.html` (render từ md theo template HTML của toolkit report `shared/report-toolkit`: KPI, Hình 1, thẻ câu hỏi có evidence nguyên văn kèm file:dòng, category/priority theo chuẩn). Gọi `/gdd-review <file GDD | tên feature | thư mục GDD> [<…>]` [`sections=<§|tiêu đề>[;…]`] [`lens=<conflict|scope|missing>[,…]`] [`context=none`] [`extra=<file|thư mục>`] [`run=<tên>`] [`title=<tiêu đề>`] [`rounds=<n>`] [`--verify`]. `--verify` = không audit lại GDD, chỉ cho VERIFIER kiểm câu hỏi đang có trong report đã được GDD mới trả lời chưa — dùng khi Game Design vừa sửa tài liệu và muốn biết còn bao nhiêu câu cần resolve ("check câu hỏi đã resolve chưa", "còn bao nhiêu câu hỏi"). Main session thu nguồn + chạy script, giao find → verify độc lập → synthesize → critic cho agent `gdd-review` (vai Technical Leader). Dùng khi user muốn review/audit GDD để ra câu hỏi cho Game Design, cập nhật report GDD, hoặc đóng câu hỏi đã trả lời. GDD do gdd-forge sinh (có `concept.md` + `decisions.md`) mà user chỉ muốn tự kiểm khi viết ⇒ dùng `/review`, không phải skill này. Chỉ có MỘT report cố định `reports/gdd-review/gdd-report.{md,html}` (không tạo thư mục theo ngày): chưa có thì tạo (full flow); đã có thì CẬP NHẬT tại chỗ theo thay đổi của repo GDD (verify lại câu hỏi bị ảnh hưởng, tìm câu mới ở mục vừa sửa), GDD user nêu mà report chưa có thì thêm vào report đó. Chỉ ghi `reports/gdd-review/`, không sửa GDD, không commit.
---

# gdd-review

Main session chạy skill này trực tiếp — không dùng Workflow. Phần deterministic (thu nguồn, script) do main session làm; phần phán đoán giao cho subagent `gdd-review` qua Agent tool: `subagent_type` = `gdd-forge:gdd-review` nếu có trong danh sách agent, không thì `gdd-review` (cài kiểu copy); không có cả hai ⇒ general-purpose agent được dặn đọc `<abs path của ${CLAUDE_SKILL_DIR}/../../agents/gdd-review.md>` và làm đúng vai trong đó.

Model: orchestrator là chính main session, chạy bằng model user đang chat — không spawn agent orchestrator. Worker tìm cho rộng thì rẻ, worker lọc thì chính xác — mỗi lần spawn truyền `model` đúng bảng:

| Vai | `model` |
|---|---|
| FINDER · QUOTE-FIX | `"haiku"` |
| VERIFIER · CRITIC · SYNTHESIZER | `"sonnet"` |

Worker chỉ theo luật của skill này: agent khai `omitClaudeMd: true` nên không nạp `CLAUDE.md` + `.claude/rules/**` của project (trước đây ~240k token nền mỗi agent, 78% token của run). Định nghĩa agent nạp lúc mở session — sửa frontmatter thì mở session mới rồi mới chạy.

`<SK>` = path tuyệt đối của `${CLAUDE_SKILL_DIR}`. `<TK>` = path tuyệt đối của `${CLAUDE_SKILL_DIR}/../../shared/report-toolkit` (toolkit report, [README](../../shared/report-toolkit/README.md)). Mọi prompt giao agent `gdd-review` mở đầu bằng `SK: <SK>. TK: <TK>.` — agent không tự tìm được hai thư mục này. `<GDD>` = key `gdd.path` (`CLAUDE.local.md`); `<GLOSSARY>` = key `gdd.glossary`, `<PREFIX>` = key `gdd.filePrefix` (`CLAUDE.md` §Project config). `<R>` = `reports/gdd-review` — cố định, không tạo thư mục theo ngày/run. Mọi lệnh chạy từ repo root.

Luật review: [review-standard.md](review-standard.md). Nhãn report và category đóng (bản máy đọc): [profile.json](profile.json).

## Report: md là bản gốc, html render từ md

Chỉ dùng hai file: `reports/gdd-review/gdd-report.md` + `reports/gdd-review/gdd-report.html`, cùng nội dung. Audit tất cả GDD, một file hay nhiều file đều cập nhật thẳng vào hai file này — không bao giờ tạo report mới. Chỉ tạo khi hai file chưa tồn tại. Chỉ [`report_md.py`](scripts/report_md.py) được ghi hai file này (`<R>` là mặc định, bỏ được):

| Lệnh | Việc |
|---|---|
| `python3 -I <SK>/scripts/report_md.py write <R> --gdd <GDD>` | `data/` → md → html. Đọc ngược md vừa sinh và so với `data/`; lệch thì không ghi gì và báo lỗi |
| `python3 -I <SK>/scripts/report_md.py load <R> --gdd <GDD>` | md → dựng lại `data/{run,questions,scope,inventory,audit}.json` → html. Từ chối nếu `data/questions.json` mới hơn md và khác nội dung (run dở chưa render); `--force` thì lấy theo md |
| `python3 -I <SK>/scripts/report_md.py check <R>` | html mang sha256 của md đã render ra nó; lệch ⇒ exit 1 |
| `python3 -I <SK>/scripts/report_md.py clean <R>` | Xoá cache `data/` + `src/`, chỉ còn md + html. Từ chối khi html lệch md, `data/questions.json` khác md, hoặc `data/work/` còn unit có `find-` mà chưa có `verified-` |

- md và html luôn cập nhật cùng nhau qua `write`, không ghi riêng một file. Trước khi báo xong chạy `check`; `inSync: false` ⇒ `write` lại.
- md giữ câu hỏi và mục Ngoài phạm vi GDD dạng chữ đọc được (sửa tay được — `load` nhận các sửa đó, sai định dạng thì báo số dòng); meta run, danh sách module, câu đã đóng (`dropped`) nằm trong khối ẩn `<!-- gdd-review:data … -->` cuối file. Path trong md tương đối `<GDD>` (`$RUN/…` = `<R>/…`), nên md dùng được trên máy khác.
- `<R>/data/` và `<R>/src/` chỉ là cache trong lúc chạy (gitignore): `load` + `update_run.py` dựng lại, chạy xong thì `clean` xoá (§7) — xong việc `<R>` chỉ còn md + html. Không bao giờ sửa html tay; không render html bằng `render_audit.py` trực tiếp.
- `report_status.py` báo `legacy` (thư mục run theo ngày kiểu cũ còn report) ⇒ hỏi user có gộp/xoá không; không tự đọc report trong đó.

## 0. Chọn chế độ — tạo hay cập nhật

Resolve target theo §1 (nếu user có nêu), rồi:

```
python3 -I <SK>/scripts/report_status.py --gdd <GDD> [<target file|thư mục> …]
# exists · inSync · date · targets (số GDD) · covers · missing (GDD user nêu mà report chưa có) · cache (data/ còn sót) · legacy
```

| Tình huống | Chế độ |
|---|---|
| `exists = false`, không `--verify` | **tạo** — full flow §1–§7; không nêu target ⇒ hỏi (§1) |
| `exists = false`, có `--verify` | dừng, báo chưa có report để verify — `--verify` không bao giờ tự tạo report |
| Có `--verify` | **verify** (§Verify) mọi câu hỏi trong report. Target user nêu chỉ để báo: có target trong `missing` ⇒ nói rõ verify không thêm GDD, muốn thêm thì chạy `/gdd-review <target>` không `--verify` |
| Không nêu target, hoặc `missing` rỗng | **cập nhật** (§Cập nhật report) |
| `missing` khác rỗng | **cập nhật + thêm GDD** — §Cập nhật report với `update_run.py … --add <missing…>`: GDD mới thành target, quét cả file như GDD mới, câu hỏi gộp vào report đang có (id cũ giữ nguyên) |
| User nói rõ "review lại từ đầu" / "tạo lại report" | `AskUserQuestion` xác nhận (report hiện tại bị thay, id câu hỏi đánh lại từ đầu, câu đã đóng mất lịch sử). Đồng ý ⇒ xoá `<R>/data/`, `<R>/src/`, full flow §1–§7 với target user nêu (không nêu ⇒ đúng target của report hiện tại) |

`cache = true` (lần trước dừng giữa chừng hoặc chưa `clean`) ⇒ xử như §Chạy tiếp run dở trước, rồi mới chọn chế độ.

**Cập nhật** hoặc **verify** ⇒ trước mọi bước: `python3 -I <SK>/scripts/report_md.py load <R> --gdd <GDD>` — md là bản gốc (có thể đã được sửa tay, `data/` đã bị `clean`). `load` từ chối vì run dở ⇒ xử như §Chạy tiếp run dở, không `--force` khi chưa hỏi user.

`sections=` / `lens=` / `context=` / `extra=` / `title=` chỉ áp khi **tạo**; report đã có thì giữ phạm vi đang có — user có nêu ⇒ nói rõ tham số bị bỏ qua và cách đổi (tạo lại report).

Báo user một dòng trước khi làm: chế độ, report (ngày, số GDD, commit GDD lúc review), GDD sẽ thêm (nếu có), lý do.

## 1. Tham số

Mỗi target là path, tên file, stem (`Stamina`, `X3-GameMode-Arena-System`) hoặc tên thư mục của `<GDD>` (`04. Game Mode System`). Resolve: path có thật ⇒ dùng; không thì tìm trong `<GDD>` file `.md` hoặc thư mục có tên chứa chuỗi đó (không phân biệt hoa thường). Nhiều kết quả ⇒ `AskUserQuestion` (liệt kê path, multiSelect khi user có thể muốn nhiều file). Không có kết quả hoặc thiếu target ⇒ hỏi đúng một câu. Thiếu key `gdd.path` ⇒ hỏi user, không đoán; user đồng ý thì ghi key vào `CLAUDE.local.md`. Thiếu `gdd.glossary` ⇒ chạy không có glossary (bỏ `--glossary`, `run.json` `glossary: null`); thiếu `gdd.filePrefix` ⇒ prefix rỗng. `<GDD>` không tồn tại ⇒ dừng, báo user path đã thử.

| Tham số | Giá trị |
|---|---|
| `targets` | path tuyệt đối sau khi resolve |
| `context` | `context=none` ⇒ không lấy GDD liên quan; mặc định lấy một cấp `[[...]]` + `<GLOSSARY>` |
| `extra` | `extra=<file|thư mục>` lặp được — GDD đối chiếu thêm ngoài `[[...]]` |
| `label` · `short` | một target ⇒ tên file bỏ `.md` · stem bỏ `<PREFIX>`; thư mục ⇒ tên thư mục; nhiều file ⇒ ghép `short` bằng ` + ` |
| `note` | một target ⇒ `version` frontmatter (vd `v1.11`); nhiều ⇒ "`<n>` GDD" |
| `title` | `title=`, không có thì `<short> GDD — Câu hỏi cho Game Design` |
| `rounds` | `rounds=`, mặc định 2 |
| `sections` | `sections=<sel>[;<sel>…]` — chỉ review các mục được chọn; phần còn lại của GDD chỉ để đối chiếu. `<sel>` là số mục (`4`, `§8.1`; số cha gồm cả mục con) hoặc chuỗi con của tiêu đề (`Edge Cases`); thêm tiền tố `<stem>:` để áp riêng một target (`Stamina:4.1;Arena:5`), không có tiền tố thì áp mọi target. Mặc định: cả GDD |
| `lens` | `lens=<conflict|scope|missing>[,…]` — chỉ tìm các loại vấn đề này. Mặc định cả ba |

Có `sections=` hoặc `lens=` ⇒ thêm một câu vào `run.json` `notes` nêu phạm vi đã review (mục nào của GDD nào, lens nào), để Game Design biết report không phủ cả tài liệu.

## 2. Thu nguồn

```
mkdir -p <R>/data/work
python3 -I <SK>/scripts/collect_sources.py --gdd <GDD> --run <R> [--context none] [--glossary <GLOSSARY>] [--extra <p> …] <target> [<target> …] > <R>/data/sources.json
```

Ghi `<R>/data/run.json` = `{title, date, mode: "single", new: {label, short, note}, old: null, notes: [..], targets: [..], context: [..], linesPerPage: 50, sections: <chuỗi sections= hoặc null>, lenses: [..], contextMode: "links"|"none", extra: [..], glossary: <GLOSSARY>, filePrefix: <PREFIX>, gddCommit: <git -C <GDD> rev-parse HEAD>}` (`targets`/`context` chép từ `sources.json`; `gddCommit` là mốc để lần cập nhật sau biết GDD đã đổi gì). `notes` luôn có: "Số trang `tr. N` là trang ảo 50 dòng của bản nối các GDD; vị trí thật ghi ở chip `<file> · L<dòng>`."; thêm một câu liệt kê GDD đối chiếu (tên file) khi có; thêm `unresolvedLinks` của `sources.json` khi khác rỗng.

```
python3 -I <SK>/scripts/prepare.py <R>            # chép labels từ profile.json vào run.json, chạy prepare_source.py
python3 -I <SK>/scripts/build_inventory.py <R>    # inventory.json + data/modules/<key>.json: module system + mỗi GDD một module, mục = heading cấp 2–3
```

`build_inventory.py` dừng với "sections= không khớp" ⇒ đưa nguyên danh sách đó cho user bằng `AskUserQuestion`, sửa `sections` trong `run.json` rồi chạy lại.

Báo user: target (key, prefix, số mục được review, số trang được review), GDD đối chiếu, tổng số trang. Unit của bước 3:

| Unit | Khi | Lens |
|---|---|---|
| `<key>` mỗi module `role = "target"` | luôn | các lens trong `lenses` |
| `<key>` mỗi module `role = "context"` | `scope` ∈ `lenses` và KHÔNG có `sections=` (GDD đối chiếu cũng phải sạch API/DB — review-standard §1; khi đã thu hẹp phạm vi thì không quét cả file đối chiếu) | `scope` |
| `x-cross` | ≥2 target và `conflict` ∈ `lenses` | `conflict` |

Báo số unit trước khi fan-out.

## 3. Find → Verify

Spawn `subagent_type: "gdd-review"`, chạy background, giữ ≤8 agent cùng lúc; agent nào xong thì đẩy unit đó sang bước kế ngay. Mỗi unit:

| Bước | Việc | Khi |
|---|---|---|
| 1 | FINDER `model: "haiku"`: `Vai FINDER. Run: <R>. Unit: <unit>. Lens: <lens của unit, ngăn bằng dấu phẩy>.` | mỗi unit |
| 2 | `python3 -I <SK>/scripts/check_form.py <R> <unit>` — kiểm/sửa quote nguyên văn, trang, category, luật, module, priority; ghi `votes-<unit>-form.json` (backup `find-<unit>.raw.json`) | finder xong và `candidates` > 0 |
| 3 | VERIFIER `model: "sonnet"`: `Vai VERIFIER. Run: <R>. Unit: <unit>.` → `votes-<unit>-answer.json` | sau bước 2 |
| 4 | `python3 -I <TK>/scripts/resolve_votes.py <R> <unit>` → `data/work/verified-<unit>.json` | verifier xong, hoặc finder ra 0 candidate |

Agent không ghi được file hoặc trả lỗi ⇒ `SendMessage` cho chính agent đó làm lại một lần; vẫn lỗi thì giao agent mới. Agent trả JSON trong câu trả lời vì Write bị chặn ⇒ main session ghi nguyên văn vào đúng file rồi chạy tiếp. Vẫn không có file: FINDER ⇒ unit vào `failedUnits` (không được quét); VERIFIER ⇒ vẫn chạy `resolve_votes.py`, candidate thiếu verdict thành `unverified`.

Xong bước ⇒ báo user tổng `kept` / `dropped` / `unverified`.

## 4. Synthesize

Agent `model: "sonnet"`:

```
Vai SYNTHESIZER. Run: <R>. Mode: init. Units: <mọi unit có verified-<unit>.json>.
```

Không ra `questions.json` ⇒ dừng run, báo user (các file `verified-*.json` còn để chạy lại bước này).

## 5. Critic

Lặp `round` = 1…`rounds`:
1. Agent `model: "sonnet"`: `Vai CRITIC. Run: <R>. Round: <round>. Lens: <lenses>.`
2. `candidates` = 0 ⇒ dừng.
3. `check_form.py <R> crit<round>`, một VERIFIER với `Unit: crit<round>`, rồi `resolve_votes.py <R> crit<round>`.
4. `kept` = 0 ⇒ dừng. Còn lại ⇒ `Vai SYNTHESIZER. Run: <R>. Mode: merge. Units: crit<round>.` rồi sang vòng kế.

Critic lỗi ⇒ dừng vòng critic, ghi lại để báo.

## 6. Render

```
python3 -I <SK>/scripts/build_scope_section.py <R>   # câu Out of scope → data/scope.json (mục "Nội dung ngoài phạm vi GDD", một dòng mỗi GDD), bỏ khỏi câu hỏi
python3 -I <SK>/scripts/locate_quotes.py <R>
python3 -I <TK>/scripts/assemble_audit.py <R>
python3 -I <TK>/scripts/validate_audit.py <R>/data/audit.json --new <R>/src/new --profile <SK>/profile.json
```

Validate còn error ⇒ một agent `model: "haiku"`: `Vai QUOTE-FIX. Run: <R>.`, rồi main session chạy lại ba lệnh trên để xác nhận. Sau đó:

```
python3 -I <SK>/scripts/report_md.py write <R> --gdd <GDD>   # gdd-report.md + gdd-report.html, cùng nội dung (§Report)
```

`write` báo round-trip lệch ⇒ có field chứa xuống dòng / khoảng trắng đầu-cuối mà md không giữ nguyên văn được: sửa field đó trong `data/questions.json` (hoặc `scope.json`), chạy lại từ `assemble_audit.py`.

`locate_quotes.py` báo `unlocated` > 0 ⇒ các quote đó hiện `tr. N` thay vì `<file> · L<dòng>`; nêu số này khi báo kết quả.

## 7. Báo kết quả

- Link `reports/gdd-review/gdd-report.md` và `reports/gdd-review/gdd-report.html`; trước khi báo chạy `report_md.py check <R>` — `inSync: false` ⇒ chạy lại `write`, không báo xong khi hai file lệch.
- Số câu hỏi theo priority, theo category (Conflict / Thiếu info / Trình bày) và theo module; số GDD và mục ở mục Ngoài phạm vi GDD (`data/scope.json`) — đọc `data/questions.json`; số candidate bị bác bỏ, số bị gộp.
- `unverified`, `failedUnits`, critic lỗi, `unresolvedLinks` — có thì nói rõ, đề xuất chạy lại đúng các unit đó (§Chạy tiếp run dở).
- Error/warning cuối của `validate_audit.py`; còn error ⇒ report chưa đạt, nói thẳng.
- Report là để gửi Game Design ⇒ đề xuất một dòng publish thành Artifact.
- Dọn cache, việc cuối cùng: `python3 -I <SK>/scripts/report_md.py clean <R>`. Bỏ qua bước này (giữ cache, nói rõ với user) khi còn `unverified`, `failedUnits` hay critic lỗi — chạy lại các unit đó cần `data/work/`. `clean` từ chối ⇒ báo nguyên lý do, không `--force` khi chưa hỏi user.

## Cập nhật report

Cập nhật report đang có tại chỗ: giữ id câu hỏi, chỉ làm lại phần GDD đã đổi kể từ `gddCommit` của report, cộng các GDD mới thêm bằng `--add` (cả file). Tham số `reverify=all` ⇒ verify lại MỌI câu hỏi theo chuẩn hiện tại (vd sau khi review-standard thêm luật), kể cả khi GDD không đổi.

0. **Nạp report.** `python3 -I <SK>/scripts/report_md.py load <R> --gdd <GDD>` (§0) — câu hỏi lấy từ `gdd-report.md`, kể cả sửa tay.
1. **Làm mới nguồn.** `python3 -I <SK>/scripts/update_run.py <R> --gdd <GDD> [--force] [--add <missing…>]` — `--add` = các file `missing` của `report_status.py` (thêm vào target, `changedModules` = `"*"`, `new.note` = số GDD mới; có `--add` thì luôn refresh). Thêm GDD làm `title`/`new.label` không còn đúng phạm vi (vd tên liệt kê thư mục) ⇒ sửa hai field đó trong `data/run.json` trước §6. Script dò file + mục đã đổi bằng git (gồm cả thay đổi chưa commit), lưu work file cũ vào `data/work/archive/<thời điểm>/`, chạy lại collect → prepare → build_inventory với key/prefix module cũ, ghi `data/work/update.json` (`changedFiles`, `changedModules` = key → danh sách mục đã đổi hoặc `"*"` nếu file mới). Không file nào đổi ⇒ script không chạm run và in `refreshed: false`: không `reverify=all` thì báo user "GDD chưa đổi kể từ lần review" (repo GDD local có thể chưa `git pull` — nhắc user), chỉ render lại nếu report còn tên cũ, rồi `report_md.py clean <R>` và dừng; có `reverify=all` thì chạy lại với `--force`. Script dừng vì GDD đổi tên/xoá ⇒ hỏi user; dừng vì `run.json` thiếu `glossary`/`filePrefix` (run cũ) ⇒ điền từ key `gdd.glossary`/`gdd.filePrefix` rồi chạy lại.
2. **Chọn câu verify lại.** `python3 -I <SK>/scripts/stage_update.py <R> [--all]` — câu có evidence/`api` chạm GDD đã đổi (hoặc quote không còn nguyên văn) vào unit `rev-<key>-<n>` (≤25 câu/unit, `cid` = id câu hỏi); gỡ dòng "Ngoài phạm vi GDD" của module đã đổi khỏi `scope.json` để quét lại. Báo user: số câu verify lại / tổng, số module đã đổi.
3. **Verify lại câu cũ.** Mỗi unit `rev-*`: `check_form.py` → VERIFIER `model: "sonnet"` → `resolve_votes.py` (như §3 bước 2–4). Xong hết ⇒ `python3 -I <SK>/scripts/apply_reverify.py <R> <unit …>`: câu bị bác chuyển vào `dropped` (reason "cập nhật <ngày>: …"), câu `revise` thay tại chỗ, giữ nguyên id.
4. **Tìm câu mới ở mục đã đổi.** Mỗi key trong `changedModules` có `role = "target"`: FINDER `Vai FINDER. Run: <R>. Unit: <key>. Lens: <lenses của run>. Mode: update.` → `check_form.py` → VERIFIER → `resolve_votes.py`. Chạy song song với bước 3 được, nhưng merge SAU khi `apply_reverify.py` xong: `Vai SYNTHESIZER. Run: <R>. Mode: merge. Units: <các key>.` (`model: "sonnet"`) — id mới nối tiếp prefix, câu trùng câu đang có thì gộp evidence.
5. Bỏ critic. §6 Render, rồi §7 Báo kết quả kèm phần thay đổi: số câu bị bỏ (đã được GDD trả lời / không còn đúng), số câu sửa, số câu mới, GDD đã đổi, GDD mới thêm. Có GDD mới thêm ⇒ nhắc một dòng: conflict giữa GDD mới và GDD cũ chỉ được tìm ở phía GDD mới (không chạy critic/lens xuyên tài liệu) — muốn quét đủ thì tạo lại report.

## Verify

`--verify`: không tìm câu hỏi mới, không critic — chỉ kiểm từng câu hỏi đang có trong `gdd-report.md` so với GDD hiện tại, rồi ghi lại md + html chỉ còn câu chưa được giải quyết. Giữ id câu hỏi. Tham số khác (`sections=`, `lens=`, `rounds=`…) bị bỏ qua; phạm vi là phạm vi của report hiện tại. Chạy được khi run chỉ còn `gdd-report.md` (+ html): `data/` và `src/` được dựng lại ở bước 0–1.

0. **Nạp report.** `python3 -I <SK>/scripts/report_md.py load <R> --gdd <GDD>` (§0). Câu GD/dev đã xoá tay khỏi md thì không kiểm nữa; câu sửa tay thì kiểm theo bản đã sửa.
1. **Làm mới nguồn.** `python3 -I <SK>/scripts/update_run.py <R> --gdd <GDD> --verify`. `refreshed: false` ⇒ GDD chưa đổi kể từ lần review nên không câu nào có thể đã được trả lời: báo user số câu đang mở (đọc `data/questions.json`) và nhắc `git pull` repo GDD local, `report_md.py clean <R>`, dừng. Script dừng vì GDD đổi tên/xoá hoặc `run.json` thiếu key ⇒ xử như §Cập nhật report bước 1.
2. **Dựng unit.** `python3 -I <SK>/scripts/stage_update.py <R> --verify` — MỌI câu hỏi vào unit `rev-<key>-<n>` (đáp án có thể nằm ở bất kỳ mục/GDD nào vừa sửa, không chỉ GDD của câu); mục Ngoài phạm vi GDD được máy kiểm lại tại chỗ: quote không còn trong GDD thì bỏ, dòng hết quote thì xoá (`scopeCleared`), còn một phần thì `scopePartial`. Báo user số câu sẽ kiểm, số unit.
3. **Verify.** Mỗi unit: `check_form.py <R> <unit>` → VERIFIER `model: "sonnet"`: `Vai VERIFIER. Run: <R>. Unit: <unit>. Mode: resolve.` → `resolve_votes.py <R> <unit>` (song song như §3, ≤8 agent). Lỗi agent xử như §3.
4. **Áp kết quả.** `python3 -I <SK>/scripts/apply_reverify.py <R> <unit …> --verify` — câu `resolved`/`obsolete` chuyển vào `dropped` (reason `verify <ngày>: …`), câu trả lời một phần được thu hẹp tại chỗ, ghi một note vào `run.json` (số câu đã trả lời / đã kiểm, số còn mở theo priority) để report hiện cho Game Design.
5. §6 Render, rồi báo user:
   - Còn mở: tổng + theo priority (`openByPriority`), số GDD còn dòng Ngoài phạm vi.
   - Đã giải quyết: danh sách `id — title` của `closed.resolved`; không còn áp dụng: `closed.obsolete`; bị bác vì lý do khác (`closed.refuted`, VERIFIER không theo `Mode: resolve`) ⇒ nêu riêng để user xem lại.
   - Trả lời một phần: `revisedIds`. `unchecked` > 0 hoặc `unverified` ⇒ đề xuất chạy lại đúng các unit đó.
   - Một dòng: verify không tìm câu hỏi mới — mục GD vừa viết thêm có thể đẻ câu hỏi mới, muốn quét thì chạy `/gdd-review` không `--verify` (§Cập nhật report).

## Chạy tiếp run dở

Không chạy lại bước 2. Unit thiếu `data/work/find-<unit>.json` chạy lại từ FINDER; thiếu `votes-<unit>-form.json` chạy `check_form.py`; thiếu `votes-<unit>-answer.json` chạy lại VERIFIER; thiếu `verified-<unit>.json` chạy `resolve_votes.py`. Rồi bước 4–7 (bước 4 ghi lại `questions.json` từ đầu).

## Thành phần

| Phần | Vai |
|---|---|
| `review-standard.md` | Luật GR-NN (conflict · out of scope · thiếu info · trình bày), category, priority, cách viết câu hỏi cho Game Design |
| `profile.json` | Category đóng + nhãn report (`Câu hỏi cho Game Design`, `Mục GDD`, `GDD ghi`…) — `validate_audit.py --profile` và `render_audit.py` (qua `meta.labels`) đọc |
| `scripts/collect_sources.py` | Target + một cấp `[[...]]` + bản sao glossary (`--glossary`); bỏ qua thư mục `reports/` ở gốc `<GDD>` (report nằm trong chính repo GDD) |
| `scripts/prepare.py` | Chép `labels` vào `run.json`, gọi `prepare_source.py` với target trước, đối chiếu sau |
| `scripts/build_inventory.py` | `inventory.json` + `data/modules/<key>.json` từ heading GDD, cấp key/prefix module |
| `scripts/check_form.py` | Phần máy kiểm được của verify: quote nguyên văn + sửa trang, category đóng, luật GR có thật, module, priority Out of scope/Lỗi trình bày; ghi `votes-<unit>-form.json` kèm `flags` cho VERIFIER |
| `scripts/report_md.py` | Ghi / đọc `gdd-report.md` (bản gốc) và render `gdd-report.html` từ nó, kèm sha256 của md để `check` biết hai file còn khớp (§Report) |
| `scripts/report_status.py` | Trạng thái report duy nhất: có chưa, `inSync`, phủ target nào, `missing` (GDD user nêu mà report chưa có), cache còn sót, thư mục run kiểu cũ — chọn chế độ §0 |
| `scripts/update_run.py` | Cập nhật / verify: dò GDD đổi bằng git từ `gddCommit`, archive work file, chuẩn bị lại nguồn giữ key/prefix, ghi `data/work/update.json` |
| `scripts/stage_update.py` | Cập nhật: dựng unit `rev-<key>-<n>` cho câu hỏi chạm GDD đã đổi (`--all` = mọi câu), gỡ dòng Ngoài phạm vi của module đã đổi. `--verify` = mọi câu, kiểm lại dòng Ngoài phạm vi theo quote thay vì gỡ |
| `scripts/apply_reverify.py` | Cập nhật / verify: áp kết quả verify lại vào `questions.json`, giữ id; `--verify` tách `resolved`/`obsolete` và ghi note số câu còn mở vào `run.json` |
| `scripts/build_scope_section.py` | Chuyển câu Out of scope thành mục riêng "Nội dung ngoài phạm vi GDD" (`data/scope.json`), một dòng mỗi GDD |
| `scripts/locate_quotes.py` | Gắn `loc` = `<file> · L<dòng>` cho evidence |
| `scripts/gddsource.py` | Dựng lại layout dòng của `prepare_source.py` (trang ↔ file ↔ dòng) |

Toolkit dùng chung (`shared/report-toolkit/`, [README](../../shared/report-toolkit/README.md)): `prepare_source.py`, `resolve_votes.py`, `assemble_audit.py`, `validate_audit.py`, `render_audit.py` (skill này gọi qua `report_md.py`, không gọi thẳng), template `templates/audit-report.html`. Đổi layout HTML thì sửa ở toolkit; đổi layout md thì sửa `report_md.py` (writer và parser đi cặp — `write` tự kiểm round-trip); đổi luật review thì sửa ở skill này.
