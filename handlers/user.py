from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from utils.helpers import main_menu
from utils.ai import smart_reply
from utils.db import add_user, check_limit, get_user_status, get_global_limit

# 🏁 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    context.user_data['mode'] = 'general'
    
    # Check status logic
    user_data = get_user_status(user.id)
    limit = user_data.get('daily_limit', 0)
    is_premium = user_data.get('premium', False)

    if is_premium:
        if limit == -1:
            status_text = "💎 Unlimited (VIP)"
        else:
            status_text = "🌟 Pro (ប្រចាំខែ)"
    else:
        status_text = "👤 Free (ប្រចាំថ្ងៃ)"

    # អត្ថបទស្វាគមន៍
    msg = (
        f"✨ សួស្តី {user.first_name or 'អ្នកប្រើថ្មី'}!\n"
        f"ស្ថានភាពរបស់អ្នក៖ *{status_text}*\n\n"
        f"សូមស្វាគមន៍មកកាន់ *Smart AI Assistant* 🤖\n\n"
        "ជួយអ្នកបានច្រើនដូចជា៖\n"
        "📚 ពិនិត្យអក្សរសាស្ត្រ និង Grammar\n"
        "🇨🇳 សន្ទនាជាភាសាចិន (មានបកប្រែ)\n"
        "🌐 បកប្រែភាសា ↔ ខ្មែរ / អង់គ្លេស\n"
        "📸 អានអក្សរពីរូបភាព OCR\n"
        "📘 ពន្យល់ពាក្យចិន (Meaning)\n"
        "💬 General AI សម្រាប់សំណួរទូទៅ\n\n"
        "ជ្រើសមុខងារពី Menu ខាងក្រោម ⬇️"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu(user.id))

# ⚙️ Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ ជំនួយ: សូមប្រើ Menu ខាងក្រោម", reply_markup=main_menu(update.effective_user.id))

# 💸 Upgrade Info
async def upgrade_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (
        "💎 *Upgrade Options*\n\n"
        "1️⃣ **Pro (1$/ខែ)**\n"
        "   • 1,000 សារ/ថ្ងៃ\n"
        "   • ល្បឿនលឿន\n\n"
        "2️⃣ **Unlimited (Add-on)**\n"
        "   • ប្រើមិនកំណត់\n\n"
        "🏦 *ABA Bank*\n"
        "• Account: `096 666 7292`\n"
        "• Name: *Hem SopheaK*\n\n"
        "👉 ទាក់ទង Admin: @Samross_Ph_Care\n"
        f"🆔 ID របស់អ្នក៖ `{user_id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=False)

# 🧹 Reset
async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['mode'] = 'general'
    await update.message.reply_text("🧹 Reset រួចរាល់។", reply_markup=main_menu(update.effective_user.id))

# 👤 Profile Logic (Fix 0/0 Bug & Plan Names)
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_status(user.id)
    global_limit = get_global_limit()
    
    is_premium = data.get('premium', False)
    expiry_raw = data.get('expiry')
    usage = data.get('usage', 0)
    user_limit = data.get('daily_limit', 0)
    
    # 1. គណនា Limit
    if user_limit == -1:
        limit_display = "♾️ មិនកំណត់"
    else:
        # បើ Premium តែ Limit=0 (ករណី Error ពីមុន) -> គួរតែ Fix Data តែបង្ហាញឲ្យត្រូវសិន
        effective_limit = user_limit if user_limit != 0 else global_limit
        limit_display = f"{effective_limit} សារ"

    # 2. កំណត់ឈ្មោះ Plan
    plan_name = "👤 Free (ប្រចាំថ្ងៃ)"
    if is_premium:
        if user_limit == -1:
            plan_name = "💎 Unlimited (VIP)"
        elif expiry_raw == "Forever":
            plan_name = "🌟 Pro (មួយជីវិត)"
        else:
            plan_name = "🌟 Pro (ប្រចាំខែ)"

    # 3. បង្ហាញថ្ងៃផុតកំណត់
    expiry_display = "គ្មាន (N/A)"
    if is_premium:
        if expiry_raw == "Forever":
            expiry_display = "មួយជីវិត (Forever)"
        elif expiry_raw:
            try:
                date_obj = datetime.strptime(expiry_raw, "%Y-%m-%d")
                expiry_display = date_obj.strftime("%d-%m-%Y")
            except:
                expiry_display = expiry_raw
    
    # 4. បិទ Tip បើគាត់ Upgrade រួចហើយ
    tip_msg = "\n💡 *Tip:* Upgrade ដើម្បីទទួលបាន Limit ច្រើនជាងនេះ!"
    if is_premium and user_limit == -1:
        tip_msg = "" # បើ Unlimited ហើយ មិនបាច់បង្ហាញ Tip ទេ

    msg = (
        f"👤 *គណនីរបស់អ្នក (Profile)*\n"
        f"━━━━━━━━━━━━━━\n"
        f"📛 ឈ្មោះ: {user.first_name}\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"🏷️ គម្រោង: *{plan_name}*\n"
        f"📅 ផុតកំណត់: *{expiry_display}*\n"
        f"📊 ការប្រើថ្ងៃនេះ: *{usage} / {limit_display}*\n"
        f"━━━━━━━━━━━━━━{tip_msg}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu(user.id))

# 🔀 MAIN ROUTER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    user_mode = context.user_data.get('mode', 'general')

    # --- Menu Buttons Check ---
    if text == "🤖 General AI":
        context.user_data['mode'] = 'general'
        await update.message.reply_text("🤖 General AI: សួរសំណួរទូទៅបាន...", reply_markup=main_menu(user.id))
        return
    elif text == "🇨🇳🗣 Chinese Conversation":
        context.user_data['mode'] = 'chinese_conv'
        await update.message.reply_text("🇨🇳🗣 ចូល Mode សន្ទនាចិន...", reply_markup=main_menu(user.id))
        return
    elif text == "📚 Chinese Word Meaning":
        context.user_data['mode'] = 'chinese_meaning'
        await update.message.reply_text("📚 ចូល Mode ពន្យល់ពាក្យចិន...", reply_markup=main_menu(user.id))
        return
    elif text == "📘 Grammar (EN/CN/PH)":
        context.user_data['mode'] = 'grammar'
        await update.message.reply_text("📘 ចូល Mode Grammar...", reply_markup=main_menu(user.id))
        return
    elif text == "🌐 Auto Translation":
        context.user_data['mode'] = 'translate'
        await update.message.reply_text("🌐 ចូល Mode បកប្រែ...", reply_markup=main_menu(user.id))
        return
    elif text == "📸 OCR Translate":
        await update.message.reply_text("📸 សូមផ្ញើរូបភាព (Photo) ដើម្បីឱ្យខ្ញុំអានអក្សរ...", reply_markup=main_menu(user.id))
        return
    elif text == "💸 Donate (ឧបត្ថម្ភ)":
        await upgrade_info(update, context)
        return
    elif text == "⚙️ ជំនួយ (Help)":
        await help_command(update, context)
        return
    elif text == "🧹 Reset Chat":
        await reset_chat(update, context)
        return
    elif text == "👤 Profile":
        await show_profile(update, context)
        return

    # --- Check Limit ---
    try:
        is_allowed = check_limit(user.id)
        if not is_allowed:
            udata = get_user_status(user.id)
            current_limit = udata.get('daily_limit', 0)
            if current_limit == 0: current_limit = get_global_limit()
            
            await update.message.reply_text(
                f"⚠️ **Limit Reached!**\n"
                f"Limit: {current_limit} messages/day.\nUpgrade to Pro or Unlimited.", 
                parse_mode="Markdown"
            )
            return
    except Exception as e:
        print(f"Error checking limit: {e}")
        pass

    # --- Process AI ---
    prompt = text
    loading_text = "⌛ ..."

    if user_mode == 'general':
        prompt = text
        loading_text = "⌛ កំពុងគិត..."
    elif user_mode == 'chinese_conv':
        prompt = (f"Translate to Chinese (Mandarin): '{text}'.\n"
                  "Format EXACTLY:\n🇨🇳 **Chinese:** ...\n🗣 **Pinyin:** ...\n🇰🇭 **Meaning:** ...")
        loading_text = "🈶 កំពុងបកប្រែ..."
    elif user_mode == 'chinese_meaning':
        prompt = (f"Analyze word: '{text}'.\n"
                  "Format EXACTLY:\n🇨🇳 **Word:** ...\n🗣 **Pinyin:** ...\n🇬🇧 **English:** ...\n🇰🇭 **Khmer:** ...\n💡 **Example:** ...")
        loading_text = "📖 កំពុងស្វែងរក..."
    elif user_mode == 'grammar':
        prompt = (f"Check grammar: '{text}'.\n"
                  "Format EXACTLY:\n❌ **Original:** ...\n✅ **Corrected:** ...\n📝 **Explanation:** (Khmer)")
        loading_text = "✍️ កំពុងពិនិត្យ..."
    elif user_mode == 'translate':
        prompt = f"Translate to Khmer/English: {text}"
        loading_text = "🌐 កំពុងបកប្រែ..."

    msg = await update.message.reply_text(loading_text)
    
    try:
        reply = smart_reply(prompt)
        
        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id, 
                message_id=msg.message_id, 
                text=reply, 
                parse_mode="Markdown"
            )
        except Exception:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id, 
                message_id=msg.message_id, 
                text=reply
            )
            
    except Exception as e:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"⚠️ Error: {e}")

# 🔥 Register Handlers
def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("upgrade", upgrade_info))
    app.add_handler(CommandHandler("reset", reset_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))