# 📡 4Chan /b/ → Telegram Bot

A Python bot that monitors 4chan's /b/ board and automatically posts new threads, the most replied thread, and the last bumped thread to a Telegram channel.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Step 1 — Telegram Bot Setup](#step-1--telegram-bot-setup)
- [Step 2 — Oracle Cloud Server Setup](#step-2--oracle-cloud-server-setup)
- [Step 3 — SSH Connection](#step-3--ssh-connection)
- [Step 4 — Bot Installation](#step-4--bot-installation)
- [Step 5 — Running the Bot](#step-5--running-the-bot)
- [Bot Behavior](#bot-behavior)
- [Server Info](#server-info)
- [Useful Commands](#useful-commands)

---

## Project Overview

This project automatically monitors 4chan's `/b/` (Random) board using the official 4chan JSON API and forwards every new thread to a private Telegram channel. It also posts periodic highlights: the most replied thread and the most recently bumped thread.

---

## Features

- 🆕 **New Thread Detection** — Detects and posts every new thread on /b/ within 60 seconds
- 🖼️ **Image Support** — Sends the OP image alongside the thread text when available
- 🏆 **Most Replied** — Posts the thread with the most replies every 30 minutes
- 💬 **Last Bump** — Posts the most recently bumped thread every 15 minutes
- 💾 **State Persistence** — Remembers seen threads across restarts via `seen_threads.json`
- 🛡️ **No Flood on Start** — On first launch, indexes existing threads without posting them

---

## Tech Stack

- **Language:** Python 3
- **Libraries:** `requests` (HTTP calls), standard library only
- **APIs:** 4chan JSON API (read-only), Telegram Bot API
- **Server:** Oracle Cloud Free Tier (Ubuntu 22.04)
- **Shell Access:** Oracle Cloud Shell

---

## Step 1 — Telegram Bot Setup

1. Open Telegram and search for **@BotFather**
2. Type `/newbot` and follow the instructions
3. Copy the **Bot Token** provided (e.g. `123456:ABCdef...`)
4. Create a Telegram channel and add your bot as **Admin**
5. Send a message in the channel, then visit:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
6. Find the `"id"` field inside `"chat"` — this is your **Chat ID** (negative number like `-1004472784843`)

> ⚠️ Never share your Bot Token publicly. If exposed, revoke it immediately via @BotFather → `/mybots` → **Revoke current token**

---

## Step 2 — Oracle Cloud Server Setup

We used **Oracle Cloud Free Tier** which provides an always-free Ubuntu VM.

1. Go to [cloud.oracle.com](https://cloud.oracle.com) and create a free account
2. Navigate to **Compute** → **Instances** → **Create Instance**
3. Select **Ubuntu 22.04** as the OS
4. Download the generated SSH key pair (`.key` file)
5. Click **Create**
6. Once created, go to **Networking** → **Attached VNICs** → assign a **Public IP address** if not already set

**Instance Details:**
| Field | Value |
|-------|-------|
| Name | 4ChanRandomBot |
| OS | Ubuntu 22.04 |
| Region | Canada Southeast (Montreal) |
| Public IP | 151.145.58.148 |
| Username | ubuntu / lemouchard |

---

## Step 3 — SSH Connection

We encountered Windows permission issues with the `.key` file and ended up using **Oracle Cloud Shell** directly in the browser to connect.

### Via Oracle Cloud Shell (recommended)

1. Go to your instance page on Oracle Cloud
2. Click the **Cloud Shell** icon in the top right of the Oracle console
3. Generate a new SSH key pair in Cloud Shell:
   ```bash
   ssh-keygen -t rsa -b 2048 -f ~/.ssh/oracle_new -N ""
   cat ~/.ssh/oracle_new.pub
   ```
4. Add the public key to the server via the **Serial Console**:
   - Go to **Actions** → **More actions** → **Troubleshoot instance**
   - Click **connect to the instance's serial console**
   - Run:
     ```bash
     echo "YOUR_PUBLIC_KEY" >> /home/ubuntu/.ssh/authorized_keys
     chmod 700 /home/ubuntu/.ssh
     chmod 600 /home/ubuntu/.ssh/authorized_keys
     ```
5. Connect from Cloud Shell:
   ```bash
   ssh -i ~/.ssh/oracle_new lemouchard@151.145.58.148
   ```

### Via MobaXterm (Windows)

1. Download [MobaXterm](https://mobaxterm.mobatek.net)
2. New Session → SSH
3. Host: `151.145.58.148`, Username: `ubuntu`
4. Use private key: select your `.key` or `.ppk` file

> ⚠️ Note: Windows has strict SSH key permission requirements. If you get a "bad permissions" error, use Oracle Cloud Shell instead.

---

## Step 4 — Bot Installation

Once connected to the server:

```bash
# Update system
sudo apt update -y

# Install Python
sudo apt install python3 python3-pip -y

# Install dependencies
pip3 install requests --break-system-packages

# Create and edit the bot script
nano ~/4chan_telegram_bot.py
```

Paste the bot script and fill in:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID   = "YOUR_CHAT_ID"
```

---

## Step 5 — Running the Bot

```bash
# Start the bot in the background
nohup python3 ~/4chan_telegram_bot.py &

# Check logs
tail -f nohup.out
```

On first launch the bot will index all existing threads without posting them. After that, every new thread will be forwarded to Telegram automatically.

---

## Bot Behavior

### New Thread Posts
Every 60 seconds the bot checks for new threads. When a new thread is detected it sends:
- 📌 Thread number as header
- **Bold title** (subject if available, otherwise first 80 chars of the post)
- Thread text excerpt
- 🖼️ OP image (if available)
- 🔗 Direct link to the thread

### Most Replied (every 30 minutes)
Posts the thread with the highest reply count:
```
🏆 Most Replied #XXXXXXXXX
Bold title or excerpt
🔗 /b/XXXXXXXXX
```

### Last Bump (every 15 minutes)
Posts the most recently active thread:
```
💬 Last Bump #XXXXXXXXX
Bold title or excerpt
🔗 /b/XXXXXXXXX
```

---

## Server Info

| Field | Value |
|-------|-------|
| Provider | Oracle Cloud Free Tier |
| IP | 151.145.58.148 |
| OS | Ubuntu 22.04 |
| Script location | `~/4chan_telegram_bot.py` |
| Logs | `~/nohup.out` |
| State file | `~/seen_threads.json` |
| Telegram Channel | @random4chan |
| Chat ID | -1004472784843 |

---

## Useful Commands

```bash
# Start the bot
nohup python3 ~/4chan_telegram_bot.py &

# Stop the bot
pkill -f 4chan_telegram_bot.py

# Restart the bot
pkill -f 4chan_telegram_bot.py && nohup python3 ~/4chan_telegram_bot.py &

# Check if bot is running
ps aux | grep 4chan_telegram_bot.py

# Watch logs live
tail -f nohup.out

# Clear logs
> nohup.out

# Reset seen threads (bot will re-index from scratch)
rm ~/seen_threads.json

# Edit the script
nano ~/4chan_telegram_bot.py

# Check Telegram bot status
curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
```

---

## Limitations

- 4chan's API is **read-only** — replying to threads from Telegram is not possible due to hCaptcha requirements
- Oracle Cloud Shell **disconnects after ~20 minutes of inactivity** — the bot keeps running via `nohup` but you'll need to reconnect to check logs
- /b/ threads are very short-lived — some threads may 404 before the bot can fetch their details

---

*Project built on June 14, 2026*
