#!/usr/bin/env python3
"""
🧹 GPIO PIN RESET TOOL
Gibt ALLE GPIO-Pins frei und tötet blockierende Prozesse
Nutzung: python3 reset_gpio.py
"""

import os
import sys
import time
import subprocess

print("\n" + "="*60)
print("🧹 GPIO PIN RESET TOOL")
print("="*60 + "\n")

# ============================================================
# 1. PROZESS-CLEANUP
# ============================================================
print("📋 SCHRITT 1: Prozess-Cleanup")
print("-" * 60)

def kill_gpio_processes():
    """Tötet alle Prozesse die GPIO nutzen könnten"""
    
    processes_to_kill = [
        'test_pitop1.py',
        'test_pitop2.py',
        'main.py',
        'pitop',
        'python.*gpio',
    ]
    
    current_pid = os.getpid()
    killed_count = 0
    
    for process_name in processes_to_kill:
        try:
            # Finde alle PIDs
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid_str in pids:
                    if pid_str:
                        pid = int(pid_str)
                        if pid != current_pid:
                            try:
                                os.kill(pid, 9)
                                print(f"  ✅ Prozess getötet: {process_name} (PID: {pid})")
                                killed_count += 1
                            except ProcessLookupError:
                                pass
                            except PermissionError:
                                print(f"  ⚠️ Keine Berechtigung für PID {pid} - versuche sudo")
                                try:
                                    subprocess.run(['sudo', 'kill', '-9', str(pid)], check=True)
                                    print(f"  ✅ Mit sudo getötet: PID {pid}")
                                    killed_count += 1
                                except:
                                    print(f"  ❌ Konnte PID {pid} nicht töten")
        except Exception as e:
            pass
    
    if killed_count == 0:
        print("  ℹ️ Keine blockierenden Prozesse gefunden")
    else:
        print(f"  ✅ {killed_count} Prozess(e) getötet")
    
    # Kurze Pause
    time.sleep(1)

kill_gpio_processes()

# ============================================================
# 2. GPIOZERO CLEANUP
# ============================================================
print("\n📋 SCHRITT 2: gpiozero Cleanup")
print("-" * 60)

try:
    from gpiozero import Device
    from gpiozero.pins.lgpio import LGPIOFactory
    
    # Aktuelle Factory schließen
    try:
        Device.pin_factory.close()
        print("  ✅ gpiozero Factory geschlossen")
    except:
        print("  ℹ️ Keine aktive Factory gefunden")
    
    # Factory reset
    Device.pin_factory = None
    print("  ✅ gpiozero Factory zurückgesetzt")
    
except ImportError:
    print("  ⚠️ gpiozero nicht installiert")
except Exception as e:
    print(f"  ⚠️ gpiozero Fehler: {e}")

# ============================================================
# 3. LGPIO CLEANUP (NUCLEAR OPTION)
# ============================================================
print("\n📋 SCHRITT 3: lgpio Hardcore Cleanup")
print("-" * 60)

try:
    import lgpio
    
    pins_freed = 0
    chips_closed = 0
    
    # Durchlaufe alle möglichen GPIO-Chips (0-4)
    for chip_num in range(5):
        try:
            # Versuche Chip zu öffnen
            handle = lgpio.gpiochip_open(chip_num)
            print(f"  🔓 Chip {chip_num} geöffnet (Handle: {handle})")
            
            # Befreie ALLE GPIO-Pins auf diesem Chip (0-53 für Sicherheit)
            for gpio_pin in range(54):
                try:
                    lgpio.gpio_free(handle, gpio_pin)
                    pins_freed += 1
                except:
                    pass  # Pin war nicht belegt
            
            # Chip schließen
            lgpio.gpiochip_close(handle)
            chips_closed += 1
            print(f"  ✅ Chip {chip_num} geschlossen")
            
        except Exception as e:
            # Chip existiert nicht oder ist nicht verfügbar
            if "No such file" not in str(e):
                print(f"  ℹ️ Chip {chip_num}: {e}")
    
    print(f"\n  📊 Ergebnis:")
    print(f"     Chips verarbeitet: {chips_closed}")
    print(f"     Pins befreit: {pins_freed}")
    
except ImportError:
    print("  ⚠️ lgpio nicht installiert")
except Exception as e:
    print(f"  ⚠️ lgpio Fehler: {e}")

# ============================================================
# 4. PI-TOP SDK CLEANUP
# ============================================================
print("\n📋 SCHRITT 4: pi-top SDK Cleanup")
print("-" * 60)

try:
    # PMA (Peripheral Management Agent)
    try:
        from pitop.pma import PMA
        pma = PMA()
        pma.close()
        print("  ✅ pi-top PMA geschlossen")
    except:
        print("  ℹ️ PMA bereits geschlossen oder nicht aktiv")
    
    # Device Manager
    try:
        from pitop.common.device_manager import DeviceManager
        dm = DeviceManager()
        dm.close()
        print("  ✅ DeviceManager geschlossen")
    except:
        print("  ℹ️ DeviceManager bereits geschlossen")
    
except ImportError:
    print("  ⚠️ pi-top SDK nicht installiert")
except Exception as e:
    print(f"  ⚠️ pi-top SDK Fehler: {e}")

# ============================================================
# 5. SYSTEM GPIO SYSFS CLEANUP
# ============================================================
print("\n📋 SCHRITT 5: System GPIO Cleanup (sysfs)")
print("-" * 60)

try:
    # Alte sysfs Methode - für Legacy-Support
    gpio_path = "/sys/class/gpio"
    
    if os.path.exists(gpio_path):
        unexported = 0
        
        # Liste alle exportierten GPIOs
        for item in os.listdir(gpio_path):
            if item.startswith("gpio"):
                try:
                    gpio_num = item.replace("gpio", "")
                    unexport_path = f"{gpio_path}/unexport"
                    
                    with open(unexport_path, 'w') as f:
                        f.write(gpio_num)
                    
                    unexported += 1
                except:
                    pass
        
        if unexported > 0:
            print(f"  ✅ {unexported} sysfs GPIO(s) unexported")
        else:
            print("  ℹ️ Keine sysfs GPIOs zum Cleanup gefunden")
    else:
        print("  ℹ️ sysfs GPIO nicht verfügbar (modern kernel)")
        
except Exception as e:
    print(f"  ⚠️ sysfs Cleanup Fehler: {e}")

# ============================================================
# 6. HARDWARE PAUSE
# ============================================================
print("\n📋 SCHRITT 6: Hardware Settle Time")
print("-" * 60)
print("  ⏳ Warte 2 Sekunden für Hardware-Reset...")
time.sleep(2)
print("  ✅ Hardware bereit")

# ============================================================
# 7. VERIFIKATION
# ============================================================
print("\n📋 SCHRITT 7: Verifikation")
print("-" * 60)

# Prüfe ob noch Prozesse laufen
result = subprocess.run(
    ['pgrep', '-f', 'pitop|gpio'],
    capture_output=True,
    text=True
)

if result.stdout.strip():
    print("  ⚠️ Warnung: Noch aktive GPIO-Prozesse gefunden:")
    for line in result.stdout.strip().split('\n'):
        print(f"     PID: {line}")
else:
    print("  ✅ Keine blockierenden Prozesse mehr aktiv")

# Prüfe GPIO-Status
try:
    import lgpio
    handle = lgpio.gpiochip_open(0)
    print("  ✅ GPIO-Chip 0 erfolgreich geöffnet (verfügbar)")
    lgpio.gpiochip_close(handle)
except Exception as e:
    print(f"  ⚠️ GPIO-Chip Test: {e}")

# ============================================================
# FERTIG
# ============================================================
print("\n" + "="*60)
print("✅ GPIO RESET ABGESCHLOSSEN")
print("="*60)
print("\n💡 Nächste Schritte:")
print("   1. Warte 5 Sekunden")
print("   2. Starte dein Programm: python3 test_pitop1.py")
print("\n❓ Falls Fehler weiterhin auftreten:")
print("   → Reboot: sudo reboot")
print("   → Oder mit sudo ausführen: sudo python3 reset_gpio.py")
print("\n")