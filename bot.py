import os
import sys
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers import user, admin, group, ocr
# 👇 ដូរត្រង់នេះ (ពី load_users ទៅ init_db)
from utils.db import init_db

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("❌ Missing Token")
        return

    # 👇 ហៅ Database ឱ្យដំណើរការ
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ Database Connection Failed: {e}")
        return
    
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .build()
    )

    user.register(app)
    admin.register(app)
    group.register(app)
    ocr.register(app)

    logger.info("🤖 Bot Started with PostgreSQL!")
    app.run_polling()

if __name__ == "__main__":
    main()