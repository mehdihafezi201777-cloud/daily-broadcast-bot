import os
import json
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytz

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # آیدی عددی خودت

# فایل دیتا
DATA_FILE = "data.json"

# بارگذاری دیتا
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"chats": [], "texts": [], "times": ["09:00", "14:00", "21:00"]}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()
TEHRAN_TZ = pytz.timezone("Asia/Tehran")
bot = Bot(token=TOKEN)

# ========== دستورات مدیریتی (فقط تو پی‌وی) ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "عمو جان، خوش اومدی.\n\n"
        "📌 /addchat @username یا -100123456\n"
        "📌 /removechat @username یا -100123456\n"
        "📌 /listchats - لیست گروه‌ها\n"
        "📌 /settext 1 - متن اول\n"
        "📌 /settext 2 - متن دوم\n"
        "📌 /settext 3 - متن سوم\n"
        "📌 /settime 1 09:00 - ساعت اول\n"
        "📌 /settime 2 14:00 - ساعت دوم\n"
        "📌 /settime 3 21:00 - ساعت سوم\n"
        "📌 /status - وضعیت فعلی"
    )

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    chat = context.args[0] if context.args else None
    if not chat:
        await update.message.reply_text("مثال: /addchat @channel")
        return
    if chat not in data["chats"]:
        data["chats"].append(chat)
        save_data(data)
        await update.message.reply_text(f"✅ {chat} اضافه شد.")
    else:
        await update.message.reply_text("❗ قبلاً اضافه شده.")

async def remove_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    chat = context.args[0] if context.args else None
    if not chat:
        await update.message.reply_text("مثال: /removechat @channel")
        return
    if chat in data["chats"]:
        data["chats"].remove(chat)
        save_data(data)
        await update.message.reply_text(f"✅ {chat} حذف شد.")
    else:
        await update.message.reply_text("❗ پیدا نشد.")

async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not data["chats"]:
        await update.message.reply_text("❗ هیچ گروهی اضافه نشده.")
        return
    text = "📋 لیست گروه‌ها:\n" + "\n".join([f"- {c}" for c in data["chats"]])
    await update.message.reply_text(text)

async def set_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("مثال: /settext 1 سلام عمو")
        return
    index = int(context.args[0]) - 1
    new_text = " ".join(context.args[1:])
    if 0 <= index < 3:
        if len(data["texts"]) < 3:
            data["texts"] += [""] * (3 - len(data["texts"]))
        data["texts"][index] = new_text
        save_data(data)
        await update.message.reply_text(f"✅ متن {index+1} تغییر کرد.")
    else:
        await update.message.reply_text("❗ شماره ۱ تا ۳.")

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("مثال: /settime 1 09:00")
        return
    index = int(context.args[0]) - 1
    new_time = context.args[1]
    if 0 <= index < 3:
        data["times"][index] = new_time
        save_data(data)
        await update.message.reply_text(f"✅ ساعت {index+1} تغییر کرد.")
    else:
        await update.message.reply_text("❗ شماره ۱ تا ۳.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    texts = data.get("texts", ["", "", ""])
    times = data.get("times", ["09:00", "14:00", "21:00"])
    msg = f"📊 وضعیت فعلی:\n\n"
    for i in range(3):
        msg += f"⏰ {times[i]} — {texts[i] if texts[i] else '(متن تنظیم نشده)'}\n"
    msg += f"\n📌 تعداد گروه‌ها: {len(data['chats'])}"
    await update.message.reply_text(msg)

# ========== تابع ارسال خودکار ==========

async def send_to_all(text):
    for chat in data["chats"]:
        try:
            await bot.send_message(chat_id=chat.strip(), text=text)
        except Exception as e:
            print(f"❌ ارسال به {chat} نشد: {e}")

async def scheduler():
    while True:
        now = datetime.now(TEHRAN_TZ).strftime("%H:%M")
        times = data.get("times", ["09:00", "14:00", "21:00"])
        texts = data.get("texts", ["", "", ""])

        for i, t in enumerate(times):
            if now == t and texts[i]:
                await send_to_all(texts[i])
                await asyncio.sleep(60)  # جلوگیری از ارسال دوباره

        await asyncio.sleep(30)

# ========== اجرا ==========

async def main():
    app = Application.builder().token(TOKEN).build()

    # دستورات مدیریتی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addchat", add_chat))
    app.add_handler(CommandHandler("removechat", remove_chat))
    app.add_handler(CommandHandler("listchats", list_chats))
    app.add_handler(CommandHandler("settext", set_text))
    app.add_handler(CommandHandler("settime", set_time))
    app.add_handler(CommandHandler("status", status))

    # اجرای شیدولر
    asyncio.create_task(scheduler())

    print("ربات روشنه عمو...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
