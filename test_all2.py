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
    
    def header(self, name):
        self.test_count += 1
        print(f"\n{'='*60}\n{BLUE}🧪 TEST {self.test_count}: {name}{NC}\n{'='*60}\n")
    
    def success(self, msg):
        print(f"{GREEN}✅ {msg}{NC}")
        self.passed += 1
    
    def fail(self, msg):
        print(f"{RED}❌ {msg}{NC}")
        self.failed += 1
    
    def wait(self):
        print(f"\n{YELLOW}👉 ENTER für nächsten Test...{NC}")
        input()
    
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
                    "footer": {"text": "Test Suite"}
                }]
            }
            return post(self.notify.webhook_url, json=payload, timeout=5).status_code == 204
        except:
            return False
    
    def test_button1(self):
        self.header("BUTTON 1 - Start (D0)")
        try:
            button = Button1()
            pressed = False
            button.on_short_press(lambda: setattr(self, 'pressed', True) or print(f"{GREEN}✅ Button 1!{NC}"))
            print("👆 Drücke Button 1 (5s)...")
            for _ in range(5):
                if hasattr(self, 'pressed'):
                    pressed = True
                    break
                sleep(1)
            if pressed:
                self.success("Button 1 OK")
                self.discord("Button 1", "✅ Button 1 funktioniert")
            else:
                self.fail("Button 1 nicht gedrückt")
        except Exception as e:
            self.fail(f"Button 1: {e}")
        self.wait()
    
    def test_button2(self):
        self.header("BUTTON 2 - Pause (D1)")
        try:
            button = Button2()
            pressed = False
            button.on_short_press(lambda: setattr(self, 'pressed2', True) or print(f"{GREEN}✅ Button 2!{NC}"))
            print("👆 Drücke Button 2 (5s)...")
            for _ in range(5):
                if hasattr(self, 'pressed2'):
                    pressed = True
                    break
                sleep(1)
            if pressed:
                self.success("Button 2 OK")
                self.discord("Button 2", "✅ Button 2 funktioniert")
            else:
                self.fail("Button 2 nicht gedrückt")
        except Exception as e:
            self.fail(f"Button 2: {e}")
        self.wait()
    
    def test_led(self):
        self.header("LED - Rote Status-LED (D2)")
        try:
            led = LED()
            print("🔴 LED AN...")
            led.on()
            sleep(2)
            self.success("LED leuchtet")
            
            print("💡 LED AUS...")
            led.off()
            sleep(1)
            self.success("LED aus")
            
            print("⚡ LED BLINK (5s)...")
            led.blink(0.3, 0.3)
            sleep(5)
            led.off()
            self.success("LED blinkt")
            
            self.discord("LED", "✅ LED funktioniert\n🔴 An ✓\n💡 Aus ✓\n⚡ Blink ✓")
        except Exception as e:
            self.fail(f"LED: {e}")
        self.wait()
    
    def test_buzzer(self):
        self.header("BUZZER - Signale (D3)")
        try:
            buzzer = Buzzer()
            print("🔊 Beep...")
            buzzer.beep(0.2)
            sleep(0.3)
            self.success("Beep OK")
            
            print("🔊🔊 Doppel-Beep...")
            buzzer.double_beep()
            sleep(0.5)
            self.success("Doppel-Beep OK")
            
            print("📢 Langer Beep...")
            buzzer.long_beep(1.5)
            self.success("Long Beep OK")
            
            self.discord("Buzzer", "✅ Buzzer OK\n🔊 Beep ✓\n🔊🔊 Double ✓\n📢 Long ✓")
        except Exception as e:
            self.fail(f"Buzzer: {e}")
        self.wait()
    
    def test_co2(self):
        self.header("CO2 SENSOR (I2C 0x5A)")
        try:
            co2 = CO2Sensor()
            print("🌫️ Lese CO2...")
            sleep(1)
            level = co2.read()
            tvoc = co2.tvoc_level
            status = co2.get_alarm_status()
            
            print(f"  eCO2: {level} ppm")
            print(f"  TVOC: {tvoc} ppb")
            print(f"  Status: {status}")
            
            if level > 0:
                self.success(f"CO2: {level} ppm ({status})")
                self.discord("CO2", f"✅ CO2 OK\n🌫️ {level} ppm\n💨 {tvoc} ppb\nStatus: {status}")
            else:
                self.fail("CO2 ungültig")
        except Exception as e:
            self.fail(f"CO2: {e}")
        self.wait()
    
    def test_steps(self):
        self.header("STEP COUNTER (I2C 0x14)")
        try:
            steps = StepCounter()
            print("🚶 Starte...")
            steps.start()
            self.success("Läuft")
            
            print("\n👟 BEWEGE GERÄT! (10s)\n")
            for i in range(10):
                print(f"  {i+1}s: {steps.read()} Schritte", end='\r')
                sleep(1)
            
            final = steps.stop()
            cal = final * config.CALORIES_PER_STEP
            dist = final * config.METERS_PER_STEP
            
            print(f"\n\n✅ {final} Schritte")
            self.success(f"{final} Schritte")
            self.discord("Steps", f"✅ Steps OK\n👟 {final} Schritte\n🔥 {cal:.1f} kcal\n📏 {dist:.1f} m")
        except Exception as e:
            self.fail(f"Steps: {e}")
        self.wait()
    
    def test_db(self):
        self.header("DATABASE - Supabase")
        try:
            if not self.db.client:
                self.fail("Keine DB")
                return
            
            print("📊 Prüfe Tabellen...")
            sessions = self.db.client.table('sessions').select("id").limit(5).execute()
            breaks = self.db.client.table('breakdata').select("id").limit(5).execute()
            co2 = self.db.client.table('co2_measurements').select("id").limit(5).execute()
            
            s_count = len(sessions.data) if hasattr(sessions, 'data') else 0
            b_count = len(breaks.data) if hasattr(breaks, 'data') else 0
            c_count = len(co2.data) if hasattr(co2, 'data') else 0
            
            print(f"  Sessions: {s_count}")
            print(f"  Breaks: {b_count}")
            print(f"  CO2: {c_count}")
            
            self.success("Supabase OK")
            self.discord("Database", f"✅ Supabase OK\n📊 {s_count} Sessions\n☕ {b_count} Breaks\n🌫️ {c_count} CO2")
        except Exception as e:
            self.fail(f"DB: {e}")
        self.wait()
    
    def test_discord_ready(self):
        self.header("DISCORD - Ready Message")
        try:
            if not self.notify.is_enabled:
                self.fail("Discord nicht konfiguriert")
                return
            
            print("📨 Sende Ready...")
            payload = {
                "embeds": [{
                    "title": "🤖 Learning Assistant bereit!",
                    "description": (
                        "**ready to serve** 🚀\n\n"
                        "✅ Supabase ✓\n"
                        "✅ Discord ✓\n"
                        "✅ Hardware ✓\n"
                        "✅ Ready! 🎓"
                    ),
                    "color": 3066993,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
            
            if post(self.notify.webhook_url, json=payload, timeout=5).status_code == 204:
                self.success("Ready-Message OK")
            else:
                self.fail("Discord Fehler")
        except Exception as e:
            self.fail(f"Discord: {e}")
        self.wait()
    
    def test_report(self):
        self.header("SESSION REPORT")
        try:
            if not self.db.client:
                self.fail("Keine DB")
                return
            
            print("📊 Lade Session...")
            result = self.db.client.table('sessions').select('*').order('created_at', desc=True).limit(1).execute()
            
            if not result.data:
                print("⚠️ Keine Sessions!")
                self.fail("Keine Daten")
                return
            
            session = result.data[0]
            sid = session.get('session_id')
            
            print(f"✅ Session: {sid[:8]}...")
            print(f"   User: {session.get('user_name')}")
            
            report = self.db.get_session_report_data(sid)
            if not report:
                self.fail("Report-Fehler")
                return
            
            template = MessageTemplates.session_report(session.get('user_name', 'User'), report)
            
            print("\n📤 Sende Report...")
            payload = {
                "embeds": [{
                    "title": template['title'],
                    "description": template['description'],
                    "color": template['color'],
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
            
            if post(self.notify.webhook_url, json=payload, timeout=5).status_code == 204:
                self.success("Report versendet")
            else:
                self.fail("Report Fehler")
        except Exception as e:
            self.fail(f"Report: {e}")
        self.wait()
    
    def summary(self):
        print(f"\n{'='*60}\n{BLUE}📊 SUMMARY{NC}\n{'='*60}\n")
        pct = (self.passed / self.test_count * 100) if self.test_count > 0 else 0
        
        print(f"Tests: {self.test_count}")
        print(f"{GREEN}✅ Bestanden: {self.passed}{NC}")
        print(f"{RED}❌ Fehlgeschlagen: {self.failed}{NC}")
        print(f"\n{BLUE}Erfolgsquote: {pct:.0f}%{NC}")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALLE TESTS BESTANDEN!{NC}")
        else:
            print(f"\n{YELLOW}⚠️ {self.failed} fehlgeschlagen{NC}")
        
        print(f"{'='*60}\n")
        
        color = 3066993 if self.failed == 0 else 15158332
        self.discord(
            "TEST ABGESCHLOSSEN",
            f"✅ {self.passed}/{self.test_count}\n❌ {self.failed}/{self.test_count}\n📊 {pct:.0f}%",
            color
        )
    
    def run_all(self):
        print(f"\n{'='*60}\n{BLUE}🧪 TEST SUITE - PRÄSENTATION{NC}\n{'='*60}\n")
        print("Enter zum Start...")
        input()
        
        try:
            self.test_button1()
            self.test_button2()
            self.test_led()
            self.test_buzzer()
            self.test_co2()
            self.test_steps()
            self.test_db()
            self.test_discord_ready()
            self.test_report()
            self.summary()
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}🛑 Unterbrochen{NC}\n")
            self.summary()
            sys.exit(0)

if __name__ == "__main__":
    TestSuite().run_all()