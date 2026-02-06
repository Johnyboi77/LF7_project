### Setup & Deployment Anleitung für PiTop 4 Projekt ###

# Virtual Environment erstellen aktivieren (wichtig für Installationen!)
cd LF7_project
python3 -m venv venv
source venv/bin/activate

# Altes Archiv löschen
cd /mnt/c/Users/knig
rm LF7_project.tar.gz
ls
cd LF7_project

# SSH-Verbindung zum PiTop 1 herstellen (jeweils neues Terminal)
--> Brauchen zuerst Wlan
--> Laptop & Pitop müssen anschlieeßnd im gleichen Netz sein

ssh pi@10.128.206.178
ssh pi@10.128.206.115

>Passwort: pi-top

# Alten Code auf SD Karte/Stick löschen (nach SSH Verbindung)
rm -rf ~/LF7_project

# Altes Archiv auf Laptop löschen
cd /mnt/c/Users/knigh
rm -f LF7_project.tar.gz

# Neues Archiv erstellen (Terminal ohne SSH Verbindung)
cd /mnt/c/Users/knigh

tar -czf LF7_project.tar.gz \
  --exclude='LF7_project/.git' \
  --exclude='LF7_project/venv' \
  --exclude='LF7_project/node_modules' \
  LF7_project/

# Archiv auf PiTops übertragen (Laptop Terminal)
cd /mnt/c/Users/knigh
scp LF7_project.tar.gz pi@10.128.206.178:~/
scp LF7_project.tar.gz pi@10.128.206.115:~/

>Passwort: pi-top

# Projekt entpacken, in Verzeichnis wechseln & Archivdatei löschen
tar -xzf LF7_project.tar.gz
cd ~/LF7_project
rm ~/LF7_project.tar.gz

# Virtual Environment auf PiTop erstellen (jeweils in Terminal mit SSH)
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Python-Pakete installieren #
pip install --upgrade pip
pip install -r requirements.txt

sudo apt-get install python3-pitop python3-gpiozero

### Troubleshooting ###

# Logout von Virtual Environment (venv) um neues zu generieren
exit 

# Deaktivieren von (venv)
deactivate

# Pythen Cache löschen
cd /mnt/c/Users/knigh/LF7_project
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

