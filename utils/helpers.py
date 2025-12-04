from telegram import ReplyKeyboardMarkup, KeyboardButton

def main_menu(user_id=None):
    kb = [
        # ជួរទី ១
        [KeyboardButton("👤 Profile"), KeyboardButton("💸 Donate (ឧបត្ថម្ភ)")],
        # ជួរទី ២
        [KeyboardButton("🤖 General AI"), KeyboardButton("🇨🇳🗣 Chinese Conversation")],
        # ជួរទី ៣
        [KeyboardButton("📚 Chinese Word Meaning"), KeyboardButton("📘 Grammar (EN/CN/PH)")],
        # ជួរទី ៤
        [KeyboardButton("📸 OCR Translate"), KeyboardButton("🌐 Auto Translation")],
        # ជួរទី ៥
        [KeyboardButton("🧹 Reset Chat"), KeyboardButton("⚙️ ជំនួយ (Help)")],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=False)
