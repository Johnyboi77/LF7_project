#!/usr/bin/env python3
"""
test_db.py - Schneller Supabase Verbindungstest
"""

import os
import sys

# Device Override für config.py
os.environ['DEVICE_OVERRIDE'] = 'pitop1'

def main():
    print("\n" + "="*50)
    print("🔍 SUPABASE VERBINDUNGSTEST")
    print("="*50 + "\n")
    
    # 1. dotenv laden
    try:
        from dotenv import load_dotenv
        for f in ['.env.pitop1', '.env.pitop2', '.env']:
            if os.path.exists(f):
                load_dotenv(f)
                print(f"✅ {f} geladen")
                break
    except ImportError:
        print("❌ python-dotenv fehlt!")
        return 1
    
    # 2. Credentials prüfen
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ SUPABASE_URL oder SUPABASE_KEY fehlt!")
        return 1
    
    print(f"✅ URL: {url}")
    print(f"✅ KEY: {key[:20]}...")
    
    # 3. Client erstellen
    try:
        from supabase import create_client
        client = create_client(url, key)
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