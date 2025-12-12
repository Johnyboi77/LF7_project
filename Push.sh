#!/bin/bash
#ausführen mit:  ./Push.sh

REPO_PATH="/mnt/c/Users/knigh/LF7_project"
REMOTE_URL="https://github.com/Johnyboi77/LF7_project.git"
BRANCH="dev"

# TO change branch
# -->     git checkout -b dev

cd "$REPO_PATH" || exit 1

# Initialize if needed
if [ ! -d ".git" ]; then
    
    cd /mnt/c/Users/knigh/LF7_project
    git init
    git remote add origin "$REMOTE_URL"
    git branch -M main
    
fi 

git add .
git commit -m "$(date '+%Y-%m-%d %H:%M:%S') - Neue Bibliothek eingebunden - Lokale Tests erfolgreich"
git push origin "$BRANCH"

echo "✅ Push erfolgreich!"

# Einmalig ausführen - speichert deine Credentials dauerhaft
#    git config --global credential.helper store