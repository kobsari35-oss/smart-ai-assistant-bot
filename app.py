from flask import Flask
from threading import Thread
from bot import main as start_bot
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running and connected to PostgreSQL!"

def run():
    # Render ត្រូវការ Port នេះ
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()  # 1. បើក Web Server (ដើម្បីកុំឱ្យ Render បិទ)
    start_bot()   # 2. បើក Telegram Bot