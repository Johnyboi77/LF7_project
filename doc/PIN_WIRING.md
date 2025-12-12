# test1_led.py
LED Rot (CO2 Warnung)
Port: D2
GPIO: 22
Hinweise: Leuchtet >1000ppm, blinkt >1500ppm. Widerstände integriert.
Troubleshooting:
LED bleibt dunkel → GPIO22 prüfen, Modul evtl. defekt.

# test2_button1.py
Button 1 (Session Start/Reset/Ende)
Port: D0
GPIO: 17
Hinweise: Kurz = Start, Doppelklick = Reset, Lang >5s = Ende.
Troubleshooting:
Keine Erkennung → Kabel prüfen, GPIO17 korrekt?

# test3_button2.py
Button 2 (Pause Storno)
Port: D1
GPIO: 27
Hinweise: Macht letzte Pause rückgängig.
Troubleshooting:
Keine Reaktion → Kabel prüfen, GPIO27 prüfen.

# test4_buzzer.py
Buzzer (aktiv)
Port: D5
GPIO: 25
Hinweise: Kein PWM nötig. Nicht zu lange piepen lassen.
Troubleshooting:
Kein Ton → Kabel, GPIO25, Modul prüfen.

# test5_co2sensor.py
CO2 Sensor SGP30
Port: I2C-1
GPIO intern: SDA=2, SCL=3
Hinweise: Einstecken + 15s warm-up. I2C-Adresse 0x58.
Troubleshooting:
i2cdetect zeigt nichts → Kabel falsch.
Werte ändern sich nicht → 60s laufen lassen oder reboot.

# test6_step_counter.py
BMA400 Step Counter
Port: I2C-1
I2C-Adresse: 0x14
Hinweise: Muss fest montiert sein. Reset bei jeder Pause.
Troubleshooting:
i2cdetect zeigt 0x14 nicht → Kabel falsch.
Schritte = 0 → Keine Bewegung oder locker montiert.

# --> Allgemeine Troubleshooting Schritte
I2C prüfen → i2cdetect -y 1
Erwartete Adressen:
0x58 = SGP30
0x14 = BMA400

GPIO prüfen → gpio readall

# Python-Test:
python3
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
print("OK")

# Grove-Kabel prüfen → Stecker darf nicht verdreht sein.

# PiTop-spezifisch 
pt-devices list