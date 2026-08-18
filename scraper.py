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
}


def get_vinted_items():
  session = requests.Session()
  session.headers.update(headers)

  try:
    print(f"Initialisation de la session pour l'utilisateur {USER_ID}...")
    # 1. Requête sur la page d'accueil pour récupérer le cookie de session et les headers anonymes
    init_res = session.get("https://www.vinted.fr", timeout=15)

    # Récupération du jeton d'accès anonyme si présent dans les cookies
    anon_token = session.cookies.get("access_token_web")
    if anon_token:
      session.headers.update({"Authorization": f"Bearer {anon_token}"})

    # 2. Endpoint exact des articles du membre
    api_url = f"https://www.vinted.fr/api/v2/users/{USER_ID}/items?page=1&per_page=20"
    print(f"Extraction ciblée du dressing via : {api_url}")

    res = session.get(api_url, timeout=15)

    if res.status_code == 200:
      data = res.json()
      items_data = data.get("items", [])

      formatted_items = []
      for item in items_data:
        # Formatage du prix
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

      print(f"✅ {len(formatted_items)} de VOS articles ont été enregistrés.")

    else:
      print(f"❌ Erreur API Vinted (Statut {res.status_code})")

  except Exception as e:
    print(f"❌ Erreur : {e}")


if __name__ == "__main__":
  get_vinted_items()
