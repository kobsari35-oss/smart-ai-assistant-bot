import os
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from utils.db import (
    set_premium, remove_user_premium, get_all_users, 
    set_global_limit
)

# 👇 ADMIN ID: យកពី Environment (Render) បើអត់មានយកលេខបន្ទាប់
ADMIN_ID = int(os.getenv("ADMIN_ID", "5574913183"))

def is_admin(uid):
    return uid == ADMIN_ID

# 📢 Broadcast (ផ្ញើសារទៅកាន់សមាជិកទាំងអស់)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if not context.args:
        await update.message.reply_text("⚠️ សូមសរសេរអត្ថបទដែលចង់ផ្សាយ។\nExample: `/broadcast Hello All`")
        return
    
    msg_text = " ".join(context.args)
    users = get_all_users()
    
    status_msg = await update.message.reply_text(f"🚀 កំពុងផ្ញើទៅកាន់ {len(users)} នាក់...")
    
    sent = 0
    failed = 0
    
    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=uid, 
                text=f"📢 **សេចក្តីជូនដំណឹង:**\n\n{msg_text}", 
                parse_mode="Markdown"
            )
            sent += 1
            await asyncio.sleep(0.05) # ការពារ Telegram Block (Flood limit)
        except Exception:
            failed += 1
            
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=status_msg.message_id,
        text=f"✅ **ការផ្សាយចប់សព្វគ្រប់!**\n\n📤 ជោគជ័យ: {sent}\n❌ បរាជ័យ: {failed}"
    )

# 👥 មើលចំនួន User សរុប
async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    users = get_all_users()
    await update.message.reply_text(f"👥 Total Users: {len(users)}\nIDs (Top 20): {users[:20]}...")

# ⚙️ កំណត់ Limit ទូទៅ (សម្រាប់ Free User)
async def set_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("⚠️ សូមដាក់ចំនួន Limit។ ឧទាហរណ៍: /setlimit 20")
        return
    try:
        limit = int(context.args[0])
        set_global_limit(limit)
        await update.message.reply_text(f"✅ Global Free Limit បានប្តូរទៅជា: {limit} សារ/ថ្ងៃ")
    except ValueError:
        await update.message.reply_text("⚠️ លេខមិនត្រឹមត្រូវ។")

# 🔥🔥 UPDATE: ADD PREMIUM COMMAND 🔥🔥
async def add_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return

    # ✅ Fix: Check args to prevent crash
    if not context.args:
        await update.message.reply_text(
            "⚠️ របៀបប្រើ៖ `/addpremium <User_ID> <Duration>`\n"
            "ឧទាហរណ៍: `/addpremium 123456 1m` (1 ខែ)\n"
            "Duration: d=ថ្ងៃ, m=ខែ, y=ឆ្នាំ, ទទេ=មួយជីវិត",
            parse_mode="Markdown"
        )
        return

    try:
        target_id = int(context.args[0])
        
        # Default = Unlimited Forever
        duration = 0 
        limit = -1 
        plan_text = "💎 Unlimited (VIP)"
        duration_text = "មួយជីវិត (Forever)"

        if len(context.args) > 1:
            raw = context.args[1].lower()
            
            # d, m, y = Pro (មាន Limit 1000)
            if raw.endswith("d"): 
                duration = int(raw[:-1])
                limit = 1000 
                plan_text = "🌟 Pro (ប្រចាំថ្ងៃ)"
                duration_text = f"{duration} ថ្ងៃ"
                
            elif raw.endswith("m"): 
                duration = int(raw[:-1]) * 30
                limit = 1000
                plan_text = "🌟 Pro (ប្រចាំខែ)"
                duration_text = f"{int(raw[:-1])} ខែ"
                
            elif raw.endswith("y"): 
                duration = int(raw[:-1]) * 365
                limit = 1000
                plan_text = "🌟 Pro (ប្រចាំឆ្នាំ)"
                duration_text = f"{int(raw[:-1])} ឆ្នាំ"
        
        # Save to DB
        set_premium(target_id, duration if duration > 0 else None, limit)
        
        msg = (
            f"✅ **ដាក់គម្រោងជោគជ័យ!**\n"
            f"👤 User: `{target_id}`\n"
            f"🏷️ គម្រោង: **{plan_text}**\n"
            f"⏳ រយៈពេល: {duration_text}\n"
            f"📊 Limit: {limit if limit > 0 else '♾️'} សារ/ថ្ងៃ"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

async def remove_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("⚠️ សូមដាក់ User ID។ ឧទាហរណ៍: /removepremium 123456")
        return
    try:
        target_id = int(context.args[0])
        remove_user_premium(target_id)
        await update.message.reply_text(f"🔻 ដកសិទ្ធិ Premium ពី `{target_id}` -> ត្រឡប់ជា **Free (ប្រចាំថ្ងៃ)**", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

def register(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("users", user_list))
    app.add_handler(CommandHandler("setlimit", set_limit_command))
    app.add_handler(CommandHandler("addpremium", add_premium))
    app.add_handler(CommandHandler("removepremium", remove_premium))
