#!/usr/bin/env python3
"""
test_all.py - Komplette Test-Suite für Präsentation
Testet: Hardware → Services → Database → Discord
"""

import sys
from time import sleep
from datetime import datetime
from requests import post

import config
from hardware.button1 import Button1
from hardware.button2 import Button2
from hardware.led import LED
from hardware.buzzer import Buzzer
from hardware.Co2_sensor import CO2Sensor
from hardware.step_counter import StepCounter
from services.notification_service import NotificationService
from database.supabase_manager import SupabaseManager
from services.discord_message_templates import MessageTemplates

# Farben für Terminal
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class TestSuite:
    def __init__(self):
        self.test_count = 0
        self.passed = 0
        self.failed = 0
        self.db = SupabaseManager()
        self.notify = NotificationService()
    
    def print_header(self, test_name):
        self.test_count += 1
        print(f"\n{'='*60}")
        print(f"{BLUE}🧪 TEST {self.test_count}: {test_name}{NC}")
        print(f"{'='*60}\n")
    
    def print_success(self, message):
        print(f"{GREEN}✅ {message}{NC}")
        self.passed += 1
    
    def print_fail(self, message):
        print(f"{RED}❌ {message}{NC}")
        self.failed += 1
    
    def wait_for_next(self):
        print(f"\n{YELLOW}👉 Drücke ENTER für nächsten Test...{NC}")
        try:
            input()
        except KeyboardInterrupt:
            raise
        print()
    
    def send_discord(self, title, message, color=3447003):
        """Sendet Test-Nachricht zu Discord"""
        if not self.notify.is_enabled:
            return False
        
        try:
            payload = {
                "embeds": [{
                    "title": f"🧪 {title}",
                    "description": message,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Test Suite"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            return response.status_code == 204
        except:
            return False
    
    # ===== HARDWARE TESTS =====
    
    def test_button1(self):
        self.print_header("BUTTON 1 - Arbeitsstart (D0)")
        
        try:
            button = Button1()
            print("👆 Drücke Button 1 kurz...")
            
            pressed = False
            def on_press():
                nonlocal pressed
                pressed = True
                print(f"{GREEN}✅ Button 1 erkannt!{NC}")
            
            button.on_short_press(on_press)
            
            print("⏳ Warte 5 Sekunden...")
            for i in range(5):
                if pressed:
                    break
                sleep(1)
            
            if pressed:
                self.print_success("Button 1 funktioniert")
                self.send_discord("Button 1", "✅ Button 1 (Arbeitsstart) erfolgreich getestet")
            else:
                self.print_fail("Button 1 nicht gedrückt")
        
        except Exception as e:
            self.print_fail(f"Button 1 Fehler: {e}")
        
        self.wait_for_next()
    
    def test_button2(self):
        self.print_header("BUTTON 2 - Pause starten (D1)")
        
        try:
            button = Button2()
            print("👆 Drücke Button 2 kurz...")
            
            pressed = False
            def on_press():
                nonlocal pressed
                pressed = True
                print(f"{GREEN}✅ Button 2 erkannt!{NC}")
            
            button.on_short_press(on_press)
            
            print("⏳ Warte 5 Sekunden...")
            for i in range(5):
                if pressed:
                    break
                sleep(1)
            
            if pressed:
                self.print_success("Button 2 funktioniert")
                self.send_discord("Button 2", "✅ Button 2 (Pause) erfolgreich getestet")
            else:
                self.print_fail("Button 2 nicht gedrückt")
        
        except Exception as e:
            self.print_fail(f"Button 2 Fehler: {e}")
        
        self.wait_for_next()
    
    def test_led(self):
        self.print_header("LED - Rote Status-LED (D2)")
        
        try:
            led = LED()
            
            print("🔴 LED einschalten...")
            led.on()
            sleep(2)
            self.print_success("LED leuchtet")
            
            print("💡 LED ausschalten...")
            led.off()
            sleep(1)
            self.print_success("LED aus")
            
            print("⚡ LED blinken (5 Sekunden)...")
            led.blink(0.3, 0.3)
            sleep(5)
            led.off()
            self.print_success("LED blinkt")
            
            self.send_discord("LED", "✅ Rote Status-LED funktioniert\n🔴 An ✓\n💡 Aus ✓\n⚡ Blink ✓")
        
        except Exception as e:
            self.print_fail(f"LED Fehler: {e}")
        
        self.wait_for_next()
    
    def test_buzzer(self):
        self.print_header("BUZZER - Akustische Signale (D3)")
        
        try:
            buzzer = Buzzer()
            
            print("🔊 Kurzer Beep...")
            buzzer.beep(0.2)
            sleep(0.3)
            self.print_success("Beep OK")
            
            print("🔊🔊 Doppel-Beep...")
            buzzer.double_beep()
            sleep(0.5)
            self.print_success("Doppel-Beep OK")
            
            print("📢 Langer Beep (Timer-Ende)...")
            buzzer.long_beep(1.5)
            self.print_success("Langer Beep OK")
            
            self.send_discord("BUZZER", "✅ Buzzer funktioniert\n🔊 Beep ✓\n🔊🔊 Doppel-Beep ✓\n📢 Long Beep ✓")
        
        except Exception as e:
            self.print_fail(f"Buzzer Fehler: {e}")
        
        self.wait_for_next()
    
    def test_co2(self):
        self.print_header("CO2 SENSOR - Luftqualität (I2C 0x5A)")
        
        try:
            co2 = CO2Sensor()
            
            print("🌫️ Lese CO2-Wert...")
            sleep(1)  # Sensor braucht kurz
            
            level = co2.read()
            tvoc = co2.tvoc_level
            status = co2.get_alarm_status()
            
            print(f"  eCO2: {level} ppm")
            print(f"  TVOC: {tvoc} ppb")
            print(f"  Status: {status}")
            
            # Status-Emoji
            status_emoji = {
                'ok': '✅',
                'warning': '⚠️',
                'critical': '🚨'
            }.get(status, '❓')
            
            if level > 0:
                self.print_success(f"CO2 gelesen: {level} ppm ({status})")
                self.send_discord(
                    "CO2 SENSOR",
                    f"✅ CO2-Sensor funktioniert\n\n"
                    f"🌫️ **eCO2:** {level} ppm\n"
                    f"💨 **TVOC:** {tvoc} ppb\n"
                    f"{status_emoji} **Status:** {status}"
                )
            else:
                self.print_fail("CO2-Wert ungültig")
        
        except Exception as e:
            self.print_fail(f"CO2 Fehler: {e}")
        
        self.wait_for_next()
    
    def test_step_counter(self):
        self.print_header("STEP COUNTER - Schrittzähler (I2C 0x14)")
        
        try:
            steps = StepCounter()
            
            print("🚶 Starte Schrittzähler...")
            steps.start()
            self.print_success("Schrittzähler läuft")
            
            print("\n👟 BEWEGE DAS GERÄT oder gehe umher!")
            print("⏳ Zähle 10 Sekunden...\n")
            
            for i in range(10):
                current = steps.read()
                print(f"  {i+1}s: {current} Schritte", end='\r')
                sleep(1)
            
            final_steps = steps.stop()
            print(f"\n\n✅ Gemessen: {final_steps} Schritte")
            
            # Berechne Kalorien & Distanz
            calories = final_steps * config.CALORIES_PER_STEP
            distance = final_steps * config.METERS_PER_STEP
            
            self.print_success(f"Schrittzähler: {final_steps} Schritte")
            self.send_discord(
                "STEP COUNTER",
                f"✅ Schrittzähler funktioniert\n\n"
                f"👟 **Schritte:** {final_steps}\n"
                f"🔥 **Kalorien:** {calories:.1f} kcal\n"
                f"📏 **Distanz:** {distance:.1f} m"
            )
        
        except Exception as e:
            self.print_fail(f"Step Counter Fehler: {e}")
        
        self.wait_for_next()
    
    # ===== SERVICE TESTS =====
    
    def test_database(self):
        self.print_header("DATABASE - Supabase Connection")
        
        try:
            if not self.db.client:
                self.print_fail("DB nicht verbunden")
                return
            
            print("📊 Prüfe Tabellen...")
            
            # Test Sessions
            sessions = self.db.client.table('sessions').select("id").limit(5).execute()
            session_count = len(sessions.data) if hasattr(sessions, 'data') else 0
            print(f"  Sessions: {session_count} gefunden")
            
            # Test Break Data
            breaks = self.db.client.table('breakdata').select("id").limit(5).execute()
            break_count = len(breaks.data) if hasattr(breaks, 'data') else 0
            print(f"  Breaks: {break_count} gefunden")
            
            # Test CO2 Measurements
            co2_data = self.db.client.table('co2_measurements').select("id").limit(5).execute()
            co2_count = len(co2_data.data) if hasattr(co2_data, 'data') else 0
            print(f"  CO2 Measurements: {co2_count} gefunden")
            
            self.print_success("Supabase erreichbar")
            self.send_discord(
                "DATABASE",
                f"✅ Supabase verbunden\n\n"
                f"📊 **Sessions:** {session_count}\n"
                f"☕ **Breaks:** {break_count}\n"
                f"🌫️ **CO2 Daten:** {co2_count}"
            )
        
        except Exception as e:
            self.print_fail(f"DB Fehler: {e}")
        
        self.wait_for_next()
    
    def test_discord_ready(self):
        self.print_header("DISCORD - Ready Message")
        
        try:
            if not self.notify.is_enabled:
                self.print_fail("Discord Webhook nicht konfiguriert")
                return
            
            print("📨 Sende 'Ready'-Nachricht...")
            
            payload = {
                "embeds": [{
                    "title": "🤖 Learning Assistant ist bereit!",
                    "description": (
                        "**i am ready to serve** 🚀\n\n"
                        "Das System wurde erfolgreich deployed!\n\n"
                        "✅ Supabase verbunden\n"
                        "✅ Discord Webhook aktiv\n"
                        "✅ Hardware konfiguriert\n"
                        "✅ Ready to learn! 🎓"
                    ),
                    "color": 3066993,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Learning Assistant - Test Suite"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            
            if response.status_code == 204:
                self.print_success("Ready-Message versendet")
            else:
                self.print_fail(f"Status {response.status_code}")
        
        except Exception as e:
            self.print_fail(f"Discord Fehler: {e}")
        
        self.wait_for_next()
    
    def test_session_report(self):
        self.print_header("SESSION REPORT - Datenauswertung")
        
        try:
            if not self.db.client:
                self.print_fail("Keine DB-Verbindung")
                return
            
            print("📊 Lade letzte Session aus Datenbank...")
            
            session_response = self.db.client.table('sessions')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if not session_response.data:
                print("⚠️  Keine Sessions in Datenbank!")
                print("💡 Tipp: Starte main_pitop1.py um Test-Daten zu erzeugen")
                self.print_fail("Keine Test-Daten")
                return
            
            session = session_response.data[0]
            session_id = session.get('session_id')
            
            print(f"✅ Session gefunden: {session_id[:8]}...")
            print(f"   User: {session.get('user_name')}")
            print(f"   Arbeitszeit: {session.get('total_work_time', 0)}s")
            print(f"   Pausenzeit: {session.get('total_pause_time', 0)}s")
            
            # Hole Report-Daten
            report_data = self.db.get_session_report_data(session_id)
            
            if not report_data:
                self.print_fail("Report-Daten konnten nicht geladen werden")
                return
            
            # Erstelle Discord-Report
            template = MessageTemplates.session_report(
                session.get('user_name', 'User'),
                report_data
            )
            
            print("\n📤 Sende Session-Report zu Discord...")
            
            payload = {
                "embeds": [{
                    "title": template['title'],
                    "description": template['description'],
                    "color": template['color'],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Learning Assistant"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            
            if response.status_code == 204:
                self.print_success("Session-Report versendet")
            else:
                self.print_fail(f"Status {response.status_code}")
        
        except Exception as e:
            self.print_fail(f"Report Fehler: {e}")
        
        self.wait_for_next()
    
    # ===== SUMMARY =====
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}📊 TEST SUMMARY{NC}")
        print(f"{'='*60}\n")
        
        print(f"Durchgeführte Tests: {self.test_count}")
        print(f"{GREEN}✅ Bestanden: {self.passed}{NC}")
        print(f"{RED}❌ Fehlgeschlagen: {self.failed}{NC}")
        
        percentage = (self.passed / self.test_count * 100) if self.test_count > 0 else 0
        print(f"\n{BLUE}Erfolgsquote: {percentage:.0f}%{NC}")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALLE TESTS BESTANDEN!{NC}")
        else:
            print(f"\n{YELLOW}⚠️ {self.failed} Test(s) fehlgeschlagen{NC}")
        
        print(f"{'='*60}\n")
        
        # Finale Discord-Nachricht
        color = 3066993 if self.failed == 0 else 15158332
        self.send_discord(
            "TEST-SUITE ABGESCHLOSSEN",
            f"**Ergebnisse:**\n\n"
            f"✅ Bestanden: {self.passed}/{self.test_count}\n"
            f"❌ Fehlgeschlagen: {self.failed}/{self.test_count}\n"
            f"📊 Erfolgsquote: {percentage:.0f}%",
            color=color
        )
    
    def run_all(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}🧪 COMPLETE TEST SUITE - PRÄSENTATION{NC}")
        print(f"{'='*60}\n")
        print("Testet alle Hardware, Services & Datenbank")
        print("Enter zum Starten...\n")
        input()
        
        try:
            # Hardware Tests
            self.test_button1()
            self.test_button2()
            self.test_led()
            self.test_buzzer()
            self.test_co2()
            self.test_step_counter()
            
            # Service Tests
            self.test_database()
            self.test_discord_ready()
            self.test_session_report()
            
            # Summary
            self.print_summary()
        
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}🛑 Tests unterbrochen{NC}\n")
            self.print_summary()
            sys.exit(0)

if __name__ == "__main__":
    suite = TestSuite()
    suite.run_all()