#!/usr/bin/env python3
"""
test_db.py - Schneller Supabase Verbindungstest (Standalone)
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("\n" + "="*50)
    print("🔍 SUPABASE VERBINDUNGSTEST")
    print("="*50 + "\n")
    
    # 1. .env laden (hardcoded)
    env_file = '.env.pitop1'  # Oder '.env.pitop2' für PiTop 2
    
    if not os.path.exists(env_file):
        print(f"❌ {env_file} nicht gefunden!")
        print(f"   Verfügbare .env Dateien:")
        for f in os.listdir('.'):
            if f.startswith('.env'):
                print(f"   - {f}")
        return 1
    
    load_dotenv(env_file)
    print(f"✅ {env_file} geladen")
    
    # 2. Credentials aus Environment holen
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL oder SUPABASE_KEY fehlt in .env!")
        return 1
    
    print(f"✅ URL: {SUPABASE_URL}")
    print(f"✅ KEY: {SUPABASE_KEY[:20]}...")
    
    # 3. Client erstellen
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase Client erstellt")
    except Exception as e:
        print(f"❌ Client-Fehler: {e}")
        return 1
    
    # 4. Tabellen testen
    print("\n📊 Teste Tabellen...")
    tables = ['sessions', 'co2_measurements', 'breakdata']
    
    for table in tables:
        try:
            result = client.table(table).select("id").limit(1).execute()
            count = len(result.data) if result.data else 0
            print(f"  ✅ {table}: OK ({count} Einträge)")
        except Exception as e:
            print(f"  ❌ {table}: {e}")
    
    # 5. Schreib-Test
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