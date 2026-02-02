Setup & Deployment Anleitung für PiTop 4 Projekt

# Baum anzeigen (auf Laptop)
cd /mnt/c/Users/knigh/LF7_project && tree -L 3 -I 'node_modules|.next|.git|dist|build'

# 1. In Projektverzeichnis gehen
cd /mnt/c/Users/knigh/LF7_project

# 2. Virtual Environment aktivieren (wichtig für Installationen!)
source ~/grove_env/bin/activate


# PITOP VORBEREITUNG / 1 und 2 (Jeweils in neuem Terminal) 
--> Brauchen zuerst WLAN!!! Laptop & Pitop müssen anschlieeßnd im gleichen Netz sein

# 3. PiTop mit USB-Stick oder MicroSD booten
 --> (Nach Reset nötig, da von anderen Gruppen genutzt!)

# 4. SSH-Verbindung zum PiTop 1 herstellen (Terminal 2)
ssh pi@192.168.0.53 
# Passwort: pi-top

# 4.1 SSH-Verbindung zum PiTop 2 herstellen (terminal 3)
ssh pi@
# Passwort:

# Falls altes Projekt vorhanden → löschen

rm -rf ~/LF7_project
#Alte Projekte anderer Gruppen auch löschen!

# 4.3 Altes Archiv auf Laptop löschen (zweites Terminal!)
cd /mnt/c/Users/knigh
rm -f LF7_project.tar.gz
echo "✅ Altes Archiv gelöscht"

# 4.5 Neues Archiv erstellen (OHNE venv, node_modules, .git)
cd /mnt/c/Users/knigh

tar -czf LF7_project.tar.gz \
  --exclude='LF7_project/.git' \
  --exclude='LF7_project/venv' \
  --exclude='LF7_project/node_modules' \
  LF7_project/

# 5. Archiv auf PiTops übertragen 
scp LF7_project.tar.gz pi@192.168.0.53:~/
# Passwort: pi-top

scp LF7_project.tar.gz pi@:~/ 


# 5.1. Upload prüfen (auf PiTop via SSH)
ls -la

# 5.2  Optional: .env Dateien extra übertragen (falls nicht im Archiv)

cd /mnt/c/Users/knigh/LF7_project
scp .env.pitop1 .env.pitop2 pi@192.168.0.53:~/LF7_project/

# 6. Projekt entpacken und in Verzeichnis wechseln
tar -xzf LF7_project.tar.gz
cd ~/LF7_project

# 8. Archivdatei löschen (aufräumen)
rm ~/LF7_project.tar.gz

# 9. Virtual Environment auf PiTop erstellen
python3 -m venv venv
source venv/bin/activate
# Ausgabe sollte jetzt (venv) vor dem Pfad zeigen

# 10. Python-Pakete installieren
pip install -r requirements.txt

Startcommands

# Terminal 1 - PiTop 1 (Arbeitsplatz)
ssh pi@192.168.0.53
cd ~/LF7_project
source venv/bin/activate
python3 main_pitop1.py

# Terminal 2 - PiTop 2 (Pausenzone)
ssh pi@192.168.0.54
cd ~/LF7_project
source venv/bin/activate
python3 main_pitop2.py

### Logout von (venv) pi@pi-top:~ $
exit 

#### Falls Daten neu generiert werden müssen
rm -rf LF7_project

### Outlier 

Zur Konfig wegen Supabase:

✅ resolv.conf sieht gut aus!
Lass uns mit Python testen (ohne extra Pakete zu installieren):

Test 1: DNS mit Python
bash
# DNS direkt mit Python testen
python3 -c "import socket; print(socket.gethostbyname('google.com'))"
Test 2: Ping nochmal versuchen
bash
ping -c 2 google.com
Test 3: Supabase URL testen
bash
python3 -c "import socket; print(socket.gethostbyname('lbaeftxthrpajcgdxdcz.supabase.co'))"
Führe alle 3 aus und zeig mir was passiert!

Wenn Python die DNS-Auflösung schafft, sollte auch dein test_db.py funktionieren:

bash
# Dann direkt dein Script testen
cd /mnt/c/Users/knigh/LF7_project
source venv/bin/activate
python test_db.py
🎯 Zeig mir die Ausgabe!
