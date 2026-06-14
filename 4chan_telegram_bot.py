"""
4chan /b/ → Telegram Bot
========================
Surveille les nouveaux threads sur /b/ et les envoie dans ton channel Telegram.

SETUP :
1. Crée un bot Telegram via @BotFather → copie le token
2. Ajoute le bot à ton channel et récupère le CHAT_ID
   (envoie un msg dans ton channel, puis visite :
    https://api.telegram.org/bot<TOKEN>/getUpdates)
3. Remplis les variables BOT_TOKEN et CHAT_ID ci-dessous
4. Installe les dépendances : pip install requests
5. Lance : python 4chan_telegram_bot.py

DÉPENDANCES : requests (stdlib uniquement sinon)
"""

import requests
import time
import json
import os
import html
import logging

# ─────────────────────────────────────────────
#  ⚙️  CONFIGURATION  — À remplir !
# ─────────────────────────────────────────────
BOT_TOKEN = "VOTRE_BOT_TOKEN_ICI"          # ex: 123456:ABCdef...
CHAT_ID   = "VOTRE_CHAT_ID_ICI"            # ex: -1001234567890 ou @moncanal

BOARD     = "b"                             # board 4chan
INTERVAL  = 60                              # secondes entre chaque vérification
STATE_FILE = "seen_threads.json"            # fichier pour mémoriser les threads déjà vus
MAX_MESSAGE_LENGTH = 4000                   # limite Telegram (4096 chars)
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

FOURCHAN_API  = f"https://a.4cdn.org/{BOARD}/threads.json"
FOURCHAN_BASE = f"https://boards.4chan.org/{BOARD}/thread/"
TELEGRAM_API  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
FOURCHAN_IMG  = "https://i.4cdn.org/{board}/{tim}{ext}"


# ── Persistance des threads déjà vus ──────────────────────────────────────────

def load_seen() -> set:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen), f)


# ── Appels 4chan API ───────────────────────────────────────────────────────────

def fetch_catalog() -> list[dict]:
    """Retourne la liste des threads du catalog /b/."""
    try:
        r = requests.get(FOURCHAN_API, timeout=15, headers={"User-Agent": "4chan-tg-bot/1.0"})
        r.raise_for_status()
        pages = r.json()
        threads = []
        for page in pages:
            threads.extend(page.get("threads", []))
        return threads
    except Exception as e:
        log.error(f"Erreur catalog : {e}")
        return []


# ── Formatage du message Telegram ─────────────────────────────────────────────

def clean(text: str | None) -> str:
    if not text:
        return ""
    return html.unescape(text).replace("<br>", "\n").replace("<wbr>", "")


def build_message(thread: dict) -> str:
    no   = thread.get("no", "?")
    sub  = clean(thread.get("sub", ""))
    com  = clean(thread.get("com", ""))
    url  = f"{FOURCHAN_BASE}{no}"

    parts = [f"📌 <b>Nouveau thread #{no}</b>"]
    if sub:
        parts.append(f"<b>{sub[:200]}</b>")
    if com:
        excerpt = com[:800] + ("…" if len(com) > 800 else "")
        parts.append(excerpt)
    parts.append(f'\n🔗 <a href="{url}">/b/{no}</a>')

    return "\n".join(parts)


def get_image_url(thread: dict) -> str | None:
    tim = thread.get("tim")
    ext = thread.get("ext")
    if tim and ext and ext.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        return FOURCHAN_IMG.format(board=BOARD, tim=tim, ext=ext)
    return None


# ── Envoi Telegram ─────────────────────────────────────────────────────────────

def send_telegram(thread: dict):
    text      = build_message(thread)
    image_url = get_image_url(thread)

    if image_url:
        # Essaie d'envoyer avec image
        payload = {
            "chat_id":    CHAT_ID,
            "photo":      image_url,
            "caption":    text[:1024],       # caption limité à 1024
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }
        r = requests.post(TELEGRAM_PHOTO, json=payload, timeout=15)
        if r.ok:
            return
        log.warning(f"Photo échouée ({r.status_code}), envoi texte seul…")

    # Texte seul (ou fallback)
    payload = {
        "chat_id":                  CHAT_ID,
        "text":                     text[:MAX_MESSAGE_LENGTH],
        "parse_mode":               "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(TELEGRAM_API, json=payload, timeout=15)
    if not r.ok:
        log.error(f"Telegram error {r.status_code}: {r.text[:200]}")


# ── Boucle principale ─────────────────────────────────────────────────────────

def main():
    log.info(f"🤖 Bot démarré — surveillance de /b/ toutes les {INTERVAL}s")

    if BOT_TOKEN == "VOTRE_BOT_TOKEN_ICI" or CHAT_ID == "VOTRE_CHAT_ID_ICI":
        log.error("❌ Configure BOT_TOKEN et CHAT_ID avant de lancer le bot !")
        return

    seen = load_seen()
    log.info(f"📂 {len(seen)} threads déjà connus chargés.")

    # Premier passage : on mémorise sans envoyer (évite le flood au démarrage)
    if not seen:
        log.info("Premier démarrage : indexation des threads existants sans envoi…")
        threads = fetch_catalog()
        seen = {str(t["no"]) for t in threads}
        save_seen(seen)
        log.info(f"✅ {len(seen)} threads indexés. Le bot enverra uniquement les nouveaux.")

    while True:
        try:
            threads = fetch_catalog()
            new_threads = [t for t in threads if str(t["no"]) not in seen]

            if new_threads:
                log.info(f"🆕 {len(new_threads)} nouveau(x) thread(s) trouvé(s)")
                for thread in new_threads:
                    tid = str(thread["no"])
                    log.info(f"  → Envoi thread #{tid}")
                    send_telegram(thread)
                    seen.add(tid)
                    time.sleep(1)   # anti-flood Telegram (30 msg/s max)
                save_seen(seen)
            else:
                log.info("Aucun nouveau thread.")

        except KeyboardInterrupt:
            log.info("Arrêt demandé.")
            break
        except Exception as e:
            log.error(f"Erreur inattendue : {e}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
