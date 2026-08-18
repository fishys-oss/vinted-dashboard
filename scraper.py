import json
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USER_ID = "249331091"


def get_vinted_items():
  profile_url = f"https://www.vinted.fr/member/{USER_ID}"
  print(f"Lancement du navigateur vers : {profile_url}...")

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        locale="fr-FR",
    )
    page = context.new_page()

    try:
      page.goto(profile_url, wait_until="domcontentloaded", timeout=30000)
      page.wait_for_timeout(3000)  # Pause pour laisser charger le JS React

      content = page.content()
      soup = BeautifulSoup(content, "html.parser")

      formatted_items = []

      # Recherche des cartes d'articles dans la grille du profil
      cards = soup.select(
          ".feed-grid__item, [data-testid*='grid-item'],"
          " .web_ui__ItemBox__box, .item-box"
      )

      for card in cards:
        title_elem = card.select_one(
            ".item-box__title, [data-testid*='title'],"
            " .web_ui__ItemBox__title"
        )
        price_elem = card.select_one(
            ".item-box__price, [data-testid*='price'],"
            " .web_ui__ItemBox__price"
        )
        link_elem = card.select_one("a[href*='/items/']")

        if price_elem:
          price_text = (
              price_elem.text.replace("€", "").replace(",", ".").strip()
          )
          try:
            # Extraction des chiffres du prix
            import re

            match = re.search(r"\d+(\.\d+)?", price_text)
            price = float(match.group()) if match else 0.0
          except Exception:
            price = 0.0

          title = (
              title_elem.text.strip() if title_elem else "Article Vinted"
          )

          url = profile_url
          if link_elem and "href" in link_elem.attrs:
            href = link_elem["href"]
            url = (
                href if href.startswith("http") else f"https://www.vinted.fr{href}"
            )

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

      print(f"✅ {len(formatted_items)} de VOS articles enregistrés.")

      with open("data.json", "w", encoding="utf-8") as f:
        json.dump(formatted_items, f, indent=2, ensure_ascii=False)

    except Exception as e:
      print(f"❌ Erreur Playwright : {e}")
    finally:
      browser.close()


if __name__ == "__main__":
  get_vinted_items()
