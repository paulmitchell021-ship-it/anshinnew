"""Kiem tra bai Claude vua soan. In ra cac slot KHONG dat (moi dong: slot<TAB>ly do). Exit 0 luon.
  python3 scripts/check.py 2026-11-09 1,2
"""
import pathlib, re, struct, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OFFICIAL = re.compile(r'https?://([a-z0-9-]+\.)*(go\.jp|lg\.jp|kyoukaikenpo\.or\.jp|nhk\.or\.jp|jasso\.go\.jp)/|https?://www\.(city|pref)\.[a-z0-9.-]+\.jp/')


def used_titles():
    t = (ROOT / 'nhat-ky-chu-de.md').read_text(encoding='utf-8')
    return {m.group(1).strip().upper() for m in re.finditer(r'^\| \d\d\.\d\d \| (.+?) \|$', t, re.M)}


def png_size(p):
    b = p.read_bytes()[:24]
    return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else (0, 0)


def check(date, slot, used):
    d = ROOT / 'posts' / date
    txt, png = d / f'bai-{slot}.txt', d / f'bai-{slot}.png'
    if not txt.exists() or not png.exists():
        return 'thiếu file'
    t = txt.read_text(encoding='utf-8').strip()
    first = t.split('\n')[0].strip()
    n = len(t)
    if n < 400 or n > 1500:
        return f'độ dài {n} ký tự (cần 400–1500)'
    if '✅ NÊN LÀM' not in t:
        return 'thiếu khung ✅ NÊN LÀM'
    if '💬' not in t or 'Comment' not in t:
        return 'thiếu câu kêu gọi 💬 Comment'
    if 'Nguồn' not in t:
        return 'thiếu dòng Nguồn'
    links = re.findall(r'https?://\S+', t)
    if not links:
        return 'thiếu link nguồn'
    if not any(OFFICIAL.match(l) for l in links):
        return 'không có link nguồn chính thức'
    if re.search(r'(^|\s)#\w', t) or '**' in t:
        return 'có hashtag hoặc markdown'
    if first.upper() in used:
        return 'trùng tiêu đề đã đăng'
    if png_size(png) != (1080, 1350):
        return f'ảnh sai kích thước {png_size(png)}'
    return None


if __name__ == '__main__':
    date, slots = sys.argv[1], sys.argv[2].split(',')
    used = used_titles()
    for s in slots:
        r = check(date, s, used)
        if r:
            print(f'{s}\t{r}')
