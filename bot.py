import os
import json
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)
import pytz


TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("BOT_TOKEN تنظیم نشده")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID تنظیم نشده")

ADMIN_ID = int(ADMIN_ID)

DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "chats": [],
            "texts": ["", "", ""],
            "times": ["09:00", "14:00", "21:00"]
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


data = load_data()

TEHRAN_TZ = pytz.timezone("Asia/Tehran")
bot = Bot(token=TOKEN)


def is_admin(update):
    return update.effective_user and update.effective_user.id == ADMIN_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update):
        return

    await update.message.reply_text(
        """
🤖 ربات آماده است

/addchat @channel
/removechat @channel

/listchats

/settext 1 متن
/settext 2 متن
/settext 3 متن

/settime 1 09:00
/settime 2 14:00
/settime 3 21:00

/status
"""
    )


async def add_chat(update, context):

    if not is_admin(update):
        return

    if not context.args:
        await update.message.reply_text("مثال: /addchat @channel")
        return

    chat = context.args[0]

    if chat not in data["chats"]:
        data["chats"].append(chat)
        save_data(data)

    await update.message.reply_text("✅ اضافه شد")


async def remove_chat(update, context):

    if not is_admin(update):
        return

    if not context.args:
        return

    chat = context.args[0]

    if chat in data["chats"]:
        data["chats"].remove(chat)
        save_data(data)

    await update.message.reply_text("✅ حذف شد")


async def list_chats(update, context):

    if not is_admin(update):
        return

    if not data["chats"]:
        await update.message.reply_text("لیست خالی است")
        return

    await update.message.reply_text(
        "\n".join(data["chats"])
    )


async def set_text(update, context):

    if not is_admin(update):
        return

    if len(context.args) < 2:
        return

    index = int(context.args[0]) - 1
    text = " ".join(context.args[1:])

    if 0 <= index < 3:
        data["texts"][index] = text
        save_data(data)

    await update.message.reply_text("✅ متن تغییر کرد")


async def set_time(update, context):

    if not is_admin(update):
        return

    if len(context.args) < 2:
        return

    index = int(context.args[0]) - 1
    time = context.args[1]

    if 0 <= index < 3:
        data["times"][index] = time
        save_data(data)

    await update.message.reply_text("✅ ساعت تغییر کرد")


async def status(update, context):

    if not is_admin(update):
        return

    msg = "📊 وضعیت:\n\n"

    for i in range(3):
        msg += (
            f"⏰ {data['times'][i]}\n"
            f"📝 {data['texts'][i] or 'خالی'}\n\n"
        )

    msg += f"گروه‌ها: {len(data['chats'])}"

    await update.message.reply_text(msg)



async def send_to_all(text):

    for chat in data["chats"]:

        try:
            await bot.send_message(
                chat_id=chat,
                text=text
            )

        except Exception as e:
            print(
                f"خطا در ارسال {chat}: {e}"
            )


async def scheduler():

    while True:

        now = datetime.now(
            TEHRAN_TZ
        ).strftime("%H:%M")

        for i, t in enumerate(data["times"]):

            if now == t and data["texts"][i]:

                await send_to_all(
                    data["texts"][i]
                )

                await asyncio.sleep(60)


        await asyncio.sleep(30)



async def after_start(app):

    app.create_task(
        scheduler()
    )



def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(after_start)
        .build()
    )


    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("addchat", add_chat)
    )

    app.add_handler(
        CommandHandler("removechat", remove_chat)
    )

    app.add_handler(
        CommandHandler("listchats", list_chats)
    )

    app.add_handler(
        CommandHandler("settext", set_text)
    )

    app.add_handler(
        CommandHandler("settime", set_time)
    )

    app.add_handler(
        CommandHandler("status", status)
    )


    print("Bot started...")

    app.run_polling()



if __name__ == "__main__":
    main()
