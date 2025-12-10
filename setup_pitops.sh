#!/bin/bash
# setup_pitops.sh - Intelligentes Setup & Deploy Script
# Erkennt automatisch ob Installation nötig ist oder nur Code-Update

set -e  # Bei Fehler abbrechen

echo "════════════════════════════════════════════════════════"
echo "🚀 LEARNING ASSISTANT - SETUP & DEPLOY"
echo "════════════════════════════════════════════════════════"
echo ""

# ===== KONFIGURATION =====
PITOP1_IP="192.168.0.53"  # ← ANPASSEN!
PITOP2_IP="192.168.0.54"  # ← ANPASSEN!
PITOP_USER="pi"
PROJECT_DIR="/home/pi/LF7_project"

# ===== FUNKTIONEN =====

check_ssh() {
    local ip=$1
    local name=$2
    
    echo "📡 Prüfe Verbindung zu $name ($ip)..."
    
    if ssh -o ConnectTimeout=5 -o BatchMode=yes $PITOP_USER@$ip exit 2>/dev/null; then
        echo "   ✅ $name erreichbar"
        return 0
    else
        echo "   ❌ $name nicht erreichbar!"
        echo "   💡 Prüfe:"
        echo "      - Ist PiTop eingeschaltet?"
        echo "      - Ist IP korrekt? ($ip)"
        echo "      - SSH aktiviert?"
        return 1
    fi
}

is_first_setup() {
    local ip=$1
    
    # Prüft ob Projektordner existiert
    if ssh $PITOP_USER@$ip "[ -d $PROJECT_DIR ]" 2>/dev/null; then
        return 1  # Nicht erstes Setup
    else
        return 0  # Erstes Setup
    fi
}

setup_pitop() {
    local ip=$1
    local name=$2
    local device_id=$3
    
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "🔧 SETUP: $name ($device_id)"
    echo "════════════════════════════════════════════════════════"
    
    if is_first_setup $ip; then
        echo "📦 Erstes Setup - Installiere alles..."
        
        ssh $PITOP_USER@$ip << 'ENDSSH'
# Update System
echo "1️⃣  System Update..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Python & Tools
echo "2️⃣  Python & Tools installieren..."
sudo apt-get install -y python3-pip python3-venv i2c-tools git -qq

# I2C aktivieren
echo "3️⃣  I2C aktivieren..."
sudo raspi-config nonint do_i2c 0

# Projektordner erstellen
echo "4️⃣  Projektordner erstellen..."
mkdir -p ~/LF7_project

echo "✅ Basis-Installation abgeschlossen"
ENDSSH
    else
        echo "✅ Setup bereits vorhanden, überspringe Installation"
    fi
    
    # Code kopieren (IMMER)
    echo "📤 Kopiere Code nach $name..."
    rsync -avz --quiet \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.log' \
        --exclude='.env*' \
        --exclude='node_modules' \
        ./ $PITOP_USER@$ip:$PROJECT_DIR/
    
    # .env Datei kopieren
    echo "📝 Kopiere .env Datei..."
    if [ -f ".env.$device_id" ]; then
        scp -q .env.$device_id $PITOP_USER@$ip:$PROJECT_DIR/.env
        echo "   ✅ .env.$device_id → .env"
    else
        echo "   ⚠️  .env.$device_id nicht gefunden!"
    fi
    
    # Dependencies installieren
    echo "📦 Python Packages installieren..."
    ssh $PITOP_USER@$ip << ENDSSH
cd $PROJECT_DIR

# Virtual Environment erstellen (falls nicht vorhanden)
if [ ! -d "venv" ]; then
    echo "   📦 Erstelle Virtual Environment..."
    python3 -m venv venv
fi

# Aktivieren und Packages installieren
source venv/bin/activate
pip3 install --quiet --upgrade pip
pip3 install --quiet -r requirements.txt

echo "✅ Dependencies installiert"
ENDSSH
    
    # Grove Library (nur für PiTop 2)
    if [ "$device_id" = "pitop2" ]; then
        echo "🌳 Grove Library prüfen..."
        ssh $PITOP_USER@$ip << 'ENDSSH'
if ! python3 -c "import grove" 2>/dev/null; then
    echo "   📦 Installiere Grove Library..."
    curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s - > /dev/null 2>&1
    echo "   ✅ Grove Library installiert"
else
    echo "   ✅ Grove Library bereits installiert"
fi
ENDSSH
    fi
    
    # Berechtigungen setzen
    ssh $PITOP_USER@$ip << ENDSSH
cd $PROJECT_DIR
chmod +x *.sh 2>/dev/null || true
echo "✅ Berechtigungen gesetzt"
ENDSSH
    
    echo "✅ $name setup abgeschlossen!"
}

test_connection() {
    local ip=$1
    local name=$2
    
    echo ""
    echo "🧪 Teste $name..."
    
    ssh $PITOP_USER@$ip << ENDSSH
cd $PROJECT_DIR
source venv/bin/activate

# Config testen
python3 -c "import config; print('✅ Config OK')" 2>/dev/null || echo "❌ Config Fehler"

# Supabase testen
python3 -c "from database.supabase_manager import SupabaseManager; db = SupabaseManager(); print('✅ Supabase OK' if db.client else '❌ Supabase Fehler')" 2>/dev/null || echo "❌ Supabase Fehler"
ENDSSH
}

# ===== HAUPTPROGRAMM =====

# Verbindungen prüfen
if ! check_ssh $PITOP1_IP "PiTop 1"; then
    echo ""
    echo "❌ Abbruch: PiTop 1 nicht erreichbar"
    exit 1
fi

if ! check_ssh $PITOP2_IP "PiTop 2"; then
    echo ""
    echo "❌ Abbruch: PiTop 2 nicht erreichbar"
    exit 1
fi

echo ""
echo "✅ Beide PiTops erreichbar"

# Setup PiTop 1
setup_pitop $PITOP1_IP "PiTop 1" "pitop1"

# Setup PiTop 2
setup_pitop $PITOP2_IP "PiTop 2" "pitop2"

# Tests
test_connection $PITOP1_IP "PiTop 1"
test_connection $PITOP2_IP "PiTop 2"

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ SETUP & DEPLOY ABGESCHLOSSEN!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📋 Nächste Schritte:"
echo "   1. ./start_both.sh     # Beide Systeme starten"
echo "   2. ./stop_both.sh      # Beide Systeme stoppen"
echo ""
echo "💡 Bei Code-Änderungen:"
echo "   - Einfach ./setup_pitops.sh nochmal ausführen"
echo "   - Installation wird übersprungen, nur Code wird kopiert"
echo ""
