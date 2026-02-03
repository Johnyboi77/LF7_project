Setup & Deployment Anleitung für PiTop 4 Projekt

# Baum anzeigen (auf Laptop)
cd /mnt/c/Users/knigh/LF7_project && tree -L 3 -I 'node_modules|.next|.git|dist|build'

# 1. In Projektverzeichnis gehen
cd /mnt/c/Users/knigh/LF7_project

# 2. Virtual Environment erstellen aktivieren (wichtig für Installationen!)
python3 -m venv venv
source venv/bin/activate

# 3. Altes Archiv löschen
cd /mnt/c/Users/knig
rm LF7_project.tar.gz
ls
cd LF7_project

# PITOP VORBEREITUNG / 1 und 2 (Jeweils in neuem Terminal) 
--> Brauchen zuerst WLAN!!! Laptop & Pitop müssen anschlieeßnd im gleichen Netz sein

# 4. SSH-Verbindung zum PiTop 1 herstellen (Terminal 2)
ssh pi@10.128.206.178
ssh pi@10.128.206.54
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
cd /mnt/c/Users/knigh
scp LF7_project.tar.gz pi@10.128.206.178:~/
scp LF7_project.tar.gz pi@10.128.206.54:~/
# Passwort: pi-top

scp LF7_project.tar.gz pi@:~/ 

# 6. Projekt entpacken und in Verzeichnis wechseln
tar -xzf LF7_project.tar.gz
cd ~/LF7_project

# 8. Archivdatei löschen (aufräumen)
rm ~/LF7_project.tar.gz

# 9. Virtual Environment auf PiTop erstellen
python3 -m venv venv
source venv/bin/activate
# Ausgabe sollte jetzt (venv) vor dem Pfad zeigen

### 10. Python-Pakete installieren ###
pip install --upgrade pip
pip install -r requirements.txt

# Terminal 1 - PiTop 1 (Arbeitsplatz)
ssh pi@ ...
cd ~/LF7_project
source venv/bin/activate
python3 main_pitop1.py

# Terminal 2 - PiTop 2 (Pausenzone)
ssh pi@ ...
cd ~/LF7_project
source venv/bin/activate
python3 main_pitop2.py

### Logout von (venv) pi@pi-top:~ $
exit 

#### Falls Daten neu generiert werden müssen
rm -rf LF7_project

# Pythen Cache löschen
cd /mnt/c/Users/knigh/LF7_project
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete


### TEST SCRIPTE ausführen

# 1. Pythen Cache löschen
cd /mnt/c/Users/knigh/LF7_project
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 2. Virtual Environment aktivieren
python3 -m venv venv
source venv/bin/activate

# 3. Test Skript ausführen (Datenbank Skript)
python3 test_db.py