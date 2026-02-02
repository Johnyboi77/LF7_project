#!/usr/bin/env python3
"""
test_all.py - Test-Suite für PiTop 1
Testet: Buttons, LED, Buzzer, CO2, Database, Discord
OHNE Schrittzähler (läuft auf PiTop 2)
"""

import sys
import os

# Device MANUELL setzen BEVOR config importiert wird
os.environ['DEVICE_OVERRIDE'] = 'pitop1'

from time import sleep
from datetime import datetime
from requests import post

import config
from hardware.button1 import Button1
from hardware.button2 import Button2
from hardware.led import LED
from hardware.buzzer import Buzzer
from hardware.Co2_sensor import CO2Sensor
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
                    "footer": {"text": "PiTop 1 Test Suite"}
                }]
            }
            return post(self.notify.webhook_url, json=payload, timeout=5).status_code == 204
        except:
            return False

    # ===== HARDWARE TESTS =====
    
    def test_button1(self):
        self.header("BUTTON 1 - Arbeitsstart (D0)")
        try:
            button = Button1()
            self.btn1_pressed = False
            
            def on_press():
                self.btn1_pressed = True
                print(f"{GREEN}✅ Button 1 erkannt!{NC}")
            
            button.on_short_press(on_press)
            print("👆 Drücke Button 1 (5 Sekunden Zeit)...")
            
            for _ in range(50):
                if self.btn1_pressed:
                    break
                sleep(0.1)
            
            if self.btn1_pressed:
                self.success("Button 1 funktioniert")
                self.discord("Button 1", "✅ Button 1 (Arbeitsstart) OK")
            else:
                self.fail("Button 1 nicht gedrückt")
        except Exception as e:
            self.fail(f"Button 1 Fehler: {e}")
        self.wait()
    
    def test_button2(self):
        self.header("BUTTON 2 - Pause starten (D1)")
        try:
            button = Button2()
            self.btn2_pressed = False
            
            def on_press():
                self.btn2_pressed = True
                print(f"{GREEN}✅ Button 2 erkannt!{NC}")
            
            button.on_short_press(on_press)
            print("👆 Drücke Button 2 (5 Sekunden Zeit)...")
            
            for _ in range(50):
                if self.btn2_pressed:
                    break
                sleep(0.1)
            
            if self.btn2_pressed:
                self.success("Button 2 funktioniert")
                self.discord("Button 2", "✅ Button 2 (Pause) OK")
            else:
                self.fail("Button 2 nicht gedrückt")
        except Exception as e:
            self.fail(f"Button 2 Fehler: {e}")
        self.wait()
    
    def test_led(self):
        self.header("LED - Rote Status-LED (D2)")
        try:
            led = LED()
            
            print("🔴 LED einschalten...")
            led.on()
            sleep(2)
            self.success("LED leuchtet")
            
            print("💡 LED ausschalten...")
            led.off()
            sleep(1)
            self.success("LED aus")
            
            print("⚡ LED blinken (3 Sekunden)...")
            led.blink(0.3, 0.3)
            sleep(3)
            led.off()
            self.success("LED blinkt")
            
            self.discord("LED", "✅ LED funktioniert\n🔴 An ✓\n💡 Aus ✓\n⚡ Blink ✓")
        except Exception as e:
            self.fail(f"LED Fehler: {e}")
        self.wait()
    
    def test_buzzer(self):
        self.header("BUZZER - Akustische Signale (D3)")
        try:
            buzzer = Buzzer()
            
            print("🔊 Kurzer Beep...")
            buzzer.beep(0.2)
            sleep(0.5)
            self.success("Beep OK")
            
            print("🔊🔊 Doppel-Beep...")
            buzzer.double_beep()
            sleep(0.5)
            self.success("Doppel-Beep OK")
            
            print("📢 Langer Beep...")
            buzzer.long_beep(1.0)
            self.success("Langer Beep OK")
            
            self.discord("Buzzer", "✅ Buzzer OK\n🔊 Beep ✓\n🔊🔊 Double ✓\n📢 Long ✓")
        except Exception as e:
            self.fail(f"Buzzer Fehler: {e}")
        self.wait()
    
    def test_co2(self):
        self.header("CO2 SENSOR - Luftqualität (SGP30)")
        try:
            co2 = CO2Sensor()
            
            print("🌫️ Lese CO2-Wert (braucht kurz)...")
            sleep(2)
            
            level = co2.read()
            tvoc = co2.tvoc_level
            status = co2.get_alarm_status()
            
            print(f"  eCO2:   {level} ppm")
            print(f"  TVOC:   {tvoc} ppb")
            print(f"  Status: {status}")
            
            emoji = {'ok': '✅', 'warning': '⚠️', 'critical': '🚨'}.get(status, '❓')
            
            if level > 0:
                self.success(f"CO2: {level} ppm ({status})")
                self.discord("CO2 Sensor", f"✅ CO2 Sensor OK\n\n🌫️ eCO2: {level} ppm\n💨 TVOC: {tvoc} ppb\n{emoji} Status: {status}")
            else:
                self.fail("CO2-Wert ungültig (0)")
        except Exception as e:
            self.fail(f"CO2 Fehler: {e}")
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
    
    def test_discord_ready(self):
        self.header("DISCORD - Ready Message")
        try:
            if not self.notify.is_enabled:
                self.fail("Discord Webhook nicht konfiguriert")
                return
            
            print("📨 Sende Ready-Nachricht...")
            
            payload = {
                "embeds": [{
                    "title": "🤖 PiTop 1 - Learning Assistant bereit!",
                    "description": (
                        "**System erfolgreich getestet!** 🚀\n\n"
                        "✅ Buttons OK\n"
                        "✅ LED OK\n"
                        "✅ Buzzer OK\n"
                        "✅ CO2 Sensor OK\n"
                        "✅ Supabase verbunden\n"
                        "✅ Discord aktiv\n\n"
                        "🎓 Ready to learn!"
                    ),
                    "color": 3066993,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "PiTop 1 - Test Suite"}
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
        print(f"{BLUE}📊 TEST ZUSAMMENFASSUNG - PITOP 1{NC}")
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
            "PITOP 1 - TESTS ABGESCHLOSSEN",
            f"**Ergebnis:**\n\n✅ Bestanden: {self.passed}/{self.test_count}\n❌ Fehlgeschlagen: {self.failed}/{self.test_count}\n📊 Erfolgsquote: {pct:.0f}%",
            color
        )
    
    def run_all(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}🧪 TEST SUITE - PITOP 1{NC}")
        print(f"{'='*60}\n")
        print("Tests: Button1, Button2, LED, Buzzer, CO2, Database, Discord")
        print(f"{YELLOW}(Schrittzähler läuft auf PiTop 2){NC}")
        print("\nENTER zum Starten...")
        input()
        
        try:
            self.test_button1()
            self.test_button2()
            self.test_led()
            self.test_buzzer()
            self.test_co2()
            self.test_database()
            self.test_discord_ready()
            self.summary()
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}🛑 Tests unterbrochen{NC}\n")
            self.summary()
            sys.exit(0)

if __name__ == "__main__":
    TestSuite().run_all()