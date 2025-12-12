# config.py
"""
Zentrale Konfiguration für beide PiTops
Lädt automatisch die richtige .env Datei
"""

import os
import sys
from dotenv import load_dotenv

# ===== .ENV LADEN =====

def load_env_for_device():
    """Lädt richtige .env basierend auf --device Argument"""
    
    # Via Command-Line: python3 main_pitop1.py --device=pitop1
    for arg in sys.argv:
        if arg.startswith('--device='):
            device = arg.split('=')[1]
            env_file = f'.env.{device}'
            
            if os.path.exists(env_file):
                load_dotenv(env_file)
                print(f"✅ Loaded {env_file}")
                return device
            else:
                print(f"⚠️  {env_file} nicht gefunden!")
    
    # Fallback: DEVICE_ID aus Environment
    device_id = os.getenv('DEVICE_ID')
    if device_id:
        env_file = f'.env.{device_id}'
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"✅ Loaded {env_file}")
            return device_id
    
    # Fallback: .env (default)
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded .env (default)")
        return os.getenv('DEVICE_ID', 'unknown')
    
    print("❌ Keine .env Datei gefunden!")
    return 'unknown'

# Config laden
CURRENT_DEVICE = load_env_for_device()

# ===== DEVICE INFO =====
DEVICE_ID = os.getenv('DEVICE_ID', CURRENT_DEVICE)
USER_NAME = os.getenv('USER_NAME', 'Alicia')

# ===== SUPABASE =====
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# ===== DISCORD =====
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

# ===== USER CONFIG =====
USER_WEIGHT = int(os.getenv('USER_WEIGHT', 55))
USER_HEIGHT = int(os.getenv('USER_HEIGHT', 165))

# ===== HARDWARE FLAGS =====
HAS_CO2_SENSOR = os.getenv('HAS_CO2_SENSOR', 'false').lower() == 'true'
HAS_BUTTONS = os.getenv('HAS_BUTTONS', 'false').lower() == 'true'
HAS_LED = os.getenv('HAS_LED', 'false').lower() == 'true'
HAS_BUZZER = os.getenv('HAS_BUZZER', 'false').lower() == 'true'
HAS_STEP_COUNTER = os.getenv('HAS_STEP_COUNTER', 'false').lower() == 'true'

# ===== PITOP 4 EXPANSION PORTS (PiTop 1) =====
# Verfügbare Ports: D0, D1, D2, D3, D4, D5, D6, D7
# PiTop steuert Farben und Features selbst
BUTTON1_PORT = os.getenv('BUTTON1_PORT', 'D0')
BUTTON2_PORT = os.getenv('BUTTON2_PORT', 'D1')
LED_PORT = os.getenv('LED_PORT', 'D2')
BUZZER_PORT = os.getenv('BUZZER_PORT', 'D3')

# ===== I2C SENSOREN =====
# CO2 & Step Counter kommunizieren über I2C
I2C_BUS = int(os.getenv('I2C_BUS', 1))
CO2_SENSOR_ADDRESS = int(os.getenv('CO2_SENSOR_ADDRESS', '0x5A'), 16)
STEP_SENSOR_ADDRESS = int(os.getenv('STEP_SENSOR_ADDRESS', '0x14'), 16)

# ===== TIMER =====
WORK_DURATION = 30 * 60      # 30 Minuten
BREAK_DURATION = 10 * 60     # 10 Minuten

# ===== BUTTON SETTINGS =====
SHORT_PRESS_MAX = 2.0         # < 2s = Kurz
END_SESSION_PRESS = 5.0       # 5+s = Session beenden
DOUBLE_CLICK_INTERVAL = 0.5   # 0.5s zwischen Klicks für Doppelklick

# ===== CO2 =====
CO2_WARNING_THRESHOLD = 600
CO2_CRITICAL_THRESHOLD = 800
CO2_MEASUREMENT_INTERVAL = 120  # 2 Minuten

# ===== BUZZER PATTERNS =====
BUZZER_CO2_DURATION = 0.2
BUZZER_CO2_INTERVAL = 0.3
BUZZER_CO2_REPETITIONS = 5
BUZZER_TIMER_DURATION = 2.0

# ===== MOVEMENT TRACKING =====
CALORIES_PER_STEP = 0.05      # ~0.05 kcal pro Schritt
METERS_PER_STEP = 0.75        # ~0.75m pro Schritt

# ===== MONITORING =====
STEP_UPDATE_INTERVAL = 5      # Schrittzähler Update-Interval (Sekunden)
PAUSE_POLL_INTERVAL = 1       # DB Polling Interval (Sekunden)

# ===== DEBUG OUTPUT =====
if __name__ != '__main__':  # Nur beim Import
    print(f"\n{'='*60}")
    print(f"🔧 CONFIG LOADED: {DEVICE_ID}")
    print(f"{'='*60}")
    print(f"User: {USER_NAME} ({USER_WEIGHT}kg, {USER_HEIGHT}cm)")
    print(f"Supabase: {'✅' if SUPABASE_URL else '❌'}")
    print(f"Discord: {'✅' if DISCORD_WEBHOOK_URL else '❌'}")
    
    print(f"\n🔌 PITOP PORTS:")
    print(f"  Button 1: {BUTTON1_PORT}")
    print(f"  Button 2: {BUTTON2_PORT}")
    print(f"  LED: {LED_PORT}")
    print(f"  Buzzer: {BUZZER_PORT}")
    print(f"  I2C Bus: {I2C_BUS}")
    
    print(f"\n📊 HARDWARE:")
    print(f"  CO2 Sensor: {'✅' if HAS_CO2_SENSOR else '❌'}")
    print(f"  Buttons: {'✅' if HAS_BUTTONS else '❌'}")
    print(f"  LED: {'✅' if HAS_LED else '❌'}")
    print(f"  Buzzer: {'✅' if HAS_BUZZER else '❌'}")
    print(f"  Step Counter: {'✅' if HAS_STEP_COUNTER else '❌'}")
    
    print(f"\n⏱️  TIMERS:")
    print(f"  Work: {WORK_DURATION // 60} Minuten")
    print(f"  Break: {BREAK_DURATION // 60} Minuten")
    
    print(f"{'='*60}\n")