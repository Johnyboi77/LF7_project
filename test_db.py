#!/usr/bin/env python3
"""
test_db.py - Supabase Verbindungstest
Testet alle Datenbankoperationen schrittweise
"""

import os
import sys
import socket
from datetime import datetime

# Farben für Terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def ok(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def fail(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def warn(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def header(msg):
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{Colors.RESET}\n")


def test_network():
    """Test 1: Grundlegende Netzwerkverbindung"""
    header("TEST 1: Netzwerk-Konnektivität")
    
    # Test DNS-Auflösung
    hosts_to_test = [
        ("google.com", "Google"),
        ("fyffbzuxzgvhctxrzgol.supabase.co", "Supabase"),
        ("discord.com", "Discord")
    ]
    
    results = {}
    for host, name in hosts_to_test:
        try:
            ip = socket.gethostbyname(host)
            ok(f"{name} DNS: {host} → {ip}")
            results[name] = True
        except socket.gaierror as e:
            fail(f"{name} DNS fehlgeschlagen: {e}")
            results[name] = False
    
    # Test Socket-Verbindung zu Supabase
    print()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('fyffbzuxzgvhctxrzgol.supabase.co', 443))
        sock.close()
        if result == 0:
            ok("Port 443 (HTTPS) zu Supabase erreichbar")
            results['port'] = True
        else:
            fail(f"Port 443 nicht erreichbar (Error: {result})")
            results['port'] = False
    except Exception as e:
        fail(f"Socket-Test fehlgeschlagen: {e}")
        results['port'] = False
    
    return all(results.values())


def test_env():
    """Test 2: Umgebungsvariablen laden"""
    header("TEST 2: Umgebungsvariablen")
    
    # Versuche .env Dateien zu laden
    env_files = ['.env.pitop1', '.env.pitop2', '.env']
    loaded = False
    
    try:
        from dotenv import load_dotenv
        ok("python-dotenv installiert")
    except ImportError:
        fail("python-dotenv nicht installiert!")
        print("   → pip install python-dotenv")
        return False, None, None
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            ok(f"Gefunden und geladen: {env_file}")
            loaded = True
            break
    
    if not loaded:
        fail("Keine .env Datei gefunden!")
        return False, None, None
    
    # Prüfe benötigte Variablen
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    print()
    if url:
        ok(f"SUPABASE_URL: {url[:50]}...")
    else:
        fail("SUPABASE_URL nicht gesetzt!")
    
    if key:
        ok(f"SUPABASE_KEY: {key[:20]}...{key[-10:]}")
    else:
        fail("SUPABASE_KEY nicht gesetzt!")
    
    return bool(url and key), url, key


def test_supabase_connection(url, key):
    """Test 3: Supabase Client erstellen"""
    header("TEST 3: Supabase Client")
    
    try:
        from supabase import create_client, Client
        ok("supabase-py installiert")
    except ImportError:
        fail("supabase-py nicht installiert!")
        print("   → pip install supabase")
        return False, None
    
    try:
        client: Client = create_client(url, key)
        ok("Supabase Client erstellt")
        return True, client
    except Exception as e:
        fail(f"Client-Erstellung fehlgeschlagen: {e}")
        return False, None


def test_read_operations(client):
    """Test 4: Lese-Operationen"""
    header("TEST 4: Lese-Operationen")
    
    tables_to_test = ['sessions', 'users', 'breaks']
    results = {}
    
    for table in tables_to_test:
        try:
            result = client.table(table).select("*").limit(1).execute()
            count = len(result.data) if result.data else 0
            ok(f"SELECT auf '{table}': {count} Datensätze (limit 1)")
            results[table] = True
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "permission denied" in error_msg:
                warn(f"Tabelle '{table}' existiert nicht oder keine Berechtigung")
            else:
                fail(f"Fehler bei '{table}': {e}")
            results[table] = False
    
    return any(results.values())


def test_write_operations(client):
    """Test 5: Schreib-Operationen (mit Cleanup)"""
    header("TEST 5: Schreib-Operationen")
    
    test_data = {
        'device': 'test_device',
        'user_name': 'TEST_USER',
        'session_type': 'test',
        'start_time': datetime.now().isoformat(),
        'duration_seconds': 0
    }
    
    inserted_id = None
    
    # INSERT Test
    try:
        result = client.table('sessions').insert(test_data).execute()
        if result.data:
            inserted_id = result.data[0].get('id')
            ok(f"INSERT erfolgreich (ID: {inserted_id})")
        else:
            warn("INSERT ausgeführt, aber keine Daten zurückgegeben")
    except Exception as e:
        fail(f"INSERT fehlgeschlagen: {e}")
        return False
    
    # UPDATE Test
    if inserted_id:
        try:
            result = client.table('sessions').update({
                'duration_seconds': 999
            }).eq('id', inserted_id).execute()
            ok(f"UPDATE erfolgreich")
        except Exception as e:
            fail(f"UPDATE fehlgeschlagen: {e}")
    
    # DELETE Test (Cleanup)
    if inserted_id:
        try:
            result = client.table('sessions').delete().eq('id', inserted_id).execute()
            ok(f"DELETE erfolgreich (Test-Daten bereinigt)")
        except Exception as e:
            fail(f"DELETE fehlgeschlagen: {e}")
            warn(f"Bitte manuell löschen: ID {inserted_id}")
    
    return True


def test_realtime(client):
    """Test 6: Echtzeit-Verbindung (optional)"""
    header("TEST 6: API-Latenz")
    
    import time
    
    latencies = []
    for i in range(3):
        start = time.time()
        try:
            client.table('sessions').select("id").limit(1).execute()
            latency = (time.time() - start) * 1000
            latencies.append(latency)
            info(f"Request {i+1}: {latency:.0f}ms")
        except Exception as e:
            fail(f"Request {i+1} fehlgeschlagen: {e}")
    
    if latencies:
        avg = sum(latencies) / len(latencies)
        if avg < 500:
            ok(f"Durchschnittliche Latenz: {avg:.0f}ms (gut)")
        elif avg < 2000:
            warn(f"Durchschnittliche Latenz: {avg:.0f}ms (langsam)")
        else:
            fail(f"Durchschnittliche Latenz: {avg:.0f}ms (sehr langsam!)")
        return True
    return False


def main():
    print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║          SUPABASE VERBINDUNGSTEST                        ║
║          Pi-Top Learning Assistant                       ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
    """)
    
    results = {}
    
    # Test 1: Netzwerk
    results['network'] = test_network()
    if not results['network']:
        fail("\n⛔ Netzwerk-Test fehlgeschlagen!")
        print("   Behebe zuerst die DNS/Netzwerk-Probleme.")
        sys.exit(1)
    
    # Test 2: Environment
    results['env'], url, key = test_env()
    if not results['env']:
        fail("\n⛔ Umgebungsvariablen fehlen!")
        sys.exit(1)
    
    # Test 3: Client
    results['client'], client = test_supabase_connection(url, key)
    if not results['client']:
        fail("\n⛔ Supabase Client konnte nicht erstellt werden!")
        sys.exit(1)
    
    # Test 4: Lesen
    results['read'] = test_read_operations(client)
    
    # Test 5: Schreiben
    results['write'] = test_write_operations(client)
    
    # Test 6: Latenz
    results['latency'] = test_realtime(client)
    
    # Zusammenfassung
    header("ZUSAMMENFASSUNG")
    
    all_passed = all(results.values())
    
    for test, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {test.upper():15} [{status}]")
    
    print()
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALLE TESTS BESTANDEN!{Colors.RESET}")
        print(f"   Supabase-Verbindung funktioniert einwandfrei.")
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  EINIGE TESTS FEHLGESCHLAGEN{Colors.RESET}")
        print(f"   Überprüfe die Fehlermeldungen oben.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())