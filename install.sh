#!/bin/bash
# install.sh - Setup Script für den Learning Assistant

echo "🚀 Learning Assistant - Installation"
echo "===================================="

# System Update
echo "📦 System Update..."
sudo apt-get update
sudo apt-get upgrade -y

# Python Dependencies
echo "🐍 Python Packages installieren..."
sudo apt-get install -y python3-pip python3-dev i2c-tools

# I2C aktivieren
echo "🔧 I2C aktivieren..."
sudo raspi-config nonint do_i2c 0

# Python Requirements
echo "📚 Python Libraries installieren..."
pip3 install -r requirements.txt

# Grove Library
echo "🌳 Grove Library installieren..."
curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -

# Datenbank erstellen
echo "💾 Datenbank initialisieren..."
python3 -c "from database.db_manager import DatabaseManager; import config; DatabaseManager(config.DB_PATH)"

# I2C Geräte testen
echo ""
echo "🔍 I2C Geräte scannen:"
sudo i2cdetect -y 1

echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "1. Raspberry Pi neu starten: sudo reboot"
echo "2. .env Datei erstellen für Discord/Telegram Tokens"
echo "3. GPIO Pins in config.py anpassen"
echo "4. Starten mit: python3 main.py"