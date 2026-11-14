# report-toolkit — data model (toolkit dùng chung)

> Trong gdd-forge, toolkit này chỉ phục vụ skill `gdd-review` (§3–§4). Các mục nói về `/api-req-audit`, `/api-contract-gen` là phần gốc từ repo Project-X3-GDD, giữ để tham khảo.

Hợp đồng dữ liệu chung của hai skill `/api-req-audit` và `/api-contract-gen` (agent `api-req-audit` · `api-contract-gen`). Script trong `scripts/` và agent đọc/ghi đúng các format dưới đây. Đổi một field ở đây ⇒ sửa cùng lúc `scripts/*.py` và vai trong `.claude/agents/api-*.md`.

## 1. Nguồn đã chuẩn bị (`prepare_source.py`)

```
python3 shared/report-toolkit/scripts/prepare_source.py --in <file> [--in <file> …] --out <dir> --label <label> [--short <short>] [--lines-per-page 50]
```

`--in` lặp lại được khi mọi file là `.md`/`.txt` (một Spec = `spec.md` + file contract cùng thư mục): các file nối lại thành một nguồn, trước mỗi file một dòng `===== FILE: <path tương đối> =====`.

| File | Nội dung |
|---|---|
| `<dir>/source.json` | `{label, short, path, format, sha256, pages, unit}` — `unit` luôn `"page"`; nhiều `--in` thêm `paths` (mảng), `path` = file đầu, `format` = `md` |
| `<dir>/pages/p001.txt` … | text của từng trang, UTF-8 |
| `<dir>/full.txt` | mọi trang nối lại, trước mỗi trang một dòng `===== PAGE <n> =====` |

- PDF: `pdftotext -raw` từng trang (`-raw` giữ thứ tự hàng của bảng; chế độ mặc định xen cột).
- `.md` / `.txt` / `.html` / `.docx`: chuyển sang text, tách trang theo ký tự `\f` nếu có, không thì cắt mỗi `--lines-per-page` dòng thành một "trang". Cite `tr. N` khi đó là trang ảo — ghi rõ trong `meta.notes` của report.

## 2. Literal quote

Mọi `quote` trong report là chuỗi chép NGUYÊN VĂN từ nguồn — không dịch, không rút gọn, không thêm `…`. `validate_audit.py` kiểm theo hai tầng, cùng một trang (hoặc nối trang đó với trang kế, cho quote vắt trang):

1. khớp sau khi gộp whitespace và bỏ ký tự `|` `*` `` ` ``;
2. nếu không, khớp sau khi (NFKC) bỏ MỌI khoảng trắng và `|` `*` `` ` ``; gạch nối ở cuối dòng nằm giữa hai chữ cái coi như có-hoặc-không (`non-⏎empty` khớp cả `non-empty` lẫn `nonempty`) — chịu được ngắt dòng trong ô bảng, gạch nối cuối dòng, heading mất dấu cách của `pdftotext`. Mọi dấu khác vẫn phải khớp nguyên văn: toán tử so sánh (`<=` ≠ `>=`), dấu trừ, dấu thập phân, khoảng (`1-100` ≠ `1100`, kể cả khi `-` ở cuối dòng nằm giữa hai chữ số), `%`, `…`.

Không khớp cả hai ⇒ error. Khớp ở trang khác ⇒ error kèm trang đúng. Quote chứa `…`/`...` mà trang nguồn không có ⇒ error riêng (quote bị rút gọn).

## 3. `audit.json` — input của `render_audit.py`

```
python3 shared/report-toolkit/scripts/render_audit.py <audit.json> <out.html>
python3 shared/report-toolkit/scripts/validate_audit.py <audit.json> --new <dir-new> [--old <dir-old>] [--profile <profile.json>]
                                          # --profile = {categories, rules, ruleId}: thay tập category đóng và nguồn rule id (mặc định audit-standard §6 + constitution.md AC-NN)
python3 shared/report-toolkit/scripts/extract_report.py <report.html> <audit.json>   # HTML theo template → audit.json
```

Mọi chuỗi văn xuôi (`meta.notes[]`, `modules[].title` · `short` · `heading` · `diffNote`, `questions[].api` · `title` · `issue` · `ask`, `diffs[].label` · `tag`, `rows[].note`) dùng `` `x` `` để đánh dấu code; renderer escape HTML rồi đổi thành `<code>x</code>`. Code span KHÔNG chứa backtick: số `` ` `` trong chuỗi phải chẵn và không có hai backtick liền nhau — `validate_audit.py` báo error. `quote`, `value`, `gloss` render nguyên văn (escape, giữ xuống dòng), KHÔNG đổi backtick.

`value` trong ô diff hiển thị như quote của nguồn nên cũng là NGUYÊN VĂN (§2): không tìm thấy ở trang nào của nguồn ⇒ error; tìm thấy ngoài `oldPages`/`newPages` ⇒ warning. `oldPages`/`newPages` vượt số trang của nguồn ⇒ error. `evidence[].src = "old"` khi `mode = "single"` ⇒ error.

```jsonc
{
  "meta": {
    "title": "X5 GM API — Thay đổi giữa hai phiên bản và câu hỏi cho Backend",
    "date": "2026-10-11",
    "mode": "diff",                       // "diff" (có bản cũ) | "single"
    "new": {"label": "X5_GM20261010", "short": "20261010", "note": "bản tiếng Anh"},
    "old": {"label": "X5_GM20260722", "short": "20260722"},   // null khi mode=single
    "notes": ["Bản gốc tiếng Trung của X5_GM20261010 chưa nhận được; …"],
    "labels": {"questions": "Câu hỏi cho Game Design", "unit": "Mục GDD", "unitBreakdown": "Nhóm", "unitDef": "…", "priorityDef": "…", "evidence": "GDD ghi", "figure": "Hình 1 — Câu hỏi theo nhóm"},
                                          // tuỳ chọn, mọi key tuỳ chọn: đổi nhãn report cho người đọc khác Backend (vd `/gdd-review` chép từ profile.json); vắng ⇒ nhãn mặc định của template
    "kpiOverride": {"total": 37, "new": 1, "changed": 2, "desc": 2, "unchanged": 32, "modules": {"announcements": 5}}
                                          // tuỳ chọn, chỉ extract_report.py ghi (HTML không liệt kê endpoint): KPI Endpoint (+ "removed") và số endpoint của module ở dòng "Không thay đổi"; có thì renderer dùng thay cho đếm modules[].endpoints
  },
  "modules": [                            // thứ tự = thứ tự trong tài liệu mới
    {
      "key": "mail",                      // slug a-z0-9, unique; dùng cho id="q-<key>" / id="m-<key>"
      "prefix": "MAIL",                   // tiền tố ID câu hỏi, 2–5 chữ HOA, unique
      "title": "Mail",                    // nhãn Hình 1 + heading mục 2 (có thể kèm chú thích: "Redeem codes (mã đổi quà)")
      "short": "Mail",                    // nhãn mục lục + heading mục 3
      "heading": "`/gm/mail/send` có thay đổi",   // phần sau dấu "·" ở heading mục 3; bỏ trống ⇒ tự sinh
      "diffNote": "Không đổi: …",         // <p class="note"> đầu mục 3 của module; tuỳ chọn
      "endpoints": [{"path": "/gm/mail/send", "status": "changed"}]
                                          // status ∈ new | changed | desc | unchanged | removed
                                          // mode=single ⇒ mọi status = "unchanged"
    }
  ],
  "questions": [
    {
      "id": "MAIL-001",                   // <prefix>-NNN, unique; prefix phải khớp module
      "module": "mail",
      "priority": "high",                 // high | mid | low  → Cao | Trung bình | Thấp
      "category": "Chưa định nghĩa hành vi/ràng buộc",   // tập đóng, xem audit-standard.md §Category
      "rules": ["AC-26"],                 // id rule trong constitution.md mà câu hỏi dựa vào; không render
      "api": "`/gm/mail/send` · `is_deduct_mail`",
      "title": "…",
      "issue": "…",
      "evidence": [{"src": "new", "page": 9, "quote": "…"}],   // 1–6 quote; src ∈ new | old; tuỳ chọn "loc": nhãn vị trí hiển thị thay "tr. N" (vd "X3-GameMode-Stamina-System.md · L220"), validator vẫn kiểm theo page
      "ask": "…?"
    }
  ],
  "diffs": [                              // bỏ trống khi mode=single; thứ tự render = thứ tự mảng
    {
      "module": "mail",
      "kind": "modified",                 // added | modified | removed  (đếm KPI "Điểm khác biệt")
      "label": "Mô tả của `attach`: …",
      "tag": "đối chiếu trực tiếp hai tài liệu",   // tuỳ chọn
      "oldPages": "tr. 10",               // null ⇒ "(không có)"; có thể là "tr. 11–12"
      "newPages": "tr. 9",
      "rows": [
        {
          "kind": "changed",              // added | removed | changed | unchanged
          "key": "attach",
          "plainKey": false,              // true ⇒ key là chữ thường (sans), không phải tên field
          "old": [                        // null ⇒ ô "—"
            {"label": "Description", "value": "附件资源数组…", "gloss": "Mảng tài nguyên…", "changed": true}
                                          // label null ⇒ không in nhãn; value null ⇒ "—"; gloss tuỳ chọn
          ],
          "new": [{"label": "Description", "value": "Array of …", "changed": true}],
          "note": "văn bản mới chỉ nêu …" // tuỳ chọn
        }
      ]
    }
  ]
}
```

Tuỳ chọn `"scope": {"title", "intro", "rows": [{"module", "doc", "sections": [..], "kinds": [..], "evidence": [§3 evidence]}]}` — mục cuối report (sau mục 2, hoặc mục 3 khi mode=diff) liệt kê nội dung nên xoá khỏi tài liệu, không tính là câu hỏi; `assemble_audit.py` đọc từ `data/scope.json` (`/gdd-review` ghi), validator kiểm quote như evidence câu hỏi; `rows[].module` là key trong inventory nhưng không bắt buộc có trong `modules[]`. Module inventory có `"role": "context"` mà không có câu hỏi nào bị `assemble_audit.py` bỏ khỏi `modules[]`.

Số liệu KHÔNG ghi trong JSON — renderer tự đếm: KPI endpoint (theo `status`), KPI điểm khác biệt (theo `diffs[].kind`), KPI câu hỏi (theo `priority`), Hình 1, mục lục, số bảng `3.N`, đoạn "Không thay đổi".

## 4. Fragment của `/api-req-audit`

Run dir `reports/api-audit/<run>/`. Cột "Ai ghi" là main session, script, hoặc vai của agent `api-req-audit`. `<unit>` = key module · `x-consistency` · `x-examples` · `crit<N>` (critic vòng N).

```
python3 -I shared/report-toolkit/scripts/resolve_votes.py <run-dir> <unit>
```

| Path | Ai ghi | Nội dung |
|---|---|---|
| `src/new/`, `src/old/` | main session (`prepare_source.py`) | §1 |
| `data/run.json` | main session | `{title, date, mode, new:{label,short,note}, old:{label,short,note}\|null, notes:[..]}` — `assemble_audit.py` chép thành `meta` của §3; `title` rỗng ⇒ tự sinh từ `new.label` |
| `data/inventory.json` | MAP | `{modules:[{key,prefix,title,short,pages:[n..],oldPages:[n..]\|null,endpoints:[{path,status}]}], commonPages:[n..], totalEndpoints:n, grepUnmatched:["path — lý do"]}` |
| `data/diff-<key>.json` | DIFF, sửa bởi DIFF-VERIFIER | `{"module": key, "heading": "…", "diffNote": "…"\|null, "endpoints": [{path,status}], "diffs": [ …§3 diffs… ]}` |
| `data/work/find-<unit>.json` | FINDER · CRITIC | `{"candidates": [ …§3 question chưa có id, thêm "cid" … ], "checked": {"operations": [..], "rules": [..]}, "notes": [..]}` |
| `data/work/votes-<unit>-<lens>.json` | VERIFIER (`lens` ∈ `answer` · `form`) | `{"verdicts": [{cid, verdict: "keep"\|"revise"\|"refute", reason, answerEvidence?, rewrite?: {field cần sửa}}]}` |
| `data/work/verified-<unit>.json` | `resolve_votes.py` | `{"unit", "kept": [candidate đã áp rewrite], "dropped": [{cid,title,reason,evidence}], "unverified": [cid]}` — có verdict `refute` ⇒ dropped; `revise` ⇒ áp các field khác rỗng của `rewrite`; thiếu verdict của một lens ⇒ unverified (vẫn giữ); module không có trong inventory ⇒ `system` |
| `data/questions.json` | SYNTHESIZER | `{"questions": [ …§3 question có id… ], "dropped": [{"cid","reason"}]}` |
| `data/audit.json` | `assemble_audit.py` | §3 đầy đủ |
| `index.html` | `render_audit.py` | output |

## 5. Contract (`/api-contract-gen`)

Run dir `reports/api-contract/<run>/`. Output chính `contract.md` theo `templates/contract.md`; kiểm bằng

```
python3 shared/report-toolkit/scripts/validate_contract.py <contract.md> [--gaps <gaps.json>] [--json]
```

Fragment (cột "Ai ghi" là main session, hoặc vai của agent `api-contract-gen`):

| Path | Ai ghi | Nội dung |
|---|---|---|
| `src/new/`, `src/answers/` | main session (`prepare_source.py`) | §1 |
| `data/run.json` | main session | `{service, date, source:{label, short, kind}, lang}` — `kind` ∈ `spec` · `inline` · `doc` |
| `data/prior-audit.json` | main session | `audit.json` §3 của một lượt `/api-req-audit` (khi có `audit=`) |
| `data/inventory.json` | MAP | shape §4, mỗi module thêm `auditIds:[..]` |
| `data/sec-system.md` · `sec-<key>.md` · `sec-errors.md` | DRAFTER, sửa bởi REPAIRER | section của contract; `system` ghi phần đầu + Error Code Table |
| `data/gaps-<key>.json` | DRAFTER, sửa bởi REPAIRER | `{gaps:[…]}` cùng shape `gaps.json`, chỉ gap của module |
| `data/work/check-<key>-<lens>-<round>.json` | CHECKER (`lens` ∈ `rules` · `fidelity`) | `{clean, checked:{operations, rules}, findings:[{kind, rule?, where, problem, fix, source?}]}` — `kind` ∈ `violation` · `invented` · `dropped` · `mistranscribed` · `gap-missing` · `gap-bad` · `format` |
| `contract.md` · `data/gaps.json` | ASSEMBLER, sửa bởi RECONCILER | output |

`data/gaps.json` = `{gaps:[{id, module, endpoint, rule, question, source_quote, page, audit?}]}` — mọi `NEEDS CLARIFICATION` trong contract có đúng một dòng ở đây; `--gaps` kiểm: đủ field, `id` unique, tập `id` bằng tập id `NEEDS CLARIFICATION` của contract, `rule` là id `AC-NN` có trong `constitution.md`.

Bảng `Open Questions` của contract: cột `ID | Endpoint | Rule | Question` (thêm `| Audit` khi có report audit), mỗi hàng đủ số ô của header; `Rule` là một hay nhiều id `AC-NN` có trong `constitution.md`; path trong `Endpoint` phải là `Path` của một operation trong contract (gap ở phần chung/bảng tham chiếu ghi tên section, không ghi path). Hàng `Error Code Table` có đúng 3 ô. Code fence đóng bằng cùng ký tự và độ dài ≥ fence mở (CommonMark); `NEEDS CLARIFICATION` nằm trong inline code span không tính là gap.
