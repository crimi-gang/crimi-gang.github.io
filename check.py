#!/usr/bin/env python3
"""Check all local HTML links, assets, fragments and essential metadata."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote
import re

ROOT = Path(__file__).resolve().parent
HOST = 'https://crimi-gang.github.io'

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.base = './'
        self.references = []
        self.ids = set()
        self.h1 = 0
        self.description = False
        self.errors = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'base':
            self.base = a.get('href', './')
        if 'id' in a:
            if a['id'] in self.ids:
                self.errors.append(f'duplicate ID: {a["id"]}')
            self.ids.add(a['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'meta' and a.get('name') == 'description':
            self.description = bool(a.get('content'))
        if tag == 'img' and 'alt' not in a:
            self.errors.append('image without alt attribute')
        if tag == 'img' and a.get('src') and not (a.get('width') and a.get('height')):
            self.errors.append('image without intrinsic dimensions')
        if tag == 'img' and a.get('srcset'):
            self.references.extend(part.strip().split()[0] for part in a['srcset'].split(','))
        if a.get('data-full-src'):
            self.references.append(a['data-full-src'])
        for attr in ('href', 'src'):
            if a.get(attr):
                self.references.append(a[attr])

pages = {}
for file in ROOT.rglob('*.html'):
    if '.git' in file.parts:
        continue
    parser = Page()
    parser.feed(file.read_text())
    pages[file] = parser

errors = []
links = 0
for file, page in pages.items():
    rel = file.relative_to(ROOT)
    if page.h1 != 1 or not page.description:
        errors.append(f'{rel}: expected one H1 and a meta description')
    errors.extend(f'{rel}: {error}' for error in page.errors)
    page_url = f'{HOST}/{rel.as_posix()}'
    base = urljoin(page_url, page.base)
    for ref in page.references:
        url = urlparse(urljoin(base, ref))
        if url.scheme not in ('https', 'http') or url.netloc != 'crimi-gang.github.io':
            continue
        target = ROOT / unquote(url.path).lstrip('/')
        if url.path.endswith('/'):
            target /= 'index.html'
        if not target.is_file():
            errors.append(f'{rel}: missing target {ref}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{rel}: missing fragment {ref}')
        links += 1
for ref in re.findall(r'url\([\'\"]?([^\)\'\"]+)', (ROOT / 'styles.css').read_text()):
    if not (ROOT / ref).is_file():
        errors.append(f'styles.css: missing asset {ref}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'OK: {len(pages)} pages, {links} local references, fragments, image alt text and metadata.')
