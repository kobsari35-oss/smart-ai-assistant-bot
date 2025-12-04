from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from utils.ai import smart_reply

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please ask a question after /ai")
        return
    msg = await update.message.reply_text("⌛...")
    reply = smart_reply(text)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"🤖 {reply}")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for m in update.message.new_chat_members:
        if not m.is_bot:
            await update.message.reply_text(f"👋 Hello {m.first_name}!")

def register(app):
    app.add_handler(CommandHandler("ai", ai))
    app.add_handler(CommandHandler("ask", ai))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))