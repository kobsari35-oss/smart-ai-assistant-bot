import os
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from utils.ai import smart_reply

async def ocr_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("📸 កំពុងមើលរូបភាព (Processing)...")
    file_path = f"ocr_{update.effective_user.id}.jpg"
    
    try:
        # 1. Download Photo
        photo = update.message.photo[-1]
        file = await photo.get_file()
        await file.download_to_drive(file_path)
        
        # 2. Process with AI (Send image path)
        prompt = (
            "Extract all text from this image and translate it to Khmer. "
            "Format: \n📝 **Original:** ...\n🇰🇭 **Khmer:** ..."
        )
        
        # ហៅ smart_reply ដោយដាក់ image_path
        reply = smart_reply(prompt, image_path=file_path)
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id, 
            message_id=msg.message_id, 
            text=f"🖼 **លទ្ធផល OCR:**\n{reply}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id, 
            message_id=msg.message_id, 
            text=f"⚠️ Error: {e}"
        )
    finally:
        # 3. Cleanup: លុបរូបចោលវិញដាច់ខាត ទោះជោគជ័យឬបរាជ័យ
        if os.path.exists(file_path):
            os.remove(file_path)

def register(app):
    app.add_handler(MessageHandler(filters.PHOTO, ocr_image))