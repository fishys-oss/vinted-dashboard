import json
from datetime import datetime
import requests

USER_ID = "249331091"

# Headers reproduisant un vrai navigateur
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
    # Step 1 : Initialisation des cookies de session
    print("Initialisation de la session Vinted...")
    init_res = session.get("https://www.vinted.fr", timeout=15)

    # Step 2 : Récupération des articles via la route API des membres
    api_url = f"https://www.vinted.fr/api/v2/users/{USER_ID}/items?page=1&per_page=20"
    print(f"Interrogation de l'API : {api_url}")

    res = session.get(api_url, timeout=15)

    if res.status_code == 200:
      data = res.json()
      items_data = data.get("items", [])

      formatted_items = []
      for item in items_data:
        # Traitement du prix (structure objet ou valeur simple)
        price_val = item.get("price")
        if isinstance(price_val, dict):
          price = float(price_val.get("amount", 0))
        elif isinstance(price_val, (int, float, str)):
          price = float(price_val)
        else:
          price = 0.0

        formatted_items.append({
            "id": str(item.get("id")),
            "title": item.get("title", "Article Vinted"),
            "price": price,
            "url": item.get("url", ""),
            "scraped_at": datetime.now().isoformat(),
        })

      # Écriture dans le fichier JSON
      with open("data.json", "w", encoding="utf-8") as f:
        json.dump(formatted_items, f, indent=2, ensure_ascii=False)

      print(f"✅ {len(formatted_items)} articles enregistrés dans data.json")

    else:
      print(f"❌ Erreur API Vinted (Statut {res.status_code})")
      # Si échec, écriture d'un fichier vide pour éviter de casser le pipeline
      with open("data.json", "w", encoding="utf-8") as f:
        json.dump([], f)

  except Exception as e:
    print(f"❌ Erreur d'exécution : {e}")


if __name__ == "__main__":
  get_vinted_items()
