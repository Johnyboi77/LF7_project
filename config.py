# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ===== HARDWARE GPIO PINS =====
BUTTON1_PIN = 17  # Arbeit + Session Management
BUTTON2_PIN = 27  # Pause
BUZZER_PIN = 18
LED_RED_PIN = 23

# ===== DATENBANK =====
DB_PATH = "learning_assistant.db"

# ===== DISCORD BENACHRICHTIGUNGEN =====
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
USER_NAME = "Alicia"

# ===== TIMER =====
WORK_DURATION = 30 * 60    # 30 Minuten
BREAK_DURATION = 10 * 60   # 10 Minuten

# ===== BUTTON EINSTELLUNGEN =====
SHORT_PRESS_MAX = 2.0      # < 2 Sek = Kurz
LONG_PRESS_MIN = 2.0       # 2-5 Sek = Lang (Reset)
END_SESSION_PRESS = 5.0    # 5+ Sek = Session beenden

# ===== CO2 SCHWELLENWERTE =====
CO2_WARNING_THRESHOLD = 600
CO2_CRITICAL_THRESHOLD = 800

# ===== BUZZER PATTERNS =====
BUZZER_CO2_DURATION = 0.2
BUZZER_CO2_INTERVAL = 0.3
BUZZER_CO2_REPETITIONS = 5
BUZZER_TIMER_DURATION = 2.0