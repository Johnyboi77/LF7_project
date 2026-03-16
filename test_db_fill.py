"""Supabase Datenbank mit Test-Daten füllen"""

import os
import sys
from datetime import datetime

# ⚠️ WICHTIG: Device Override MUSS VOR import config stehen!
os.environ['DEVICE_OVERRIDE'] = 'pitop2'

import config
from supabase import create_client
import uuid


def main():
    print("\n" + "="*50)
    print("📝 SUPABASE DATENBANK FÜLLEN")
    print("="*50 + "\n")

    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("❌ SUPABASE Credentials fehlen!")
        return 1

    try:
        client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        print("✅ Client erstellt\n")
    except Exception as e:
        print(f"❌ Fehler beim Client erstellen: {e}")
        return 1

    # Generiere IDs
    session_id = str(uuid.uuid4())

    # 1. Sessions Tabelle
    print("📊 Füge Daten in 'sessions' ein...")
    try:
        client.table('sessions').insert({
            'session_id': session_id,
            'device_id': config.DEVICE_ID,
            'user_name': '',
            'timer_status': '',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'user_weight': 0.0,
            'user_height': 0.0,
            'pause_count': 0,
            'total_work_time': 0,
            'total_pause_time': 0,
            'created_at': datetime.now().isoformat()
        }).execute()
        print("  ✅ sessions: OK")
    except Exception as e:
        print(f"  ❌ sessions: {e}")
        return 1

    # 2. Co2_measurements Tabelle
    print("📊 Füge Daten in 'co2_measurements' ein...")
    try:
        client.table('co2_measurements').insert({
            'session_id': session_id,
            'co2_level': 0,
            'tvoc_level': 0,
            'is_alarm': False,
            'alarm_type': '',
            'device_id': config.DEVICE_ID,
            'created_at': datetime.now().isoformat()
        }).execute()
        print("  ✅ co2_measurements: OK")
    except Exception as e:
        print(f"  ❌ co2_measurements: {e}")
        return 1

    # 3. Breakdata Tabelle
    print("📊 Füge Daten in 'breakdata' ein...")
    try:
        client.table('breakdata').insert({
            'session_id': session_id,
            'pause_number': 0,
            'step_count': 0,
            'calories_burned': 0.0,
            'distance_meters': 0.0,
            'device_id': config.DEVICE_ID,
            'created_at': datetime.now().isoformat()
        }).execute()
        print("  ✅ breakdata: OK")
    except Exception as e:
        print(f"  ❌ breakdata: {e}")
        return 1

    print("\n🎉 DATENBANK ERFOLGREICH GEFÜLLT!")
    print(f"   Session ID: {session_id}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
