import argparse
import json
import os
import re

import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://etherscan.io/tokens"
ROOT = "https://etherscan.io"
PRICE_RE = re.compile(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)")

def load_html(source):
    if not source:
        resp = requests.get(DEFAULT_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        return resp.text
    if source.startswith("http://") or source.startswith("https://"):
        resp = requests.get(source, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        return resp.text
    with open(source, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_tokens(html):
    soup = BeautifulSoup(html, "lxml")
    out = []
    seen = set()

    rows = soup.select("tr")
    if not rows:
        rows = soup.select("a[href*='/token/']")

    for node in rows:
        if node.name == "tr":
            a = node.find("a", href=True)
            if not a or "/token/" not in a.get("href", ""):
                continue
            name = a.get_text(" ", strip=True)
            href = a["href"]
            text = node.get_text(" ", strip=True)
        else:
            a = node
            name = a.get_text(" ", strip=True)
            href = a.get("href", "")
            text = node.get_text(" ", strip=True)

        m = PRICE_RE.search(text)
        if not m:
            continue
        price = float(m.group(1).replace(",", ""))
        url = href if href.startswith("http") else ROOT.rstrip("/") + href

        key = (name, url)
        if key in seen:
            continue
        seen.add(key)
        out.append({"token": name, "price_usd": price, "url": url})

    out.sort(key=lambda x: x["price_usd"], reverse=True)
    return out

def main():
    ap = argparse.ArgumentParser(description="Etherscan tokens scraper to JSON")
    ap.add_argument("--source", "-s", default=None, help="URL или путь к локальному .html")
    ap.add_argument("--limit", "-n", type=int, default=50, help="Сколько позиций сохранить")
    ap.add_argument("--out", "-o", default="tokens.json", help="Куда сохранить JSON")
    args = ap.parse_args()

    html = load_html(args.source)
    items = parse_tokens(html)
    if args.limit and args.limit > 0:
        items = items[:args.limit]

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(items)} items to {args.out}")
    for r in items[:3]:
        print(f"- {r['token']} | ${r['price_usd']} | {r['url']}")

if __name__ == "__main__":
    main()