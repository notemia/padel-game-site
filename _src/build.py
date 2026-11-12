#!/usr/bin/env python3
"""Builds padel-game.fun: one landing page, privacy, support and terms per language.

Run:  python3 _src/build.py   (from the repo root)
Site copy lives in lang_*.py. Shot names and the disclaimer come from the app's
own strings, so the site says exactly what the app says.
"""
import glob, hashlib, html, importlib, json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)                    # repo root, served as the site
APP = os.environ.get('PADL_APP', '/Users/vladimir/claude/Padl')
sys.path.insert(0, HERE)

BASE = 'https://padel-game.fun/'
MAIL = 'mailto:helpyoutofeel@gmail.com'
EULA = 'https://www.apple.com/legal/internet-services/itunes/dev/stdeula/'
# Paste the App Store address here once the app is live: the hero button then leads to the store.
STORE_URL = ''

# code, folder, hreflang, og:locale, App Store locale, app strings key, native name
LANGS = [
    ('en',   '',       'en',      'en_US', 'en-US',   'en',      'English'),
    ('es',   'es/',    'es',      'es_ES', 'es-ES',   'es',      'Español'),
    ('ru',   'ru/',    'ru',      'ru_RU', 'ru',      'ru',      'Русский'),
    ('it',   'it/',    'it',      'it_IT', 'it',      'it',      'Italiano'),
    ('de',   'de/',    'de',      'de_DE', 'de-DE',   'de',      'Deutsch'),
    ('fr',   'fr/',    'fr',      'fr_FR', 'fr-FR',   'fr',      'Français'),
    ('ptbr', 'pt-br/', 'pt-BR',   'pt_BR', 'pt-BR',   'pt-BR',   'Português (Brasil)'),
    ('pt',   'pt/',    'pt-PT',   'pt_PT', 'pt-PT',   'pt-PT',   'Português (Portugal)'),
    ('nl',   'nl/',    'nl',      'nl_NL', 'nl-NL',   'nl',      'Nederlands'),
    ('sv',   'sv/',    'sv',      'sv_SE', 'sv',      'sv',      'Svenska'),
    ('ar',   'ar/',    'ar',      'ar_SA', 'ar-SA',   'ar',      'العربية'),
    ('zh',   'zh/',    'zh-Hans', 'zh_CN', 'zh-Hans', 'zh-Hans', '简体中文'),
    ('ja',   'ja/',    'ja',      'ja_JP', 'ja',      'ja',      '日本語'),
    ('ko',   'ko/',    'ko',      'ko_KR', 'ko',      'ko',      '한국어'),
]
PAGES = ('', 'privacy.html', 'support.html', 'terms.html')

e = lambda s: html.escape(s, quote=False)
a = lambda s: html.escape(s, quote=True)

# ---- The app's own strings. Russian, English and Spanish sit inline in the Swift code;
# every other language is a table keyed by the English string.
_Q = r'"((?:[^"\\]|\\.)*)"'
_LT = re.compile(r'L\.t\(\s*' + _Q + r'\s*,\s*' + _Q + r'\s*,\s*' + _Q + r'\s*\)')
_un = lambda s: s.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
INLINE = {'ru': {}, 'es': {}}
SWIFT = {}
for path in glob.glob(os.path.join(APP, 'Padl', '**', '*.swift'), recursive=True):
    SWIFT[os.path.basename(path)] = src = open(path, encoding='utf-8').read()
    for ru, en, es in _LT.findall(src):
        INLINE['ru'][_un(en)] = _un(ru)
        INLINE['es'][_un(en)] = _un(es)
TABLES = {}

def app(en, key):
    """The app's wording of an English string in the given language."""
    if key == 'en':
        return en
    if key in INLINE:
        return INLINE[key][en]
    if key not in TABLES:
        TABLES[key] = json.load(open(os.path.join(APP, 'Padl', 'Resources', 'Loc', f'loc_{key}.json'), encoding='utf-8'))
    return TABLES[key][en]


SHOTS = [_un(m[1]) for m in re.findall(r'name:\s*L\.t\(\s*' + _Q + r'\s*,\s*' + _Q, SWIFT['ShotLibrary.swift'])]
assert len(SHOTS) == 13, SHOTS
DISCLAIMER = next(k for k in INLINE['ru'] if k.startswith('Padl is an educational and entertainment app.'))

def store_name(store):
    with open(os.path.join(APP, 'fastlane', 'metadata', store, 'name.txt'), encoding='utf-8') as f:
        return f.read().strip()

def asset(name):
    """Asset address tied to the file's content: Cloudflare lets browsers keep files for hours."""
    with open(os.path.join(SITE, name), 'rb') as f:
        return f'/{name}?v={hashlib.md5(f.read()).hexdigest()[:8]}'

def alternates(page=''):
    alt = ''.join(f'<link rel="alternate" hreflang="{h}" href="{BASE}{f}{page}">\n' for _, f, h, *_ in LANGS)
    return alt + f'<link rel="alternate" hreflang="x-default" href="{BASE}{page}">\n'

def head_tags(url, L, title, desc, page=''):
    code, folder, hl, ogl, store, key, native = L
    rtl = ' dir="rtl"' if code == 'ar' else ''
    return f"""<!doctype html>
<html lang="{hl}"{rtl}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{a(desc)}">
<link rel="canonical" href="{url}">
{alternates(page)}<meta name="theme-color" content="#2468d8">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{a(store_name(store))}">
<meta property="og:title" content="{a(title)}">
<meta property="og:description" content="{a(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="{ogl}">
<link rel="icon" href="{asset('favicon.ico')}" sizes="any">
<link rel="icon" href="{asset('assets/favicon-32.png')}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{asset('assets/icon-180.png')}">
<link rel="stylesheet" href="{asset('style.css')}">
"""

def lang_menu(code, page=''):
    return ''.join(f'<a href="/{f2}{page}" hreflang="{h2}" lang="{h2}"' + (' aria-current="true"' if c2 == code else '') + f'>{n2}</a>'
                   for c2, f2, h2, _o, _s, _k, n2 in LANGS)

def header(L, d, page=''):
    code, folder, hl, ogl, store, key, native = L
    return f"""<header class="top">
  <a class="brand" href="/{folder}"><img src="{asset('assets/icon-64.png')}" alt="" width="32" height="32"><span>{e(store_name(store))}</span></a>
  <nav><a href="/{folder}support.html">{e(d['foot_support'])}</a><a href="/{folder}privacy.html">{e(d['foot_privacy'])}</a>
  <details class="langs"><summary aria-label="{a(d['lang_label'])}">{e(native)}</summary><div>{lang_menu(code, page)}</div></details></nav>
</header>
"""

def footer(L, d):
    folder = L[1]
    return f"""<footer>
  <small>{e(d['foot'])}<br>© 2026 Vladimir Dyagay</small>
  <nav><a href="/{folder}terms.html">{e(d['foot_terms'])}</a><a href="/{folder}support.html">{e(d['foot_support'])}</a><a href="/{folder}privacy.html">{e(d['foot_privacy'])}</a><a href="https://notemia.app/">Notemia apps</a></nav>
</footer>
<script src="{asset('app.js')}"></script>
</body>
</html>
"""

SHOT_FILES = ('match', 'shot', 'rally', 'home')
# Names of the app's own screens and buttons, written in the copy as {home}, {settings} and so on.
UI = {'home': 'Home', 'start': 'New to padel? Start here', 'match': 'Play a 3D match', 'settings': 'Settings',
      'language': 'Language', 'score': 'Score', 'startmatch': 'Start match', 'restore': 'Restore purchases'}
def ui(text, key):
    for token, en in UI.items():
        text = text.replace('{' + token + '}', app(en, key))
    assert '{' not in text, text
    return text

def build(L, d):
    code, folder, hl, ogl, store, key, native = L
    url = BASE + folder
    if STORE_URL:
        cta = f'<a class="btn" href="{a(STORE_URL)}">{e(d["cta_store"])}</a>'
    else:
        mail = MAIL + '?subject=' + urllib.parse.quote(d['notify_subject'], safe='')
        cta = f'<a class="btn" href="{a(mail)}">{e(d["cta"])}</a>'
    ld = json.dumps({"@context": "https://schema.org", "@type": "MobileApplication", "name": store_name(store),
                     "alternateName": "Padl", "url": url, "inLanguage": hl, "description": d['desc'],
                     "applicationSubCategory": "Padel lessons and 3D match", "operatingSystem": "iOS 18 or later",
                     "applicationCategory": "SportsApplication", "image": BASE + "assets/icon.png",
                     "screenshot": [BASE + f"assets/s/{store}-match.webp"],
                     "author": {"@type": "Person", "name": "Vladimir Dyagay"}}, ensure_ascii=False).replace('</', '<\\/')
    who = ''.join(f'<div><dt>{e(t)}</dt><dd>{e(p)}</dd></div>' for t, p in d['who'])
    shots = [asset(f'assets/s/{store}-{n}.webp') for n in SHOT_FILES]
    items = ''.join(
        f'<li><button type="button" data-shot="{a(src)}"' + (' aria-current="true"' if i == 0 else '') +
        f'><b>{e(t)}</b><span>{e(p)}</span></button></li>'
        for i, ((t, p), src) in enumerate(zip(d['items'], shots)))
    sep = '、' if code in ('zh', 'ja') else '، ' if code == 'ar' else ', '
    names = sep.join(app(s, key) for s in SHOTS)
    pad = d['pad']
    return head_tags(url, L, d['title'], d['desc']) + f"""<script type="application/ld+json">{ld}</script>
</head>
<body>
{header(L, d)}
<main>
<div class="hero">
  <h1><span>{e(d['h1a'])}</span>{e(d['h1b'])}</h1>
  <div class="pitch">
    <p>{e(d['short'])}</p>
    {cta}
  </div>
  <video data-loop muted loop playsinline preload="metadata" poster="{asset(f'assets/v/{store}.jpg')}" aria-label="{a(d['hero_aria'])}" width="590" height="1278"><source src="{asset(f'assets/v/{store}.mp4')}" type="video/mp4"></video>
</div>
<section class="why">
  <div class="why-in">
    <div class="why-text">
      <h2>{e(d['why_h'])}</h2>
      <p>{e(d['sub'])}</p>
      <p>{e(d['sub2'])}</p>
    </div>
    <figure class="try">
      <figcaption>{e(d['t_try'])}</figcaption>
      <div class="deck" id="deck" dir="ltr">
        <svg viewBox="0 0 520 230" aria-hidden="true">
          <rect class="turf" x="20" y="200" width="480" height="30"/>
          <path class="glass" d="M20 200V128M500 200V128"/><path class="mesh" d="M20 128V104M500 128V104"/>
          <path class="floor" d="M20 200H500"/>
          <path class="net" d="M260 200V179"/><path class="tape" d="M255 179H265"/>
          <polyline class="arc" id="arc" points=""/>
          <ellipse class="spot" id="spot" cx="-40" cy="200" rx="13" ry="4"/>
          <circle class="ball" id="ball" cx="110" cy="172" r="6.5"/>
        </svg>
        <span class="tag tag-net">{e(d['t_net'])}</span><span class="tag tag-glass">{e(d['t_glass'])}</span>
        <button type="button" class="aim" id="aim" aria-label="{a(d['t_aim'])}"></button>
      </div>
      <p class="say" id="say" aria-live="polite" data-idle="{a(pad['idle'])}" data-in="{a(pad['in'])}" data-glass="{a(pad['glass'])}" data-net="{a(pad['net'])}" data-short="{a(pad['short'])}">{e(pad['idle'])}</p>
      <small>{e(d['t_hint'])}</small>
    </figure>
  </div>
</section>
<section class="who">
  <h2>{e(d['who_h'])}</h2>
  <dl>{who}</dl>
</section>
<section class="columns">
  <div class="plan">
    <h2>{e(d['c_h2'])}</h2>
    <p class="lead">{e(d['c_lead'])}</p>
    <ul class="inside">{items}</ul>
    <p class="shots"><b>{e(d['shots_label'])}</b> {e(names)}</p>
  </div>
  <div class="screen"><img id="shot" src="{a(shots[0])}" alt="" width="600" height="1304" loading="lazy"></div>
</section>
</main>
""" + footer(L, d)

def build_doc(kind, L, d, X):
    """kind: 'privacy', 'support' or 'terms'. App Store Connect links to these addresses."""
    code, folder, hl, ogl, store, key, native = L
    page = kind + '.html'
    name = store_name(store)
    body = []
    mail = f'<a href="{MAIL}">helpyoutofeel@gmail.com</a>'
    if kind == 'privacy':
        body.append(f'<p class="short"><strong>{e(X["short_label"])}</strong> {e(X["short"])}</p>')
        body += [f'<h2>{e(h)}</h2><p>{e(p)}</p>' for h, p in X['sections']]
        body.append(f'<h2>{e(X["contact_h"])}</h2><p>{mail}</p>')
    elif kind == 'terms':
        body.append(f'<p class="short">{e(X["intro"])}</p>')
        body.append(f'<h2>{e(X["lic"][0])}</h2><p>{e(X["lic"][1])} <a href="{EULA}">{e(X["eula"])}</a></p>')
        body.append(f'<h2>{e(X["pro"][0])}</h2><p>{e(X["pro"][1])}</p>')
        body.append(f'<h2>{e(app("Disclaimer", key))}</h2><p>{e(app(DISCLAIMER, key))}</p>')
        body += [f'<h2>{e(h)}</h2><p>{e(p)}</p>' for h, p in (X['use'], X['changes'])]
        body.append(f'<h2>{e(X["contact_h"])}</h2><p>{mail}</p>')
    else:
        body.append('<div class="contact">' + ''.join(
            f'<p><strong>{e(h)}</strong>{e(p)}</p><a class="btn {c}" href="{a(MAIL + "?subject=" + urllib.parse.quote(sub, safe=""))}">{e(b)}</a>'
            for (h, p, b, sub), c in zip(X['cards'], ('', 'line'))) + '</div>')
        body.append('<div class="rows">' + ''.join(f'<details><summary>{e(q)}</summary><p>{e(ui(t, key))}</p></details>' for q, t in X['faq']) + '</div>')
    title = f'{name}: {X["h1"]}'
    return head_tags(BASE + folder + page, L, title, X['desc'], page) + f"""</head>
<body class="plain">
{header(L, d, page)}
<main class="doc">
  <h1>{e(X['h1'])}</h1>
  <p class="quiet">{e(name)} (Padl). {e(X['sub'])}</p>
  {''.join(body)}
</main>
""" + footer(L, d)

def check(code, m):
    need = ['title','desc','lang_label','h1a','h1b','short','cta','cta_store','notify_subject','hero_aria','why_h','sub','sub2',
            't_try','t_net','t_glass','t_aim','t_hint','pad','who_h','who','c_h2','c_lead','items','shots_label',
            'foot','foot_support','foot_privacy','foot_terms']
    miss = [k for k in need if k not in m.D]
    assert not miss, (code, miss)
    assert len(m.D['who']) == 3 and len(m.D['items']) == 4 and set(m.D['pad']) == {'idle','in','glass','net','short'}, code
    for k in ['desc','h1','sub','short_label','short','sections','contact_h']:
        assert k in m.P, (code, 'P', k)
    assert len(m.P['sections']) == 7, (code, len(m.P['sections']))
    for k in ['desc','h1','sub','cards','faq']:
        assert k in m.S, (code, 'S', k)
    assert len(m.S['cards']) == 2 and len(m.S['faq']) == 9, (code, len(m.S['faq']))
    for k in ['desc','h1','sub','intro','lic','eula','pro','use','changes','contact_h']:
        assert k in m.T, (code, 'T', k)

def main():
    only = os.environ.get('ONLY')
    for L in LANGS:
        if only and L[0] not in only.split(','): continue
        code, folder = L[0], L[1]
        m = importlib.import_module('lang_' + code)
        check(code, m)
        os.makedirs(os.path.join(SITE, folder), exist_ok=True)
        open(os.path.join(SITE, folder, 'index.html'), 'w', encoding='utf-8').write(build(L, m.D))
        for kind, X in (('privacy', m.P), ('support', m.S), ('terms', m.T)):
            open(os.path.join(SITE, folder, kind + '.html'), 'w', encoding='utf-8').write(build_doc(kind, L, m.D, X))
        print('wrote', folder or '/')
    blocks = ''
    for pg in PAGES:
        alts = ''.join(f'    <xhtml:link rel="alternate" hreflang="{h}" href="{BASE}{f}{pg}"/>\n' for _, f, h, *_ in LANGS) + f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{pg}"/>\n'
        blocks += ''.join(f'  <url><loc>{BASE}{f}{pg}</loc>\n{alts}  </url>\n' for _, f, *_ in LANGS)
    head = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write(head + blocks + '</urlset>\n')

if __name__ == '__main__':
    main()
