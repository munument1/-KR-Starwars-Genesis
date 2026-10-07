#!/usr/bin/env python3
import html as htmlmod
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
UA = "KR-Starwars-Genesis-Image-Audit/1.0 (+https://github.com/munument1/-KR-Starwars-Genesis)"

PAGES = {
    "install/index.html": "https://genesismodlist.com/install/",
    "updating/index.html": "https://genesismodlist.com/updating/",
    "hd-overhaul-install/index.html": "https://genesismodlist.com/hd-overhaul-install/",
    "self-help/index.html": "https://genesismodlist.com/self-help/",
    "wabbajack-issues/index.html": "https://genesismodlist.com/wabbajack-issues/",
    "mod-organizer-issues/index.html": "https://genesismodlist.com/mod-organizer-issues/",
    "ingame-issues/index.html": "https://genesismodlist.com/ingame-issues/",
    "incompatible-apps/index.html": "https://genesismodlist.com/incompatible-apps/",
    "controller-support/index.html": "https://genesismodlist.com/controller-support/",
    "ultrawide-support/index.html": "https://genesismodlist.com/ultrawide-support/",
    "linux-support/index.html": "https://genesismodlist.com/linux-support/",
    "modifying-install/index.html": "https://genesismodlist.com/modifying-install/",
    "performance/index.html": "https://genesismodlist.com/performance/",
    "menu-lag/index.html": "https://genesismodlist.com/menu-lag/",
    "fps-boosts/index.html": "https://genesismodlist.com/fps-boosts/",
    "potato-pc-settings/index.html": "https://genesismodlist.com/potato-pc-settings/",
    "settings/index.html": "https://genesismodlist.com/settings/",
    "faq/index.html": "https://genesismodlist.com/f-a-q/",
    "wiki/index.html": "https://genesismodlist.com/wiki/",
    "controls-keybinds/index.html": "https://genesismodlist.com/controls-keybinds/",
    "tips-tricks/index.html": "https://genesismodlist.com/tips-tricks/",
    "quests/index.html": "https://genesismodlist.com/quests/",
    "lore/index.html": "https://genesismodlist.com/lore/",
    "core-gameplay-changes/index.html": "https://genesismodlist.com/core-gameplay-changes/",
    "the-team/index.html": "https://genesismodlist.com/the-team/",
    "volunteer/index.html": "https://genesismodlist.com/volunteer/",
    "credits/index.html": "https://genesismodlist.com/credits/",
    "donate/index.html": "https://genesismodlist.com/donate/",
    "translations/index.html": "https://genesismodlist.com/translations/",
    "uninstallation/index.html": "https://genesismodlist.com/uninstallation/",
    "game-keys/index.html": "https://genesismodlist.com/game-keys/",
}

IMG_RE = re.compile(r'<img\b[^>]*?(?:src|data-src)=["\']([^"\']+)["\'][^>]*>', re.I | re.S)

def fetch(url):
    last = None
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml"
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                charset = r.headers.get_content_charset() or "utf-8"
                return data.decode(charset, errors="replace")
        except Exception as e:
            last = e
            time.sleep(4 + i * 4)
    raise last

def canonical_image(url):
    url = htmlmod.unescape(url)
    if url.startswith("//"):
        url = "https:" + url
    if "wp-content/uploads/" not in url:
        return None
    path = unquote(urlsplit(url).path)
    m = re.search(r'(/wp-content/uploads/[^?#]+)', path)
    if not m:
        return None
    # Upload paths are case-sensitive. Lowercasing hides broken references.
    return m.group(1)

def images_in(raw):
    out = []
    for m in IMG_RE.finditer(raw):
        c = canonical_image(m.group(1))
        if c:
            out.append(c)
    return out

def public_url(path):
    return "https://genesismodlist.com" + path

def main():
    original = {}
    failures = []
    for idx,(local, url) in enumerate(PAGES.items(), start=1):
        try:
            raw = fetch(url)
            original[local] = set(images_in(raw))
            print(f"[{idx}/{len(PAGES)}] {local}: upstream {len(original[local])} unique images")
        except Exception as e:
            failures.append((local, url, str(e)))
            print(f"[{idx}/{len(PAGES)}] ERROR {url}: {e}")
        time.sleep(1.5)

    # Ignore site-wide theme images that appear on most pages.
    freq = Counter(img for imgs in original.values() for img in imgs)
    threshold = max(8, int(len(original) * 0.55))
    global_images = {img for img,count in freq.items() if count >= threshold}
    if global_images:
        print("\nIgnored site-wide images:")
        for img in sorted(global_images):
            print("  ", img, f"({freq[img]} pages)")

    missing_total = 0
    print("\n=== IMAGE PARITY REPORT ===")
    for local, url in PAGES.items():
        if local not in original:
            continue
        local_path = ROOT / local
        if not local_path.exists():
            print(f"\n{local}: LOCAL FILE MISSING")
            continue
        local_imgs = set(images_in(local_path.read_text(encoding="utf-8")))
        upstream_imgs = original[local] - global_images
        missing = sorted(upstream_imgs - local_imgs)
        extra = sorted(local_imgs - upstream_imgs - global_images)
        if missing:
            missing_total += len(missing)
            print(f"\n{local}  upstream={len(upstream_imgs)} local={len(local_imgs)} missing={len(missing)}")
            for img in missing:
                print("  MISSING", public_url(img))
        elif upstream_imgs:
            print(f"OK {local}: {len(upstream_imgs)} upstream images represented")
        if extra:
            print(f"  NOTE extra/local-only images: {len(extra)}")

    if failures:
        print("\nFetch failures (not audited):")
        for local,url,err in failures:
            print(f"  {local} <- {url}: {err}")

    print(f"\nMissing unique upstream images: {missing_total}")
    # Report only; do not fail because some translated summary pages intentionally omit decorative art.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
