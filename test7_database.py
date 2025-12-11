"""
test7_database.py - Einfacher Supabase Insert Test
Fügt Testdaten in alle Tabellen ein
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Lade .env.pitop1 Datei
load_dotenv('.env.pitop1')

# Supabase Credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Test Session ID
TEST_SESSION_ID = f"TEST-{int(datetime.now().timestamp())}"

def main():
    print("\n🚣 Fülle Datenbank mit Testdaten...")
    print(f"   Session ID: {TEST_SESSION_ID}\n")
    
    # Supabase Client initialisieren
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase verbunden")
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return
    
    # 1. Session einfügen
    try:
        session_data = {
            'session_id': TEST_SESSION_ID,
            'start_time': datetime.now().isoformat(),
            'user_name': 'Test User',
            'user_weight': 75,
            'user_height': 175,
            'device_id': 'TEST-DEVICE',
            'timer_status': 'running'
        }
        supabase.table('sessions').insert(session_data).execute()
        print("✅ Tabelle 'sessions' gefüllt")
    except Exception as e:
        print(f"❌ sessions: {e}")
        return
    
    # 2. Breakdata einfügen
    try:
        breakdata = {
            'session_id': TEST_SESSION_ID,
            'timestamp': datetime.now().isoformat(),
            'pause_number': 0,
            'step_count': 100,
            'calories_burned': 10,
            'distance_meters': 80,
            'device_id': 'TEST-DEVICE'
        }
        supabase.table('breakdata').insert(breakdata).execute()
        print("✅ Tabelle 'breakdata' gefüllt")
    except Exception as e:
        print(f"❌ breakdata: {e}")
    
    # 3. CO2 Measurement einfügen
    try:
        co2_data = {
            'session_id': TEST_SESSION_ID,
            'timestamp': datetime.now().isoformat(),
            'co2_level': 450,
            'tvoc_level': 50,
            'is_alarm': False,
            'device_id': 'TEST-DEVICE'
        }
        supabase.table('co2_measurements').insert(co2_data).execute()
        print("✅ Tabelle 'co2_measurements' gefüllt")
    except Exception as e:
        print(f"❌ co2_measurements: {e}")
    
    print("\n🎉 Datenbank erfolgreich gefüllt!\n")

if __name__ == "__main__":
    main()