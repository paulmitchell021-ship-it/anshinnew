"""Render Anshin Care infographic (1080x1350) from a JSON spec. Usage: python render.py spec.json out.png"""
import json, sys, base64, html, re, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
LOGO = base64.b64encode((HERE / 'logo_w.png').read_bytes()).decode()

def rich(t):
    """**x** -> yellow bold; escapes rest."""
    t = html.escape(t)
    return re.sub(r'\*\*(.+?)\*\*', r'<b class="hl">\1</b>', t)

def lbl(t):
    t = html.escape(t)
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;font-family:'Inter',sans-serif;color:#13294b;background:#eef3fa;position:relative;overflow:hidden}
.top{position:absolute;left:0;top:0;width:1080px;height:440px;background:linear-gradient(120deg,#0a2a5e 0%,#0d3f8f 45%,#1668e3 100%)}
.wm{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.wm span{position:absolute;font-weight:800;font-size:30px;letter-spacing:2px;transform:rotate(-22deg);white-space:nowrap}
.wm img{position:absolute;opacity:.07}
.content{position:absolute;inset:0;padding:48px 64px 0 64px}
.hdr{display:flex;justify-content:space-between;align-items:flex-start}
.brand{display:flex;align-items:center;gap:14px}
.brand img{width:64px}
.brand b{display:block;color:#fff;font-size:30px;font-weight:800;letter-spacing:1.5px}
.brand small{display:block;color:#d6e4fb;font-size:17px;font-weight:500;margin-top:2px}
.badge{background:#ffc928;color:#0d2a5a;font-weight:800;font-size:23px;letter-spacing:1.2px;padding:13px 22px 13px 20px;border-radius:40px;margin-top:8px;display:flex;align-items:center;gap:10px;box-shadow:0 4px 14px rgba(0,0,0,.18)}
.badge i{width:9px;height:9px;border-radius:50%;background:#e53935;display:inline-block}
.kicker{color:#a9c8f5;font-weight:800;font-size:23px;letter-spacing:3.2px;margin-top:30px;text-transform:uppercase}
h1{font-weight:900;letter-spacing:-2px;line-height:1.06;margin-top:8px;color:#fff}
h1 .y{color:#ffc928}
.cards{display:flex;gap:20px;margin-top:22px}
.card{flex:1;background:#fff;border-radius:22px;padding:22px 26px;box-shadow:0 6px 22px rgba(13,42,90,.10);border-left:7px solid #1668e3}
.card.g{border-left-color:#1e9e4a}.card.r{border-left-color:#e53935}
.card h3{color:#1668e3;font-weight:800;font-size:22px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}
.card ul{padding-left:24px}.card li{font-size:22px;line-height:1.5;color:#1d2b45}
.stat{flex:1;background:#fff;border-radius:22px;padding:16px 14px 14px;text-align:center;box-shadow:0 6px 22px rgba(13,42,90,.10);border-left:6px solid #1668e3}
.stat b{display:block;font-size:44px;font-weight:900;color:#0d2a5a;letter-spacing:-1px}
.stat span{display:block;font-size:19px;color:#5b6b84;line-height:1.15;margin-top:2px}
.tbl{background:#fff;border-radius:22px;padding:18px;margin-top:18px;box-shadow:0 6px 22px rgba(13,42,90,.08)}
.th{display:flex;justify-content:space-between;background:#0d3270;color:#fff;font-weight:800;font-size:20px;letter-spacing:1.8px;padding:14px 22px;border-radius:12px 12px 0 0;text-transform:uppercase}
.tr{display:flex;align-items:center;padding:9px 22px;border-bottom:1px solid #e3e9f3;font-size:21px}
.tr:nth-child(odd){background:#f6f9fe}
.tr.hi{background:#fff6d6}
.tr .k{flex:0 0 var(--kw,330px);font-weight:800;color:#0d2a5a}
.tr .v{flex:1;color:#1d2b45;line-height:1.3}
.tr.hi .v{font-weight:800;color:#13294b}
.note{background:#fff;border-radius:22px;padding:20px 26px;margin-top:18px;font-size:20.5px;line-height:1.45;color:#1d2b45;box-shadow:0 6px 22px rgba(13,42,90,.08)}
.note b{color:#0d2a5a}
.todo{background:linear-gradient(120deg,#0b2c66,#11458f);border-radius:22px;padding:24px 30px;margin-top:18px}
.todo h3{color:#ffc928;font-weight:800;font-size:25px;letter-spacing:2.6px;margin-bottom:10px}
.todo .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px 30px}
.todo .it{display:flex;align-items:center;gap:14px;color:#fff;font-size:22px;font-weight:500}
.todo .n{flex:0 0 34px;height:34px;border-radius:8px;background:#ffc928;color:#0d2a5a;font-weight:900;font-size:19px;display:flex;align-items:center;justify-content:center}
.cta{background:#1a6fe8;border-radius:22px;padding:24px 32px;margin-top:16px;color:#fff;font-size:24.5px;font-weight:600}
.cta .hl{color:#ffd54a;font-weight:800}
.foot{position:absolute;left:0;bottom:0;width:1080px;height:96px;background:#0b2350;display:flex;align-items:center;justify-content:space-between;padding:0 64px}
.foot .l{display:flex;align-items:center;gap:14px}
.foot img{width:58px}
.foot b{display:block;color:#fff;font-size:27px;font-weight:800;letter-spacing:.5px}
.foot small{display:block;color:#c6d4ea;font-size:18px;margin-top:2px}
.foot .src{color:#c6d4ea;font-size:18px}
"""

def watermark():
    out = []
    for r in range(9):
        for c in range(4):
            x = c * 330 - 60 + (r % 2) * 160
            y = r * 165 - 30
            col = 'rgba(255,255,255,.07)' if y < 420 else 'rgba(13,42,90,.045)'
            out.append(f'<span style="left:{x}px;top:{y}px;color:{col}">ANSHIN CARE</span>')
    for x, y, s in [(560, 330, 150), (900, 330, 140), (60, 640, 130), (380, 600, 330), (820, 900, 140), (60, 1000, 130), (520, 1170, 120), (900, 1150, 120)]:
        out.append(f'<img src="data:image/png;base64,{LOGO}" style="left:{x}px;top:{y}px;width:{s}px">')
    return '<div class="wm">' + ''.join(out) + '</div>'

def build(s):
    p = []
    p.append(f'''<div class="hdr"><div class="brand"><img src="data:image/png;base64,{LOGO}"><div><b>ANSHIN CARE</b><small>Đồng hành cùng người Việt tại Nhật</small></div></div>
<div class="badge"><i></i>{html.escape(s["badge"])}</div></div>''')
    p.append(f'<div class="kicker">{html.escape(s["kicker"])}</div>')
    size = s.get('title_size', 92)
    lines = ''.join(f'<div>{l}</div>' for l in s['title_html'])
    p.append(f'<h1 style="font-size:{size}px">{lines}</h1>')
    if 'stats' in s:
        p.append('<div class="cards">' + ''.join(f'<div class="stat"><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>' for a, b in s['stats']) + '</div>')
    if 'cards' in s:
        p.append('<div class="cards">' + ''.join(
            f'<div class="card {c.get("color","")}"><h3>{html.escape(c["title"])}</h3><ul>' + ''.join(f'<li>{html.escape(i)}</li>' for i in c['items']) + '</ul></div>'
            for c in s['cards']) + '</div>')
    for t in s.get('tables', []):
        rows = ''.join(f'<div class="tr {"hi" if i == 0 and t.get("hi_first", True) else ""}"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}</div></div>' for i, (k, v) in enumerate(t['rows']))
        p.append(f'<div class="tbl" style="--kw:{t.get("kw",330)}px"><div class="th"><span>{html.escape(t["h"][0])}</span><span>{html.escape(t["h"][1])}</span></div>{rows}</div>')
    if 'note' in s:
        p.append(f'<div class="note">{lbl(s["note"])}</div>')
    items = ''.join(f'<div class="it"><span class="n">{i+1}</span>{html.escape(x)}</div>' for i, x in enumerate(s['todo']))
    p.append(f'<div class="todo"><h3>{html.escape(s.get("todo_title","NÊN LÀM"))}</h3><div class="grid">{items}</div></div>')
    p.append(f'<div class="cta">{rich(s["cta"])}</div>')
    foot = f'''<div class="foot"><div class="l"><img src="data:image/png;base64,{LOGO}"><div><b>anshin.vn</b><small>Nenkin · Hoàn thuế · Trợ cấp</small></div></div><div class="src">{html.escape(s["source"])}</div></div>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="top"></div>{watermark()}<div class="content">{"".join(p)}</div>{foot}</body></html>'

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    out = sys.argv[2]
    doc = build(spec)
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        pg.set_content(doc); pg.wait_for_timeout(300)
        # overflow check: content bottom must stay above footer
        bottom = pg.evaluate("Math.max(...[...document.querySelectorAll('.content > *')].map(e=>e.getBoundingClientRect().bottom))")
        print('content bottom', round(bottom), '(limit 1230)')
        pg.screenshot(path=out); b.close()
        if bottom > 1230:
            print('LOI: chu bi tran xuong chan trang. Rut ngan chu hoac bot hang bang roi chay lai.')
            sys.exit(2)
