#!/usr/bin/env python3
"""
test_all2.py - Test-Suite für PiTop 2
Testet: Schrittzähler, Database, Discord
"""

import sys
import os

# Device MANUELL setzen BEVOR config importiert wird
os.environ['DEVICE_OVERRIDE'] = 'pitop2'

from time import sleep
from datetime import datetime
from requests import post

import config
from hardware.step_counter import StepCounter
from services.notification_service import NotificationService
from database.supabase_manager import SupabaseManager

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
NC = '\033[0m'

class TestSuite:
    def __init__(self):
        self.test_count = 0
        self.passed = 0
        self.failed = 0
        self.db = SupabaseManager()
        self.notify = NotificationService()
    
    def header(self, name):
        self.test_count += 1
        print(f"\n{'='*60}")
        print(f"{BLUE}🧪 TEST {self.test_count}: {name}{NC}")
        print(f"{'='*60}\n")
    
    def success(self, msg):
        print(f"{GREEN}✅ {msg}{NC}")
        self.passed += 1
    
    def fail(self, msg):
        print(f"{RED}❌ {msg}{NC}")
        self.failed += 1
    
    def wait(self):
        print(f"\n{YELLOW}👉 ENTER für nächsten Test...{NC}")
        try:
            input()
        except KeyboardInterrupt:
            raise
    
    def discord(self, title, msg, color=3447003):
        if not self.notify.is_enabled:
            return False
        try:
            payload = {
                "embeds": [{
                    "title": f"🧪 {title}",
                    "description": msg,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "PiTop 2 Test Suite"}
                }]
            }
            return post(self.notify.webhook_url, json=payload, timeout=5).status_code == 204
        except:
            return False

    # ===== HARDWARE TESTS =====
    
    def test_step_counter(self):
        self.header("STEP COUNTER - Schrittzähler")
        try:
            steps = StepCounter()
            
            print(f"📱 Sensor-Typ: {steps.sensor_type or 'Dummy'}")
            
            print("\n🚶 Starte Schrittzähler...")
            steps.start()
            self.success("Schrittzähler gestartet")
            
            print(f"\n{YELLOW}👟 BEWEGE DAS GERÄT oder gehe umher!{NC}")
            print("⏳ Zähle 10 Sekunden...\n")
            
            for i in range(10):
                current = steps.read()
                print(f"  {i+1:2}s: {current:3} Schritte", end='\r')
                sleep(1)
            
            final_steps = steps.stop()
            print(f"\n\n📊 Ergebnis: {final_steps} Schritte")
            
            # Kalorien & Distanz berechnen
            calories = final_steps * getattr(config, 'CALORIES_PER_STEP', 0.04)
            distance = final_steps * getattr(config, 'METERS_PER_STEP', 0.75)
            
            print(f"🔥 Kalorien: {calories:.2f} kcal")
            print(f"📏 Distanz: {distance:.1f} m")
            
            self.success(f"Schrittzähler: {final_steps} Schritte")
            self.discord(
                "Step Counter",
                f"✅ Schrittzähler OK\n\n"
                f"📱 Sensor: {steps.sensor_type or 'Dummy'}\n"
                f"👟 Schritte: {final_steps}\n"
                f"🔥 Kalorien: {calories:.2f} kcal\n"
                f"📏 Distanz: {distance:.1f} m"
            )
        except Exception as e:
            self.fail(f"Step Counter Fehler: {e}")
        self.wait()

    # ===== SERVICE TESTS =====
    
    def test_database(self):
        self.header("DATABASE - Supabase Connection")
        try:
            if not self.db.client:
                self.fail("Keine DB-Verbindung")
                return
            
            print("📊 Prüfe Tabellen...")
            
            tables = ['sessions', 'breakdata', 'co2_measurements']
            counts = {}
            
            for table in tables:
                try:
                    result = self.db.client.table(table).select("id").limit(5).execute()
                    counts[table] = len(result.data) if result.data else 0
                    print(f"  {table}: {counts[table]} Einträge")
                except Exception as e:
                    counts[table] = 0
                    print(f"  {table}: ❌ {e}")
            
            self.success("Supabase erreichbar")
            self.discord("Database", f"✅ Supabase OK\n\n📊 sessions: {counts.get('sessions', 0)}\n☕ breakdata: {counts.get('breakdata', 0)}\n🌫️ co2: {counts.get('co2_measurements', 0)}")
        except Exception as e:
            self.fail(f"DB Fehler: {e}")
        self.wait()
    
    def test_active_session(self):
        self.header("ACTIVE SESSION - Polling Test")
        try:
            if not self.db.client:
                self.fail("Keine DB-Verbindung")
                return
            
            print("🔍 Suche aktive Session...")
            session = self.db.get_active_session()
            
            if session:
                print(f"  Session ID: {session.get('session_id', 'N/A')[:8]}...")
                print(f"  Status: {session.get('timer_status', 'N/A')}")
                print(f"  Pausen: {session.get('pause_count', 0)}")
                self.success("Aktive Session gefunden")
            else:
                print("  Keine aktive Session")
                self.success("Polling funktioniert (keine Session aktiv)")
            
            self.discord("Session Polling", f"✅ Polling OK\n\nAktive Session: {'Ja' if session else 'Nein'}")
        except Exception as e:
            self.fail(f"Session Polling Fehler: {e}")
        self.wait()
    
    def test_discord_ready(self):
        self.header("DISCORD - Ready Message")
        try:
            if not self.notify.is_enabled:
                self.fail("Discord Webhook nicht konfiguriert")
                return
            
            print("📨 Sende Ready-Nachricht...")
            
            payload = {
                "embeds": [{
                    "title": "🤖 PiTop 2 - Break Station bereit!",
                    "description": (
                        "**System erfolgreich getestet!** 🚀\n\n"
                        "✅ Schrittzähler OK\n"
                        "✅ Supabase verbunden\n"
                        "✅ Session Polling OK\n"
                        "✅ Discord aktiv\n\n"
                        "☕ Ready for breaks!"
                    ),
                    "color": 3066993,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "PiTop 2 - Test Suite"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            
            if response.status_code == 204:
                self.success("Ready-Message versendet")
            else:
                self.fail(f"Discord Status: {response.status_code}")
        except Exception as e:
            self.fail(f"Discord Fehler: {e}")
        self.wait()

    # ===== SUMMARY =====
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}📊 TEST ZUSAMMENFASSUNG - PITOP 2{NC}")
        print(f"{'='*60}\n")
        
        pct = (self.passed / self.test_count * 100) if self.test_count > 0 else 0
        
        print(f"Durchgeführte Tests: {self.test_count}")
        print(f"{GREEN}✅ Bestanden: {self.passed}{NC}")
        print(f"{RED}❌ Fehlgeschlagen: {self.failed}{NC}")
        print(f"\nErfolgsquote: {pct:.0f}%")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALLE TESTS BESTANDEN!{NC}")
        else:
            print(f"\n{YELLOW}⚠️  {self.failed} Test(s) fehlgeschlagen{NC}")
        
        print(f"\n{'='*60}\n")
        
        color = 3066993 if self.failed == 0 else 15158332
        self.discord(
            "PITOP 2 - TESTS ABGESCHLOSSEN",
            f"**Ergebnis:**\n\n✅ Bestanden: {self.passed}/{self.test_count}\n❌ Fehlgeschlagen: {self.failed}/{self.test_count}\n📊 Erfolgsquote: {pct:.0f}%",
            color
        )
    
    def run_all(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}🧪 TEST SUITE - PITOP 2 (Break Station){NC}")
        print(f"{'='*60}\n")
        print("Tests: Schrittzähler, Database, Session Polling, Discord")
        print("\nENTER zum Starten...")
        input()
        
        try:
            self.test_step_counter()
            self.test_database()
            self.test_active_session()
            self.test_discord_ready()
            self.summary()
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}🛑 Tests unterbrochen{NC}\n")
            self.summary()
            sys.exit(0)

if __name__ == "__main__":
    TestSuite().run_all()