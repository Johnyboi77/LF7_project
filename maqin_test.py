# test_hardware.py
from pitop import Button, Buzzer, LED

# Teste jeden Button einzeln
btn = Button("D0")  # Anpassen an deine Beschriftung
buzzer = Buzzer("D3")

def test():
    print("Drücke den Button...")
    buzzer.on()
    time.sleep(0.5)
    buzzer.off()

btn.when_pressed = test
signal.pause()

# 1. Button 1 kurz → "🟦 ARBEITSZEIT: 30:00"
# 2. Warten 5 Sekunden → "🟦 Arbeitszeit: 29:55"
# 3. Button 2 kurz → "⚠️ Laufender Timer wird überschrieben!"
  #                 "🟩 PAUSENZEIT: 10:00"
# 4. Button 1 kurz → "⚠️ Laufender Timer wird überschrieben!"
                   "🟦 ARBEITSZEIT: 30:00"
# Test 2: CO2-Warnung Demo

# Normal (< 600 ppm):     ⚫ LED aus
# Erhöht (600-800 ppm):   🔴 LED an
# Kritisch (> 800 ppm):   🔴 LED an + Buzzer piept
# Demo-Tipp: Atmet direkt auf den Sensor, um schnell hohe Werte zu erreichen! 😮‍💨