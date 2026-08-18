import json
from datetime import datetime
import requests

USER_ID = "249331091"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": f"https://www.vinted.fr/member/{USER_ID}",
}


def get_vinted_items():
  session = requests.Session()
  session.headers.update(headers)

  try:
    # 1. Visite du profil pour récupérer les cookies de session Vinted
    print(f"Initialisation de la session pour l'utilisateur {USER_ID}...")
    session.get(f"https://www.vinted.fr/member/{USER_ID}", timeout=15)

    # 2. Test de la route API Wardrobe (Dressing)
    api_url = f"https://www.vinted.fr/api/v2/users/{USER_ID}/wardrobe?page=1&per_page=20"
    print(f"Extraction des articles via : {api_url}")

    res = session.get(api_url, timeout=15)

    # 3. Fallback sur le catalogue si la route wardrobe échoue
    if res.status_code == 404:
      print("Route /wardrobe introuvable, essai via /catalog/items...")
      api_url = f"https://www.vinted.fr/api/v2/catalog/items?user_id={USER_ID}&per_page=20"
      res = session.get(api_url, timeout=15)

    if res.status_code == 200:
      data = res.json()
      items_data = data.get("items", [])

      formatted_items = []
      for item in items_data:
        # Traitement du prix (objet ou valeur brute)
        price_val = item.get("price")
        if isinstance(price_val, dict):
          price = float(price_val.get("amount", 0))
        elif isinstance(price_val, (int, float, str)):
          price = float(price_val)
        else:
          price = 0.0

        item_id = str(item.get("id"))
        title = item.get("title") or "Article Vinted"
        url = item.get("url") or f"https://www.vinted.fr/items/{item_id}"

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

    else:
      print(f"❌ Erreur API Vinted (Statut {res.status_code})")

  except Exception as e:
    print(f"❌ Erreur : {e}")


if __name__ == "__main__":
  get_vinted_items()
