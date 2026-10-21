#!/usr/bin/env python3
"""Create committed, responsive WebP assets. Requires cwebp (libwebp)."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import hashlib
import json
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'image-manifest.json'

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names = set()
    def handle_starttag(self, tag, attrs):
        source = dict(attrs).get('src', '')
        if tag == 'img' and source:
            name = urlsplit(source).path
            if name.endswith('.png') and '/' not in name:
                self.names.add(name)

def main():
    encoder = shutil.which('cwebp')
    if not encoder:
        raise SystemExit('Install libwebp to update image variants. Existing variants can be built without it.')
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    names = set(old)
    for file in ROOT.glob('*.html'):
        parser = Images()
        parser.feed(file.read_text())
        names.update(parser.names)
    manifest = {}
    for name in sorted(names):
        source = ROOT / name
        data = source.read_bytes()
        width, height = struct.unpack('>II', data[16:24])
        digest = hashlib.sha256(data).hexdigest()[:12]
        previous = old.get(name, {})
        if previous.get('source_hash') == digest and all((ROOT / v['path']).exists() for v in previous['variants']):
            manifest[name] = previous
            continue
        variants = []
        for size in sorted({min(width, 320), min(width, 640), min(width, 1280), width}):
            output = ROOT / f'{source.stem}-{size}.webp'
            subprocess.run([encoder, '-quiet', '-q', '90', '-m', '6', '-sharp_yuv', '-alpha_q', '100', '-metadata', 'none', '-resize', str(size), '0', str(source), '-o', str(output)], check=True)
            variants.append({'path': output.name, 'width': size, 'hash': hashlib.sha256(output.read_bytes()).hexdigest()[:10]})
        manifest[name] = {'width': width, 'height': height, 'source_hash': digest, 'variants': variants}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Optimized {len(manifest)} images into {sum(len(x["variants"]) for x in manifest.values())} responsive variants.')

if __name__ == '__main__':
    main()
