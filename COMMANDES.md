# 📖 Documentation — Bot 4chan → Telegram
# Répertoire : D:\Root\Claude\4ChanRandomBot

---

## 🔧 SETUP INITIAL

```bash
# 1. Installer les dépendances
sudo apt update -y && sudo apt install python3 python3-pip -y
pip3 install requests --break-system-packages

# 2. Uploader le script (depuis ton PC)
scp -i ~/.ssh/oracle.key 4chan_telegram_bot.py ubuntu@151.145.58.148:~/
```

---

## 🤖 GESTION DU BOT

```bash
# Démarrer le bot (en arrière-plan)
nohup python3 ~/4chan_telegram_bot.py &

# Arrêter le bot
pkill -f 4chan_telegram_bot.py

# Redémarrer le bot
pkill -f 4chan_telegram_bot.py && nohup python3 ~/4chan_telegram_bot.py &

# Vérifier si le bot tourne
ps aux | grep 4chan_telegram_bot.py
```

---

## 📋 LOGS

```bash
# Voir les logs en temps réel
tail -f nohup.out

# Voir les 20 dernières lignes
tail -20 nohup.out

# Voir tous les logs
cat nohup.out

# Effacer les logs
> nohup.out
```

---

## 🧪 TESTS

```bash
# Tester l'envoi d'un thread avec image
python3 -c "
import requests, html
BOT_TOKEN = 'TON_TOKEN'
CHAT_ID = '-1004472784843'
BOARD = 'b'
ids = []
for page in requests.get(f'https://a.4cdn.org/{BOARD}/threads.json').json():
    for t in page['threads']:
        ids.append(t['no'])
for no in ids[:30]:
    r = requests.get(f'https://a.4cdn.org/{BOARD}/thread/{no}.json').json()
    t = r['posts'][0]
    if t.get('tim'):
        com = html.unescape(t.get('com','')).replace('<br>','\n').replace('<wbr>','')
        sub = html.unescape(t.get('sub',''))
        title = sub if sub else (com[:80] + '...' if len(com) > 80 else com)
        image_url = f'https://i.4cdn.org/{BOARD}/{t[\"tim\"]}{t[\"ext\"]}'
        text = f'📌 <b>#{no}</b>\n<b>{title}</b>\n\n🔗 <a href=\"https://boards.4chan.org/{BOARD}/thread/{no}\">/b/{no}</a>'
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={'chat_id': CHAT_ID,'photo': image_url,'caption': text[:1024],'parse_mode': 'HTML'})
        print(f'Envoyé: #{no}')
        break
"

# Vérifier la connexion Telegram
curl -s "https://api.telegram.org/botTON_TOKEN/getMe"

# Vérifier le Chat ID
curl -s "https://api.telegram.org/botTON_TOKEN/getUpdates"
```

---

## ✏️ MODIFIER LE SCRIPT

```bash
# Ouvrir l'éditeur
nano ~/4chan_telegram_bot.py

# Sauvegarder dans nano : Ctrl+X → Y → Enter
```

---

## 🔑 INFOS IMPORTANTES

| Variable      | Valeur                          |
|---------------|---------------------------------|
| IP Serveur    | 151.145.58.148                  |
| Utilisateur   | ubuntu (ou lemouchard)          |
| CHAT_ID       | -1004472784843                  |
| Channel       | @random4chan                    |
| Script        | ~/4chan_telegram_bot.py         |
| Logs          | ~/nohup.out                     |
| State file    | ~/seen_threads.json             |

---

## 🔄 RÉINITIALISER LES THREADS VUS

```bash
# Efface la mémoire des threads (le bot repart à zéro)
rm ~/seen_threads.json
```

---

## 🌐 CONNEXION AU SERVEUR

```bash
# Depuis Cloud Shell Oracle
ssh -i ~/.ssh/oracle_new lemouchard@151.145.58.148

# Depuis ton PC (MobaXterm ou PowerShell)
ssh -i D:\Root\Claude\4ChanRandomBot\ssh-key-2026-06-14.key ubuntu@151.145.58.148
```
