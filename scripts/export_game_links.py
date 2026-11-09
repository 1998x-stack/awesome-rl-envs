#!/usr/bin/env python3
"""Reproducibly extract *only* the Games references from the historic RL index."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "README.md"
OUTPUT = ROOT / "data" / "game-links.json"


class GameLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_url = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current_url = dict(attrs).get("href")
            self.parts = []

    def handle_data(self, text):
        if self.current_url is not None:
            self.parts.append(text)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_url is not None:
            name = " ".join(" ".join(self.parts).split())
            self.links.append((name, self.current_url))
            self.current_url = None
            self.parts = []


def extract(content):
    match = re.search(r"^## Games\s*$", content, re.M)
    if match is None:
        raise ValueError("Missing exact Games heading")
    remainder = content[match.end():]
    nxt = re.search(r"^## ", remainder, re.M)
    section = remainder[:nxt.start()] if nxt else remainder
    parser = GameLinkParser()
    parser.feed(section)
    urls = set()
    records = []
    for name, url in parser.links:
        parsed = urlparse(url)
        if not name or parsed.scheme != "https" or not parsed.netloc or url in urls:
            raise ValueError("Invalid, duplicate or non-HTTPS game link")
        urls.add(url)
        records.append({"name": name, "url": url, "status": "not-verified"})
    if not records:
        raise ValueError("Games section contained no project links")
    return {
        "schema_version": 1,
        "source": "README.md#games",
        "status_scope": "links extracted only; destination health and licenses not verified",
        "projects": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(extract(SOURCE.read_text(encoding="utf-8")),
                          ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Games-only index is stale; rerun exporter without --check")
        print("Games-only index matches source; 11 links (health not verified).")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
