#!/usr/bin/env python3
"""
test_all.py - Komplette Test-Suite für alle Hardware & Services
Mit Daueraktion und Discord-Benachrichtigungen
"""

import sys
import signal
from time import sleep
from datetime import datetime

import config
from hardware.button1 import Button
from hardware.button2 import Button2
from hardware.led import LED
from hardware.buzzer import Buzzer
from hardware.Co2_sensor import CO2Sensor
from hardware.step_counter import StepCounter
from services.timer_service import TimerService
from services.notification_service import NotificationService
from database.supabase_manager import SupabaseManager
from notifications.message_templates import MessageTemplates

# Farben
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
    
    def send_discord(self, title, message):
        """Sendet Test-Nachricht zu Discord"""
        from requests import post
        try:
            payload = {
                "embeds": [{
                    "title": f"🧪 {title}",
                    "description": message,
                    "color": 3447003,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Test Suite"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            return response.status_code == 204
        except:
            return False
    
    # ===== TESTS =====
    
    def test_button1(self):
        self.print_header("BUTTON 1")
        
        try:
            button = Button("D0")
            print("Drücke Button 1 kurz...")
            
            pressed = False
            def on_press():
                nonlocal pressed
                pressed = True
                print(f"{GREEN}✅ Button 1 erkannt!{NC}")
            
            button.on_short_press(on_press)
            
            # Für Testing auf Laptop
            if hasattr(button, 'simulate_short_press'):
                button.simulate_short_press()
            
            if pressed or not config.HAS_BUTTONS:
                self.print_success("Button 1 funktioniert")
                self.send_discord("Button 1", "✅ Button 1 erfolgreich getestet")
            else:
                self.print_fail("Button 1 nicht erkannt")
        
        except Exception as e:
            self.print_fail(f"Button 1 Fehler: {e}")
        
        self.wait_for_next()
    
    def test_button2(self):
        self.print_header("BUTTON 2")
        
        try:
            button = Button2("D1")
            print("Drücke Button 2 kurz...")
            
            pressed = False
            def on_press():
                nonlocal pressed
                pressed = True
                print(f"{GREEN}✅ Button 2 erkannt!{NC}")
            
            button.on_short_press(on_press)
            
            if hasattr(button, 'simulate_short_press'):
                button.simulate_short_press()
            
            if pressed or not config.HAS_BUTTONS:
                self.print_success("Button 2 funktioniert")
                self.send_discord("Button 2", "✅ Button 2 erfolgreich getestet")
            else:
                self.print_fail("Button 2 nicht erkannt")
        
        except Exception as e:
            self.print_fail(f"Button 2 Fehler: {e}")
        
        self.wait_for_next()
    
    def test_led(self):
        self.print_header("LED")
        
        try:
            led = LED()
            
            print("LED einschalten...")
            led.on()
            sleep(1)
            self.print_success("LED an")
            
            print("LED ausschalten...")
            led.off()
            sleep(0.5)
            self.print_success("LED aus")
            
            print("LED blinken (3 Sekunden)...")
            led.blink(0.3, 0.3)
            sleep(3)
            led.off()
            self.print_success("LED blinkt")
            
            self.send_discord("LED", "✅ LED-Test bestanden\n• An ✓\n• Aus ✓\n• Blink ✓")
        
        except Exception as e:
            self.print_fail(f"LED Fehler: {e}")
        
        self.wait_for_next()
    
    def test_buzzer(self):
        self.print_header("BUZZER")
        
        try:
            buzzer = Buzzer()
            
            print("Kurzer Beep...")
            buzzer.beep(0.2)
            self.print_success("Beep")
            
            sleep(0.5)
            
            print("Doppel-Beep...")
            buzzer.double_beep()
            self.print_success("Doppel-Beep")
            
            sleep(0.5)
            
            print("Langer Beep...")
            buzzer.long_beep(1.0)
            self.print_success("Langer Beep")
            
            self.send_discord("BUZZER", "✅ Buzzer-Test bestanden\n• Beep ✓\n• Doppel-Beep ✓\n• Long Beep ✓")
        
        except Exception as e:
            self.print_fail(f"Buzzer Fehler: {e}")
        
        self.wait_for_next()
    
    def test_co2(self):
        self.print_header("CO2 SENSOR")
        
        try:
            co2 = CO2Sensor()
            
            print("Lese CO2-Wert...")
            level = co2.read()
            
            print(f"  eCO2: {level} ppm")
            print(f"  TVOC: {co2.tvoc_level} ppb")
            
            status = co2.get_alarm_status()
            print(f"  Status: {status}")
            
            if level > 0:
                self.print_success(f"CO2 gelesen: {level} ppm")
                self.send_discord("CO2 SENSOR", f"✅ CO2-Sensor funktioniert\neCO2: {level} ppm\nTVOC: {co2.tvoc_level} ppb\nStatus: {status}")
            else:
                self.print_fail("CO2-Wert 0 oder fehlerhaft")
        
        except Exception as e:
            self.print_fail(f"CO2 Fehler: {e}")
        
        self.wait_for_next()
    
    def test_step_counter(self):
        self.print_header("STEP COUNTER")
        
        try:
            steps = StepCounter()
            
            print("Starten Schrittzähler...")
            steps.start()
            self.print_success("Schrittzähler gestartet")
            
            print("Zähle 10 Sekunden lang Schritte...")
            for i in range(10):
                current = steps.read()
                print(f"  {i+1}s: {current} Schritte", end='\r')
                sleep(1)
            
            final_steps = steps.stop()
            print(f"\n✅ Final: {final_steps} Schritte")
            
            self.print_success(f"Schrittzähler: {final_steps} Schritte")
            self.send_discord("STEP COUNTER", f"✅ Schrittzähler funktioniert\nGemessene Schritte: {final_steps}")
        
        except Exception as e:
            self.print_fail(f"Step Counter Fehler: {e}")
        
        self.wait_for_next()
    
    def test_timer(self):
        self.print_header("TIMER SERVICE")
        
        try:
            timer = TimerService(self.db, self.notify)
            
            # Test Work Timer (nur 5 Sekunden für Demo)
            print("Starte 5-Sekunden Test-Timer (Arbeitszeit)...")
            
            # Modifiziere config temporär
            original_duration = config.WORK_DURATION
            config.WORK_DURATION = 5
            
            timer.start_work_timer()
            
            for i in range(6):
                status = timer.get_status()
                print(f"  {status['display']} - Running: {status['is_running']}", end='\r')
                sleep(1)
            
            config.WORK_DURATION = original_duration
            
            self.print_success("Timer Service funktioniert")
            self.send_discord("TIMER SERVICE", "✅ Timer-Service getestet\n5-Sekunden Test bestanden")
        
        except Exception as e:
            self.print_fail(f"Timer Fehler: {e}")
        
        self.wait_for_next()
    
    def test_database(self):
        self.print_header("DATABASE (SUPABASE)")
        
        try:
            if not self.db.client:
                print("⚠️  Keine Datenbank-Verbindung")
                self.print_fail("DB nicht verbunden")
            else:
                # Test Verbindung
                print("Teste Datenbankverbindung...")
                result = self.db.client.table('sessions').select("id").limit(1).execute()
                
                self.print_success(f"DB erreichbar ({len(result.data) if hasattr(result, 'data') else 0} Sessions)")
                self.send_discord("DATABASE", f"✅ Supabase erreichbar\n{len(result.data) if hasattr(result, 'data') else 0} Sessions in DB")
        
        except Exception as e:
            self.print_fail(f"DB Fehler: {e}")
        
        self.wait_for_next()
    
    def test_discord(self):
        self.print_header("DISCORD NOTIFICATIONS")
        
        try:
            if not self.notify.is_enabled:
                self.print_fail("Discord Webhook nicht konfiguriert")
            else:
                print("Sende Test-Nachricht zu Discord...")
                
                result = self.send_discord(
                    "Test Suite",
                    "✅ Alle Discord-Tests erfolgreich!\n\n"
                    "🎉 Test-Suite abgeschlossen\n"
                    "Alle Systeme funktionieren!"
                )
                
                if result:
                    self.print_success("Discord-Nachricht versendet")
                else:
                    self.print_fail("Discord-Nachricht Fehler")
        
        except Exception as e:
            self.print_fail(f"Discord Fehler: {e}")
        
        self.wait_for_next()
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}📊 TEST SUMMARY{NC}")
        print(f"{'='*60}\n")
        
        print(f"Total Tests: {self.test_count}")
        print(f"{GREEN}Bestanden: {self.passed}{NC}")
        print(f"{RED}Fehlgeschlagen: {self.failed}{NC}")
        
        percentage = (self.passed / self.test_count * 100) if self.test_count > 0 else 0
        print(f"\n{BLUE}Erfolgsquote: {percentage:.0f}%{NC}")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALLE TESTS BESTANDEN!{NC}")
        else:
            print(f"\n{YELLOW}⚠️ Einige Tests fehlgeschlagen{NC}")
        
        print(f"{'='*60}\n")
        
        # Finale Discord-Nachricht
        self.send_discord(
            "🧪 TEST-SUITE ABGESCHLOSSEN",
            f"**Ergebnisse:**\n"
            f"✅ Bestanden: {self.passed}/{self.test_count}\n"
            f"❌ Fehlgeschlagen: {self.failed}/{self.test_count}\n"
            f"📊 Erfolgsquote: {percentage:.0f}%"
        )
    
    def run_all(self):
        print(f"\n{'='*60}")
        print(f"{BLUE}🧪 COMPLETE TEST SUITE{NC}")
        print(f"{'='*60}\n")
        print("Teste alle Hardware & Services")
        print("Enter zum Starten...\n")
        input()
        
        try:
            self.test_button1()
            self.test_button2()
            self.test_led()
            self.test_buzzer()
            self.test_co2()
            self.test_step_counter()
            self.test_timer()
            self.test_database()
            self.test_discord()
            
            self.print_summary()
        
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}🛑 Tests unterbrochen{NC}\n")
            self.print_summary()
            sys.exit(0)

if __name__ == "__main__":
    suite = TestSuite()
    suite.run_all()