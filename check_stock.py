import os
import requests
from bs4 import BeautifulSoup

URL = "https://tuburiaparate.ro/tuburi-tigari-rollo-micro-slim-blue"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
# Citim variabila de test (implicit False)
FORCE_AVAILABLE = os.environ.get("FORCE_AVAILABLE", "false").lower() == "true"

def send_notification(message):
    if not NTFY_TOPIC:
        print("Eroare: NTFY_TOPIC nu este setat.")
        return

    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": "Stoc Disponibil: Tuburi Rollo!",
            "Priority": "high",
            "Tags": "tada,shopping_cart",
            "Click": URL
        }
    )

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Eroare la accesarea paginii: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text(separator=" ", strip=True).lower()

    if "rollo micro slim blue" not in page_text:
        print("Atenție: Conținutul paginii nu pare cel așteptat.")
        return

    out_of_stock_indicators = [
        "stoc indisponibil",
        "stoc disponibil: 0"
    ]

    is_out_of_stock = any(indicator in page_text for indicator in out_of_stock_indicators)

    # Dacă nu mai e indisponibil SAU dacă am pornit modul de test
    if not is_out_of_stock or FORCE_AVAILABLE:
        prefix = "[TEST] " if FORCE_AVAILABLE else ""
        print(f"{prefix}PRODUSUL ESTE ÎN STOC! Trimit notificare...")
        send_notification(
            f"{prefix}Tuburi Tigari Rollo Micro Slim Blue 200 au revenit în stoc pe tuburiaparate.ro! Apasă aici pentru a comanda."
        )
    else:
        print("Produsul este încă indisponibil.")

if __name__ == "__main__":
    check_stock()