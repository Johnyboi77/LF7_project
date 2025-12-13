#!/usr/bin/env python3
"""
Zentrale Konfiguration - Lädt automatisch .env.pitop1 oder .env.pitop2
basierend auf dem Script-Namen
"""

import os
import sys
from dotenv import load_dotenv

# ===== .ENV LADEN =====
def load_env_for_device():
    """Lädt .env automatisch basierend auf Script-Namen"""
    
    # Script-Name extrahieren (z.B. "main_pitop1.py" → "pitop1")
    script_name = os.path.basename(sys.argv[0])  # z.B. "main_pitop1.py"
    
    # Versuche Device-ID aus Script-Namen zu extrahieren
    if 'pitop1' in script_name:
        device = 'pitop1'
    elif 'pitop2' in script_name:
        device = 'pitop2'
    else:
        # Fallback: Via Command-Line Argument
        for arg in sys.argv:
            if arg.startswith('--device='):
                device = arg.split('=')[1]
                break
        else:
            # Kein Device erkannt
            print("❌ Konnte Device nicht erkennen!")
            print(f"   Script-Name: {script_name}")
            print("   Erwartet: main_pitop1.py oder main_pitop2.py")
            print("   Oder nutze: --device=pitop1")
            sys.exit(1)
    
    # .env File laden
    env_file = f'.env.{device}'
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded {env_file} (auto-detected from {script_name})")
        return device
    else:
        print(f"❌ {env_file} nicht gefunden!")
        sys.exit(1)

# Config laden
CURRENT_DEVICE = load_env_for_device()

# ===== AUS .ENV LADEN =====
DEVICE_ID = os.getenv('DEVICE_ID', CURRENT_DEVICE)
USER_NAME = os.getenv('USER_NAME', 'Alicia')
USER_WEIGHT = int(os.getenv('USER_WEIGHT', '55'))
USER_HEIGHT = int(os.getenv('USER_HEIGHT', '165'))

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

# ===== HARDCODED KONSTANTEN =====

# Timer Durations
WORK_DURATION = 30 * 60      # 30 Minuten
BREAK_DURATION = 10 * 60     # 10 Minuten

# Button Settings
SHORT_PRESS_MAX = 2.0
END_SESSION_PRESS = 5.0
DOUBLE_CLICK_INTERVAL = 0.5

# CO2 Thresholds
CO2_WARNING_THRESHOLD = 600
CO2_CRITICAL_THRESHOLD = 800
CO2_MEASUREMENT_INTERVAL = 120

# Buzzer Patterns
BUZZER_CO2_DURATION = 0.2
BUZZER_CO2_INTERVAL = 0.3
BUZZER_CO2_REPETITIONS = 5
BUZZER_TIMER_DURATION = 2.0

# Movement Tracking
CALORIES_PER_STEP = 0.05
METERS_PER_STEP = 0.75

# Monitoring Intervals
STEP_UPDATE_INTERVAL = 5
PAUSE_POLL_INTERVAL = 1

# ===== DEBUG OUTPUT =====
if __name__ != '__main__':
    print(f"🔧 CONFIG: {DEVICE_ID} - {USER_NAME}")