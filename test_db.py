#!/usr/bin/env python3
"""Supabase Verbindungstest"""

import os
import sys

# ⚠️ WICHTIG: Device Override MUSS VOR import config stehen!
os.environ['DEVICE_OVERRIDE'] = 'pitop2'

import config
from supabase import create_client
import uuid

def main():
    print("\n" + "="*50)
    print("🔍 SUPABASE VERBINDUNGSTEST")
    print("="*50 + "\n")
    
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("❌ SUPABASE Credentials fehlen!")
        return 1
    
    print(f"✅ URL: {config.SUPABASE_URL}")
    print(f"✅ KEY: {config.SUPABASE_KEY[:20]}...")
    print(f"✅ Device: {config.DEVICE_ID}")
    
    try:
        client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        print("✅ Client erstellt")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return 1
    
    # Tabellen testen
    print("\n📊 Teste Tabellen...")
    for table in ['sessions', 'co2_measurements', 'breakdata']:
        try:
            result = client.table(table).select("id").limit(1).execute()
            print(f"  ✅ {table}: OK")
        except Exception as e:
            print(f"  ❌ {table}: {e}")
    
    # Schreib-Test
    print("\n📝 Teste Schreiben...")
    try:
        test_id = str(uuid.uuid4())
        
        client.table('sessions').insert({
            'session_id': test_id,
            'device_id': 'test',
            'user_name': 'TEST',
            'timer_status': 'test'
        }).execute()
        print("  ✅ INSERT OK")
        
        client.table('sessions').delete().eq('session_id', test_id).execute()
        print("  ✅ DELETE OK")
        
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
    
    print("\n🎉 VERBINDUNG ERFOLGREICH!\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
