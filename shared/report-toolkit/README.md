# report-toolkit — toolkit report dùng chung

Nhập từ `.claude/skills/api-docs/` của repo Project-X3-GDD (gốc của toolkit là report audit API; các ví dụ X5 GM API trong `audit-standard.md`, `DATA.md` và template giữ nguyên làm mẫu). Không phải skill. Đây là chuẩn, template và script report mà skill dưới đây dùng:

| Skill | Agent | Việc |
|---|---|---|
| `/gdd-review` | `gdd-review` | GDD → report câu hỏi cho Game Design theo template; luật và category riêng (`skills/gdd-review/review-standard.md` + `profile.json`), dùng `meta.labels` · `evidence[].loc` · `validate_audit.py --profile` |

Main session chạy skill trực tiếp (không Workflow): chuẩn bị nguồn và chạy script tự làm, phần phán đoán giao cho agent cùng tên qua Agent tool.

## Thành phần

| Phần | Vai |
|---|---|
| `audit-standard.md` | Chuẩn viết report: module, câu hỏi (title/issue/evidence/ask), category đóng, priority, diff, KPI |
| `DATA.md` | Format dữ liệu dùng chung giữa script và agent |
| `templates/audit-report.html` | Report mẫu (X5 GM API 20260722 → 20261010); renderer lấy CSS từ đây |
| `scripts/prepare_source.py` | PDF/MD/HTML/DOCX → text theo trang (`pdftotext -raw` cho PDF); nhiều `--in` `.md`/`.txt` → một nguồn |
| `scripts/resolve_votes.py` | Candidate của một unit + verdict của hai verifier → `verified-<unit>.json` (giữ · bác bỏ · chưa đủ verify) |
| `scripts/assemble_audit.py` · `validate_audit.py` · `render_audit.py` | Fragment → `audit.json` → kiểm literal quote → HTML |

Script chạy bằng `python3 -I` (stdlib, Python 3.9). Đổi format dữ liệu ⇒ sửa `DATA.md`, script và vai trong `agents/gdd-review.md` trong cùng change.
