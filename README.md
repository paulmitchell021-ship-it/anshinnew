# Anshin Care – content Telegram tự động

Mỗi ngày hệ thống tự soạn 2 bài (chữ + infographic), gửi bản nháp vào nhóm duyệt lúc 20:00 tối hôm trước, rồi đăng vào nhóm "Anshin - Sale" lúc 8:00. Mọi thứ chạy trên GitHub Actions; phần soạn bài dùng Claude Code với gói Claude của công ty (không dùng API).

## Lịch chạy (giờ Việt Nam)
| Giờ | Workflow | Việc |
|---|---|---|
| 19:07 | `soan-bai` | Claude soạn 2 bài cho ngày mai, kiểm tra tự động; bài lỗi thì thay bằng bài dự phòng trong `queue/` |
| 20:02 → 23:47, 15 phút/lần | `duyet` | Gửi nháp vào nhóm duyệt, nhận nút **✅ Duyệt** / **🔄 Làm bài khác**, sau 1 giờ không ai thao tác thì **tự duyệt** |
| khi bấm 🔄 | `soan-bai` (gọi lại) | Soạn bài khác tránh chủ đề bị từ chối, gửi nháp mới với 1 giờ chờ mới (tối đa 3 lần, sau đó dùng bài dự phòng) |
| 07:38 → đúng 08:00 | `dang-bai` | Đăng bài đã duyệt / tự duyệt vào nhóm sale, ghi `nhat-ky-chu-de.md`, báo kết quả vào nhóm duyệt |
| 08:20 | `dang-bai` | Chạy bù nếu lần 8:00 bị trễ hoặc lỗi (không đăng trùng) |

Lịch của GitHub có thể trễ vài phút đến 15–30 phút; bấm nút trong nhóm duyệt có thể mất tới ~15 phút bot mới phản hồi. Gõ `/trangthai` trong nhóm duyệt để xem trạng thái bài ngày mai.

## Cài đặt một lần
**Secrets** (Settings → Secrets and variables → Actions → New repository secret):

| Tên | Giá trị |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | Mã từ lệnh `claude setup-token` (đăng nhập tài khoản Claude trả phí của công ty) |
| `TELEGRAM_BOT_TOKEN` | Token bot @Anshincontent_bot (lấy ở @BotFather) |
| `TELEGRAM_GROUP_ID` | ID nhóm "Anshin - Sale" (dạng `-100…`) |
| `TELEGRAM_REVIEW_CHAT_ID` | ID nhóm duyệt bài (dạng `-100…` hoặc `-…`) |
| `REVIEWERS` | ID Telegram của người được duyệt, cách nhau bởi dấu phẩy (để trống = ai trong nhóm duyệt cũng bấm được) |

**Quyền workflow:** Settings → Actions → General → Workflow permissions → chọn **Read and write permissions** → Save.

## Thư mục
- `CLAUDE.md`: quy tắc chọn chủ đề, văn phong, form infographic (Claude đọc mỗi lần soạn).
- `.claude/skills/soan-bai/`: các bước soạn bài.
- `nhat-ky-chu-de.md`: toàn bộ tiêu đề đã đăng, để không trùng.
- `posts/YYYY-MM-DD/`: bài từng ngày (`bai-N.txt`, `bai-N.json`, `bai-N.png`).
- `queue/`: bài dự phòng (mỗi thư mục 1 bài: `bai.txt`, `bai.png`). Nên giữ ít nhất 2 bài.
- `state/`: trạng thái duyệt từng ngày.
- `scripts/`: `review.py` (duyệt, đăng), `check.py` (kiểm tra bài), `tg.py` (Telegram).
- `tool/`: `render.py` + logo + font để vẽ infographic.

## Chạy tay khi cần
Actions → chọn workflow → **Run workflow**:
- `soan-bai`: nhập ngày và bài cần soạn (vd `1` hoặc `1,2`).
- `dang-bai`: đăng ngay bài của một ngày (đã đăng thì không đăng lại).

Font Inter (SIL Open Font License) trong `tool/fonts/`.
