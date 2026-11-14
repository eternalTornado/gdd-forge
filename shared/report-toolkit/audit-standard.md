# API Requirement Audit — chuẩn report

Chuẩn mà report mẫu `templates/audit-report.html` ("X5 GM API — Thay đổi giữa hai phiên bản và câu hỏi cho Backend", X5_GM20260722 → X5_GM20261010, 34 câu hỏi, 30 điểm khác biệt) đã dùng. Đủ để một agent khác tái tạo report cùng chất lượng cho tài liệu khác. Dữ liệu đi qua `audit.json` (DATA.md §3); renderer tự đếm mọi số liệu. Checklist phát hiện vấn đề là [constitution.md](constitution.md): mỗi câu hỏi ghi id luật nó dựa vào trong field `rules`.

Mỗi quy ước dưới đây dẫn một ví dụ từ template (ID câu hỏi, hoặc số bảng `3.N`).

## 1. Ngôn ngữ

- Văn xuôi tiếng Việt, câu ngắn, vào thẳng vấn đề. Keyword kỹ thuật, tên field, path, kiểu, error code giữ English và đặt trong backtick (`` `is_deduct_mail` ``, `` `/gm/mail/send` ``, `` `1001` ``). Ví dụ: MAIL-001 "Dòng `is_deduct_mail` ghi …".
- Backtick chỉ dùng ở `issue`, `ask`, `api`, `label`, `heading`, `diffNote`, `rows[].note`. `title` của câu hỏi và `title`/`short` của module KHÔNG có backtick — tên field/path viết trơn (34/34 tiêu đề của template: "code_list là []string ở create và []RedeemCode ở list" — RDM-003).
- Thuật ngữ được dùng như từ tiếng Việt (call, path, field, parameter, response, list, update, create, mail, role, deduct, bound) giữ English, không dịch. Riêng "call": Vấn đề dùng "call" ("Tài liệu không nêu call làm gì khi …" — MAIL-001); Câu hỏi dùng "lời gọi" và "fail với `<code>`" ("lời gọi fail với `1001`, bỏ qua entry đó, hay cấp nó?" — MAIL-001; PLR-003).
- Quote chép nguyên văn ngôn ngữ nguồn, không dịch, không rút gọn, không thêm `…` (DATA.md §2).
- Nguồn không phải tiếng Anh hay tiếng Việt (bản cũ tiếng Trung) ⇒ quote nguyên văn + dòng `Dịch nghĩa:` tiếng Việt (field `gloss`). Ví dụ bảng 3.2: `附件资源数组（装备，装备胚子比较特殊不支持邮件发送/扣除）` → "Dịch nghĩa: Mảng tài nguyên đính kèm (trang bị, phôi trang bị …)".
- Tên module trong tiêu đề có thể kèm chú thích tiếng Việt trong ngoặc: "Redeem codes (mã đổi quà)", "Sensitive-word windows (khung giờ tắt lọc từ)".
- Cấm từ định lượng mơ hồ ("vài", "nhiều", "khoảng") — nêu số hoặc liệt kê (`.claude/rules/Shared/ai-discipline.md` R10).

## 2. Cấu trúc report

`mode = diff` (có bản cũ — template):

| Phần | Nội dung |
|---|---|
| Tiêu đề | `<Tên tài liệu> — Thay đổi giữa hai phiên bản và câu hỏi cho Backend`; dòng phụ `<old.label> → <new.label> (<new.note>) · <date>` — vd "X5_GM20260722 → X5_GM20261010 (bản tiếng Anh) · 2026-10-11" |
| Mục lục | 4 mục: 1. Tổng quan · 2. Câu hỏi cho Backend · 3. Khác biệt theo module · Ghi chú (chỉ khi có `meta.notes`). Số đếm: mục 2 = tổng câu hỏi (34), mục 3 = tổng bảng diff (30); mục con = nhãn `short` của module kèm số câu hỏi (mục 2) hoặc số bảng (mục 3) của module đó. Mục 2 chỉ liệt kê module có ≥1 câu hỏi; mục 3 chỉ liệt kê module có ≥1 bảng |
| 1. Tổng quan | 3 KPI + Hình 1 |
| 2. Câu hỏi cho Backend | Một nhóm `h3` mỗi module có câu hỏi, theo thứ tự module trong tài liệu: `<title> · N câu hỏi` |
| 3. Khác biệt theo module | Legend, rồi một nhóm mỗi module có diff: `<short> · <heading>`, ghi chú `Không đổi: …`, các bảng `3.N`; cuối mục: dòng `Không thay đổi: …` |
| Ghi chú (footer) | Provenance (§10) |

### Mode single

`mode = single` (không có bản cũ): `diffs` rỗng, mọi endpoint `status = unchanged` (DATA.md §3). Renderer dựng report khác mode diff ở các phần sau; mục 2 giữ nguyên chuẩn.

| Phần | Nội dung |
|---|---|
| Tiêu đề | `<Tên tài liệu> — Câu hỏi cho Backend` (`meta.title`; vắng thì renderer dùng `<new.label> — Câu hỏi cho Backend`); dòng phụ `<new.label> (<new.note>) · <date>`, không có `→` |
| Mục lục | 1. Tổng quan · 2. Câu hỏi cho Backend (kèm số đếm và mục con như mode diff) · Ghi chú (chỉ khi có `meta.notes`); không có mục 3 |
| KPI | 2 KPI. Endpoint: breakdown duy nhất `Module <số module>`, định nghĩa "Đếm theo API trong tài liệu."; Câu hỏi cho Backend như mode diff. Không có KPI Điểm khác biệt |
| Hình 1 | "Hình 1 — Câu hỏi theo module": một hàng mỗi module có ≥1 câu hỏi, theo thứ tự module; bề rộng thanh = `n / n_max × 55%` với `n` = số câu hỏi; thanh chia ba đoạn Cao/Trung bình/Thấp; cuối hàng `N (cao a, trung bình b, thấp c)`, bỏ vế bằng 0. Module không có câu hỏi gom vào một dòng `Không có câu hỏi: <title>; <title>` |
| 3. Khác biệt theo module | Không có |

## 3. KPI và Hình 1

Ba KPI của mode diff (mode single: §2 Mode single), định nghĩa nguyên văn (render dưới mỗi KPI):

| KPI | Breakdown | Định nghĩa |
|---|---|---|
| Endpoint | Mới · Có thay đổi · Chỉ đổi mô tả · Giữ nguyên (`status` new/changed/desc/unchanged); thêm Bị bỏ (`status` removed) khi có ≥1 endpoint bị bỏ | Đếm theo API. 'Có thay đổi': parameter, kiểu hoặc quy tắc đổi. 'Chỉ đổi mô tả': chỉ đổi chữ, đơn vị hoặc ví dụ. |
| Điểm khác biệt | Thêm · Sửa · Bỏ (`diffs[].kind`) | Đếm theo từng nội dung cụ thể trong tài liệu (một field, một dòng bảng, một quy tắc). Một endpoint có thể có nhiều điểm; chi tiết ở mục 3. |
| Câu hỏi cho Backend | Cao · Trung bình · Thấp | Mức ưu tiên là đánh giá của nhóm phân tích: Cao — đổi request/response hoặc việc cấp/trừ tài nguyên; Trung bình — đổi quy tắc kiểm tra form; Thấp — lỗi trình bày tài liệu. |

Template: Endpoint 37 (Mới 1 · Có thay đổi 2 · Chỉ đổi mô tả 2 · Giữ nguyên 32); Điểm khác biệt 30 (16 · 12 · 2); Câu hỏi 34 (24 · 7 · 3).

Phân loại `status` của endpoint — ví dụ template: `/gm/resources/list` = new; `/gm/mail/send`, `/gm/redeem/create` = changed (thêm field/parameter); `/gm/player/role/list-by-id` = desc (thêm đơn vị "(seconds)", bảng 3.22); `/gm/sensitive/close-window/list` = desc (đặt tên kiểu và bỏ ví dụ, bảng 3.29–3.30).

**Hình 1 — Điểm khác biệt theo module** (mode diff):

- Một hàng mỗi module có ≥1 bảng diff, theo thứ tự module trong tài liệu; nhãn = `title` của module (vd "Resources list (mới)").
- Bề rộng thanh = `n / n_max × 55%` (`n` = số bảng của module, `n_max` = số bảng của module nhiều nhất). Template: Mail 15 → 55.0%, Redeem 6 → 22.0%, System 1 → 3.7%.
- Thanh chia ba đoạn Thêm/Sửa/Bỏ theo tỉ lệ; cuối hàng: `N (thêm a, sửa b, bỏ c) · Q câu hỏi`, bỏ vế bằng 0 — vd "15 (thêm 5, sửa 9, bỏ 1) · 8 câu hỏi", "1 (thêm 1) · 6 câu hỏi".
- Module không có diff gom vào một dòng `Không thay đổi:` ngăn bằng `; `, kèm `· Q câu hỏi` khi Q > 0 — vd "Announcements (thông báo) · 3 câu hỏi; Messages (marquee/system message); Activation codes (mã kích hoạt) · 1 câu hỏi; …".

## 4. Module

Một module = một chương của tài liệu (theo heading nguồn), cộng module **System** cho phần quy tắc chung + bảng mã lỗi + mọi câu hỏi xuyên module. Thứ tự = thứ tự chương trong tài liệu mới; System luôn đứng đầu.

| key | prefix | title (Hình 1 + mục 2) | short (mục lục + mục 3) | Endpoint | Câu hỏi | Bảng diff |
|---|---|---|---|---|---|---|
| `system` | CORE | System — quy tắc chung & mã lỗi | System | 0 | 6 | 1 |
| `announcements` | ANN | Announcements (thông báo) | Announcements | 5 | 3 | 0 |
| `messages` | MES | Messages (marquee/system message) | Messages | 1 | 0 | 0 |
| `activation` | ACT | Activation codes (mã kích hoạt) | Activation codes | 3 | 1 | 0 |
| `mail` | MAIL | Mail | Mail | 1 | 8 | 15 |
| `resources` | RES | Resources list (mới) | Resources list | 1 | 2 | 5 |
| `players` | PLR | Players & roles | Players & roles | 6 | 3 | 1 |
| `redeem` | RDM | Redeem codes (mã đổi quà) | Redeem codes | 4 | 4 | 6 |
| `servers` | SRV | Servers & server groups | Servers & server groups | 10 | 3 | 0 |
| `features` | FEA | Features (bật/tắt tính năng) | Features | 2 | 2 | 0 |
| `sensitive` | SEN | Sensitive-word windows (khung giờ tắt lọc từ) | Sensitive-word windows | 4 | 2 | 2 |

- Mọi module PHẢI có đủ `key` (slug unique), `prefix` (unique) và `short` (DATA.md §3), kể cả module không có câu hỏi và không có diff. Messages là trường hợp đó: `key`/`prefix` của nó không xuất hiện trong HTML (không có anchor `q-`/`m-`), `short` hiện ở cuối mục 3 ("Messages (1)") và `title` ở dòng `Không thay đổi:` của Hình 1. Giá trị `messages`/MES trong bảng là giá trị `extract_report.py` dựng lại từ template. Module vẫn PHẢI có trong `modules[]` để endpoint của nó được đếm.
- `prefix` 2–5 chữ HOA, viết tắt tên chương; module "(mới)" nghĩa là chương không có trong bản cũ.
- `heading` mục 3 = tóm tắt trạng thái endpoint: "`/gm/mail/send` có thay đổi", "`/gm/resources/list` mới", "`/gm/player/role/list-by-id` chỉ đổi mô tả", và "`<path>` bị bỏ" cho endpoint `status = removed`; System dùng "quy tắc chung cho mọi API".

## 5. Câu hỏi (qcard)

Mỗi câu hỏi là một thẻ, thứ tự field:

1. **Dòng đầu**: ID · Priority · Category · API.
2. **Tiêu đề** (`title`).
3. **Vấn đề** (`issue`).
4. **Tài liệu ghi** (`evidence`).
5. **Câu hỏi** (`ask`).

### ID

- `<PREFIX>-NNN`, 3 chữ số, đánh theo thứ tự tạo trong module. Không đánh lại số khi sắp xếp hay khi bỏ câu hỏi: template có MAIL-009 nhưng không có MAIL-008.
- Trong module, thẻ sắp theo priority (Cao → Trung bình → Thấp), cùng priority theo số ID. Vì vậy CORE-006 (Cao) đứng trước CORE-005 (Trung bình), ANN-003 (Cao) đứng trước ANN-001.

### API

Path và field liên quan, phân cách ` · ` giữa path và field, `, ` giữa nhiều path/field: "`/gm/mail/send` · `is_deduct_mail`" (MAIL-001); "`/gm/player/role/kick`, `/gm/player/acct/ban`, `/gm/player/acct/unban` · `role_ids`, `accts`" (PLR-003). Vấn đề không gắn path cụ thể: "mọi API" (CORE-001), hoặc mô tả tập path — "mọi lời gọi không trả data, `/gm/mail/send` · `data`" (CORE-002). Bỏ phần field khi vấn đề là cả endpoint (PLR-001 "`/gm/player/acct/ban`").

### Tiêu đề

Một dòng nêu khiếm khuyết, không nêu đáp án đoán trước, không backtick (§1). Các dạng đã dùng:
- "Không nêu …": "Không nêu thời điểm áp dụng deduct (lúc gửi hay lúc claim)" (MAIL-002).
- "Chưa định nghĩa …": "Chưa định nghĩa kết quả của bound = true trên loại không hỗ trợ binding" (MAIL-005).
- Đối chiếu hai câu: "code có kiểu int ở đây và int32 ở template chung" (RES-001); "Mức sàn khi deduct vật phẩm: 'trừ đến hết số đang có' so với lower bound MinInt32" (MAIL-003).
- Khác path cùng loại: "… khác với các path list cùng loại" (ANN-001).

### Vấn đề

- Chỉ mô tả điều tài liệu **nói** (quote ngắn trong ngoặc kép) và điều tài liệu **không nói** ("Tài liệu không nêu …"). Không suy đoán cách server làm, không đề xuất, không đánh giá.
- Cite field/path bằng backtick; nêu đủ các path bị ảnh hưởng.
- Nêu luật chung có liên quan khi nó làm câu hỏi sắc hơn — ANN-001: "Theo quy tắc chung (\"Not sending a parameter and sending its zero value behave identically\"), `page` không gửi là 0 …".
- Liệt kê các cách hiểu mà tài liệu để ngỏ: "trang đầu, list rỗng hay mã lỗi `1001`" (ANN-001).
- Có thể trỏ câu hỏi khác thay vì lặp: CORE-003 "Riêng `/gm/resources/list` trả `data` chính là mảng trần (RES-002)."

### Tài liệu ghi

- 1–6 quote (template: tối thiểu 1 — MAIL-001; tối đa 6 — CORE-005), mỗi quote kèm trang `tr. N` của nguồn.
- Quote PHẢI chứng minh được vấn đề khi đọc một mình: câu khẳng định gây vấn đề, và — khi là lỗi không nhất quán/khác path — quote **đối chứng** từ path khác. ANN-002 quote `end_time` của announcement (tr. 3) cùng `valid_to` của redeem (tr. 19) và `expire_time` của activation (tr. 8); SRV-001 quote `server_id` của create (tr. 23) cùng của list-by-acct "must be > 0" (tr. 15).
- Quote của luật chung được phép khi Vấn đề dựa vào nó (ANN-001 quote tr. 1).
- Dòng bảng quote cả dòng, giữ cột (`| 1004 | All | Unauthorized API access |` — CORE-001); `validate_audit.py` bỏ `|` khi so.
- Quote phải nằm trên đúng trang được ghi (DATA.md §2).

### Câu hỏi

- Câu hỏi **đóng**: BE trả lời bằng một lựa chọn, một giá trị (số, tập ký tự, khoá sắp xếp, error code) hoặc có/không; không hỏi ý kiến thiết kế.
- Đọc một mình vẫn hiểu: mọi path/field mà đáp án phụ thuộc được nêu tên ngay trong câu hỏi, hoặc mô tả tập path khi tập đó lớn ("Các response list phân trang" — CORE-006; "Với lời gọi không trả về data" — CORE-002). Đại từ ("chúng", "nó") chỉ trỏ thứ đã nêu tên trước đó trong cùng câu hỏi (CORE-003 "… và `/gm/server-group/all` có trả mảng của chúng …"). Module chỉ có một endpoint được phép chỉ nêu field (MAIL-001, MAIL-006 — Mail chỉ có `/gm/mail/send`).

Dạng câu hỏi (tập đóng). Category gợi dạng mặc định; câu hỏi nhiều vế dùng mỗi vế một dạng (CORE-002: chọn phương án + có/không).

| Dạng | Dùng cho | Ví dụ |
|---|---|---|
| Chọn phương án — "A, B, hay C?" | Chưa định nghĩa hành vi/ràng buộc, Thiếu sót bảo mật: tài liệu im lặng, các cách hiểu liệt kê được | "lời gọi fail với `1001`, bỏ qua entry đó, hay cấp nó?" (MAIL-001); "Port 31041 có nhận HTTPS không, hay chỉ HTTP thường?" (CORE-001) |
| Chọn nguồn — mỗi phương án gắn nguồn của nó ("như <bảng/ví dụ/dòng X> nói") | Mâu thuẫn trong tài liệu, Không nhất quán kiểu/định dạng, Không nhất quán giữa các API khi hai chỗ diễn đạt khác nhau | "… như từ "gems" trong các dòng `bound` và `support_bound` nói, hay không, như dòng của nó trong bảng nói?" (MAIL-004); RDM-002, SEN-001. Chỉ cần xác nhận một cách đọc ⇒ một vế kèm nguồn: "… như ví dụ của chúng thể hiện không?" (CORE-003; RES-002, RDM-003) |
| Có/không — "có … không?" | Đáp án là một cờ hay một thuộc tính đúng/sai | RES-001, CORE-004; vế đầu của ANN-002, CORE-006 |
| Giá trị — "là bao nhiêu", "những ký tự nào", "theo thứ tự nào", "trả về gì" | Đáp án là một con số, một tập, một khoá sắp xếp, hay một mã/response mà tài liệu không gợi ý phương án | CORE-005, MAIL-006, RDM-001, SRV-003; vế sau của CORE-006, FEA-002 |
| Xác nhận lỗi trình bày — "… có phải lỗi đánh máy không, tức <giá trị đúng>?" | Lỗi đặt tên/chính tả | "… có phải lỗi đánh máy không, tức body là `{"type": 6, "count": 50}`?" (MAIL-007) |

- Hỏi hành vi dạng mở ("… làm gì với …") chỉ khi Vấn đề đã liệt kê đủ phương án: SRV-002 hỏi "`/gm/server/create` làm gì với `server_id` đã tồn tại" vì Vấn đề đã ghi "(ghi đè hay trả mã lỗi)" và "(thêm mới hay `1002`)".
- Một phương án là từ chối ⇒ hỏi cả error code: "… có từ chối … không; và với error code nào?" (ANN-002, SEN-002); hoặc gắn mã vào phương án: "từ chối với `1001`" (SRV-001).
- Hai vế hỏi của cùng một vấn đề nối bằng "; và" khi vế trước có dấu phẩy hoặc liệt kê phương án ("A hay B"): "… là null hay là `{}`; và …" (CORE-002), "… lúc mail được gửi hay lúc player claim mail; và …" (MAIL-002), "…; và một lời gọi được phép mang bao nhiêu code?" (ACT-001). Vế trước không có dấu phẩy và không liệt kê phương án ⇒ ", và": "`attach` được chứa tối đa bao nhiêu entry, và có được phép rỗng không?" (MAIL-006); SRV-002, CORE-006. Luật này chỉ áp cho chỗ nối hai vế hỏi, không áp cho liệt kê đối tượng trong một vế (SRV-003 "… trong group, và cho `server_id` chưa được tạo …").

## 6. Category (tập đóng)

Đúng 6 giá trị, ghi nguyên văn:

| Category | Định nghĩa | Ví dụ |
|---|---|---|
| Chưa định nghĩa hành vi/ràng buộc | Tài liệu im lặng về một hành vi hay ràng buộc mà client phải biết để gọi đúng, ở path được hỏi — kể cả khi path khác có quy tắc đó làm đối chứng | ANN-003, MAIL-001, PLR-001, SRV-002, FEA-002; đối chứng từ path khác: ANN-001, ANN-002, SRV-001, SEN-002 (19 câu) |
| Mâu thuẫn trong tài liệu | Hai chỗ trong tài liệu (prose, bảng, ví dụ, template chung) cho kết quả khác nhau cho cùng một trường hợp, không thể cùng đúng | MAIL-003, MAIL-004, RES-002, RDM-002, RDM-004, FEA-001, SEN-001 (7 câu) |
| Không nhất quán giữa các API | Câu hỏi xuyên module (§8) mà khái niệm của tiêu đề được nêu ở một số path và vắng, hoặc diễn đạt khác, ở path khác | CORE-002, CORE-003, CORE-004, CORE-005 (4 câu) |
| Không nhất quán kiểu/định dạng | Cùng một field/khái niệm mang hai kiểu mà cả hai câu vẫn có thể cùng đúng trên wire | RES-001, RDM-003 (2 câu) |
| Thiếu sót bảo mật | Thiếu thông tin về xác thực, bảo mật đường truyền, quyền | CORE-001 (1 câu) |
| Lỗi đặt tên/chính tả | Lỗi đánh máy hay cú pháp của tài liệu, ý định rõ từ ngữ cảnh | MAIL-007 (1 câu) |

Phân loại theo thứ tự, dừng ở bước đầu tiên khớp:

1. Thiếu thông tin xác thực, bảo mật đường truyền hay quyền ⇒ **Thiếu sót bảo mật** (CORE-001).
2. Lỗi đánh máy/cú pháp mà ý định rõ từ ngữ cảnh ⇒ **Lỗi đặt tên/chính tả** (MAIL-007). Ví dụ sai mà có hơn một cách hiểu đúng không thuộc bước này (FEA-001: id nào; SEN-001: sửa nhãn hay sửa giá trị).
3. Câu hỏi xuyên module (path trong `api` thuộc ≥2 module, §8) và khái niệm mà tiêu đề nêu được tài liệu nêu ở một số path, vắng hoặc diễn đạt khác ở path khác ⇒ **Không nhất quán giữa các API** (CORE-002, CORE-003, CORE-004, CORE-005). Bước này đứng trước bước 4–5: CORE-003 có dòng `Response` trái ví dụ trên từng path, nhưng vấn đề nó hỏi là wrapper của list được diễn đạt theo hai cách trên nhiều path (mảng trần ở dòng `Response` và ở `/gm/resources/list`, `data.list` ở ví dụ). Câu hỏi xuyên module mà khái niệm của tiêu đề vắng ở mọi path thì không thuộc bước này (CORE-006: không path nào trả tổng số lượng ⇒ bước 6).
4. Cùng tên field mang hai kiểu, và hai câu vẫn có thể cùng đúng trên wire ⇒ **Không nhất quán kiểu/định dạng** (RES-001: `int` và `int32` đều là số nguyên; RDM-003: hai bảng mô tả response của hai endpoint khác nhau).
5. Hai câu về cùng một khái niệm không thể cùng đúng ⇒ **Mâu thuẫn trong tài liệu**: prose với bảng (MAIL-003, MAIL-004, RDM-002), hai dòng mô tả cùng field (RDM-004), template chung với bảng của path (RES-002: `data` là object và là mảng), ví dụ trái bảng tham chiếu (FEA-001), nhãn ví dụ trái giá trị (SEN-001).
6. Còn lại — tài liệu im lặng ở path được hỏi ⇒ **Chưa định nghĩa hành vi/ràng buộc**. Quote đối chứng từ path hay module khác không đổi category (ANN-001, ANN-002, SRV-001, SEN-002).

## 7. Priority

Thang nguyên văn (KPI 3): **Cao** — đổi request/response hoặc việc cấp/trừ tài nguyên; **Trung bình** — đổi quy tắc kiểm tra form; **Thấp** — lỗi trình bày tài liệu.

Luật xếp — hỏi "đáp án làm client đổi gì":

- Đổi cái client gửi/parse (shape `data`, presence, ngữ nghĩa update, kết quả với khoá không tồn tại) hoặc đổi tài nguyên được cấp/trừ ⇒ **Cao**. Ví dụ: CORE-002, ANN-003, MAIL-001, PLR-003, SRV-002.
- Chỉ đổi validation phía form (độ dài, khoảng giá trị, default, ràng buộc thời gian, số phần tử) ⇒ **Trung bình**. Ví dụ: CORE-005, ANN-001, ANN-002, MAIL-006, RDM-001, SRV-001, SEN-002.
- Hành vi API đã rõ ở chỗ khác, chỉ văn bản tài liệu sai ⇒ **Thấp**. Ví dụ: MAIL-007, FEA-001, SEN-001.
- Thiếu sót bảo mật ⇒ **Cao** (CORE-001): đáp án đổi cách client kết nối và gửi credential.
- Câu hỏi nhiều vế khác mức ⇒ lấy mức cao nhất trong các vế. ACT-001 hỏi kết quả cho code không tồn tại (Cao) và số code tối đa (Trung bình) ⇒ Cao.

## 8. Khi nào gộp, khi nào không hỏi

**Gộp:**
- Một vấn đề trên nhiều path cùng module ⇒ một câu hỏi liệt kê mọi path (PLR-003 gộp kick/ban/unban; SRV-003 gộp add-server/del-server; SEN-002 gộp create/update).
- Một vấn đề xuyên module ⇒ một câu ở module System (prefix CORE) thay vì lặp ở từng module: CORE-003 (players + servers), CORE-004 (servers + sensitive), CORE-005 (mail + players + servers), CORE-006 (announcements + redeem + servers).
- Xuyên module = các path trong field `api` thuộc ≥2 module, hoặc `api` là "mọi API" / một tập path trải ≥2 module (CORE-001, CORE-002). Path chỉ xuất hiện làm quote đối chứng không tính: ANN-002 (đối chứng redeem, activation), SEN-002 (đối chứng redeem), SRV-001 (đối chứng players) ở lại module của chúng.
- Khía cạnh đã có câu riêng ⇒ trỏ ID thay vì hỏi lại (CORE-003 trỏ RES-002).

**Không hỏi:**
- Tài liệu đã trả lời ở chỗ khác — kể cả qua luật chung. Ví dụ: `page_size` của announcement có "Defaults to 20 if not sent; max 100" nên không có câu hỏi; ANN-003 chỉ hỏi trường hợp `update_fields` rỗng vì trường hợp "listed but not sent" đã được định nghĩa.
- Chỉ là phong cách/dịch thuật, không đổi hành vi: đổi `desc` → `Description` ở tiêu đề cột (bảng 3.4) là diff, không phải câu hỏi.
- Điểm khác biệt rõ nghĩa không sinh câu hỏi: bảng 3.23–3.27 (redeem thêm `codes`, `code_prefix`, quy tắc ưu tiên) không có câu hỏi riêng; chỉ phần còn để ngỏ (bộ ký tự, độ dài) thành RDM-001.

## 9. Mục 3 — Khác biệt theo module

- **Đơn vị "điểm khác biệt" = một bảng** `3.N`, đánh số liên tục toàn report theo thứ tự render. Template có 30 bảng = KPI 30.
- **Kind của bảng** (`added` / `modified` / `removed` → badge Thêm / Sửa / Bỏ) theo đối tượng mà nhãn bảng nêu: đối tượng mới — field, parameter, quy tắc, endpoint, loại tài nguyên — ⇒ Thêm (3.3 "Attach có thêm field bound" là Thêm dù có 3 dòng Giữ nguyên; 3.9–3.12); đối tượng đã có bị đổi ⇒ Sửa, kể cả khi đổi bằng cách thêm dòng/cột vào nó (3.4 thêm cột, 3.13, 3.15, 3.29 có dòng Thêm) hoặc đổi nghĩa qua chỗ nó dẫn chiếu mà mọi dòng Giữ nguyên (3.14, 3.28); đối tượng bị bỏ ⇒ Bỏ (3.7, 3.30). Kind của bảng là thứ được đếm.
- **Kind của dòng** (`added` / `removed` / `changed` / `unchanged`) độc lập với kind bảng. Dòng Giữ nguyên (chữ xám) được đưa vào khi cần ngữ cảnh: 3.3 giữ `type`/`id`/`count` để thấy `bound` đứng ở đâu; 3.14 giữ đủ 4 dòng để thấy câu chữ không đổi.
- **Cột**: `Thuộc tính` · `Bản cũ <short> (tr. N)` · `Bản mới <short> (tr. N)` · `Thay đổi`. Không có ⇒ "(không có)" ở tiêu đề cột và `—` ở ô.
- **Key của dòng**: `plainKey: true` chỉ cho nhãn do người audit tự đặt — "quy tắc", "mô tả", "ưu tiên 1", "ô của loại 5", kể cả nhãn có thuật ngữ English như "header Content-Type" (3.15). Mọi key chép từ nguồn là code (`plainKey: false`): tên field/parameter, tên cột của bảng nguồn (`Player holding limit`, `Description` — 3.4), JSON path (`list[0].id` — 3.30), token của lệnh (`curl`, `-d` — 3.15), type id (`2` — 3.5).
- **Ô**: các cặp `nhãn: giá trị` theo cột của bảng nguồn (`Field`/`Type`/`Description`, hoặc `type`/`Description`/`id`/`Player holding limit`/… cho bảng tham chiếu — 3.6); giá trị là quote nguyên văn. Dòng chỉ mang một giá trị đơn — một câu, một dòng lệnh, một tiêu đề cột — có ô không nhãn (`label: null`): 3.4, 3.13–3.15, 3.29–3.30. Ô khác giữa hai bản được tô (`changed: true`, class `cc`) — 3.2 chỉ tô `Description`.
- **Dịch nghĩa**: mọi giá trị không phải Anh/Việt kèm `gloss` (3.5, 3.8, 3.13).
- **Note** (cột Thay đổi): một câu tiếng Việt chữ thường mô tả chính xác điều đổi — "thêm field", "thêm đơn vị: (seconds)" (3.22), "Description: 元宝 → \"Bound Yuanbao\"; …" (3.8). Có thể trỏ bảng khác khi một dòng nguồn bị tách (3.5 ↔ 3.16). Bắt buộc cho dòng `changed`/`removed` (mọi bảng) và dòng `added` trong bảng Sửa (3.4, 3.13, 3.15, 3.29); tuỳ chọn cho dòng `added` trong bảng Thêm (có ở 3.3, 3.24; không có ở 3.9–3.12, 3.17–3.20); dòng `unchanged` chỉ có note khi cần giải thích vì sao giữ nó (3.4 `Description`, 3.14, 3.28).
- **Tag** "đối chiếu trực tiếp hai tài liệu": gắn cho bảng mà điểm khác biệt chỉ thấy được khi đặt hai tài liệu cạnh nhau, tài liệu mới không có dấu hiệu thay đổi nào (template: 3.16 — dòng type 2 thêm giới hạn nắm giữ, "Mail claim limit", Supports binding).
- **Ghi chú đầu module** `Không đổi: …` (`diffNote`) liệt kê phần không đổi của module có thay đổi, và vấn đề có ở cả hai bản: "Không đổi: mã lỗi 0, 1001–1004; quy tắc chung a–d (mục 1–4)." (System); Sensitive ghi lỗi ví dụ 00:00–06:00 có ở cả hai phiên bản. Endpoint không đổi liệt kê theo đuôi path, không backtick ("Không đổi: acct/ban, acct/unban, acct/ban-info, role/list-by-acct, role/kick." — Players; "Không đổi: create, update, del." — Sensitive); field vẫn backtick (Redeem: "`codes`, `code_prefix` hay `code_suffix_length`"). Bỏ `diffNote` khi module mới (Resources) hoặc mọi endpoint của module đều đổi (Mail — một endpoint, đã đổi).
- **Thứ tự bảng trong module**: các bảng nói về những phần rời nhau theo thứ tự trang của tài liệu mới (Resources 3.17–3.21, tr. 11–13; Redeem 3.23–3.28, tr. 18–20); các bảng cùng nói về một bảng nguồn đứng liền nhau thành một nhóm (Mail 3.4–3.13: bảng loại tài nguyên và quy tắc "Mail claim limit" phía trên nó); bảng mang tag đặt cuối module (3.16, dù nói về loại 2 của nhóm 3.4–3.13).
- **Gom theo chủ đề, không theo dòng nguồn**: một bảng = một nội dung có nghĩa (một field, một quy tắc, một nhóm dòng cùng bản chất). 3.10 gom các loại có giới hạn nắm giữ 1 (Title, Companion; Avatar frame được nhắc ở nhãn); 3.11/3.12 gom loại mới theo trang; 3.27 gom ba vế của quy tắc ưu tiên; 3.30 gom cả ví dụ response bị bỏ thành một bảng 12 dòng.
- **Cuối mục 3**: `Không thay đổi: <short> (<số endpoint>), …` — "Không thay đổi: Announcements (5 endpoint), Messages (1), Activation codes (3), Servers & server groups (10), Features (2)".

## 10. Footer — Ghi chú provenance

Liệt kê mọi giới hạn của nguồn ảnh hưởng tới cách đọc report (`meta.notes`):
- Bản được so là bản dịch hay bản gốc: "Bản gốc tiếng Trung của X5_GM20261010 chưa nhận được; báo cáo so sánh bản dịch tiếng Anh."
- Nguồn số trang: "Số trang bản cũ là số trang trong văn bản đã trích của X5_GM20260722 (chưa nhận PDF)."
- Nguồn không phải PDF ⇒ ghi số trang là trang ảo do `prepare_source.py` cắt (DATA.md §1).
