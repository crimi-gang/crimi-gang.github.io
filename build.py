#!/usr/bin/env python3
"""Build the static, dependency-free Crimi Gang website. Python 3.9+."""
from pathlib import Path
from html import escape
from datetime import date
import struct
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
ORIGIN = 'https://crimi-gang.github.io'
IMAGE_MANIFEST = json.loads((ROOT / 'image-manifest.json').read_text())

def asset_url(name):
    digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:10]
    return f'{name}?v={digest}'

css = (ROOT / 'styles-source.css').read_text()
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
css = re.sub(r'\s+', ' ', css)
css = re.sub(r'\s*([{}:;,])\s*', r'\1', css).strip()
(ROOT / 'styles.css').write_text(css + '\n')
ICONS = {
    'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    'up-right': '<path d="M6 18 18 6M6 6h12v12"/>',
    'heart': '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>',
    'spark': '<path d="m12 2 2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6Z"/>',
    'code': '<path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-15-2 18"/>',
    'leaf': '<path d="M20 3C7 1 1 8 5 16c8 5 17-1 15-13ZM4 21 16 9"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m3 7 9 6 9-6"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'zoom': '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M7 10h6m-3-3v6"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 3v4m10-4v4M3 11h18m-13 5h2m4 0h2"/>',
    'photo': '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8" cy="8" r="1"/><path d="m3 17 6-6 4 4 3-3 5 5"/>',
    'palette': '<path d="M12 3a9 9 0 1 0 0 18h1a2 2 0 0 0 2-2c0-1-1-2-1-3s1-2 2-2h2a3 3 0 0 0 3-3 9 9 0 0 0-9-8Z"/><path d="M7 10h.01M9 6h.01M15 6h.01M18 10h.01"/>',
    'home': '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    'check': '<path d="m5 12 4 4L19 6"/>',
    'github': '<path d="M9 19c-4 1-4-2-6-2m12 5v-3.4a3 3 0 0 0-.8-2.3c2.8-.3 5.8-1.4 5.8-6.3A5 5 0 0 0 18.6 6a4.6 4.6 0 0 0-.1-3.5S17.4 2.2 15 4a13 13 0 0 0-6 0C6.6 2.2 5.5 2.5 5.5 2.5A4.6 4.6 0 0 0 5.4 6 5 5 0 0 0 4 9.7c0 4.9 3 6 5.8 6.3a3 3 0 0 0-.8 2.3V22"/>',
}

def icon(name, cls=''):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

def img(path, alt='', cls='', eager=False, width=None, height=None, sizes=None, priority=False):
    path = path.replace('/', '-')
    source = ROOT / path
    if source.suffix == '.png' and source.exists():
        width, height = struct.unpack('>II', source.read_bytes()[16:24])
    dimensions = f' width="{width}" height="{height}"' if width and height else ''
    optimized = IMAGE_MANIFEST.get(path, {})
    current_hash = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    variants = optimized.get('variants', []) if optimized.get('source_hash') == current_hash else []
    responsive = ''
    if variants:
        if sizes is None:
            if path.endswith('-icon.png'):
                sizes = '55px'
            elif cls == 'texture-image':
                sizes = '(max-width: 760px) calc((100vw - 64px) / 2), 240px'
            elif cls == 'sbrokk-character':
                sizes = '(max-width: 760px) 270px, 350px'
            else:
                sizes = '(max-width: 760px) calc(100vw - 40px), 560px'
        chosen = next((v for v in variants if v['width'] >= 640), variants[-1])
        image_src = chosen['path'] + '?v=' + chosen['hash']
        srcset = ', '.join(v['path'] + '?v=' + v['hash'] + ' ' + str(v['width']) + 'w' for v in variants)
        full = variants[-1]['path'] + '?v=' + variants[-1]['hash']
        responsive = f' srcset="{srcset}" sizes="{sizes}" data-full-src="{full}"'
    else:
        image_src = asset_url(path)
    loading = 'loading="eager"' if eager else 'loading="lazy"'
    fetch = ' fetchpriority="high"' if priority else ''
    return f'<img src="{image_src}"{responsive} alt="{escape(alt, quote=True)}" class="{cls}" {loading}{fetch} decoding="async"{dimensions}>'

def button(url, text, kind='primary', arrow='arrow'):
    return f'<a class="button {kind}" href="{url}">{text}{icon(arrow)}</a>'

def textlink(url, text, arrow='arrow'):
    return f'<a class="text-link" href="{url}">{text}{icon(arrow)}</a>'

def phone(dark=False, cls='', eager=False, priority=False):
    return f'<div class="phone {cls}">{img("love/home-dark.png" if dark else "love/home-light.png", "Crimi Love in tema " + ("scuro" if dark else "chiaro"), eager=eager, priority=priority, sizes="(max-width: 760px) 170px, 210px")}</div>'

def tags(cozy=False, sbrokk=False):
    if sbrokk:
        return '<div class="tags"><span class="tag"><span class="status-dot"></span>In sviluppo</span><span class="tag">Puzzle comico</span><span class="tag">iPhone e iPad</span></div>'
    return '<div class="tags"><span class="tag"><span class="status-dot"></span>In sviluppo</span><span class="tag">' + ('Cozy game' if cozy else 'App di coppia') + '</span><span class="tag">' + ('iPhone e iPad' if cozy else 'iPhone') + '</span></div>'

def sbrokk_art(eager=False):
    return f'<div class="sbrokk-art"><span class="sbrokk-bubble">Tu giochi.<br>Lui sclera.</span>{img("sbrokk/furious.png", "Il protagonista di Sbrokk! con un’espressione furiosa", "sbrokk-character", eager=eager, priority=eager)}<span class="sbrokk-stamp">100 PUZZLE · UN BEL CARATTERINO</span></div>'

def project_card(cozy=False, sbrokk=False):
    if sbrokk:
        name, slug, number, kind, platform = 'Sbrokk!', 'sbrokk', '03', 'Puzzle comico', 'iPhone e iPad'
        desc = 'Cento rompicapo e un quadrato convinto che tu debba perdere. Tu risolvi i puzzle, lui perde la pazienza.'
        artwork = sbrokk_art()
        theme = 'sbrokk'
    elif cozy:
        name, slug, number, kind, platform = 'Tiny Cozy Town', 'tiny-cozy-town', '02', 'Cozy game', 'iPhone e iPad'
        desc = 'Una casetta, Mochi e un prato da riempire. Costruisci il tuo villaggio, apri nuove attività e fai spazio a Pip.'
        artwork = img('town/cottage.png', 'La casetta rosa di Tiny Cozy Town', 'cover-town')
        theme = 'cozy'
    else:
        name, slug, number, kind, platform = 'Crimi Love', 'crimi-love', '01', 'App di coppia', 'iPhone'
        desc = 'Giorni insieme, ricorrenze e foto condivise. Stiamo creando uno spazio per le cose che contano nella vita di coppia.'
        artwork = '<div class="cover-phones">' + phone() + phone(True) + '</div>'
        theme = 'love'
    return f'''<a class="project-card" href="{slug}.html" aria-label="Scopri {name}"><div class="project-cover {theme}">{artwork}</div><div class="project-caption"><div><div class="project-category"><span>{number}</span> {kind}</div><h3>{name}</h3><p>{desc}</p><div class="project-meta"><span class="development-state">In sviluppo</span><span>{platform}</span></div><span class="project-open">Guarda il progetto {icon('arrow')}</span></div></div></a>'''

def about_art():
    return '<div class="about-art" role="img" aria-label="Cristian e Noemi"><span class="people-letter">C</span><span class="people-and">&amp;</span><span class="people-letter noemi">N</span><p>Cristian &amp; Noemi<br><small>La nostra gang.</small></p></div>'

def contact_band():
    return f'<aside class="contact-band wrap"><div><h2>Hai una domanda?</h2><p>Supporto, idee e feedback sui nostri progetti.</p></div><a class="contact-address" href="mailto:crimisupport@gmail.com">crimisupport@gmail.com {icon("up-right")}</a></aside>'


def breadcrumb(label, project=False):
    return f'<nav class="breadcrumb" aria-label="Percorso"><a href="./">Home</a>{icon("arrow")}' + (f'<a href="progetti.html">Progetti</a>{icon("arrow")}' if project else '') + f'<span aria-current="page">{label}</span></nav>'

def gallery_image(path, alt, caption, wide=False):
    return f'''<figure class="gallery-item {'wide' if wide else ''}"><button class="zoom-button" data-zoom hidden aria-label="Ingrandisci: {escape(caption, quote=True)}">{icon('zoom')}</button>{img(path, alt)}<figcaption>{caption}</figcaption></figure>'''

def feature(name, title, description):
    return f'<article class="feature-item">{icon(name)}<h3>{title}</h3><p>{description}</p></article>'

def palette(colors):
    return '<div class="palette">' + ''.join(f'<div class="swatch" style="--swatch:{color}"><span>{name}</span></div>' for name, color in colors) + '</div>'

def document(title, description, content, route='', active='', bodyclass='', gallery=False):
    base = './'
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if active == key else '') + f'>{label}</a>' for key, url, label in [('home', './', 'Home'), ('projects', 'progetti.html', 'Progetti'), ('about', 'chi-siamo.html', 'Chi siamo')])
    lightbox = f'<dialog class="lightbox" aria-label="Galleria immagini"><button class="lightbox-close" aria-label="Chiudi immagine">{icon("close")}</button><img alt=""><p></p></dialog>' if gallery else ''
    share_image = {'crimi-love.html':'love-icon.png', 'tiny-cozy-town.html':'town-icon.png', 'sbrokk.html':'sbrokk-icon.png'}.get(route, 'town-cottage.png')
    ld = {"@context":"https://schema.org","@type":"WebSite","name":"Crimi Gang","url":ORIGIN,"inLanguage":"it","description":"App, giochi e idee di Cristian e Noemi, creati insieme per passione."}
    return f'''<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><base href="{base}">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="theme-color" content="#f8f6f1"><meta name="color-scheme" content="light"><link rel="icon" type="image/svg+xml" href="favicon.svg"><link rel="canonical" href="{ORIGIN}/{route}">
<meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="Crimi Gang"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{ORIGIN}/{route}"><meta property="og:image" content="{ORIGIN}/{share_image}"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="fonts-nunito-latin.woff2" as="font" type="font/woff2" crossorigin><script>document.documentElement.classList.add("js")</script><link rel="stylesheet" href="{asset_url("styles.css")}"><script src="{asset_url("site.js")}" defer></script><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>
<body class="{bodyclass or ("page-home" if not route else "page-" + route.removesuffix(".html"))}"><a class="skip-link" href="{route}#main">Vai al contenuto</a><header class="site-header"><div class="header-inner wrap"><a class="brand" href="./" aria-label="Crimi Gang, home"><span class="brand-mark" aria-hidden="true"><i></i><i></i></span><span>crimi gang<span class="dot">.</span></span></a><button class="menu-toggle" aria-label="Apri menu" aria-controls="main-nav" aria-expanded="false">{icon('menu')}</button><nav class="nav" id="main-nav" aria-label="Navigazione principale">{nav}<a class="nav-contact" href="contatti.html" {'aria-current="page"' if active == 'contact' else ''}>Contatti{icon('up-right')}</a></nav></div></header>
<main id="main">{content}</main>{lightbox}
<footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="brand" href="./"><span class="brand-mark" aria-hidden="true"><i></i><i></i></span><span>crimi gang<span class="dot">.</span></span></a><p>App e giochi di Cristian e Noemi.</p></div><nav class="footer-links" aria-label="Link nel footer"><a href="progetti.html">Progetti</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a><a href="privacy.html">Privacy</a><a href="https://github.com/crimi-gang" target="_blank" rel="noopener noreferrer">GitHub {icon('up-right')}</a></nav></div><div class="footer-bottom"><span>© {date.today().year} Crimi Gang · Cristian &amp; Noemi</span><span>Creati insieme, per passione.</span></div></div></footer></body></html>'''

home = f'''
<section class="home-hero wrap"><div class="hero-copy"><div class="eyebrow">App e giochi in sviluppo</div><h1>Due persone.<br>Tre progetti.<br><span>Crimi Gang.</span></h1><p>Cristian sviluppa, Noemi mette tutto alla prova. Siamo fidanzati e creiamo insieme, per passione.</p><div class="hero-actions">{button('progetti.html', 'Guarda i progetti')}{textlink('chi-siamo.html', 'Chi siamo')}</div></div>
<div class="hero-shelf"><a class="shelf-tile shelf-love" href="crimi-love.html" aria-label="Scopri Crimi Love"><span class="shelf-number">01 / App di coppia</span>{phone(cls='shelf-phone', eager=True, priority=True)}<span class="shelf-caption"><strong>Crimi Love</strong>{icon('up-right')}</span></a><a class="shelf-tile shelf-town" href="tiny-cozy-town.html" aria-label="Scopri Tiny Cozy Town"><span class="shelf-number">02 / Cozy game</span>{img('town/cottage.png','Casetta di Tiny Cozy Town','shelf-house',eager=True,sizes='(max-width: 760px) 150px, 260px')}<span class="shelf-caption"><strong>Tiny Cozy Town</strong>{icon('up-right')}</span></a><a class="shelf-tile shelf-sbrokk" href="sbrokk.html" aria-label="Scopri Sbrokk!"><span class="shelf-number">03 / Puzzle comico</span>{img('sbrokk/furious.png','Il protagonista di Sbrokk!','shelf-character',eager=True,sizes='(max-width: 760px) 120px, 210px')}<span class="shelf-caption"><strong>Sbrokk!</strong>{icon('up-right')}</span></a></div></section>
<section class="section wrap home-projects" aria-labelledby="projects-title"><div class="section-head"><div><div class="eyebrow">I progetti</div><h2 id="projects-title">A cosa stiamo lavorando.</h2></div><p>Un’app di coppia e due giochi.<br>Qui trovi le anteprime e i dettagli di ciascuno.</p></div><div class="project-grid">{project_card()}{project_card(True)}{project_card(sbrokk=True)}</div></section>
<section class="about-home wrap" aria-labelledby="about-title">{about_art()}<div><div class="eyebrow">Cristian &amp; Noemi</div><h2 id="about-title">Uno sviluppa.<br>L’altra trova i difetti.</h2><p>Siamo una coppia anche fuori da questi progetti. Ci piace dedicare tempo alle nostre idee, provarle e cambiare quello che non funziona.</p>{textlink('chi-siamo.html', 'Conosci la gang')}</div></section>{contact_band()}'''

projects = f'''<section class="page-intro wrap">{breadcrumb('Progetti')}<div class="eyebrow">Il nostro lavoro</div><h1>Le nostre app.<br>I nostri giochi.</h1><p>Sono tre, hanno caratteri diversi e li stiamo sviluppando insieme. Scegli un progetto per vedere come sta prendendo forma.</p></section><section class="projects-page wrap" aria-label="I nostri progetti"><div class="project-grid">{project_card()}{project_card(True)}{project_card(sbrokk=True)}</div><div class="work-note"><span class="development-state">In sviluppo</span><p>Le immagini sono anteprime. I progetti non sono ancora disponibili per il download pubblico.</p></div></section>{contact_band()}'''

love = f'''<div class="page-intro wrap">{breadcrumb('Crimi Love', True)}</div><section class="detail-hero wrap"><div><div class="app-identity">{img('love/icon.png', 'Icona di Crimi Love', width=192, height=192)}<span>Un progetto di Cristian e Noemi</span></div><h1>Crimi Love<span class="accent">.</span></h1><p class="lead">Giorni insieme, ricorrenze, foto condivise e widget. Un’app di coppia che nasce dalle cose che vogliamo tenere vicine.</p>{tags()}{'<div class="hero-actions">' + button('crimi-love.html#galleria', 'Guarda le anteprime') + '</div>'}</div><div class="detail-visual">{phone(eager=True, priority=True)}{phone(True, eager=True)}</div></section>
<dl class="detail-facts wrap"><div><dt>Pensata per</dt><dd>Due persone, una storia</dd></div><div><dt>Piattaforma</dt><dd>iPhone · iOS 17+</dd></div><div><dt>Stato del progetto</dt><dd>In sviluppo</dd></div></dl>
<section class="section editorial-grid wrap"><div><div class="eyebrow">L’idea</div><h2>Le cose da ricordare in due.</h2></div><div><p>Un anniversario da ricordare, una foto che fa sorridere, il conto dei giorni trascorsi insieme. Crimi Love raccoglie questi piccoli pezzi di quotidianità in uno spazio dedicato alla coppia.</p><p>È un progetto che nasce dalla nostra esperienza: un modo per dare un posto speciale alle cose che, per due persone, significano tanto.</p><div class="feature-list">{feature('calendar','La vostra storia','Giorni insieme, anniversari, mesiversari e compleanni: i prossimi momenti da aspettare in due.')}{feature('photo','Una foto, due sorrisi','Foto condivise e widget per portare un piccolo pezzo della vostra storia sulla schermata Home.')}{feature('heart','Più vicini','Mappa e condivisione facoltativa di posizione e batteria, con controlli dedicati nelle impostazioni.')}{feature('palette','Il vostro stile','Temi personali, colori e font per rendere questo piccolo spazio ancora più vostro.')}</div></div></section>
<section class="gallery-section" id="galleria" aria-labelledby="love-gallery"><div class="wrap"><div class="gallery-header"><div><div class="eyebrow">Dentro l’app</div><h2 id="love-gallery">Le schermate di Crimi Love.</h2></div><p>Tema chiaro e tema scuro, con dati dimostrativi. Tocca la lente per ingrandire.</p></div><div class="gallery-grid">{gallery_image('love/home-light.png','Schermata dimostrativa Crimi Love: conteggio dei giorni, ricorrenze e navigazione in tema chiaro','Il vostro spazio · Tema chiaro')}{gallery_image('love/home-dark.png','Schermata dimostrativa Crimi Love con sfondo scuro e dettagli rosa','Il vostro spazio · Tema scuro')}</div></div></section>
<section class="section visual-identity wrap"><div><div class="eyebrow">L’identità visiva</div><h2>Il rosa di Crimi Love.</h2><p>La palette originale di Crimi Love unisce il rosa ai toni profondi del prugna e ai dettagli pesca. Angoli morbidi e caratteri arrotondati riprendono lo stile nativo dell’app.</p></div><div>{palette([('Rosa','#C7517A'),('Prugna','#593052'),('Pesca','#FFDBCC'),('Rosa tenue','#F4B6C9')])}</div></section>
<section class="wrap"><div class="work-note" style="margin:0 0 55px">{icon('heart')}<p>Crimi Love è in sviluppo e non è ancora disponibile per il download pubblico. Le funzioni e l’interfaccia possono evolvere. Per curiosità o domande, <a class="text-link" href="contatti.html">scrivici</a>.</p></div></section>{contact_band()}<a class="project-next wrap" href="tiny-cozy-town.html"><div><span>Esplora un altro progetto</span><strong>Tiny Cozy Town</strong></div>{icon('arrow')}</a>'''

town_buildings = [('cottage.png', 'Casetta dei sogni'), ('bakery.png', 'Panetteria soffice'), ('florist.png', 'Fioraio dei sorrisi'), ('teaHouse.png', 'Sala da tè'), ('workshop.png', 'Laboratorio creativo')]
town_animals = [('rabbit-0.png', 'Mochi il coniglio'), ('chick-0.png', 'Pip il pulcino')]
town_decorations = [('flowers.png', 'Fiorellini'), ('bush.png', 'Cespuglio cuore'), ('bench.png', 'Panchina cozy'), ('lantern.png', 'Lanterna stellina'), ('picnic.png', 'Picnic tra amici'), ('pond.png', 'Laghetto dei sogni'), ('tree.png', 'Albero verde'), ('tree-mint.png', 'Albero menta')]

def texture_section(title, description, items, layout=''):
    figures = ''.join(f'<figure class="texture-item"><button class="texture-zoom" data-zoom hidden aria-label="Ingrandisci: {escape(label, quote=True)}">{icon("zoom")}</button>{img("town/" + file, label, "texture-image")}<figcaption>{label}</figcaption></figure>' for file, label in items)
    return f'<div class="texture-section"><div class="texture-section-head"><h3>{title}</h3><p>{description}</p></div><div class="texture-grid {layout}">{figures}</div></div>'

town = f'''<div class="page-intro wrap">{breadcrumb('Tiny Cozy Town', True)}</div><section class="detail-hero wrap"><div><div class="app-identity">{img('town/icon.png','Icona di Tiny Cozy Town', width=192, height=192)}<span>Un progetto di Cristian e Noemi</span></div><h1>Tiny<br>Cozy Town<span class="accent">.</span></h1><p class="lead">Costruisci un villaggio, apri una panetteria, sistema il prato. Mochi e Pip ti fanno compagnia, mentre decidi cosa aggiungere.</p>{tags(True)}<div class="hero-actions">{button('tiny-cozy-town.html#galleria', 'Esplora il villaggio')}</div></div><div class="detail-visual cozy">{img('town/cottage.png','La casetta rosa di Tiny Cozy Town',eager=True, priority=True)}<span class="visual-label">Casetta dei sogni</span></div></section>
<dl class="detail-facts wrap"><div><dt>Il tuo piccolo mondo</dt><dd>5 edifici · 2 animaletti</dd></div><div><dt>Piattaforme</dt><dd>iPhone e iPad · iOS 17+</dd></div><div><dt>Da far crescere</dt><dd>6 espansioni · Fino a 19 × 19</dd></div></dl>
<section class="section editorial-grid wrap"><div><div class="eyebrow">L’idea</div><h2>Si comincia con una casetta.</h2></div><div><p>Si comincia con una casetta rosa e Mochi, un coniglietto curioso. Poi arrivano il profumo del pane, i bouquet del fioraio, una tazza di tè e le creazioni del laboratorio.</p><p>Tiny Cozy Town è un gioco da vivere al proprio ritmo: piccoli gesti, nuovi amici e un villaggio che cresce un’espansione alla volta. Ogni edificio ha il suo carattere, da scegliere anche nei colori.</p><div class="feature-list">{feature('home','Cinque edifici, tante idee','Una casetta da chiamare casa e quattro attività: panetteria, fioraio, sala da tè e laboratorio creativo. Personalizzale con cinque colori gratuiti.')}{feature('heart','Mochi e Pip, in libertà','Un coniglietto e un pulcino che passeggiano sul prato e sulle stradine, aggirano gli ostacoli e si fermano per una coccola.')}{feature('leaf','Ogni angolo conta','Fiori, cespugli, panchine, lanterne, picnic e laghetti. Sistema le decorazioni e spostale liberamente per creare il tuo angolo preferito.')}{feature('spark','Un villaggio che cresce','Sei espansioni portano il terreno da 7 × 7 fino a 19 × 19. Fioraio, sala da tè e laboratorio si sbloccano con le prime tre espansioni.')}{feature('sun','Piccoli progressi, ogni giorno','Le quattro attività arrivano al livello 30. Pane da ritirare, piante da annaffiare, incarichi senza scadenza e desideri quotidiani senza penalità.')}{feature('photo','Un album di momenti','Otto traguardi permanenti accompagnano la crescita del villaggio, con ricompense e nuove decorazioni da scoprire.')}</div></div></section>
<section class="gallery-section town-gallery" id="galleria" aria-labelledby="town-gallery"><div class="wrap"><div class="gallery-header"><div><div class="eyebrow">Dentro il villaggio</div><h2 id="town-gallery">Edifici, abitanti e decorazioni.</h2></div><p>Le texture aggiornate del progetto: edifici, animaletti e decorazioni. Tocca una lente per guardarli da vicino.</p></div>
{texture_section('Una casa. Quattro piccole attività.', 'Dalla casetta al laboratorio creativo: tetti, insegne e vetrine nella loro versione aggiornata.', town_buildings, 'texture-buildings')}
{texture_section('I nostri piccoli abitanti.', 'Mochi e Pip, con la grafica attuale del gioco. Passeggiano nel villaggio e nelle nuove aree che sblocchi.', town_animals, 'texture-animals')}
{texture_section('Le cose che fanno casa.', 'Tutte e sei le decorazioni, la panchina aggiornata e le due varianti degli alberi.', town_decorations)}
<p class="muted" style="font-size:11px;margin-top:22px">La grafica che stiamo usando nel gioco, ancora in sviluppo.</p></div></section>
<section class="section visual-identity wrap"><div><div class="eyebrow">L’identità visiva</div><h2>Il prato, i tetti, i colori.</h2><p>Lavanda, rosa, crema e verde menta restano il filo del nostro piccolo mondo. Gli edifici aggiungono cinque varianti gratuite: Rosa pesca, Lilla sogno, Menta dolce, Vaniglia e Cielo sereno.</p><p>La geometria isometrica aggiornata, le nuove vetrine e la panchina in legno rendono ogni angolo ancora più curato.</p></div><div>{palette([('Lavanda','#AC98CE'),('Rosa','#EFB5C7'),('Crema','#FFFBF3'),('Menta','#DFECDA')])}</div></section>
<section class="section wrap town-extras" aria-labelledby="town-personalize"><div class="section-head"><div><div class="eyebrow">Il villaggio, a modo tuo</div><h2 id="town-personalize">Scegli i colori.<br>Fai spazio alle idee.</h2></div><p>Cinque edifici, cinque palette e nuovi obiettivi per allargare il prato un passo alla volta.</p></div><div class="gallery-grid">{gallery_image('town/buildings-palettes.png','Tutti i cinque edifici nelle varianti rosa, lavanda, menta, vaniglia e cielo','Cinque colori per ogni edificio · Le 25 combinazioni')}{gallery_image('town/expansion.png','Anteprima nativa della scheda Espandi il terreno con obiettivi completati e pulsante Espandi','Un’espansione pronta · Anteprima dell’interfaccia')}</div><p class="muted" style="font-size:12px;margin-top:22px">Le nuove attività si migliorano fino al livello 30. La scheda dell’espansione mostra gli obiettivi del prossimo passo. Regali e cartello pubblicitario sono facoltativi; l’opzione Senza pubblicità disattiva anche il cartello.</p></section>
<section class="wrap"><div class="work-note" style="margin:0 0 55px">{icon('leaf')}<p>Stiamo ancora facendo crescere il villaggio. Tiny Cozy Town è in sviluppo e non è ancora disponibile per il download pubblico. Hai un’idea o una curiosità? <a class="text-link" href="contatti.html">Scrivici</a>.</p></div></section>{contact_band()}<a class="project-next wrap" href="sbrokk.html"><div><span>Esplora un altro progetto</span><strong>Sbrokk!</strong></div>{icon('arrow')}</a>'''

sbrokk_expressions = [('suspicious', 'Sospettoso'), ('furious', 'Furioso'), ('confused', 'Confuso'), ('happy', 'Felice'), ('embarrassed', 'Imbarazzato'), ('triumphant', 'Trionfante')]
sbrokk_faces = ''.join(f'<figure class="texture-item"><button class="texture-zoom" data-zoom hidden aria-label="Ingrandisci: {label}">{icon("zoom")}</button>{img("sbrokk/" + file + ".png", "Il protagonista di Sbrokk! — " + label.lower(), "texture-image")}<figcaption>{label}</figcaption></figure>' for file, label in sbrokk_expressions)

sbrokk = f'''<div class="page-intro wrap">{breadcrumb('Sbrokk!', True)}</div>
<section class="detail-hero wrap"><div><div class="app-identity">{img('sbrokk/icon.png','Icona di Sbrokk!')}<span>Un progetto di Cristian e Noemi</span></div><div class="eyebrow sbrokk-eyebrow">Puzzle · Commedia</div><h1>Sbrokk<span class="accent">!</span></h1><p class="lead">Il gioco che non vuole farti vincere. Un quadrato arrogante, cento rompicapo e una certezza: ogni tua vittoria gli farà perdere la pazienza.</p>{tags(sbrokk=True)}<div class="hero-actions">{button('sbrokk.html#galleria', 'Guarda il gioco')}</div></div><div class="detail-visual sbrokk">{sbrokk_art(eager=True)}</div></section>
<dl class="detail-facts wrap"><div><dt>Da risolvere</dt><dd>100 livelli · 10 capitoli</dd></div><div><dt>Piattaforme</dt><dd>iPhone e iPad · iOS 17+</dd></div><div><dt>Il tuo ritmo</dt><dd>Niente vite · Niente fretta</dd></div></dl>
<section class="section editorial-grid wrap"><div><div class="eyebrow">L’idea</div><h2>Pensa fuori<br>dal suo quadrato.</h2></div><div><p>È arancione, ha un ego enorme ed è convinto che tu debba perdere. Nasconde pulsanti, si prende gioco delle parole e rende sospetto anche il gesto più semplice.</p><p>Per andare avanti serve cambiare punto di vista: toccare, trascinare, aspettare, osservare meglio. Nel frattempo lui commenta, si arrabbia e cambia espressione. Tu risolvi il puzzle. Lui deve farsene una ragione.</p><div class="feature-list">{feature('spark','Cento piccoli dispetti','100 livelli in 10 capitoli, tra regole da mettere in dubbio, parole da spostare e oggetti poco collaborativi.')}{feature('heart','Un protagonista, tanti umori','Dodici espressioni originali e battute che accompagnano mosse, errori e vittorie. Anche aspettare può provocare una reazione.')}{feature('sun','Un aiuto, quando serve','Tre indizi gratuiti per ogni livello. Nessuna vita da ricaricare e nessun acquisto per proseguire.')}{feature('code','Più modi di giocare','Tocchi, trascinamenti, gesti e inclinazione, con controlli alternativi per affrontare anche le interazioni più complesse.')}{feature('palette','Fatto di forme e suoni','Grafica vettoriale, colori caldi, musica ed effetti originali. Il gioco include italiano e inglese.')}{feature('photo','Trofei e Ufficio Reclami','Raccogli i trofei lungo il percorso. Dopo il finale ti aspetta un piccolo bonus, con tre pratiche decisamente poco ordinarie.')}</div></div></section>
<section class="gallery-section sbrokk-gallery" id="galleria" aria-labelledby="sbrokk-gallery"><div class="wrap"><div class="gallery-header"><div><div class="eyebrow">Il protagonista</div><h2 id="sbrokk-gallery">Tu giochi.<br>Lui sclera.</h2></div><p>Sei dei dodici umori del protagonista, esportati dalla grafica originale del progetto. Tocca una lente per guardarli da vicino.</p></div><div class="texture-grid sbrokk-faces">{sbrokk_faces}</div><div class="texture-section"><div class="texture-section-head"><h3>Persino un pulsante può farti un dispetto.</h3><p>Un assaggio delle scene e dei dialoghi, con colori e forme del gioco.</p></div><div class="gallery-grid">{gallery_image('sbrokk/level-1.png','Anteprima illustrativa del livello 001 Il pulsante proibito, con personaggio sospettoso e pulsante rosso Non toccare','Il pulsante proibito · Livello 001')}{gallery_image('sbrokk/level-31.png','Anteprima illustrativa del livello 031 La porta addormentata, con sveglia e porta che dorme','La porta addormentata · Livello 031')}</div></div><p class="muted sbrokk-gallery-note">Anteprime illustrative realizzate con la grafica originale del gioco. L’interfaccia è ancora in sviluppo.</p></div></section>
<section class="section visual-identity wrap"><div><div class="eyebrow">L’identità visiva</div><h2>Il carattere di Sbrokk!</h2><p>Crema e carta fanno da sfondo al corallo del protagonista e al giallo dei pulsanti. Contorni scuri, ombre nette e forme arrotondate danno al gioco il suo tono da piccolo fumetto.</p></div><div>{palette([('Crema','#F7E8CC'),('Corallo','#E96A42'),('Giallo','#F8B843'),('Inchiostro','#302934')])}</div></section>
<section class="wrap"><div class="work-note sbrokk-development">{icon('spark')}<p>Sbrokk! è in sviluppo e non è ancora disponibile per il download pubblico. Il gioco è progettato anche per giocare offline, con progressi salvati sul dispositivo. Per curiosità, idee o feedback, <a class="text-link" href="contatti.html">scrivici</a>.</p></div></section>{contact_band()}<a class="project-next wrap" href="crimi-love.html"><div><span>Esplora un altro progetto</span><strong>Crimi Love</strong></div>{icon('arrow')}</a>'''

about = f'''<section class="page-intro wrap">{breadcrumb('Chi siamo')}<div class="eyebrow">Dietro Crimi Gang</div><h1>Cristian e Noemi.<br>La nostra gang.</h1><p>Siamo fidanzati. Ci piace creare cose insieme e Crimi Gang è il nome con cui raccogliamo le nostre app e i nostri giochi.</p></section><section class="about-story wrap">{about_art()}<div class="story-copy"><h2>Due ruoli.<br>Lo stesso progetto.</h2><p>Cristian si occupa dello sviluppo: scrive il codice e costruisce le funzioni. Noemi prova i progetti e aiuta a capire dove serve ancora lavorare.</p><p>Crimi Love, Tiny Cozy Town e Sbrokk! nascono dalla stessa passione. Sono idee diverse che portiamo avanti insieme, tra sviluppo e test.</p></div></section><section class="section wrap team-section" aria-labelledby="team-title"><div class="eyebrow">Chi fa cosa</div><h2 id="team-title">Ci presentiamo.</h2><div class="team-grid"><article class="team-person"><div class="person-initial" aria-hidden="true">C</div><div><h3>Cristian</h3><div class="role">Sviluppatore</div><p>Dall’idea alla prima versione, poi alle modifiche successive. Cura lo sviluppo delle app e dei giochi.</p></div></article><article class="team-person"><div class="person-initial pink" aria-hidden="true">N</div><div><h3>Noemi</h3><div class="role">Tester</div><p>Usa i progetti, prova le funzioni e segnala i problemi. I suoi test aiutano a rendere ogni versione migliore.</p></div></article></div></section>{contact_band()}'''

contact = f'''<section class="page-intro wrap">{breadcrumb('Contatti')}<div class="eyebrow">Supporto e contatti</div><h1>Scrivici.</h1><p>Per una domanda, un problema o un’idea sui nostri progetti. La casella è la stessa per tutte e tre le app.</p></section><div class="contact-layout wrap"><section class="contact-card" aria-labelledby="email-title"><span class="eyebrow">La nostra casella</span><h2 id="email-title">crimisupport@gmail.com</h2><p>Rispondiamo da qui a supporto e feedback.</p><div class="contact-actions">{button('mailto:crimisupport@gmail.com', 'Scrivi un’email', 'primary', 'up-right')}<button class="copy-button" data-copy-email>Copia indirizzo</button></div><div class="copy-status" role="status" aria-live="polite"></div></section><div class="contact-options"><section class="contact-option"><h3>Qualcosa non funziona?</h3><p>Indica il progetto, il dispositivo e cosa è successo. I passaggi per riprodurre il problema ci aiutano a trovarlo.</p></section><section class="contact-option"><h3>Hai un suggerimento?</h3><p>Raccontaci cosa vorresti trovare in Crimi Love, Tiny Cozy Town o Sbrokk! Leggiamo i feedback mentre lavoriamo alle prossime versioni.</p></section></div></div><section class="section wrap faq-section" aria-labelledby="faq-title"><h2 id="faq-title">Prima di scriverci.</h2><div class="faq-list"><details><summary>I progetti sono già disponibili?</summary><p>Sono ancora in sviluppo e non sono disponibili per il download pubblico. Trovi immagini e informazioni nelle <a href="progetti.html">pagine dei progetti</a>.</p></details><details><summary>Cosa serve per segnalare un problema?</summary><p>Nome del progetto, versione, dispositivo e passaggi che portano al problema. Non inviare password o codici di accesso.</p></details><details><summary>Posso proporre una funzione?</summary><p>Certo. Scrivi a <a href="mailto:crimisupport@gmail.com">crimisupport@gmail.com</a> e descrivi cosa ti piacerebbe fare e perché ti sarebbe utile.</p></details></div></section>'''

def policy_inline(text):
    """Render the small trusted Markdown subset used by our policy source."""
    text = escape(text, quote=True)
    text = re.sub(r'\[([^\]]+)\]\(((?:https://|mailto:)[^\s)]+)\)', r'<a href="\2">\1</a>', text)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)


def policy_body(source):
    sections = []
    toc = []
    section = 0
    for block in source.strip().split('\n\n'):
        if block.startswith('# '):
            continue
        if block.startswith('## '):
            section += 1
            title = block[3:]
            anchor = f'sezione-{section}'
            toc.append(f'<li><a href="privacy-tiny-cozy-town.html#{anchor}">{escape(title)}</a></li>')
            sections.append(f'<h2 id="{anchor}">{escape(title)}</h2>')
        else:
            sections.append('<p>' + policy_inline(block).replace('\n', '<br>') + '</p>')
    return '<div class="privacy-layout wrap"><aside class="privacy-index"><h2>In questa pagina</h2><nav aria-label="Indice privacy Tiny Cozy Town"><ol>' + ''.join(toc) + '</ol></nav></aside><article class="privacy-copy">' + '\n'.join(sections) + '</article></div>'


privacy_site = f'''<section class="page-intro wrap">{breadcrumb('Privacy')}<div class="eyebrow">Informazioni sui dati</div><h1>La privacy,<br>con <span class="accent">chiarezza.</span></h1><p>Come gestiamo i dati di chi visita il sito Crimi Gang o ci scrive. Ultimo aggiornamento: 20 ottobre 2026.</p></section>
<article class="privacy-copy privacy-site wrap"><h2>Chi gestisce questo sito</h2><p>Il titolare è <strong>Cristian Papa</strong>. Per domande sui dati personali scrivi a <a href="mailto:crimisupport@gmail.com">crimisupport@gmail.com</a>.</p>
<div class="privacy-callout"><h2>Cerchi la privacy del gioco?</h2><p>Per salvataggi, acquisti Apple, Game Center, iCloud e annunci facoltativi, consulta l'informativa dedicata a Tiny Cozy Town.</p>{button('privacy-tiny-cozy-town.html', 'Privacy di Tiny Cozy Town', 'primary', 'arrow')}</div>
<h2>Navigazione del sito</h2><p>Questo sito è statico e ospitato su GitHub Pages. Non inseriamo strumenti di analytics, pixel pubblicitari, moduli di registrazione, cookie di profilazione o risorse incorporate di social network. Immagini, font e codice dell'interfaccia sono serviti dal sito stesso. Il menu, le gallerie e la copia dell'email funzionano nel browser senza inviare i contenuti dei tuoi appunti allo sviluppatore.</p><p>GitHub registra l'indirizzo IP dei visitatori per motivi di sicurezza anche senza un accesso a GitHub. Consulta la <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection">descrizione di GitHub Pages</a> e la <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">privacy di GitHub</a> per i dettagli di questo trattamento e i relativi criteri di conservazione. Il titolare non usa questi dati per creare profili pubblicitari dei visitatori.</p>
<h2>Quando ci scrivi</h2><p>I link email aprono il programma di posta: il sito non invia messaggi automaticamente. Se scegli di scrivere, riceviamo il tuo indirizzo, il testo e gli allegati che invii, per rispondere alla richiesta. Usiamo Gmail, secondo la <a href="https://policies.google.com/privacy">privacy di Google</a>. Non inviare password, codici di accesso o dati non necessari. Scriverci non attiva una newsletter.</p>
<h2>Finalità, conservazione e destinatari</h2><p>La gestione dell'assistenza relativa ai nostri servizi si basa sull'esecuzione del servizio o di misure richieste prima di usarlo (art. 6.1.b GDPR). Gli eventuali adempimenti obbligatori si basano sulla legge (art. 6.1.c). Per altri messaggi volontari usiamo i dati solo per il riscontro richiesto; non li riutilizziamo per campagne di marketing.</p><p>Conserviamo la corrispondenza per il tempo necessario a gestire il messaggio e le successive verifiche; oltre tale periodo solo per obblighi di legge o per accertare, esercitare o difendere un diritto, per la durata necessaria. I destinatari sono il titolare e i servizi di hosting o posta descritti, oltre alle autorità nei casi previsti dalla legge. GitHub e Google possono trattare dati anche fuori dallo Spazio economico europeo: le loro informative descrivono paesi, tempi e garanzie di trasferimento applicabili.</p>
<h2>Le tue scelte e i tuoi diritti</h2><p>Puoi visitare le pagine senza scriverci. Se non fornisci i dati necessari a una richiesta, potremmo non riuscire a rispondere. Nei casi previsti dal GDPR puoi chiedere accesso, rettifica, cancellazione, limitazione, portabilità e opposizione scrivendo al contatto indicato. Puoi inoltre rivolgerti al <a href="https://www.garanteprivacy.it/home/i-miei-diritti/diritti">Garante per la protezione dei dati personali</a> o all'autorità competente del tuo paese.</p>
<h2>Informative dei progetti</h2><p>L'informativa del sito descrive la navigazione di queste pagine e il contatto email. Il trattamento dei dati all'interno delle app è descritto nelle rispettive informative. Quella di <a href="privacy-tiny-cozy-town.html">Tiny Cozy Town</a> è disponibile qui. Crimi Love è un progetto distinto: la sua informativa sarà resa disponibile prima del rilascio pubblico.</p>
<h2>Aggiornamenti e contatti</h2><p>Eventuali nuovi servizi saranno accompagnati dall'aggiornamento di questa pagina e, quando necessario, dalle scelte di consenso pertinenti. Per informazioni: <a href="mailto:crimisupport@gmail.com">crimisupport@gmail.com</a>.</p></article>'''

privacy_town = f'''<section class="page-intro wrap">{breadcrumb('Privacy · Tiny Cozy Town')}<div class="eyebrow">Il tuo villaggio e i tuoi dati</div><h1>Privacy di<br><span class="accent">Tiny Cozy Town.</span></h1><p>Salvataggi, servizi Apple e annunci facoltativi: le informazioni per scegliere con calma.</p></section>''' + policy_body((ROOT / 'privacy-tiny-cozy-town.md').read_text(encoding='utf-8'))

contact += f'''<section class="privacy-links wrap"><h2>Una domanda sulla privacy?</h2><p>Puoi usare la stessa email per informazioni sui tuoi dati. Prima, trovi i dettagli nelle nostre informative.</p><div>{textlink('privacy.html', 'Privacy del sito')}{textlink('privacy-tiny-cozy-town.html', 'Privacy di Tiny Cozy Town')}</div></section>'''
town += f'''<section class="privacy-links wrap"><h2>Il tuo villaggio, i tuoi dati.</h2><p>Scopri come funzionano salvataggi, servizi Apple e annunci facoltativi.</p>{textlink('privacy-tiny-cozy-town.html', 'Leggi l’informativa privacy')}</section>'''

missing = f'''<section class="not-found wrap">{img('town/rabbit-0.png','Mochi il coniglio')}<div class="eyebrow">Errore 404</div><h1>Ops, un piccolo<br>giro fuori mappa.</h1><p>Questa pagina non c’è. Torniamo nel nostro piccolo universo?</p>{button('./','Torna alla home')}</section>'''

pages = [
    ('', 'Crimi Gang · App e giochi di Cristian e Noemi', 'Siamo Cristian e Noemi. Creiamo app, giochi e piccoli mondi per passione. Scopri Crimi Love, Tiny Cozy Town, Sbrokk! e la nostra storia.', home, 'home', '', False),
    ('progetti.html', 'I nostri progetti · Crimi Gang', 'Esplora Crimi Love, Tiny Cozy Town e Sbrokk!: tre progetti in sviluppo, creati da Cristian e Noemi per passione.', projects, 'projects', '', False),
    ('crimi-love.html', 'Crimi Love · Il vostro piccolo mondo | Crimi Gang', 'Crimi Love: un’app di coppia per giorni insieme, ricorrenze, foto e widget. Esplora le anteprime, i colori e l’idea del progetto.', love, 'projects', 'detail-love', True),
    ('tiny-cozy-town.html', 'Tiny Cozy Town · Un villaggio tutto tuo | Crimi Gang', 'Un cozy game isometrico per iPhone e iPad. Esplora il villaggio, le texture originali e i piccoli personaggi di Tiny Cozy Town.', town, 'projects', 'detail-town', True),
    ('sbrokk.html', 'Sbrokk! · Tu giochi. Lui sclera. | Crimi Gang', 'Un puzzle comico per iPhone e iPad: 100 livelli, 10 capitoli e un quadrato dal carattere impossibile. Scopri Sbrokk!, la grafica e le anteprime.', sbrokk, 'projects', 'detail-sbrokk', True),
    ('chi-siamo.html', 'Cristian e Noemi · Chi siamo | Crimi Gang', 'Cristian sviluppa, Noemi testa. Siamo una coppia e creiamo app e giochi insieme per passione. Questa è Crimi Gang.', about, 'about', '', False),
    ('contatti.html', 'Contatti e supporto · Crimi Gang', 'Contatta Cristian e Noemi per supporto, idee e feedback su Crimi Love, Tiny Cozy Town e Sbrokk! Scrivi a crimisupport@gmail.com.', contact, 'contact', '', False),
    ('privacy.html', 'Privacy del sito · Crimi Gang', 'Informativa privacy del sito Crimi Gang: navigazione su GitHub Pages, contatto email e diritti sui dati personali.', privacy_site, '', '', False),
    ('privacy-tiny-cozy-town.html', 'Privacy di Tiny Cozy Town · Crimi Gang', 'Informativa privacy di Tiny Cozy Town per iPhone e iPad. Titolare Cristian Papa, contatto crimisupport@gmail.com.', privacy_town, '', '', False),
]
for route, title, desc, content, active, bodyclass, gallery in pages:
    (ROOT / (route or 'index.html')).write_text(document(title, desc, content, route, active, bodyclass, gallery), encoding='utf-8')
not_found = document('Pagina non trovata · Crimi Gang', 'Questa pagina non esiste. Torna alla home di Crimi Gang.', missing)
not_found = not_found.replace('<base href="./">', f'<base href="{ORIGIN}/">')
(ROOT / '404.html').write_text(not_found, encoding='utf-8')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n', encoding='utf-8')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{ORIGIN}/{route}</loc></url>\n' for route, *_ in pages) + '</urlset>\n', encoding='utf-8')
(ROOT / '.nojekyll').touch()
print(f'Built {len(pages) + 1} pages, robots.txt and sitemap.xml.')
