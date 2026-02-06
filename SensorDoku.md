### Sensor-Dokumentation ###

# Übersicht
Sensor	  Typ	                            Anschluss	Funktion
SGP30	  Luftqualitätssensor	            I2C	        CO2 & TVOC Messung
BMA456	  3-Achsen Beschleunigungssensor	I2C	        Schrittzählung

# 1. CO2 Sensor - SGP30
>Sensor-Informationen

Eigenschaft	        Wert 
Modell	            Sensirion SGP30 Typ	MEMS Gassensor (MOX)
Schnittstelle	    I2C
I2C-Adresse	        0x58 (fest)
Betriebsspannung	1.8V - 3.3V
Messbereich         CO2	400 - 60'000 ppm
Messbereich TVOC	0 - 60'000 ppb

>Benötigte Hardware
┌──────────────────────────────────────────┐
│     SGP30                                │
│                                          │
│  VCC ──────────────── 3.3V               │
│  GND ──────────────── GND                │
│  SDA ──────────────── I2C SDA (GPIO 2)   │ 
│  SCL ──────────────── I2C SCL (GPIO 3)   │
└──────────────────────────────────────────┘
Grove-Variante: Einfach in einen der I2C-Ports des Pi-Top stecken.

>Benötigte Software

(System-Pakete)
sudo apt-get install -y python3-pip i2c-tools

(I2C aktivieren - falls nicht geschehen)
sudo raspi-config nonint do_i2c 0

(Python-Bibliotheken)

pip install adafruit-circuitpython-sgp30
pip install adafruit-blinka

>Abhängigkeiten im Code (python)

import board               # CircuitPython Board-Definitionen
import adafruit_sgp30      # SGP30 Treiber

>Wichtige Erkenntnisse - Was gut funktioniert

Aspekt	             Details
Initialisierung	     iaq_init() muss aufgerufen werden
Baseline	         Kann gespeichert/geladen werden für schnellere Kalibrierung
Messwerte	         sensor.eCO2 und sensor.TVOC direkt lesbar

>Herausforderungen

Problem	            Lösung
Aufwärmzeit	        Sensor braucht ~15-30 Sekunden für stabile Werte
Kalibrierung	    Baseline nach 12h Betrieb speichern: sensor.get_iaq_baseline()
I2C-Fehler	        Retry-Mechanismus mit 3 Versuchen implementieren
Sensor-Drift	    Baseline regelmäßig aktualisieren

>Schwellenwerte (unsere Konfiguration in python)

CO2_WARNING_THRESHOLD = 600    # ppm - Lüften empfohlen
CO2_CRITICAL_THRESHOLD = 800   # ppm - Lüften notwendig

>Baseline-Handling (in python)

--> Baseline setzen (nach Kalibrierung)
sensor.set_iaq_baseline(0x8973, 0x8AAE)

--> Baseline auslesen (nach 12h Betrieb)
eco2_base, tvoc_base = sensor.get_iaq_baseline()

# 2. Step Counter - BMA456
>Sensor-Informationen

Eigenschaft	        Wert
Modell	            Bosch BMA456
Typ	                3-Achsen MEMS Beschleunigungssensor
Schnittstelle	    I2C
I2C-Adressen	    0x18 (SDO=GND) oder 0x19 (SDO=VCC)
Chip-ID	            0x16
Betriebsspannung	1.8V - 3.3V
Messbereich	        ±2g, ±4g, ±8g, ±16g
Auflösung	        16-bit

>Benötigte Hardware

┌─────────────────────────────────────────────┐
│    BMA456                                   │
│   (Grove)                                   │
│                                             │
│  VCC ──────────────── 3.3V                  │
│  GND ──────────────── GND                   │
│  SDA ──────────────── I2C SDA (GPIO 2)      │
│  SCL ──────────────── I2C SCL (GPIO 3)      │
│  SDO ──────────────── GND (für Addr 0x18)   │
└─────────────────────────────────────────────┘
Grove-Variante: Einfach in einen der I2C-Ports des Pi-Top stecken.

>Benötigte Software

(System-Pakete)
sudo apt-get install -y python3-pip i2c-tools

(I2C aktivieren)
sudo raspi-config nonint do_i2c 0

(Python-Bibliotheken)
pip install smbus2

>Abhängigkeiten im Code (in python)

from smbus2 import SMBus       # I2C-Kommunikation

>Wichtige Register

Register	    Adresse	    Funktion
CHIP_ID	        0x00	    Chip-Identifikation (0x16)
ACC_X_LSB	    0x12        Beschleunigungsdaten Start
ACC_CONF	    0x40	    Abtastrate & Filter
ACC_RANGE	    0x41	    Messbereich
PWR_CONF	    0x7C	    Power-Konfiguration
PWR_CTRL	    0x7D	    Accelerometer Ein/Aus
CMD	            0x7E	    Soft Reset etc.

>Wichtige Erkenntnisse - Was gut funktioniert

Aspekt	            Details
Auto-Detection	    Beide I2C-Adressen (0x18, 0x19) werden gescannt
Chip-ID Check	    Verifizierung dass korrekter Sensor (0x16)
Konfiguration	    100Hz Abtastrate, ±4g Range optimal für Schrittzählung

>Herausforderungen

Problem	                    Lösung
Keine fertige Library	    Eigene Implementierung mit smbus2
Timing kritisch	            20ms Pause nach jedem I2C-Write
Soft Reset	                100ms Wartezeit nach Reset notwendig
I2C-Fehler	                Retry-Mechanismus (3 Versuche)

>Schrittzähler-Algorithmus

┌─────────────────────────────────────────────────────────┐
│                  SCHRITTZÄHLUNG                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Beschleunigung lesen (X, Y, Z)                      │
│                    ↓                                    │
│  2. Magnitude berechnen: √(x² + y² + z²)                │
│                    ↓                                    │
│  3. Glättung (Moving Average, 5 Samples)                │
│                    ↓                                    │
│  4. Dynamische Baseline tracken (100 Samples)           │
│                    ↓                                    │
│  5. Abweichung = Smoothed - Baseline                    │
│                    ↓                                    │
│  6. Peak Detection:                                     │
│     - Deviation > +0.12g → Peak Start                   │
│     - Deviation < +0.04g → Peak Ende → SCHRITT!         │
│                    ↓                                    │
│  7. Min. Interval: 0.35s zwischen Schritten             │
│                                                         │
└─────────────────────────────────────────────────────────┘

>Sensor-Initialisierung (in python)

--> 1. Soft Reset
write(REG_CMD, 0xB6)
sleep(0.1)  # 100ms warten!

--> 2. Advanced Power Save OFF
write(REG_PWR_CONF, 0x00)

--> 3. Accelerometer ON
write(REG_PWR_CTRL, 0x04)

--> 4. Config: 100Hz, Normal BW (Körpergewicht)
write(REG_ACC_CONF, 0xA8)

--> 5. Range: ±4g
write(REG_ACC_RANGE, 0x01)

>Skalierung der Rohdaten (In python)

(BMA456: 16-bit signed / Bei ±4g: 32768 LSB = 4g)

scale = range_g / 32768.0  # 4 / 32768 = 0.000122

(Umrechnung)
x_g = x_raw * scale
y_g = y_raw * scale
z_g = z_raw * scale

-->Bei Ruhe: magnitude ≈ 1.0g (Erdanziehung)

# 3. Allgemeine Hinweise

>Fallback/Dummy-Modus

Beide Sensoren haben einen automatischen Fallback wenn:
- Hardware nicht angeschlossen
- I2C-Fehler auftreten
- Python-Bibliotheken fehlen

Sensor      Fallback-Verhalten
SGP30       Gibt konstant 400 ppm CO2, 0 ppb TVOC zurück
BMA456      Gibt konstant 0 Schritte zurück

>Error-Handling (CO2 Sensor)

- Maximale Fehleranzahl: 10
- Nach 10 Fehlern wird Sensor deaktiviert
- Jede Lesung: bis zu 3 Retry-Versuche
- Pause zwischen Retries: 100ms

>Bewegungs-Berechnung (aus config.py)

Parameter               Wert        Beschreibung
CALORIES_PER_STEP       0.05        kcal pro Schritt
METERS_PER_STEP         0.75        Meter pro Schritt (~75cm Schrittlänge)

Beispiel: 1000 Schritte = 50 kcal, 750m

>Debug-Funktionen

(StepCounter Debug-Modus aktivieren)
counter.enable_debug()   # Zeigt Rohdaten im Terminal
counter.disable_debug()  # Normaler Betrieb

(Rohdaten manuell auslesen)
data = counter.get_raw_acceleration()
--> Gibt zurück: {'x': 0.01, 'y': -0.02, 'z': 0.98, 'magnitude': 0.98}

# 4. Alle benötigten Pakete

>System (apt)
sudo apt-get update
sudo apt-get install -y python3-pip i2c-tools python3-smbus

>Python (pip)
pip install adafruit-circuitpython-sgp30 adafruit-blinka smbus2

>I2C prüfen
i2cdetect -y 1

Erwartete Adressen:
0x18 oder 0x19 = BMA456 (StepCounter)
0x58           = SGP30 (CO2 Sensor)