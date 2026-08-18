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
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def get_vinted_items():
  session = requests.Session()
  session.headers.update(headers)

  try:
    print("Initialisation des cookies de session Vinted...")
    # 1. Visite du profil pour récupérer le cookie de session Vinted
    profile_res = session.get(
        f"https://www.vinted.fr/member/{USER_ID}", timeout=15
    )

    # Récupération du jeton Web s'il est présent
    anon_token = session.cookies.get("access_token_web")
    if anon_token:
      session.headers.update({"Authorization": f"Bearer {anon_token}"})

    # 2. Requête sur l'API des membres avec l'en-tête Referer obligatoire
    session.headers.update(
        {"Referer": f"https://www.vinted.fr/member/{USER_ID}"}
    )
    api_url = f"https://www.vinted.fr/api/v2/users/{USER_ID}/items?page=1&per_page=20&order=relevance"

    print(f"Extraction ciblée du dressing {USER_ID}...")
    res = session.get(api_url, timeout=15)

    # 3. Fallback sur l'API catalogue filtrée par ID utilisateur avec les bons en-têtes
    if res.status_code == 404:
      print("Tentative via la route catalogue utilisateur...")
      api_url = f"https://www.vinted.fr/api/v2/catalog/items?user_id={USER_ID}&per_page=20"
      res = session.get(api_url, timeout=15)

    if res.status_code == 200:
      data = res.json()
      items_data = data.get("items", [])

      # Filtrage de sécurité : conserver uniquement les articles appartenant au USER_ID
      formatted_items = []
      for item in items_data:
        user_info = item.get("user", {})
        item_user_id = str(user_info.get("id", ""))

        # Validation de l'ID propriétaire si présent dans la réponse
        if item_user_id and item_user_id != USER_ID:
          continue

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

      print(f"✅ {len(formatted_items)} de VOS articles enregistrés.")
    else:
      print(f"❌ Code erreur Vinted : {res.status_code}")

  except Exception as e:
    print(f"❌ Erreur : {e}")


if __name__ == "__main__":
  get_vinted_items()
