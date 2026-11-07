---
name: soan-bai
description: Soạn bài content Anshin Care cho một ngày (chữ + infographic) theo CLAUDE.md. Dùng khi workflow soan-bai gọi với ngày, các bài cần soạn và chủ đề cần tránh.
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Bash(python3 tool/render.py:*)
---

Tham số: `$ARGUMENTS` có dạng `NGAY=YYYY-MM-DD BAI=1,2 TRANH=<tiêu đề bị từ chối, cách nhau bởi |>`.

1. Đọc `CLAUDE.md` (quy tắc), `nhat-ky-chu-de.md` (chủ đề đã đăng), và 2 bài mẫu trong `posts/2026-11-07/`.
2. Nếu đang soạn lại (có TRANH): tránh hẳn các chủ đề trong TRANH, chọn hướng khác.
3. Nếu chỉ soạn 1 bài thì đọc bài còn lại của cùng ngày (nếu có) để 2 bài không trùng nhau.
4. Với mỗi bài trong BAI:
   a. Tìm tin (WebSearch), mở trang gốc (WebFetch) để kiểm chứng từng con số.
   b. Viết `posts/NGAY/bai-N.txt` đúng văn phong trong CLAUDE.md.
   c. Viết `posts/NGAY/bai-N.json` theo mẫu, chạy `python3 tool/render.py posts/NGAY/bai-N.json posts/NGAY/bai-N.png`, sửa đến khi không còn lỗi tràn chữ.
   d. Mở ảnh PNG xem lại; chữ bị vỡ dòng xấu thì sửa spec và render lại.
5. Kết thúc bằng 1 dòng cho mỗi bài: `BÀI N: <tiêu đề> | nguồn: <link chính>`.
