# services/notification_service.py über Telegramm Bot
import requests
import config

class NotificationService:
    def __init__(self):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        print("✅ Notification Service initialized")
    
    def send_message(self, message):
        """Send Telegram message"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✉️  Message sent: {message[:50]}...")
            else:
                print(f"❌ Telegram error: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
    
    def notify_work_done(self, steps=None):
        message = "🎉 *Work Session beendet!*\n\n"
        message += "Zeit für eine Pause! 🧘‍♂️\n"
        if steps:
            message += f"📊 Schritte: {steps}\n"
        self.send_message(message)
    
    def notify_pause_done(self):
        message = "⚡ *Pause vorbei!*\n\nZurück an die Arbeit! 💪"
        self.send_message(message)
    
    def notify_co2_high(self, value):
        message = f"🌡️ *CO2 Warnung!*\n\nAktuell: {value} ppm\n\n🪟 Bitte lüften!"
        self.send_message(message)