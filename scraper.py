import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests

USER_ID = "249331091"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def get_vinted_items():
  session = requests.Session()
  session.headers.update(headers)

  profile_url = f"https://www.vinted.fr/member/{USER_ID}"
  print(f"Chargement de la page profil : {profile_url}...")

  try:
    res = session.get(profile_url, timeout=15)

    if res.status_code != 200:
      print(f"❌ Code erreur Vinted : {res.status_code}")
      return

    soup = BeautifulSoup(res.text, "html.parser")
    formatted_items = []

    # Recherche des éléments d'articles dans le DOM HTML
    item_cards = soup.select(
        ".feed-grid__item, [data-testid='grid-item'], .web_ui__ItemBox__box"
    )

    for card in item_cards:
      # Titre
      title_elem = card.select_one(
          ".item-box__title, [data-testid*='title'], .web_ui__ItemBox__title"
      )
      title = (
          title_elem.text.strip() if title_elem else "Article sans titre"
      )

      # Prix
      price_elem = card.select_one(
          ".item-box__price, [data-testid*='price'], .web_ui__ItemBox__price"
      )
      price = 0.0
      if price_elem:
        price_text = (
            price_elem.text.replace("€", "").replace(",", ".").strip()
        )
        match = re.search(r"\d+(\.\d+)?", price_text)
        if match:
          price = float(match.group())

      # Lien
      link_elem = card.select_one("a[href*='/items/']")
      url = profile_url
      if link_elem and "href" in link_elem.attrs:
        href = link_elem["href"]
        url = href if href.startswith("http") else f"https://www.vinted.fr{href}"

      # ID unique basé sur l'URL ou le hash
      item_id = (
          url.split("/items/")[1].split("-")[0]
          if "/items/" in url
          else str(hash(title + str(price)))
      )

      formatted_items.append({
          "id": item_id,
          "title": title,
          "price": price,
          "url": url,
          "scraped_at": datetime.now().isoformat(),
      })

    with open("data.json", "w", encoding="utf-8") as f:
      json.dump(formatted_items, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(formatted_items)} articles enregistrés dans data.json")

  except Exception as e:
    print(f"❌ Erreur lors du scraping : {e}")


if __name__ == "__main__":
  get_vinted_items()
