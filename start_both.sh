#!/bin/bash
# start_both.sh - Startet beide PiTop Systeme

echo "════════════════════════════════════════════════════════"
echo "🚀 STARTING LEARNING ASSISTANT"
echo "════════════════════════════════════════════════════════"
echo ""

# ===== KONFIGURATION =====
PITOP1_IP="192.168.1.100"  # ← ANPASSEN!
PITOP2_IP="192.168.1.101"  # ← ANPASSEN!
PITOP_USER="pi"
PROJECT_DIR="/home/pi/LF7_project"

# ===== PiTop 1 starten =====
echo "📡 Starte PiTop 1 (Hauptsystem)..."

ssh $PITOP_USER@$PITOP1_IP << ENDSSH1
cd $PROJECT_DIR
source venv/bin/activate

# Alte Logs löschen
rm -f pitop1.log

# Im Hintergrund starten
nohup python3 main_pitop1.py --device=pitop1 > pitop1.log 2>&1 &

# PID speichern
echo \$! > pitop1.pid

echo "✅ PiTop 1 gestartet (PID: \$(cat pitop1.pid))"
ENDSSH1

sleep 2

# ===== PiTop 2 starten =====
echo "📡 Starte PiTop 2 (Mobiles System)..."

ssh $PITOP_USER@$PITOP2_IP << ENDSSH2
cd $PROJECT_DIR
source venv/bin/activate

# Alte Logs löschen
rm -f pitop2.log

# Im Hintergrund starten
nohup python3 main_pitop2.py --device=pitop2 > pitop2.log 2>&1 &

# PID speichern
echo \$! > pitop2.pid

echo "✅ PiTop 2 gestartet (PID: \$(cat pitop2.pid))"
ENDSSH2

sleep 2

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ BEIDE SYSTEME GESTARTET!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📊 Logs anzeigen:"
echo "   PiTop 1: ssh $PITOP_USER@$PITOP1_IP 'tail -f $PROJECT_DIR/pitop1.log'"
echo "   PiTop 2: ssh $PITOP_USER@$PITOP2_IP 'tail -f $PROJECT_DIR/pitop2.log'"
echo ""
echo "🛑 Systeme stoppen:"
echo "   ./stop_both.sh"
echo ""
echo "💡 Tipp: Öffne 2 Terminal-Fenster für Logs!"
echo "════════════════════════════════════════════════════════"
echo ""
