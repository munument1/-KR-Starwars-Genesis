#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PREFIX = "/-KR-Starwars-Genesis/"
SKIP_DIRS = {".git", ".github"}

def ignored(path):
    return any(part in SKIP_DIRS for part in path.parts)

def resolve_target(source, target):
    if not target or target.startswith("#") or target.startswith("mailto:") or target.startswith("data:"):
        return None
    u = urlsplit(target)
    if u.scheme in ("http", "https"):
        return None

    p = u.path
    if not p:
        return None

    if p.startswith(PROJECT_PREFIX):
        rel = p[len(PROJECT_PREFIX):]
        dest = ROOT / rel
    elif p.startswith("/"):
        dest = ROOT / p.lstrip("/")
    else:
        dest = source.parent / p

    if p.endswith("/") or dest.is_dir():
        dest = dest / "index.html"
    return dest.resolve()

def main():
    html_files = sorted(p for p in ROOT.rglob("*.html") if not ignored(p))
    errors = []
    warnings = []
    checked_links = 0

    for file in html_files:
        text = file.read_text(encoding="utf-8")
        rel = file.relative_to(ROOT)

        if not re.search(r"<title>.*?</title>", text, flags=re.I | re.S):
            errors.append(f"{rel}: missing <title>")
        if 'name="viewport"' not in text and "name='viewport'" not in text:
            errors.append(f"{rel}: missing viewport meta")
        if 'name="robots"' not in text and "name='robots'" not in text:
            warnings.append(f"{rel}: missing robots meta")

        ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', text, flags=re.I))

        for m in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']', text, flags=re.I):
            target = m.group(1)
            if target.startswith("#"):
                frag = target[1:]
                if frag and frag not in ids:
                    errors.append(f"{rel}: missing fragment #{frag}")
                continue

            dest = resolve_target(file, target)
            if dest is None:
                continue
            checked_links += 1

            try:
                dest.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: local path escapes repo: {target}")
                continue

            if not dest.exists():
                errors.append(f"{rel}: broken local link {target} -> {dest.relative_to(ROOT)}")

    print(f"HTML pages: {len(html_files)}")
    print(f"Local links checked: {checked_links}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("\nErrors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("Site validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
