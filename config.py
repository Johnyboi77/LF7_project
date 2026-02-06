"""
Zentrale Konfiguration - Lädt automatisch .env.pitop1 oder .env.pitop2
basierend auf dem Script-Namen oder DEVICE_OVERRIDE
"""

import os
import sys
from dotenv import load_dotenv

# ===== .ENV LADEN =====
def load_env_for_device():
    
    # 1. PRIORITÄT: Environment Variable Override
    if os.environ.get('DEVICE_OVERRIDE'):
        device = os.environ.get('DEVICE_OVERRIDE')
        print(f"✅ Device Override: {device}")
    
    else:
        # 2. Script-Name extrahieren (z.B. "main_pitop1.py" → "pitop1")
        script_name = os.path.basename(sys.argv[0])
        
        if 'pitop1' in script_name:
            device = 'pitop1'
        elif 'pitop2' in script_name:
            device = 'pitop2'
        else:
            # 3. Fallback: Via Command-Line Argument
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
                print("   Oder setze: DEVICE_OVERRIDE=pitop1")
                sys.exit(1)
    
    # .env File laden
    env_file = f'.env.{device}'
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded {env_file}")
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

# ===== BUTTON SETTINGS (NEU) =====
# Timing für Druckerkennung
SHORT_PRESS_MAX = float(os.getenv('SHORT_PRESS_MAX', '0.5'))  # Max 0.5s für Short Press

# Button 2 - Long Press Schwellen
CANCEL_PRESS = float(os.getenv('CANCEL_PRESS', '3.0'))        # 3s = Letzte Aktion stornieren
END_SESSION_PRESS = float(os.getenv('END_SESSION_PRESS', '7.0'))  # 7s = Session beenden

# Legacy (für Kompatibilität, falls noch verwendet)
DOUBLE_CLICK_INTERVAL = float(os.getenv('DOUBLE_CLICK_INTERVAL', '0.5'))

# CO2 Thresholds
CO2_WARNING_THRESHOLD = int(os.getenv('CO2_WARNING_THRESHOLD', '600'))
CO2_CRITICAL_THRESHOLD = int(os.getenv('CO2_CRITICAL_THRESHOLD', '800'))
CO2_MEASUREMENT_INTERVAL = int(os.getenv('CO2_MEASUREMENT_INTERVAL', '120'))
CO2_CHECK_INTERVAL = int(os.getenv('CO2_CHECK_INTERVAL', '30'))

# LED
LED_BLINK_FAST = float(os.getenv('LED_BLINK_FAST', '0.1'))

# Buzzer Patterns
BUZZER_CO2_DURATION = float(os.getenv('BUZZER_CO2_DURATION', '0.2'))
BUZZER_CO2_INTERVAL = float(os.getenv('BUZZER_CO2_INTERVAL', '0.3'))
BUZZER_CO2_REPETITIONS = int(os.getenv('BUZZER_CO2_REPETITIONS', '5'))
BUZZER_TIMER_DURATION = float(os.getenv('BUZZER_TIMER_DURATION', '2.0'))

# Movement Tracking
CALORIES_PER_STEP = float(os.getenv('CALORIES_PER_STEP', '0.05'))
METERS_PER_STEP = float(os.getenv('METERS_PER_STEP', '0.75'))

# Monitoring Intervals
STEP_UPDATE_INTERVAL = int(os.getenv('STEP_UPDATE_INTERVAL', '5'))
PAUSE_POLL_INTERVAL = int(os.getenv('PAUSE_POLL_INTERVAL', '1'))

# ===== DEBUG OUTPUT =====
if __name__ == '__main__':
    # Wenn direkt ausgeführt, zeige alle Werte
    print("\n" + "="*50)
    print("📋 AKTUELLE KONFIGURATION")
    print("="*50)
    print(f"Device:          {DEVICE_ID}")
    print(f"User:            {USER_NAME}")
    print(f"Gewicht:         {USER_WEIGHT} kg")
    print(f"Größe:           {USER_HEIGHT} cm")
    print("-"*50)
    print("⏱️  BUTTON SETTINGS:")
    print(f"Short Press Max: {SHORT_PRESS_MAX}s")
    print(f"Cancel Press:    {CANCEL_PRESS}s (Storno)")
    print(f"End Session:     {END_SESSION_PRESS}s (Session beenden)")
    print("-"*50)
    print("⏱️  TIMER:")
    print(f"Work Duration:   {WORK_DURATION // 60} min")
    print(f"Break Duration:  {BREAK_DURATION // 60} min")
    print("="*50)
else:
    print(f"🔧 CONFIG: {DEVICE_ID} - {USER_NAME}")