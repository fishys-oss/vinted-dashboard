import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

USER_ID = "249331091"
DATA_FILE = "data.json"


def load_previous_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return {item["id"]: item for item in json.load(f)}
    except Exception as e:
      print(f"Erreur chargement ancien data.json: {e}")
  return {}


def get_vinted_items():
  previous_items = load_previous_data()
  profile_url = f"https://www.vinted.fr/member/{USER_ID}"
  current_items = {}

  with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ],
    )

    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1400, "height": 900},
        locale="fr-FR",
    )

    # Masquer l'indicateur d'automatisation Playwright
    page = context.new_page()
    page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () =>"
        " undefined})"
    )

    try:
      page.goto(profile_url, wait_until="networkidle", timeout=30000)

      # Scroll fluide pour déclencher le chargement des images (Lazy-Loading)
      page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
      page.wait_for_timeout(1000)
      page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
      page.wait_for_timeout(1500)

      soup = BeautifulSoup(page.content(), "html.parser")
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
        img_elem = card.select_one("img")

        if price_elem:
          price_text = (
              price_elem.text.replace("€", "").replace(",", ".").strip()
          )
          match = re.search(r"\d+(\.\d+)?", price_text)
          price = float(match.group()) if match else 0.0

          title = (
              title_elem.text.strip() if title_elem else "Article Vinted"
          )
          url = profile_url
          if link_elem and "href" in link_elem.attrs:
            href = link_elem["href"]
            url = (
                href if href.startswith("http") else f"https://www.vinted.fr{href}"
            )

          # Extraction forcée de l'image
          img_url = ""
          if img_elem:
            img_url = (
                img_elem.get("src")
                or img_elem.get("data-src")
                or img_elem.get("data-srcset", "").split(" ")[0]
                or img_elem.get("srcset", "").split(" ")[0]
                or ""
            )

          item_id = (
              url.split("/items/")[1].split("-")[0]
              if "/items/" in url
              else str(hash(title + str(price)))
          )

          # Date fixe de première détection
          published_at = previous_items.get(item_id, {}).get("published_at")
          if not published_at:
            published_at = datetime.now().strftime("%d/%m/%Y")

          current_items[item_id] = {
              "id": item_id,
              "title": title,
              "price": price,
              "url": url,
              "image_url": img_url,
              "published_at": published_at,
              "is_sold": False,
              "is_pending": False,
          }

    except Exception as e:
      print(f"Erreur scraping: {e}")
    finally:
      browser.close()

  # Sécurité : Si aucun article n'a été trouvé (ex: blocage), on ne vide pas tout par erreur
  if not current_items and previous_items:
    print("Avertissement: Aucun article récupéré. Conservation de l'ancien état.")
    return

  final_items = []
  for item_id, item in current_items.items():
    final_items.append(item)

  for item_id, prev_item in previous_items.items():
    if item_id not in current_items:
      if not prev_item.get("is_sold", False) and not prev_item.get(
          "is_removed", False
      ):
        prev_item["is_pending"] = True
      final_items.append(prev_item)

  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(final_items, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
  get_vinted_items()
