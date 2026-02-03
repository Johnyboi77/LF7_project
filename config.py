#!/usr/bin/env python3
"""
test_db.py - Schneller Supabase Verbindungstest
"""

import os
import sys

# ⚠️ WICHTIG: Device Override MUSS VOR import config stehen!
os.environ['DEVICE_OVERRIDE'] = 'pitop1'

# JETZT erst config importieren (lädt automatisch .env.pitop1)
import config

def main():
    print("\n" + "="*50)
    print("🔍 SUPABASE VERBINDUNGSTEST")
    print("="*50 + "\n")
    
    # 1. Credentials prüfen (aus config.py)
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("❌ SUPABASE_URL oder SUPABASE_KEY fehlt in .env!")
        return 1
    
    print(f"✅ URL: {config.SUPABASE_URL}")
    print(f"✅ KEY: {config.SUPABASE_KEY[:20]}...")
    print(f"✅ Device: {config.DEVICE_ID}")
    
    # 2. Client erstellen
    try:
        from supabase import create_client
        client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        print("✅ Supabase Client erstellt")
    except Exception as e:
        print(f"❌ Client-Fehler: {e}")
        return 1
    
    # 3. Tabellen testen
    print("\n📊 Teste Tabellen...")
    tables = ['sessions', 'co2_measurements', 'breakdata']
    
    for table in tables:
        try:
            result = client.table(table).select("id").limit(1).execute()
            count = len(result.data) if result.data else 0
            print(f"  ✅ {table}: OK ({count} Einträge)")
        except Exception as e:
            print(f"  ❌ {table}: {e}")
    
    # 4. Schreib-Test
    print("\n📝 Teste Schreiben...")
    try:
        import uuid
        test_id = str(uuid.uuid4())
        
        # Insert
        client.table('sessions').insert({
            'session_id': test_id,
            'device_id': 'test',
            'user_name': 'TEST',
            'timer_status': 'test'
        }).execute()
        print("  ✅ INSERT OK")
        
        # Delete
        client.table('sessions').delete().eq('session_id', test_id).execute()
        print("  ✅ DELETE OK (cleanup)")
        
    except Exception as e:
        print(f"  ❌ Schreib-Fehler: {e}")
        return 1
    
    # Erfolg!
    print("\n" + "="*50)
    print("🎉 SUPABASE VERBINDUNG ERFOLGREICH!")
    print("="*50 + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())