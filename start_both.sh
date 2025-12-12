#!/bin/bash
# start_both.sh - Startet beide PiTop Systeme gleichzeitig
# Learning Assistant: PiTop 1 (Hauptsystem) + PiTop 2 (Mobiles System)

set -e  # Exit bei Fehler

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🚀 LEARNING ASSISTANT - STARTUP SEQUENCE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# ===== KONFIGURATION =====
PITOP1_IP="${PITOP1_IP:-192.168.0.53}"      # Default, kann überschrieben werden
PITOP2_IP="${PITOP2_IP:-}"
PITOP_USER="${PITOP_USER:-pi}"
PROJECT_DIR="/home/pi/LF7_project"
VENV_PATH="venv/bin/activate"

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ===== FUNKTIONEN =====

check_ssh_connection() {
    local ip=$1
    local device=$2
    
    echo -ne "${BLUE}🔌 Prüfe SSH-Verbindung zu $device ($ip)...${NC} "
    
    if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no "$PITOP_USER@$ip" "echo OK" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌ FEHLER!${NC}"
        echo -e "${RED}   Kann $device nicht erreichen ($ip)${NC}"
        return 1
    fi
}

check_requirements() {
    local ip=$1
    local device=$2
    
    echo -ne "${BLUE}📦 Prüfe Anforderungen auf $device...${NC} "
    
    ssh "$PITOP_USER@$ip" << ENDSSH > /dev/null 2>&1
cd $PROJECT_DIR

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "FAIL: Python3 nicht gefunden"
    exit 1
fi

# Check venv
if [ ! -f "$VENV_PATH" ]; then
    echo "FAIL: venv nicht aktivierbar"
    exit 1
fi

# Check .env
if [ ! -f ".env.${device}" ]; then
    echo "FAIL: .env.${device} nicht gefunden"
    exit 1
fi

echo "OK"
ENDSSH
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌ FEHLER!${NC}"
        return 1
    fi
}

start_pitop1() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📡 STARTE PITOP 1 (Hauptsystem - Arbeitsplatz)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # SSH Verbindung testen
    if ! check_ssh_connection "$PITOP1_IP" "PiTop 1"; then
        return 1
    fi
    
    # Requirements prüfen
    if ! check_requirements "$PITOP1_IP" "pitop1"; then
        return 1
    fi
    
    echo -ne "${BLUE}⚡ Starte main_pitop1.py...${NC} "
    
    ssh "$PITOP_USER@$PITOP1_IP" << ENDSSH1
cd $PROJECT_DIR
source $VENV_PATH

# Alte Prozesse killen (falls noch laufen)
pkill -f "python3 main_pitop1.py" || true
sleep 1

# Logs löschen
rm -f pitop1.log

# Start mit nohup
nohup python3 main_pitop1.py --device=pitop1 > pitop1.log 2>&1 &

# PID speichern
echo \$! > pitop1.pid

# Kurze Wartezeit für Startup-Fehler
sleep 2

# Check ob Prozess läuft
if ps -p \$(cat pitop1.pid) > /dev/null; then
    echo "OK"
else
    echo "FAIL"
    exit 1
fi
ENDSSH1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PiTop 1 läuft${NC}"
        echo "   📁 Log: $PROJECT_DIR/pitop1.log"
        return 0
    else
        echo -e "${RED}❌ FEHLER beim Start!${NC}"
        return 1
    fi
}

start_pitop2() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📱 STARTE PITOP 2 (Mobiles System - Pause)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # SSH Verbindung testen
    if ! check_ssh_connection "$PITOP2_IP" "PiTop 2"; then
        return 1
    fi
    
    # Requirements prüfen
    if ! check_requirements "$PITOP2_IP" "pitop2"; then
        return 1
    fi
    
    echo -ne "${BLUE}⚡ Starte main_pitop2.py...${NC} "
    
    ssh "$PITOP_USER@$PITOP2_IP" << ENDSSH2
cd $PROJECT_DIR
source $VENV_PATH

# Alte Prozesse killen
pkill -f "python3 main_pitop2.py" || true
sleep 1

# Logs löschen
rm -f pitop2.log

# Start mit nohup
nohup python3 main_pitop2.py --device=pitop2 > pitop2.log 2>&1 &

# PID speichern
echo \$! > pitop2.pid

# Kurze Wartezeit
sleep 2

# Check ob Prozess läuft
if ps -p \$(cat pitop2.pid) > /dev/null; then
    echo "OK"
else
    echo "FAIL"
    exit 1
fi
ENDSSH2
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PiTop 2 läuft${NC}"
        echo "   📁 Log: $PROJECT_DIR/pitop2.log"
        return 0
    else
        echo -e "${RED}❌ FEHLER beim Start!${NC}"
        return 1
    fi
}

# ===== MAIN STARTUP =====

echo "🔧 KONFIGURATION:"
echo "   PiTop 1: $PITOP_USER@$PITOP1_IP"
echo "   PiTop 2: $PITOP_USER@$PITOP2_IP"
echo "   Projekt: $PROJECT_DIR"
echo ""

# Beide Systeme parallel starten
PITOP1_OK=0
PITOP2_OK=0

# Starte PiTop 1
start_pitop1
PITOP1_OK=$?

# Kurze Verzögerung
sleep 2

# Starte PiTop 2
start_pitop2
PITOP2_OK=$?

# ===== SUMMARY =====

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 STARTUP STATUS"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ $PITOP1_OK -eq 0 ]; then
    echo -e "${GREEN}✅ PiTop 1${NC} - Arbeitsplatz-System läuft"
else
    echo -e "${RED}❌ PiTop 1${NC} - Startup fehlgeschlagen!"
fi

if [ $PITOP2_OK -eq 0 ]; then
    echo -e "${GREEN}✅ PiTop 2${NC} - Mobiles System läuft"
else
    echo -e "${RED}❌ PiTop 2${NC} - Startup fehlgeschlagen!"
fi

echo ""

if [ $PITOP1_OK -eq 0 ] && [ $PITOP2_OK -eq 0 ]; then
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${GREEN}🎉 BEIDE SYSTEME ERFOLGREICH GESTARTET!${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    echo "📺 LIVE LOGS ANZEIGEN:"
    echo ""
    echo "   PiTop 1 (Terminal 1):"
    echo "   $ ssh $PITOP_USER@$PITOP1_IP 'tail -f $PROJECT_DIR/pitop1.log'"
    echo ""
    echo "   PiTop 2 (Terminal 2):"
    echo "   $ ssh $PITOP_USER@$PITOP2_IP 'tail -f $PROJECT_DIR/pitop2.log'"
    echo ""
    echo "🔍 STATUS PRÜFEN:"
    echo "   $ ssh $PITOP_USER@$PITOP1_IP 'ps aux | grep main_pitop1'"
    echo "   $ ssh $PITOP_USER@$PITOP2_IP 'ps aux | grep main_pitop2'"
    echo ""
    echo "🛑 SYSTEME STOPPEN:"
    echo "   $ ./stop_both.sh"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    exit 0
else
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${RED}⚠️  EINIGE SYSTEME KONNTEN NICHT GESTARTET WERDEN!${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "🔧 DEBUGGING:"
    echo ""
    
    if [ $PITOP1_OK -ne 0 ]; then
        echo "   PiTop 1 Log:"
        echo "   $ ssh $PITOP_USER@$PITOP1_IP 'cat $PROJECT_DIR/pitop1.log'"
        echo ""
    fi
    
    if [ $PITOP2_OK -ne 0 ]; then
        echo "   PiTop 2 Log:"
        echo "   $ ssh $PITOP_USER@$PITOP2_IP 'cat $PROJECT_DIR/pitop2.log'"
        echo ""
    fi
    
    echo "💡 Häufige Probleme:"
    echo "   • SSH-Zugriff: SSH-Schlüssel konfiguriert?"
    echo "   • venv: 'python3 -m venv venv' ausgeführt?"
    echo "   • .env Dateien: '.env.pitop1' und '.env.pitop2' vorhanden?"
    echo "   • Dependencies: 'pip install -r requirements.txt' ausgeführt?"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    exit 1
fi