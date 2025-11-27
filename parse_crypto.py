import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://etherscan.io/tokens"
ROOT = "https://etherscan.io"

PRICE_RE = re.compile(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)")


def load_page():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_tokens(html):
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("tr")
    items = []
    seen = set()

    for row in rows:
        a = row.find("a", href=True)
        if not a or "/token/" not in a.get("href", ""):
            continue

        name = a.text.strip()
        href = a["href"]
        url = href if href.startswith("http") else ROOT + href

        text = row.get_text(" ", strip=True)
        m = PRICE_RE.search(text)
        if not m:
            continue

        price = float(m.group(1).replace(",", ""))

        key = (name, url)
        if key in seen:
            continue

        seen.add(key)
        items.append({
            "token": name,
            "price_usd": price,
            "url": url
        })

    # сортировка по убыванию
    items.sort(key=lambda x: x["price_usd"], reverse=True)
    return items


def save_to_json(data, filename="tokens.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main(limit=50):
    print("Загружаю страницу...")
    html = load_page()
    items = parse_tokens(html)

    if limit > 0:
        items = items[:limit]

    save_to_json(items)
    print(f"Сохранено {len(items)} записей в tokens.json")

    print("\nТоп 5 токенов:")
    for item in items[:5]:
        print(f"- {item['token']} — ${item['price_usd']}")


if __name__ == "__main__":
    main()
