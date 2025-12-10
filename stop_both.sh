#!/bin/bash
# stop_both.sh - Stoppt beide PiTop Systeme

echo "════════════════════════════════════════════════════════"
echo "🛑 STOPPING LEARNING ASSISTANT"
echo "════════════════════════════════════════════════════════"
echo ""

# ===== KONFIGURATION =====
PITOP1_IP="192.168.1.100"  # ← ANPASSEN!
PITOP2_IP="192.168.1.101"  # ← ANPASSEN!
PITOP_USER="pi"
PROJECT_DIR="/home/pi/LF7_project"

# ===== PiTop 1 stoppen =====
echo "🛑 Stoppe PiTop 1..."

ssh $PITOP_USER@$PITOP1_IP << 'ENDSSH1'
cd ~/LF7_project

if [ -f pitop1.pid ]; then
    PID=$(cat pitop1.pid)
    if kill $PID 2>/dev/null; then
        echo "   ✅ PiTop 1 gestoppt (PID: $PID)"
    else
        echo "   ⚠️  Prozess nicht gefunden, versuche pkill..."
        pkill -f main_pitop1.py && echo "   ✅ PiTop 1 gestoppt" || echo "   ℹ️  Nichts zu stoppen"
    fi
    rm -f pitop1.pid
else
    pkill -f main_pitop1.py && echo "   ✅ PiTop 1 gestoppt" || echo "   ℹ️  Nichts zu stoppen"
fi
ENDSSH1

# ===== PiTop 2 stoppen =====
echo "🛑 Stoppe PiTop 2..."

ssh $PITOP_USER@$PITOP2_IP << 'ENDSSH2'
cd ~/LF7_project

if [ -f pitop2.pid ]; then
    PID=$(cat pitop2.pid)
    if kill $PID 2>/dev/null; then
        echo "   ✅ PiTop 2 gestoppt (PID: $PID)"
    else
        echo "   ⚠️  Prozess nicht gefunden, versuche pkill..."
        pkill -f main_pitop2.py && echo "   ✅ PiTop 2 gestoppt" || echo "   ℹ️  Nichts zu stoppen"
    fi
    rm -f pitop2.pid
else
    pkill -f main_pitop2.py && echo "   ✅ PiTop 2 gestoppt" || echo "   ℹ️  Nichts zu stoppen"
fi
ENDSSH2

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ BEIDE SYSTEME GESTOPPT!"
echo "════════════════════════════════════════════════════════"
echo ""
