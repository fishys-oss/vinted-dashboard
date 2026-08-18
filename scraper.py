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
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def get_vinted_items():
  session = requests.Session()
  session.headers.update(headers)

  try:
    print("Initialisation du cookie de session Vinted...")
    session.get("https://www.vinted.fr", timeout=10)

    api_url = (
        f"https://www.vinted.fr/api/v2/users/{USER_ID}/items?page=1&per_page=20"
    )
    print(f"Extraction des articles pour l'utilisateur {USER_ID}...")
    res = session.get(api_url, timeout=10)

    if res.status_code == 200:
      data = res.json()
      items_data = data.get("items", [])

      formatted_items = []
      for item in items_data:
        formatted_items.append({
            "id": str(item.get("id")),
            "title": item.get("title"),
            "price": float(item.get("price", {}).get("amount", 0)),
            "url": item.get("url"),
            "scraped_at": datetime.now().isoformat(),
        })

      with open("data.json", "w", encoding="utf-8") as f:
        json.dump(formatted_items, f, indent=2, ensure_ascii=False)

      print(f"✅ {len(formatted_items)} articles enregistrés dans data.json")
    else:
      print(f"❌ Code erreur Vinted : {res.status_code}")

  except Exception as e:
    print(f"❌ Erreur lors de la requête : {e}")


if __name__ == "__main__":
  get_vinted_items()
