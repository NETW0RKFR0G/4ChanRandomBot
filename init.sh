#!/bin/bash
# ============================================================
#  init.sh — Setup du bot 4chan → Telegram sur Oracle Cloud
# ============================================================

echo "🚀 Installation du bot 4chan Telegram..."

# Mise à jour du système
sudo apt update -y

# Installation de Python et pip
sudo apt install python3 python3-pip -y

# Installation des dépendances Python
pip3 install requests --break-system-packages

# Création du dossier du bot
mkdir -p ~/4chanbot

# Copie du script si présent
if [ -f ~/4chan_telegram_bot.py ]; then
    cp ~/4chan_telegram_bot.py ~/4chanbot/
    echo "✅ Script copié dans ~/4chanbot/"
fi

echo ""
echo "✅ Installation terminée !"
echo "👉 Lance le bot avec : nohup python3 ~/4chan_telegram_bot.py &"
