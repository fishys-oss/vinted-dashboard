import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests

# ⚠️ REMPLACE PAR L'URL DE TON PROFIL VINTED
VINTED_URL = "https://www.vinted.fr/member/249331091"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def main():
  print("Extraction des articles Vinted...")
  try:
    response = requests.get(VINTED_URL, headers=HEADERS, timeout=15)
    if response.status_code != 200:
      print(f"Erreur HTTP : {response.status_code}")
      return

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all(
        "div", class_=re.compile("feed-grid__item|item-box")
    )

    items = []
    for card in cards:
      title_elem = card.find("a", class_=re.compile("title|link"))
      price_elem = card.find("p", class_=re.compile("price|text"))

      if title_elem and price_elem:
        title = title_elem.text.strip()
        url = (
            "https://www.vinted.fr" + title_elem["href"]
            if title_elem["href"].startswith("/")
            else title_elem["href"]
        )
        raw_price = price_elem.text.replace("€", "").replace(",", ".").strip()
        price = float(raw_price) if raw_price else 0.0

        items.append({
            "id": url.split("/")[-1],
            "title": title,
            "price": price,
            "url": url,
            "scraped_at": datetime.now().isoformat(),
        })

    with open("data.json", "w", encoding="utf-8") as f:
      json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Succès : {len(items)} articles enregistrés.")
  except Exception as e:
    print(f"Erreur : {e}")


if __name__ == "__main__":
  main()
