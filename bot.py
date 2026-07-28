import asyncio
from datetime import datetime

import pytz

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import TOKEN, ADMIN_IDS, TIMEZONE
from database import *


init_db()


def is_admin(user_id):
    return user_id in ADMIN_IDS



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(user.id)

    await update.message.reply_text(
        "✅ ثبت شدید"
    )



async def broadcast(update: Update, context):

    if not is_admin(update.effective_user.id):
        return


    if not context.args:
        await update.message.reply_text(
            "متن پیام را وارد کنید"
        )
        return


    text = " ".join(context.args)

    count = 0

    for user_id in get_users():

        try:
            await context.bot.send_message(
                user_id,
                text
            )

            count += 1

            await asyncio.sleep(0.05)

        except Exception:
            pass


    await update.message.reply_text(
        f"ارسال شد: {count}"
    )



async def set_daily(update:Update,context):

    if not is_admin(update.effective_user.id):
        return


    if len(context.args)<2:
        await update.message.reply_text(
            "/setdaily 09:00 متن پیام"
        )
        return


    time = context.args[0]
    text = " ".join(context.args[1:])


    save_setting("time",time)
    save_setting("text",text)

    await update.message.reply_text(
        "✅ ذخیره شد"
    )



async def scheduler(app):

    sent_today = None

    while True:

        now = datetime.now(
            pytz.timezone(TIMEZONE)
        )


        daily_time = get_setting("time")


        if daily_time:

            if now.strftime("%H:%M")==daily_time:

                if sent_today != now.date():

                    text=get_setting("text")

                    if text:

                        for uid in get_users():

                            try:
                                await app.bot.send_message(
                                    uid,
                                    text
                                )

                            except:
                                pass


                        sent_today=now.date()


        await asyncio.sleep(30)




async def main():

    app = Application.builder().token(
        TOKEN
    ).build()


    app.add_handler(
        CommandHandler("start",start)
    )

    app.add_handler(
        CommandHandler("broadcast",broadcast)
    )

    app.add_handler(
        CommandHandler("setdaily",set_daily)
    )


    asyncio.create_task(
        scheduler(app)
    )


    await app.run_polling()



if __name__=="__main__":
    asyncio.run(main())
