#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "KR-Starwars-Genesis-Upstream-Watch/1.0 (+https://github.com/munument1/-KR-Starwars-Genesis)"

def fetch(url, retries=3):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml"
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                charset = r.headers.get_content_charset() or "utf-8"
                return data.decode(charset, errors="replace")
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise last

def normalize_document(raw):
    # Remove content that commonly changes without the guide itself changing.
    text = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    for tag in ("script", "style", "noscript", "svg"):
        text = re.sub(rf"<{tag}\b.*?</{tag}>", " ", text, flags=re.I | re.S)
    for tag in ("nav", "header", "footer"):
        text = re.sub(rf"<{tag}\b.*?</{tag}>", " ", text, flags=re.I | re.S)

    # Genesis pages append comments and a common legal footer after the useful guide text.
    cut_markers = [
        "Genesismodlist.com is not an affiliate",
        "Loading Comments..."
    ]
    for marker in cut_markers:
        pos = text.find(marker)
        if pos != -1:
            text = text[:pos]

    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()

    # Strip the repeated site navigation if a theme rendered it outside semantic nav/header tags.
    anchors = [
        "HOME INSTALL New Install Updating Install HD Overhaul Install Translations Uninstall SUPPORT",
        "PATCH NOTES",
        "THE TEAM VOLUNTEER CREDITS DONATE"
    ]
    if len(text) > 1500:
        # Keep from the first page-specific heading/question when possible.
        candidates = [
            text.find("Welcome to the Star Wars Genesis Self Help section"),
            text.find("Starfield Launch Issues"),
            text.find("Launch Crashing"),
            text.find("If you are on this page"),
            text.find("Are you "),
            text.find("Do you "),
            text.find("Star Wars Genesis"),
        ]
        candidates = [p for p in candidates if p >= 0]
        if candidates:
            p = min(candidates)
            # Only trim a very large generic navigation prefix.
            if p > 500:
                text = text[p:]

    return text

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def emit_output(key, value):
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        print(f"{key}={value}")
        return
    with open(out, "a", encoding="utf-8") as f:
        if "\n" in str(value):
            marker = "GENESIS_UPSTREAM_EOF"
            f.write(f"{key}<<{marker}\n{value}\n{marker}\n")
        else:
            f.write(f"{key}={value}\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="upstream-sources.json")
    ap.add_argument("--baseline", default="upstream-baseline.json")
    ap.add_argument("--accept", action="store_true",
                    help="Replace the baseline with the current upstream state.")
    args = ap.parse_args()

    src = load_json(args.sources)
    if not src or "sources" not in src:
        raise SystemExit(f"Invalid source list: {args.sources}")

    now = datetime.now(timezone.utc).isoformat()
    current = {"schema": 1, "checked_at": now, "sources": {}}
    errors = []

    for item in src["sources"]:
        name = item["name"]
        url = item["url"]
        try:
            raw = fetch(url)
            normalized = normalize_document(raw)
            if not normalized:
                raise RuntimeError("normalized page text was empty")
            current["sources"][url] = {
                "name": name,
                "sha256": digest(normalized),
                "text_length": len(normalized)
            }
            print(f"OK {name}: {len(normalized)} chars")
        except Exception as exc:
            errors.append(f"- {name}: {url} — {type(exc).__name__}: {exc}")
            print(f"ERROR {name}: {exc}", file=sys.stderr)

    baseline = load_json(args.baseline)

    if baseline is None:
        if errors:
            emit_output("initialized", "false")
            emit_output("changed", "false")
            emit_output("accepted", "false")
            emit_output("summary", "초기 기준값 생성 실패: 일부 원본 페이지를 가져오지 못했습니다.\n" + "\n".join(errors))
            return 0
        write_json(args.baseline, current)
        emit_output("initialized", "true")
        emit_output("changed", "false")
        emit_output("accepted", "false")
        emit_output("summary", f"원본 변경 감지 기준값을 {len(current['sources'])}개 페이지로 초기화했습니다.")
        return 0

    if args.accept:
        if errors:
            emit_output("initialized", "false")
            emit_output("changed", "false")
            emit_output("accepted", "false")
            emit_output("summary", "기준값 갱신 중 일부 페이지를 가져오지 못해 baseline을 변경하지 않았습니다.\n" + "\n".join(errors))
            return 0
        write_json(args.baseline, current)
        emit_output("initialized", "false")
        emit_output("changed", "false")
        emit_output("accepted", "true")
        emit_output("summary", f"현재 원본 상태 {len(current['sources'])}개를 새 기준값으로 승인했습니다.")
        return 0

    old = baseline.get("sources", {})
    changes = []
    for url, cur in current["sources"].items():
        prev = old.get(url)
        if prev is None:
            changes.append(f"- **NEW** {cur['name']} — {url}")
        elif prev.get("sha256") != cur.get("sha256"):
            changes.append(
                f"- **CHANGED** {cur['name']} — {url} "
                f"(text {prev.get('text_length','?')} → {cur.get('text_length','?')})"
            )
    for url, prev in old.items():
        if url not in current["sources"] and not any(url in e for e in errors):
            changes.append(f"- **REMOVED FROM WATCH** {prev.get('name', url)} — {url}")

    summary_parts = []
    if changes:
        summary_parts.append("Genesis 원본에서 한국어판 재검토가 필요한 변경을 감지했습니다.")
        summary_parts.append("")
        summary_parts.extend(changes)
        summary_parts.append("")
        summary_parts.append("번역을 갱신한 뒤 Actions → Check Genesis upstream → Run workflow에서 accept_current=true로 실행하면 새 상태를 기준값으로 승인할 수 있습니다.")
    else:
        summary_parts.append("추적 중인 Genesis 원본 페이지에서 내용 변경을 감지하지 못했습니다.")

    if errors:
        summary_parts.append("")
        summary_parts.append("### 가져오기 실패 (변경 판정에서 제외)")
        summary_parts.extend(errors)

    emit_output("initialized", "false")
    emit_output("accepted", "false")
    emit_output("changed", "true" if changes else "false")
    emit_output("summary", "\n".join(summary_parts))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
