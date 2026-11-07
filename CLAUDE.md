# Anshin Care – content Telegram hằng ngày

Repo này tự soạn và đăng 2 bài mỗi ngày vào nhóm Telegram nội bộ "Anshin - Sale". Team sale lấy bài để đăng lại lên Facebook, Zalo, hội nhóm, nên bài phải đăng được ngay, không cần sửa.

Đối tượng đọc: người Việt sống, làm việc tại Nhật (thực tập sinh, kỹ năng đặc định, kỹ sư, du học sinh, gia đình).
Mục tiêu: tin hữu ích, chính xác, kéo khách về dịch vụ của Anshin Care: **hoàn thuế, nenkin, người phụ thuộc, thai sản, Kentaikyo (bảo hiểm xây dựng)**.

## Khi được gọi để soạn bài (skill `/soan-bai`)
Chỉ làm việc trong `posts/<ngày>/`. KHÔNG sửa `scripts/`, `state/`, `.github/`, `nhat-ky-chu-de.md`, `queue/`. KHÔNG chạy git, không gọi Telegram.

## Chọn chủ đề
1. Đọc `nhat-ky-chu-de.md`. KHÔNG lặp chủ đề đã đăng. Chỉ quay lại chủ đề cũ khi có tin mới thật sự, và nói rõ điểm mới.
2. **Bài 1 = tin chính sách mới** (nta.go.jp, nenkin.go.jp, mhlw.go.jp, moj.go.jp/isa, kentaikyo.taisyokukin.go.jp, trang tỉnh/thành phố *.lg.jp, NHK...). Chỉ dùng tin kiểm chứng được từ nguồn gốc. Không có tin đủ chắc thì viết bài kiến thức và ghi ngay câu đầu: "Đây là bài kiến thức vì tuần này chưa có tin chính sách mới đủ chắc."
3. **Bài 2 = kiến thức thực dụng theo mùa** hoặc sản phẩm (tháng 11–12: điều chỉnh thuế cuối năm, về Tết; tháng 1–3: gensen, tự khai thuế; tháng 4–6: tăng ca ảnh hưởng nenkin...). Xen kẽ sản phẩm: thai sản, Kentaikyo.
4. Mọi con số phải đối chiếu nguồn gốc (WebFetch trang chính thức). Đề xuất/thảo luận thì ghi "đang thảo luận, chưa quyết định". Nhận định riêng ghi "nhận định của Anshin Care". Không bịa câu chuyện khách; tình huống minh họa ghi rõ "tình huống minh họa".
5. Dòng Nguồn phải có **link gốc mở được** của trang chính thức Nhật (ít nhất 1 link .go.jp / .lg.jp hoặc cơ quan nhà nước).

## Văn phong bài (đúng mẫu kênh đã đăng)
600–1.200 ký tự. KHÔNG hashtag, KHÔNG markdown (không **, không #). Cấu trúc cố định:

```
<emoji> <TIÊU ĐỀ VIẾT HOA, có con số hoặc mốc ngày nếu có>
<1 đoạn 3–5 câu: chuyện gì, từ khi nào, ai bị ảnh hưởng, con số cụ thể. Giải thích từ Nhật trong ngoặc: nenmatsu chōsei, gensen, 厚生年金...>
✅ NÊN LÀM
• <việc 1>
• <việc 2>
• <việc 3>
💬 <Câu hỏi đúng đối tượng>? Comment "<TỪ KHÓA>" hoặc nhắn tin, Anshin Care kiểm tra giúp <dịch vụ> miễn phí.
Nguồn: <Tên cơ quan> (<ngày nếu có>):
<link 1>
;
<link 2>
```
- Xưng "anh chị em" hoặc "bạn", giọng thân thiện, câu ngắn. Đơn vị "man" (1 man = 10.000 yên) hoặc "yên".
- Từ khóa comment VIẾT HOA, ngắn, khớp chủ đề (NENKIN, KHAI THUẾ, TẾT, XÂY DỰNG...).
- Ví dụ chuẩn: `posts/2026-11-06/bai-1.txt`, `posts/2026-11-07/bai-2.txt`.

## Infographic (1080×1350, form cố định)
Viết spec `posts/<ngày>/bai-N.json` rồi chạy: `python3 tool/render.py posts/<ngày>/bai-N.json posts/<ngày>/bai-N.png`.
Mẫu: `tool/spec-mau-stats.json` (3 ô số liệu `stats`), `tool/spec-mau-cards.json` (2 ô `cards`, color "g" xanh lá / "r" đỏ, mỗi ô 3 gạch đầu dòng). Xem thêm các `posts/*/bai-*.json` đã dùng.
- badge: nhãn vàng góc phải, VIẾT HOA, ngắn (vd "ĐANG THẢO LUẬN · 30/10/2026", "TỪ 1/8/2026").
- kicker: dòng nhỏ VIẾT HOA trên tiêu đề (cơ quan · chủ đề).
- title_html: 2 dòng, dòng 2 màu vàng bọc `<span class='y'>...</span>`; ngắn, kiểu câu hỏi hoặc lời nhắc; title_size 86–92.
- stats: 3 ô, số ngắn (≤ 9 ký tự, vd "6,15 man", "320 yên", "12 tháng").
- tables: 1 bảng, 3–4 hàng; hàng đầu tô vàng (tắt bằng "hi_first": false); "kw" = độ rộng cột trái (330–420).
- note: 1–2 câu, nhãn in đậm bằng **...**.
- todo: đúng 4 việc, mỗi việc ≤ 30 ký tự.
- cta: "<Đối tượng>? Nhắn Anshin Care <động từ> **<dịch vụ>**."
- source: "Nguồn: <tên miền gốc> (<ngày>)".
Script báo "content bottom" phải ≤ 1230; nếu báo LỖI tràn chữ thì bớt hàng bảng/rút chữ rồi chạy lại. Luôn mở ảnh PNG xem lại (Read) trước khi kết thúc.

## Kết quả mỗi bài
`posts/<ngày>/bai-N.txt` (chữ đúng như sẽ đăng), `bai-N.json` (spec), `bai-N.png` (ảnh).
