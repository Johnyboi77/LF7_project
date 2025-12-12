#!/bin/bash
# stop_both.sh - Stoppt beide PiTop Systeme sauber

set -e

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🛑 LEARNING ASSISTANT - SHUTDOWN SEQUENCE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Konfiguration
PITOP1_IP="${PITOP1_IP:-192.168.0.53}"
PITOP2_IP="${PITOP2_IP:-}"
PITOP_USER="${PITOP_USER:-pi}"
PROJECT_DIR="/home/pi/LF7_project"

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== FUNKTIONEN =====

stop_pitop1() {
    echo -e "${BLUE}⏹️  Stoppe PiTop 1...${NC}"
    
    ssh "$PITOP_USER@$PITOP1_IP" << ENDSSH1
cd $PROJECT_DIR

# Prozess beenden
pkill -f "python3 main_pitop1.py" || true

# Warten
sleep 1

# Bestätigen
if ! pgrep -f "python3 main_pitop1.py" > /dev/null; then
    echo "OK"
else
    # Force kill bei Bedarf
    pkill -9 -f "python3 main_pitop1.py" || true
    echo "FORCE"
fi
ENDSSH1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PiTop 1 gestoppt${NC}"
        return 0
    else
        echo -e "${RED}⚠️  Fehler beim Stoppen${NC}"
        return 1
    fi
}

stop_pitop2() {
    echo -e "${BLUE}⏹️  Stoppe PiTop 2...${NC}"
    
    ssh "$PITOP_USER@$PITOP2_IP" << ENDSSH2
cd $PROJECT_DIR

# Prozess beenden
pkill -f "python3 main_pitop2.py" || true

# Warten
sleep 1

# Bestätigen
if ! pgrep -f "python3 main_pitop2.py" > /dev/null; then
    echo "OK"
else
    pkill -9 -f "python3 main_pitop2.py" || true
    echo "FORCE"
fi
ENDSSH2
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PiTop 2 gestoppt${NC}"
        return 0
    else
        echo -e "${RED}⚠️  Fehler beim Stoppen${NC}"
        return 1
    fi
}

# ===== MAIN =====

echo "🔧 KONFIGURATION:"
echo "   PiTop 1: $PITOP_USER@$PITOP1_IP"
echo "   PiTop 2: $PITOP_USER@$PITOP2_IP"
echo ""

stop_pitop1
sleep 1

stop_pitop2

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ ALLE SYSTEME GESTOPPT${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📊 Status prüfen:"
echo "   $ ssh $PITOP_USER@$PITOP1_IP 'ps aux | grep main_pitop'"
echo "   $ ssh $PITOP_USER@$PITOP2_IP 'ps aux | grep main_pitop'"
echo ""