"""Quy trinh duyet va dang bai Anshin Care.

  python3 scripts/review.py tick              # 20:00-23:45: gui nhap, nhan nut duyet, tu duyet sau 1h, goi soan lai
  python3 scripts/review.py publish [DATE]    # 08:00: dang bai da duyet vao nhom sale
  python3 scripts/review.py status [DATE]     # in trang thai

Bien moi truong: TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID (nhom sale), TELEGRAM_REVIEW_CHAT_ID (nhom duyet),
REVIEWERS (user id cach nhau boi dau phay; trong = ai trong nhom duyet cung bam duoc),
GITHUB_REPOSITORY, GH_TOKEN (de goi lai workflow soan-bai), DRY_RUN=1 (khong goi Telegram/GitHub).
"""
import datetime as dt, json, os, pathlib, re, shutil, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import tg  # noqa: E402

VN = dt.timezone(dt.timedelta(hours=7))
REVIEW_MINUTES = 60
REVIEW_OPEN_HOUR = 20          # gui nhap tu 20:00 toi hom truoc
MAX_REDO = 3                   # moi bai toi da soan lai 3 lan, sau do dung bai du phong
GROUP = os.environ.get('TELEGRAM_GROUP_ID', '')
REVIEW = os.environ.get('TELEGRAM_REVIEW_CHAT_ID', '')
REVIEWERS = {x.strip() for x in os.environ.get('REVIEWERS', '').split(',') if x.strip()}
DRY = os.environ.get('DRY_RUN') == '1'
SLOTS = ('1', '2')


def now():
    o = os.environ.get('FAKE_NOW')  # de kiem thu: 2026-11-08T20:05
    return dt.datetime.fromisoformat(o).replace(tzinfo=VN) if o else dt.datetime.now(VN)


def ddmm(date):
    return f'{date[8:10]}/{date[5:7]}'


# ---------- trang thai ----------
def state_path(date):
    return ROOT / 'state' / f'{date}.json'


def load(date):
    p = state_path(date)
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return {'date': date, 'posts': {s: {'status': 'new', 'version': 1} for s in SLOTS}, 'rejected': [], 'log': []}


def save(st):
    p = state_path(st['date'])
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding='utf-8')


def log(st, msg):
    st['log'].append(f'{now():%Y-%m-%d %H:%M} {msg}')
    print(f'[{st["date"]}] {msg}')


def post_files(date, slot):
    d = ROOT / 'posts' / date
    return d / f'bai-{slot}.png', d / f'bai-{slot}.txt'


def has_files(date, slot):
    png, txt = post_files(date, slot)
    return png.exists() and txt.exists()


def title_of(date, slot):
    _, txt = post_files(date, slot)
    return txt.read_text(encoding='utf-8').strip().split('\n')[0].strip() if txt.exists() else ''


# ---------- Telegram (co che do DRY_RUN) ----------
def T(fn, *a, **k):
    if DRY:
        print('  DRY', fn.__name__, [str(x)[:60] for x in a])
        return {'message_id': 0} if fn is not tg.send_post else [0]
    return fn(*a, **k)


def notify(text):
    if REVIEW:
        try:
            T(tg.send_message, REVIEW, text)
        except tg.TgError as e:
            print('notify loi', e)


def buttons(date, slot, ver):
    return [[{'text': '✅ Duyệt', 'callback_data': f'ok:{date}:{slot}:{ver}'},
             {'text': '🔄 Làm bài khác', 'callback_data': f'redo:{date}:{slot}:{ver}'}]]


def done_button(label):
    return [[{'text': label, 'callback_data': 'noop'}]]


# ---------- cac buoc ----------
def send_draft(st, slot):
    p = st['posts'][slot]
    png, txt = post_files(st['date'], slot)
    deadline = now() + dt.timedelta(minutes=REVIEW_MINUTES)
    head = (f'📝 NHÁP BÀI {slot} · đăng 8:00 ngày {ddmm(st["date"])}'
            f'{" · bản làm lại " + str(p["version"] - 1) if p["version"] > 1 else ""}\n'
            f'Không ai bấm thì tự duyệt lúc {deadline:%H:%M}.\n\n')
    T(tg.send_photo, REVIEW, png)
    m = T(tg.send_message, REVIEW, head + txt.read_text(encoding='utf-8'), buttons(st['date'], slot, p['version']))
    p.update(status='draft_sent', sent_at=now().isoformat(), deadline=deadline.isoformat(),
             msg_id=m['message_id'], title=title_of(st['date'], slot))
    log(st, f'gui nhap bai {slot} v{p["version"]}, han {deadline:%H:%M}')


def dispatch_regen(st, slots):
    repo, token = os.environ.get('GITHUB_REPOSITORY'), os.environ.get('GH_TOKEN')
    avoid = ' | '.join(st['rejected'])[-900:]
    body = json.dumps({'ref': os.environ.get('GITHUB_REF_NAME', 'main'),
                       'inputs': {'date': st['date'], 'slots': ','.join(slots), 'avoid': avoid}}).encode()
    if DRY or not (repo and token):
        print('  DRY dispatch soan-bai', st['date'], slots, avoid[:80])
        return
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/actions/workflows/soan-bai.yml/dispatches',
                                 data=body, method='POST',
                                 headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'})
    urllib.request.urlopen(req, timeout=30)


def use_queue(st, slot, reason, status='approved'):
    q = sorted(x for x in (ROOT / 'queue').iterdir() if x.is_dir()) if (ROOT / 'queue').exists() else []
    if not q:
        log(st, f'bai {slot}: HET bai du phong ({reason})')
        notify(f'⚠️ Bài {slot} ngày {ddmm(st["date"])}: {reason}, nhưng kho bài dự phòng đã hết. Bài này sẽ không được đăng.')
        return False
    src = q[0]
    dst = ROOT / 'posts' / st['date']
    dst.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'txt', 'json'):
        f = src / f'bai.{ext}'
        if f.exists():
            shutil.copy(f, dst / f'bai-{slot}.{ext}')
    shutil.rmtree(src)
    st['posts'][slot].update(status=status, source=f'queue/{src.name}', title=title_of(st['date'], slot))
    log(st, f'bai {slot}: dung bai du phong {src.name} ({reason})')
    return True


def handle_updates(touched):
    offp = ROOT / 'state' / 'tg-offset.txt'
    offset = int(offp.read_text()) if offp.exists() else 0
    if DRY:
        return
    try:
        ups = tg.get_updates(offset)
    except tg.TgError as e:
        print('getUpdates loi', e)
        return
    for u in ups:
        offset = u['update_id'] + 1
        cb = u.get('callback_query')
        msg = u.get('message')
        if msg and str(msg.get('chat', {}).get('id')) == REVIEW and (msg.get('text') or '').startswith('/trangthai'):
            d = (now() + dt.timedelta(days=1 if now().hour >= 12 else 0)).strftime('%Y-%m-%d')
            tg.send_message(REVIEW, status_text(d))
            continue
        if not cb or cb.get('data', 'noop') == 'noop':
            if cb:
                tg.answer_callback(cb['id'], 'Đã xử lý rồi.')
            continue
        who = cb['from']
        name = who.get('first_name', '') + (' ' + who.get('last_name', '') if who.get('last_name') else '')
        if REVIEWERS and str(who['id']) not in REVIEWERS:
            tg.answer_callback(cb['id'], 'Bạn không có quyền duyệt bài.')
            continue
        try:
            action, date, slot, ver = cb['data'].split(':')
        except ValueError:
            continue
        st = touched.setdefault(date, load(date))
        p = st['posts'].get(slot)
        if not p or str(p.get('version')) != ver or p.get('status') != 'draft_sent':
            tg.answer_callback(cb['id'], 'Bản nháp này đã cũ hoặc đã xử lý.')
            continue
        chat = cb['message']['chat']['id']
        if action == 'ok':
            p.update(status='approved', by=name)
            tg.edit_buttons(chat, cb['message']['message_id'], done_button(f'✅ Đã duyệt · {name}'))
            tg.answer_callback(cb['id'], 'Đã duyệt. Bài sẽ đăng lúc 8:00.')
            log(st, f'bai {slot} duoc duyet boi {name}')
        elif action == 'redo':
            st['rejected'].append(p.get('title', ''))
            p.update(status='redo_requested', by=name)
            tg.edit_buttons(chat, cb['message']['message_id'], done_button(f'🔄 Đang làm bài khác · {name}'))
            tg.answer_callback(cb['id'], 'Đang soạn bài khác, khoảng 10–20 phút sẽ có bản nháp mới.')
            log(st, f'bai {slot} bi tu choi boi {name}')
    offp.write_text(str(offset))


def tick():
    touched = {}
    handle_updates(touched)
    n = now()
    target = (n + dt.timedelta(days=1 if n.hour >= 12 else 0)).strftime('%Y-%m-%d')
    st = touched.setdefault(target, load(target))
    review_open = n.hour >= REVIEW_OPEN_HOUR or n.hour < 8
    regen = []
    for s in SLOTS:
        p = st['posts'][s]
        if p['status'] in ('new', 'ready') and has_files(target, s) and review_open and REVIEW:
            send_draft(st, s)
        elif p['status'] == 'draft_sent' and n >= dt.datetime.fromisoformat(p['deadline']):
            p.update(status='auto_approved')
            if p.get('msg_id'):
                T(tg.edit_buttons, REVIEW, p['msg_id'], done_button('🤖 Tự duyệt (hết 1 giờ)'))
            log(st, f'bai {s} tu duyet')
            notify(f'🤖 Bài {s} ngày {ddmm(target)} đã tự duyệt vì sau 1 giờ không ai thao tác. Bài sẽ đăng lúc 8:00.')
        elif p['status'] == 'redo_requested':
            if p['version'] >= MAX_REDO + 1:
                use_queue(st, s, f'đã làm lại {MAX_REDO} lần')
            else:
                p.update(status='regenerating', version=p['version'] + 1)
                regen.append(s)
    if regen:
        dispatch_regen(st, regen)
        log(st, f'goi soan lai bai {",".join(regen)}')
    for d in touched.values():
        save(d)


def append_log_rows(date, titles):
    p = ROOT / 'nhat-ky-chu-de.md'
    lines = p.read_text(encoding='utf-8').split('\n')
    idx = max(i for i, l in enumerate(lines) if re.match(r'^\| \d\d\.\d\d \|', l))
    for t in reversed(titles):
        lines.insert(idx + 1, f'| {date[8:10]}.{date[5:7]} | {t} |')
    p.write_text('\n'.join(lines), encoding='utf-8')


def publish(date=None):
    touched = {}
    handle_updates(touched)
    date = date or now().strftime('%Y-%m-%d')
    st = touched.setdefault(date, load(date))
    sent, titles = [], []
    for s in SLOTS:
        p = st['posts'][s]
        if p['status'] == 'published':
            continue
        if p['status'] in ('redo_requested', 'regenerating') or not has_files(date, s):
            if not use_queue(st, s, 'chưa có bài đạt' if has_files(date, s) else 'chưa soạn được bài'):
                continue
        png, txt = post_files(date, s)
        try:
            T(tg.send_post, GROUP, png, txt.read_text(encoding='utf-8'))
        except tg.TgError as e:
            log(st, f'bai {s} LOI dang: {e}')
            notify(f'❌ Đăng bài {s} ngày {ddmm(date)} lỗi: {e}')
            continue
        how = {'approved': 'đã duyệt', 'auto_approved': 'tự duyệt'}.get(p['status'], 'tự duyệt')
        p.update(status='published', published_at=now().isoformat())
        t = title_of(date, s)
        sent.append(f'• Bài {s} ({how}{", bài dự phòng" if p.get("source", "").startswith("queue") else ""}): {t[:80]}')
        titles.append(t)
        log(st, f'da dang bai {s}')
    if titles:
        append_log_rows(date, titles)
        notify(f'📣 Đã đăng {len(titles)} bài vào nhóm sale ngày {ddmm(date)}:\n' + '\n'.join(sent))
    save(st)
    for d in touched.values():
        if d is not st:
            save(d)


def status_text(date):
    st = load(date)
    names = {'new': 'chưa soạn', 'ready': 'đã soạn, chờ 20:00', 'draft_sent': 'đang chờ duyệt',
             'approved': 'đã duyệt', 'auto_approved': 'tự duyệt', 'redo_requested': 'chờ làm lại',
             'regenerating': 'đang làm lại', 'published': 'đã đăng'}
    rows = [f'Bài {s}: {names.get(p["status"], p["status"])} · {title_of(date, s)[:60]}' for s, p in st['posts'].items()]
    return f'📋 Trạng thái bài ngày {ddmm(date)}\n' + '\n'.join(rows)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'tick'
    if cmd == 'tick':
        tick()
    elif cmd == 'publish':
        publish(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == 'status':
        print(status_text(sys.argv[2] if len(sys.argv) > 2 else (now() + dt.timedelta(days=1)).strftime('%Y-%m-%d')))
    elif cmd == 'fallback':  # bai soan loi kiem tra: date slot ly-do -> lay bai du phong, van gui duyet
        st = load(sys.argv[2])
        use_queue(st, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'soạn tự động lỗi', status='ready')
        notify(f'⚠️ Bài {sys.argv[3]} ngày {ddmm(sys.argv[2])}: soạn tự động không đạt kiểm tra, đã thay bằng bài dự phòng.')
        save(st)
    elif cmd == 'mark-ready':  # goi sau khi soan xong: date slots
        st = load(sys.argv[2])
        for s in sys.argv[3].split(','):
            if has_files(st['date'], s) and st['posts'][s]['status'] in ('new', 'regenerating'):
                st['posts'][s]['status'] = 'ready'
                log(st, f'bai {s} v{st["posts"][s]["version"]} da soan xong')
        save(st)
