import requests
import itertools
import string
import time
import random
from threading import Thread, Lock
import queue
import os

DISCORD_WEBHOOK = os.getenv("WEBHOOK_URL")  # Set in Render environment
USE_PROXIES = False  # Set True if you want to use proxies
PROXIES_LIST = []    # Fill with proxies if needed, e.g. ["http://ip:port", ...]

THREADS = 10  # Number of parallel threads

lock = Lock()  # Thread-safe print/log
usernames_queue = queue.Queue()

# Generate all 3-letter lowercase usernames
letters = string.ascii_lowercase
for combo in itertools.product(letters, repeat=3):
    usernames_queue.put("".join(combo))


def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2)",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7)",
    ]
    return random.choice(agents)


def send_webhook(username):
    """Send a Discord notification"""
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": f"🔥 AVAILABLE IG USERNAME FOUND: **{username}** 🔥"}, timeout=5)
    except Exception as e:
        with lock:
            print("Webhook error:", e)


def check_username(username):
    """Check Instagram username availability"""
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    headers = {"User-Agent": random_user_agent()}
    
    proxy = None
    if USE_PROXIES and PROXIES_LIST:
        proxy = {"http": random.choice(PROXIES_LIST), "https": random.choice(PROXIES_LIST)}

    try:
        r = requests.get(url, headers=headers, proxies=proxy, timeout=6)
        if r.status_code == 404:
            return True
        elif r.status_code == 200:
            return False
        else:
            return None
    except:
        return None


def worker():
    while True:
        try:
            username = usernames_queue.get(timeout=5)
        except:
            break  # Queue empty

        result = check_username(username)

        with lock:
            print(f"Checked: {username} - Result: {result}")

        if result is True:
            with lock:
                print(f"🔥 AVAILABLE FOUND: {username} 🔥")
            send_webhook(username)
            # continue scanning for continuous mode
        time.sleep(random.uniform(1, 3))  # Random delay to reduce blocking


def main():
    while True:  # Continuous scanning
        threads = []
        for _ in range(THREADS):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        # Refill the queue for continuous scanning
        for combo in itertools.product(letters, repeat=3):
            usernames_queue.put("".join(combo))

        print("Queue refilled, continuing scan...")


if __name__ == "__main__":
    main()
