"""Telegram Bot API helpers (chi dung thu vien chuan)."""
import json, os, pathlib, urllib.request, urllib.error, uuid

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
API = f'https://api.telegram.org/bot{TOKEN}'


class TgError(Exception):
    pass


def _post(method, fields=None, files=None, timeout=60):
    fields = fields or {}
    if files:
        b = uuid.uuid4().hex
        body = b''
        for k, v in fields.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)
            body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n'.encode() + str(v).encode('utf-8') + b'\r\n'
        for k, p in files.items():
            p = pathlib.Path(p)
            body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{p.name}"\r\nContent-Type: image/png\r\n\r\n'.encode() + p.read_bytes() + b'\r\n'
        body += f'--{b}--\r\n'.encode()
        headers = {'Content-Type': f'multipart/form-data; boundary={b}'}
    else:
        body = json.dumps(fields, ensure_ascii=False).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(f'{API}/{method}', data=body, headers=headers)
    try:
        r = json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        raise TgError(f'{method} HTTP {e.code}: {e.read().decode(errors="replace")[:300]}')
    if not r.get('ok'):
        raise TgError(f'{method}: {r}')
    return r['result']


def utf16_len(s):
    return len(s.encode('utf-16-le')) // 2


def send_message(chat, text, buttons=None, reply_to=None):
    f = {'chat_id': chat, 'text': text, 'disable_web_page_preview': True}
    if buttons:
        f['reply_markup'] = {'inline_keyboard': buttons}
    if reply_to:
        f['reply_parameters'] = {'message_id': reply_to}
    return _post('sendMessage', f)


def send_photo(chat, png, caption=None):
    f = {'chat_id': chat}
    if caption:
        f['caption'] = caption
    return _post('sendPhoto', f, files={'photo': png})


def send_post(chat, png, text):
    """Dang 1 bai: anh truoc, chu sau (giong bot cu). Chu ngan <=1024 thi gop lam caption."""
    if utf16_len(text) <= 1024:
        return [send_photo(chat, png, text)['message_id']]
    return [send_photo(chat, png)['message_id'], send_message(chat, text)['message_id']]


def get_updates(offset):
    return _post('getUpdates', {'offset': offset, 'timeout': 0, 'allowed_updates': ['callback_query', 'message']})


def answer_callback(cb_id, text):
    try:
        _post('answerCallbackQuery', {'callback_query_id': cb_id, 'text': text[:190]})
    except TgError:
        pass  # callback qua han (>15 phut) thi bo qua


def edit_buttons(chat, message_id, buttons):
    try:
        _post('editMessageReplyMarkup', {'chat_id': chat, 'message_id': message_id,
                                         'reply_markup': {'inline_keyboard': buttons}})
    except TgError:
        pass
