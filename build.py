#!/usr/bin/env python3
"""Build the static, dependency-free Crimi Gang website. Python 3.9+."""
from pathlib import Path
from html import escape
from datetime import date
import struct
import json
import re

ROOT = Path(__file__).resolve().parent
ORIGIN = 'https://crimi-gang.github.io'
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

def img(path, alt='', cls='', eager=False, width=None, height=None):
    path = path.replace('/', '-')
    source = ROOT / path
    if source.suffix == '.png' and source.exists():
        width, height = struct.unpack('>II', source.read_bytes()[16:24])
    dimensions = f' width="{width}" height="{height}"' if width and height else ''
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{path}" alt="{escape(alt, quote=True)}" class="{cls}" {loading} decoding="async"{dimensions}>'

def button(url, text, kind='primary', arrow='arrow'):
    return f'<a class="button {kind}" href="{url}">{text}{icon(arrow)}</a>'

def textlink(url, text, arrow='arrow'):
    return f'<a class="text-link" href="{url}">{text}{icon(arrow)}</a>'

def phone(dark=False, cls=''):
    return f'<div class="phone {cls}">{img("love/home-dark.png" if dark else "love/home-light.png", "Anteprima dimostrativa di Crimi Love in tema " + ("scuro" if dark else "chiaro"), eager=True, width=471, height=1024)}</div>'

def tags(cozy=False):
    return '<div class="tags"><span class="tag"><span class="status-dot"></span>In sviluppo</span><span class="tag">' + ('Cozy game' if cozy else 'App di coppia') + '</span><span class="tag">' + ('iPhone e iPad' if cozy else 'iPhone') + '</span></div>'

def project_card(cozy=False):
    name = 'Tiny Cozy Town' if cozy else 'Crimi Love'
    slug = 'tiny-cozy-town' if cozy else 'crimi-love'
    desc = 'Un piccolo villaggio. Tutto il tempo che vuoi.' if cozy else 'Un piccolo mondo, solo vostro.'
    artwork = img('town/town.png', 'Il villaggio isometrico di Tiny Cozy Town con casetta rosa, panetteria e Mochi il coniglio', 'cover-town', width=1440, height=1100) if cozy else '<div class="cover-phones">' + phone() + phone(True) + '</div>' + icon('spark', 'cover-spark')
    return f'''<a class="project-card" href="{slug}.html" aria-label="Scopri {name}">
      <div class="project-cover {'cozy' if cozy else ''}"><span class="cover-label">{'Un posto in cui rallentare' if cozy else 'Le piccole cose, in due'}</span>{artwork}</div>
      <div class="project-caption"><div><h3>{img(('town' if cozy else 'love') + '/icon.png', '', width=192, height=192)}{name}</h3><p>{desc}</p>{tags(cozy)}</div><span class="card-arrow">{icon('up-right')}</span></div></a>'''

def about_art():
    return f'''<div class="about-art" role="img" aria-label="Cristian e Noemi, due persone e una passione condivisa"><div class="profile-token"><span>C</span><small>Cristian</small></div><div class="profile-token noemi"><span>N</span><small>Noemi</small></div>{icon('heart', 'about-heart')}<span class="about-note">il nostro progetto preferito? Creare insieme.</span></div>'''

def contact_band():
    return f'''<aside class="contact-band wrap"><div><div class="eyebrow">Due chiacchiere?</div><h2>Le belle idee iniziano con un ciao.</h2><p>Un suggerimento, una domanda o anche solo un saluto.</p></div>{button('contatti.html', 'Scrivici', 'light', 'up-right')}</aside>'''

def breadcrumb(label, project=False):
    return f'<nav class="breadcrumb" aria-label="Percorso"><a href="./">Home</a>{icon("arrow")}' + (f'<a href="progetti.html">Progetti</a>{icon("arrow")}' if project else '') + f'<span aria-current="page">{label}</span></nav>'

def gallery_image(path, alt, caption, wide=False):
    return f'''<figure class="gallery-item {'wide' if wide else ''}"><button class="zoom-button" data-zoom hidden aria-label="Ingrandisci: {escape(caption, quote=True)}">{icon('zoom')}</button>{img(path, alt)}<figcaption>{caption}</figcaption></figure>'''

def feature(name, title, description):
    return f'<article class="feature-item">{icon(name)}<h3>{title}</h3><p>{description}</p></article>'

def palette(colors):
    return '<div class="palette">' + ''.join(f'<div class="swatch" style="--swatch:{color}"><span>{name}<small>{color.upper()}</small></span></div>' for name, color in colors) + '</div>'

def document(title, description, content, route='', active='', bodyclass='', gallery=False):
    base = './'
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if active == key else '') + f'>{label}</a>' for key, url, label in [('home', './', 'Home'), ('projects', 'progetti.html', 'Progetti'), ('about', 'chi-siamo.html', 'Chi siamo')])
    lightbox = f'<dialog class="lightbox" aria-label="Galleria immagini"><button class="lightbox-close" aria-label="Chiudi immagine">{icon("close")}</button><img alt=""><p></p></dialog>' if gallery else ''
    ld = {"@context":"https://schema.org","@type":"WebSite","name":"Crimi Gang","url":ORIGIN,"inLanguage":"it","description":"App, giochi e idee di Cristian e Noemi, creati insieme per passione."}
    return f'''<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><base href="{base}">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="theme-color" content="#faf8f3"><link rel="icon" type="image/svg+xml" href="favicon.svg"><link rel="canonical" href="{ORIGIN}/{route}">
<meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="Crimi Gang"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{ORIGIN}/{route}"><meta property="og:image" content="{ORIGIN}/town-town.png"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="fonts-nunito-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="styles.css"><script src="site.js" defer></script><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>
<body class="{bodyclass}"><a class="skip-link" href="{route}#main">Vai al contenuto</a><header class="site-header"><div class="header-inner wrap"><a class="brand" href="./" aria-label="Crimi Gang, home"><span class="brand-mark">{icon('heart')}</span><span>crimi gang<span class="dot">.</span></span></a><button class="menu-toggle" aria-label="Apri menu" aria-controls="main-nav" aria-expanded="false">{icon('menu')}</button><nav class="nav" id="main-nav" aria-label="Navigazione principale">{nav}<a class="nav-contact" href="contatti.html" {'aria-current="page"' if active == 'contact' else ''}>Contatti{icon('up-right')}</a></nav></div></header>
<main id="main">{content}</main>{lightbox}
<footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="brand" href="./"><span class="brand-mark">{icon('heart')}</span><span>crimi gang<span class="dot">.</span></span></a><p>Piccole idee, tanto cuore.</p></div><nav class="footer-links" aria-label="Link nel footer"><a href="progetti.html">Progetti</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a><a href="privacy.html">Privacy</a><a href="https://github.com/crimi-gang" target="_blank" rel="noopener noreferrer">GitHub {icon('up-right')}</a></nav></div><div class="footer-bottom"><span>© {date.today().year} Crimi Gang · Cristian &amp; Noemi</span><span>Fatto con cura, e un po’ di {icon('heart')}</span></div></div></footer></body></html>'''

home = f'''
<section class="home-hero wrap"><div class="hero-copy"><div class="eyebrow">Ciao, siamo Crimi Gang</div><h1>Le cose belle<br>nascono<br><span class="together">insieme.</span></h1><p>Siamo Cristian e Noemi. Creiamo app, piccoli mondi e cose che ci fanno stare bene.<br>Per passione, e con un po’ di cuore.</p><div class="hero-actions">{button('progetti.html', 'Esplora i progetti')}{textlink('chi-siamo.html', 'La nostra storia')}</div><div class="hero-footnote"><div class="mini-avatars" aria-hidden="true"><span>C</span><span>N</span></div>Due persone. Una passione condivisa.</div></div>
<div class="hero-art" aria-label="I nostri mondi: Crimi Love e Tiny Cozy Town"><div class="art-orbit"></div><div class="hero-blob"></div>{phone(False, 'hero-phone')}{img('town/cottage.png', '', 'hero-house', True, 576, 552)}{img('town/rabbit-0.png', '', 'hero-rabbit', True, 216, 288)}<span class="floating-note note-love">{icon('heart')}Crimi Love</span><span class="floating-note note-town">{icon('leaf')}Tiny Cozy Town</span>{icon('spark','art-spark one')}{icon('spark','art-spark two')}{icon('spark','art-spark three')}<span class="love-stamp">CREATO CON{icon('heart')}DA NOI DUE</span></div></section>
<div class="values-strip"><div class="values-inner wrap"><span>{icon('code')}Sviluppati con passione</span>{icon('spark')}<span>{icon('heart')}Pensati per le piccole cose</span>{icon('spark')}<span>{icon('leaf')}Un passo alla volta</span></div></div>
<section class="section wrap" aria-labelledby="projects-title"><div class="section-head"><div><div class="eyebrow">Il nostro piccolo universo</div><h2 id="projects-title">Idee che prendono vita.</h2></div><p>Due progetti diversi, la stessa voglia di creare qualcosa di nostro.</p></div><div class="project-grid">{project_card()}{project_card(True)}</div></section>
<section class="section wrap" aria-labelledby="about-title"><div class="about-panel">{about_art()}<div class="about-copy"><div class="eyebrow">Dietro lo schermo, noi</div><h2 id="about-title">Una coppia.<br>Mille «e se facessimo…?»</h2><p>Cristian scrive il codice, Noemi mette tutto alla prova. Siamo fidanzati e condividiamo la curiosità di trasformare le idee in qualcosa da usare, esplorare e amare.</p>{textlink('chi-siamo.html', 'Piacere di conoscerti')}</div></div></section>{contact_band()}'''

projects = f'''<section class="page-intro wrap">{breadcrumb('Progetti')}<div class="eyebrow">Il nostro piccolo universo</div><h1>Due idee.<br>Tanto di noi.</h1><p>Un’app per sentirsi più vicini e un villaggio per rallentare. Qui trovi quello che stiamo creando, un passo alla volta.</p></section><section class="projects-page wrap" aria-label="I nostri progetti"><div class="project-grid"><div><div class="project-number">01 / CONDIVIDERE</div>{project_card()}</div><div><div class="project-number">02 / RALLENTARE</div>{project_card(True)}</div></div><div class="work-note">{icon('spark')}<p>Entrambi i progetti sono in sviluppo. Nelle pagine dedicate puoi esplorare l’idea, l’interfaccia e i dettagli visivi. Le immagini sono anteprime e possono cambiare.</p></div></section>{contact_band()}'''

love = f'''<div class="page-intro wrap">{breadcrumb('Crimi Love', True)}</div><section class="detail-hero wrap"><div><div class="app-identity">{img('love/icon.png', 'Icona di Crimi Love', width=192, height=192)}<span>Un progetto Crimi Gang</span></div><h1>Crimi Love<span class="accent">.</span></h1><p class="lead">Un piccolo mondo, solo vostro. Un’app di coppia per custodire i momenti che contano e sentirsi vicini, ogni giorno.</p>{tags()}{'<div class="hero-actions">' + button('crimi-love.html#galleria', 'Guarda le anteprime') + '</div>'}</div><div class="detail-visual">{phone()}{phone(True)}{icon('spark','cover-spark')}</div></section>
<dl class="detail-facts wrap"><div><dt>Pensata per</dt><dd>Due persone, una storia</dd></div><div><dt>Piattaforma</dt><dd>iPhone · iOS 17+</dd></div><div><dt>Stato del progetto</dt><dd>In sviluppo</dd></div></dl>
<section class="section editorial-grid wrap"><div><div class="eyebrow">L’idea</div><h2>Le piccole cose.<br>Quelle vostre.</h2></div><div><p>Un anniversario da ricordare, una foto che fa sorridere, il conto dei giorni trascorsi insieme. Crimi Love raccoglie questi piccoli pezzi di quotidianità in uno spazio dedicato alla coppia.</p><p>È un progetto che nasce dalla nostra esperienza: un modo per dare un posto speciale alle cose che, per due persone, significano tanto.</p><div class="feature-list">{feature('calendar','La vostra storia','Giorni insieme, anniversari, mesiversari e compleanni: i prossimi momenti da aspettare in due.')}{feature('photo','Una foto, due sorrisi','Foto condivise e widget per portare un piccolo pezzo della vostra storia sulla schermata Home.')}{feature('heart','Più vicini','Mappa e condivisione facoltativa di posizione e batteria, con controlli dedicati nelle impostazioni.')}{feature('palette','Il vostro stile','Temi personali, colori e font per rendere questo piccolo spazio ancora più vostro.')}</div></div></section>
<section class="gallery-section" id="galleria" aria-labelledby="love-gallery"><div class="wrap"><div class="gallery-header"><div><div class="eyebrow">Dentro l’app</div><h2 id="love-gallery">Un’occhiata al nostro mondo.</h2></div><p>Anteprime dimostrative con dati inventati, in tema chiaro e scuro. Tocca la lente per ingrandire.</p></div><div class="gallery-grid">{gallery_image('love/home-light.png','Schermata dimostrativa Crimi Love: conteggio dei giorni, ricorrenze e navigazione in tema chiaro','Il vostro spazio · Tema chiaro')}{gallery_image('love/home-dark.png','Schermata dimostrativa Crimi Love con sfondo scuro e dettagli rosa','Il vostro spazio · Tema scuro')}</div></div></section>
<section class="section visual-identity wrap"><div><div class="eyebrow">L’identità visiva</div><h2>Rosa, prugna<br>e un po’ di dolcezza.</h2><p>La palette originale di Crimi Love unisce il rosa ai toni profondi del prugna e ai dettagli pesca. Angoli morbidi e caratteri arrotondati riprendono lo stile nativo dell’app.</p></div><div>{palette([('Rosa','#C7517A'),('Prugna','#593052'),('Pesca','#FFDBCC'),('Rosa tenue','#F4B6C9')])}<div class="font-sample"><strong>Un piccolo mondo, solo vostro.</strong>Nell’app: font di sistema arrotondato. Sul web: Nunito.</div></div></section>
<section class="wrap"><div class="work-note" style="margin:0 0 55px">{icon('heart')}<p>Crimi Love è in sviluppo e non è ancora disponibile per il download pubblico. Le funzioni e l’interfaccia possono evolvere. Per curiosità o domande, <a class="text-link" href="contatti.html">scrivici</a>.</p></div></section>{contact_band()}<a class="project-next wrap" href="tiny-cozy-town.html"><div><span>Esplora l’altro progetto</span><strong>Tiny Cozy Town</strong></div>{icon('arrow')}</a>'''

textures = [('cottage.png','Una casetta tutta tua'),('bakery.png','La panetteria'),('rabbit-0.png','Mochi il coniglio'),('chick-0.png','Pip il pulcino'),('tree.png','Alberi e verde'),('flowers.png','Piccoli fiori'),('bench.png','Un posto per fermarsi'),('lantern.png','Una luce calda')]
town = f'''<div class="page-intro wrap">{breadcrumb('Tiny Cozy Town', True)}</div><section class="detail-hero wrap"><div><div class="app-identity">{img('town/icon.png','Icona di Tiny Cozy Town', width=192, height=192)}<span>Un progetto Crimi Gang</span></div><h1>Tiny<br>Cozy Town<span class="accent">.</span></h1><p class="lead">Un piccolo villaggio. Tutto il tempo che vuoi. Costruisci, decora e prenditi una pausa in un mondo dai colori gentili.</p>{tags(True)}<div class="hero-actions">{button('tiny-cozy-town.html#galleria', 'Esplora il villaggio')}</div></div><div class="detail-visual cozy">{img('town/town.png','Anteprima della grafica del villaggio: casetta rosa, panetteria lavanda, alberi e Mochi',eager=True,width=1440,height=1100)}<span class="visual-label">Grafica originale del progetto</span></div></section>
<dl class="detail-facts wrap"><div><dt>Genere</dt><dd>Cozy idle · Isometrico</dd></div><div><dt>Piattaforme</dt><dd>iPhone e iPad · iOS 17+</dd></div><div><dt>Stato del progetto</dt><dd>In sviluppo</dd></div></dl>
<section class="section editorial-grid wrap"><div><div class="eyebrow">L’idea</div><h2>Un posto piccolo.<br>Una bella pausa.</h2></div><div><p>Si comincia con una casetta rosa e Mochi, un coniglietto curioso. Poi arriva una panetteria, qualche fiore e la voglia di rendere questo angolo di mondo un po’ più tuo.</p><p>Tiny Cozy Town è un gioco da vivere al proprio ritmo: niente fretta, piccoli gesti e un villaggio che cresce insieme alle tue idee.</p><div class="feature-list">{feature('home','Costruisci e decora','Una casetta da personalizzare, una panetteria da migliorare e decorazioni da sistemare sul prato.')}{feature('heart','Incontra Mochi e Pip','Un coniglietto e un pulcino che passeggiano per il villaggio, tra una coccola e una piccola sosta.')}{feature('leaf','Prenditi cura del villaggio','Pane da ritirare, piante da annaffiare e piccoli incarichi da completare senza scadenza.')}{feature('sun','Segui il tuo ritmo','Desideri quotidiani senza penalità e un album di traguardi per accompagnare la crescita del villaggio.')}</div></div></section>
<section class="gallery-section town-gallery" id="galleria" aria-labelledby="town-gallery"><div class="wrap"><div class="gallery-header"><div><div class="eyebrow">Dentro il villaggio</div><h2 id="town-gallery">Piccolo mondo, tanti dettagli.</h2></div><p>Texture originali generate dal progetto: tegole, foglie e personaggi, da guardare da vicino.</p></div><div class="gallery-grid">{gallery_image('town/town.png','Tavola della grafica isometrica di Tiny Cozy Town, con edifici, stradine e alberi','Anteprima della grafica · Il nostro piccolo villaggio',True)}</div><div class="texture-grid" style="margin-top:24px">{''.join(f'<figure class="texture-item">{img("town/"+file,label)}<figcaption>{label}</figcaption></figure>' for file,label in textures)}</div><p class="muted" style="font-size:11px;margin-top:22px">La tavola e le texture mostrano la grafica effettiva del progetto; non sono schermate di una release pubblicata.</p></div></section>
<section class="section visual-identity wrap"><div><div class="eyebrow">L’identità visiva</div><h2>Colori gentili.<br>Un’atmosfera cozy.</h2><p>Lavanda, rosa, crema e verde menta: la palette riprende i colori originali del gioco. Le texture morbide e il disegno isometrico danno al villaggio la sua atmosfera tranquilla.</p></div><div>{palette([('Lavanda','#AC98CE'),('Rosa','#EFB5C7'),('Crema','#FFFBF3'),('Menta','#DFECDA')])}<div class="font-sample"><strong>Un passo alla volta, senza fretta.</strong>Nel gioco: font di sistema arrotondato. Sul web: Nunito.</div></div></section>
<section class="wrap"><div class="work-note" style="margin:0 0 55px">{icon('leaf')}<p>Stiamo ancora facendo crescere il villaggio. Tiny Cozy Town è in sviluppo e non è ancora disponibile per il download pubblico. Hai un’idea o una curiosità? <a class="text-link" href="contatti.html">Scrivici</a>.</p></div></section>{contact_band()}<a class="project-next wrap" href="crimi-love.html"><div><span>Esplora l’altro progetto</span><strong>Crimi Love</strong></div>{icon('arrow')}</a>'''

about = f'''<section class="page-intro wrap">{breadcrumb('Chi siamo')}<div class="eyebrow">Piacere di conoscerti</div><h1>Due persone.<br>La voglia di <span class="accent">creare.</span></h1><p>Siamo Cristian e Noemi. Siamo fidanzati, ci piace immaginare cose nuove e provare a costruirle insieme. Questo è il nostro piccolo angolo di internet.</p></section><section class="about-story wrap">{about_art()}<div class="story-copy"><h2>Da un «e se…»<br>a qualcosa di nostro.</h2><p>Crimi Gang nasce dalla passione di creare insieme. Un’idea diventa una prova, la prova diventa una schermata, e da lì si continua: si cambia, si migliora, si riparte.</p><p>Ci piacciono le cose curate, le interfacce che fanno stare bene e i dettagli che strappano un sorriso. Crimi Love e Tiny Cozy Town sono due modi diversi di raccontare questa passione.</p></div></section>
<section class="section wrap" style="border-top:1px solid var(--line)"><div class="eyebrow">La nostra piccola gang</div><h2>Ognuno fa la sua parte.</h2><div class="team-grid"><article class="team-person"><div class="person-initial" aria-hidden="true">C</div><div><h3>Cristian</h3><div class="role">Sviluppatore</div><p>Trasforma le idee in codice. Si occupa dello sviluppo delle app e del gioco, dalla prima schermata ai dettagli che fanno funzionare tutto.</p></div></article><article class="team-person"><div class="person-initial pink" aria-hidden="true">N</div><div><h3>Noemi</h3><div class="role">Tester</div><p>Prova i progetti, esplora ogni schermata e aiuta a capire cosa migliorare. Uno sguardo attento per rendere le idee più piacevoli da usare.</p></div></article></div></section>
<section class="section wrap" style="padding-top:15px"><div class="eyebrow">Il nostro modo di fare</div><h2>Ci mettiamo un po’ di noi.</h2><div class="our-way"><article><span>01 / PASSIONE</span><h3>Perché ci piace.</h3><p>Partiamo da qualcosa che vorremmo usare o da un piccolo mondo in cui ci piacerebbe passare del tempo.</p></article><article><span>02 / CURA</span><h3>Anche nei dettagli.</h3><p>Un colore, una texture, un pulsante: proviamo e miglioriamo le piccole cose che fanno la differenza.</p></article><article><span>03 / INSIEME</span><h3>Un passo alla volta.</h3><p>Sviluppo e test si incontrano, le idee si scambiano e ogni progetto cresce attraverso entrambi.</p></article></div></section>{contact_band()}'''

contact = f'''<section class="page-intro wrap">{breadcrumb('Contatti')}<div class="eyebrow">La casella della gang</div><h1>Cominciamo<br>con un <span class="accent">ciao.</span></h1><p>Hai una domanda sui nostri progetti, un suggerimento o un problema da raccontarci? Ci trovi qui.</p></section><div class="contact-layout wrap"><section class="contact-card" aria-labelledby="email-title">{icon('mail')}<h2 id="email-title">La nostra email</h2><a class="email-link" href="mailto:crimisupport@gmail.com">crimisupport@gmail.com {icon('up-right')}</a><p>Per supporto, idee, feedback e saluti.</p><div>{button('mailto:crimisupport@gmail.com?subject=Ciao%20Crimi%20Gang', 'Scrivi un’email', 'primary', 'mail')}<button class="copy-button" data-copy-email>Copia indirizzo</button></div><div class="copy-status" role="status" aria-live="polite"></div></section><div class="contact-options"><section class="contact-option"><h3>Ti serve una mano?</h3><p>Indica il nome del progetto, il dispositivo e cosa succede. Se puoi, aggiungi i passaggi per riprodurre il problema.</p>{textlink('mailto:crimisupport@gmail.com?subject=Supporto%20progetto%20Crimi%20Gang','Chiedi supporto')}</section><section class="contact-option"><h3>Hai una bella idea?</h3><p>Ci piace ascoltare nuovi punti di vista. Raccontaci cosa vorresti trovare in Crimi Love o Tiny Cozy Town.</p>{textlink('mailto:crimisupport@gmail.com?subject=Un%27idea%20per%20Crimi%20Gang','Condividi un’idea')}</section></div></div>
<section class="section wrap" style="padding-top:15px"><div class="eyebrow">Prima di scriverci</div><h2>Qualche piccola risposta.</h2><div class="faq-list"><details><summary>Posso già scaricare Crimi Love o Tiny Cozy Town?</summary><p>Entrambi i progetti sono in sviluppo e non sono ancora disponibili per il download pubblico. Trovi anteprime e dettagli nelle <a href="progetti.html">pagine dei progetti</a>.</p></details><details><summary>Come posso segnalare un problema?</summary><p>Scrivi a <a href="mailto:crimisupport@gmail.com">crimisupport@gmail.com</a> indicando il progetto, la versione che stai provando, il dispositivo e i passaggi che portano al problema. Non inviare password o codici di accesso.</p></details><details><summary>Posso proporre una funzione o condividere un feedback?</summary><p>Certo! Raccontaci la tua idea via email. Leggiamo i suggerimenti mentre continuiamo a sviluppare i progetti.</p></details></div></section>'''

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
    ('', 'Crimi Gang · Piccole idee, tanto cuore', 'Siamo Cristian e Noemi. Creiamo app, giochi e piccoli mondi per passione. Scopri Crimi Love, Tiny Cozy Town e la nostra storia.', home, 'home', '', False),
    ('progetti.html', 'I nostri progetti · Crimi Gang', 'Esplora Crimi Love e Tiny Cozy Town: due progetti in sviluppo, creati da Cristian e Noemi per passione.', projects, 'projects', '', False),
    ('crimi-love.html', 'Crimi Love · Il vostro piccolo mondo | Crimi Gang', 'Crimi Love: un’app di coppia per giorni insieme, ricorrenze, foto e widget. Esplora le anteprime, i colori e l’idea del progetto.', love, 'projects', 'detail-love', True),
    ('tiny-cozy-town.html', 'Tiny Cozy Town · Un villaggio tutto tuo | Crimi Gang', 'Un cozy game isometrico per iPhone e iPad. Esplora il villaggio, le texture originali e i piccoli personaggi di Tiny Cozy Town.', town, 'projects', 'detail-town', True),
    ('chi-siamo.html', 'Cristian e Noemi · Chi siamo | Crimi Gang', 'Cristian sviluppa, Noemi testa. Siamo una coppia e creiamo app e giochi insieme per passione. Questa è Crimi Gang.', about, 'about', '', False),
    ('contatti.html', 'Contatti e supporto · Crimi Gang', 'Contatta Cristian e Noemi per supporto, idee e feedback su Crimi Love e Tiny Cozy Town. Scrivi a crimisupport@gmail.com.', contact, 'contact', '', False),
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
