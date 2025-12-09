# Sensor Dokumentation

## 🌡️ VOC and eCO2 Gas Sensor (SGP30)

### Technische Daten
- **SKU:** 101020512
- **Chip:** SGP30
- **Schnittstelle:** I2C (Adresse 0x58)
- **Messbereich eCO2:** 400 - 60.000 ppm
- **Messbereich TVOC:** 0 - 60.000 ppb
- **Betriebsspannung:** 3.3V / 5V

### Anschluss (Grove I2C)

Sensor → Raspberry Pi
VCC → 3.3V
GND → GND
SCL → GPIO 3 (SCL)
SDA → GPIO 2 (SDA)


### Besonderheiten
- ⏳ **15 Sekunden Warm-up Zeit** nach dem Start
- 🔄 **Baseline Kalibrierung:** Sensor verbessert sich über 12h
- 📊 **eCO2 berechnet** (nicht direkt gemessen, basiert auf VOC)

### Grenzwerte
- ✅ **400-1000 ppm:** Normal (Außenluft ~400 ppm)
- ⚠️ **1000-1500 ppm:** Erhöht - Lüften empfohlen
- 🚨 **>1500 ppm:** Kritisch - Sofort lüften!

---

## 👟 Step Counter (BMA400)

### Technische Daten
- **SKU:** 101020583
- **Chip:** BMA400
- **Schnittstelle:** I2C (Adresse 0x14)
- **Messbereich:** 3-Achsen, ±2g bis ±16g
- **Betriebsspannung:** 3.3V / 5V

### Anschluss (Grove I2C)

Sensor → Raspberry Pi
VCC → 3.3V
GND → GND
SCL → GPIO 3 (SCL)
SDA → GPIO 2 (SDA)

### Funktionen
- 🚶 Schrittzählung
- 🏃 Aktivitätserkennung
- 📱 Tap/Double-Tap Detection
- 🔋 Sehr stromsparend

### Kalibrierung
- Sensor muss horizontal liegen
- Nach Reset dauert es ~2-3 Schritte bis Erkennung startet
- Am besten am Körper befestigen für beste Genauigkeit

---

## 🔧 I2C Troubleshooting

### I2C Geräte finden:
```bash
sudo i2cdetect -y 1


# Erwartete Ausgabe

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- 14 -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- 58 -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --

# 0x14 = BMA400 (Step Counter)
0x58 = SGP30 (eCO2/VOC Sensor)

Häufige Probleme:
Sensor wird nicht erkannt:

I2C aktiviert? sudo raspi-config → Interface Options → I2C
Verkabelung prüfen
Sensor mit 3.3V versorgen (nicht 5V!)
Falsche Werte:

SGP30: Warm-up Phase abwarten
Step Counter: Reset durchführen

