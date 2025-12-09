# test_discord.py
"""
Discord Webhook Test
"""

import os
from dotenv import load_dotenv
import requests

# .env Datei laden
load_dotenv()

# Webhook URL holen
webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
user_name = os.getenv("USER_NAME", "Alicia")

print("\n" + "="*60)
print("🧪 DISCORD WEBHOOK TEST")
print("="*60 + "\n")

# Prüfen ob URL geladen wurde
if not webhook_url:
    print("❌ FEHLER: DISCORD_WEBHOOK_URL nicht gefunden!")
    print("\n📋 Checkliste:")
    print("   1. Ist die .env Datei im richtigen Ordner?")
    print("   2. Steht DISCORD_WEBHOOK_URL= in der .env Datei?")
    print("   3. Wurde die Webhook-URL korrekt kopiert?")
    print("\n💡 .env Datei sollte hier sein:")
    print(f"   {os.getcwd()}/.env")
    exit(1)

print(f"✅ Webhook-URL gefunden")
print(f"✅ Nutzer: {user_name}\n")

# Test-Nachricht zusammenstellen
embed = {
    "title": f"👋 Hey {user_name}!",
    "description": (
        "**🧪 Discord Test erfolgreich!**\n\n"
        "Wenn du diese Nachricht siehst, funktioniert alles! ✅\n\n"
        "Das Learning Assistant System ist bereit."
    ),
    "color": 5763719,  # Türkis
    "thumbnail": {
        "url": "https://em-content.zobj.net/thumbs/160/twitter/348/party-popper_1f389.png"
    },
    "footer": {
        "text": "Learning Assistant Test"
    }
}

payload = {"embeds": [embed]}

# An Discord senden
print("📤 Sende Test-Nachricht an Discord...\n")

try:
    response = requests.post(webhook_url, json=payload, timeout=10)
    
    if response.status_code == 204:
        print("="*60)
        print("✅ ERFOLG!")
        print("="*60)
        print("\n🎉 Test-Nachricht wurde an Discord gesendet!")
        print(f"📱 Schau in deinen Discord-Channel nach der Nachricht.\n")
        print("✅ Discord-Integration funktioniert!")
        print("\n➡️  Nächster Schritt: python3 main.py")
        print("="*60 + "\n")
    
    elif response.status_code == 404:
        print("="*60)
        print("❌ FEHLER 404: Webhook nicht gefunden")
        print("="*60)
        print("\n💡 Mögliche Ursachen:")
        print("   1. Webhook-URL ist falsch/veraltet")
        print("   2. Webhook wurde in Discord gelöscht")
        print("   3. Channel wurde gelöscht")
        print("\n🔧 Lösung:")
        print("   1. Neuen Webhook in Discord erstellen")
        print("   2. Neue URL in .env Datei eintragen")
        print("="*60 + "\n")
    
    else:
        print(f"⚠️  Unerwarteter Status-Code: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.Timeout:
    print("❌ FEHLER: Zeitüberschreitung")
    print("💡 Überprüfe deine Internet-Verbindung")

except requests.exceptions.RequestException as e:
    print(f"❌ FEHLER: {e}")
    print("💡 Überprüfe deine Internet-Verbindung")

except Exception as e:
    print(f"❌ Unerwarteter Fehler: {e}")