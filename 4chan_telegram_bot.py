import requests
import time
import json
import os
import html
import logging
import re

BOT_TOKEN = "8110676305:AAFvh5EDC8a3CwIaQooNSAy0WNxsQe2KVC0"
CHAT_ID   = "-1004472784843"

BOARD     = "b"
INTERVAL  = 60
STATE_FILE = "seen_threads.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_all_threads():
    try:
        r = requests.get(f"https://a.4cdn.org/{BOARD}/threads.json", timeout=15, headers={"User-Agent": "bot/1.0"})
        r.raise_for_status()
        threads = []
        for page in r.json():
            for t in page.get("threads", []):
                threads.append(t)
        return threads
    except Exception as e:
        log.error(f"Erreur threads: {e}")
        return []

def fetch_thread_details(no):
    try:
        r = requests.get(f"https://a.4cdn.org/{BOARD}/thread/{no}.json", timeout=15, headers={"User-Agent": "bot/1.0"})
        r.raise_for_status()
        posts = r.json().get("posts", [])
        return posts[0] if posts else None
    except Exception as e:
        log.error(f"Erreur thread {no}: {e}")
        return None

def clean(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = text.replace("<br>", "\n").replace("<wbr>", "")
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()

def send_thread(thread, label=None):
    no  = thread.get("no", "?")
    sub = clean(thread.get("sub", ""))
    com = clean(thread.get("com", ""))
    url = f"https://boards.4chan.org/{BOARD}/thread/{no}"
    tim = thread.get("tim")
    ext = thread.get("ext", "")

    title = sub if sub else (com[:80] + "..." if len(com) > 80 else com)
    body  = com[80:880] if not sub else com[:800]

    if label == "most_replied":
        header = f"🏆 Most Replied #{no}"
    elif label == "last_bump":
        header = f"💬 Last Bump #{no}"
    else:
        header = f"📌 #{no}"

    text = header
    if title:
        text += f"\n{title}"
    if body:
        text += f"\n{body}"
    text += f"\n\n🔗 {url}"

    image_url = None
    if tim and ext.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        image_url = f"https://i.4cdn.org/{BOARD}/{tim}{ext}"

    if image_url:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", json={
            "chat_id": CHAT_ID,
            "photo": image_url,
            "caption": text[:1024],
        }, timeout=15)
        if r.ok:
            return
        log.warning(f"Photo échouée, envoi texte...")

    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": text[:4000],
        "disable_web_page_preview": True
    }, timeout=15)
    if not r.ok:
        log.error(f"Telegram error {r.status_code}: {r.text[:200]}")

def post_most_replied():
    log.info("📊 Recherche du thread Most Replied...")
    threads = fetch_all_threads()
    if not threads:
        return
    top = max(threads, key=lambda t: t.get("replies", 0))
    details = fetch_thread_details(top["no"])
    if details:
        log.info(f"  → Most Replied: #{top['no']} ({top.get('replies')} replies)")
        send_thread(details, label="most_replied")

def post_last_bump():
    log.info("💬 Recherche du thread Last Bump...")
    threads = fetch_all_threads()
    if not threads:
        return
    latest = max(threads, key=lambda t: t.get("last_modified", 0))
    details = fetch_thread_details(latest["no"])
    if details:
        log.info(f"  → Last Bump: #{latest['no']}")
        send_thread(details, label="last_bump")

def main():
    log.info(f"🤖 Bot démarré — surveillance de /b/ toutes les {INTERVAL}s")
    seen = load_seen()

    if not seen:
        log.info("Premier démarrage: indexation sans envoi...")
        threads = fetch_all_threads()
        seen = set(str(t["no"]) for t in threads)
        save_seen(seen)
        log.info(f"✅ {len(seen)} threads indexés.")

    last_most_replied = 0
    last_last_bump    = 0

    while True:
        try:
            now = time.time()

            threads = fetch_all_threads()
            new_threads = [t for t in threads if str(t["no"]) not in seen]

            if new_threads:
                log.info(f"🆕 {len(new_threads)} nouveau(x) thread(s)")
                for t in new_threads:
                    details = fetch_thread_details(t["no"])
                    if details:
                        log.info(f"  → Envoi thread #{t['no']}")
                        send_thread(details)
                    seen.add(str(t["no"]))
                    time.sleep(1)
                save_seen(seen)
            else:
                log.info("Aucun nouveau thread.")

            if now - last_most_replied >= 1800:
                post_most_replied()
                last_most_replied = now

            if now - last_last_bump >= 900:
                post_last_bump()
                last_last_bump = now

        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Erreur: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()