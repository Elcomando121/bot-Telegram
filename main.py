
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import logging
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

welcomed_users = set()
user_confirmation_messages = {}

WELCOME_MESSAGE = "السلام عليكم و رحمة الله و بركاتة: ازاي اقدر اساعد حضرتك اكتب استفسارك هنا و سوف يتم الرد في اقرب وقت ممكن شكرا لك."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_message(chat_id=user_id, text=WELCOME_MESSAGE)
    welcomed_users.add(user_id)

    user_name = update.effective_user.full_name
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"مستخدم جديد فعل البوت: {user_name} (ID: {user_id})"
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    text = update.message.text

    if text.startswith('/start'):
        return

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"رسالة جديدة من {user_name} (ID: [{user_id}]):\n\n{text}"
    )

    confirmation = await context.bot.send_message(
        chat_id=user_id, 
        text="تم استلام رسالتك، وهيرد عليك الأدمن قريباً."
    )

    user_confirmation_messages[user_id] = confirmation.message_id

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original_text = update.message.reply_to_message.text
        if "ID: [" in original_text:
            try:
                user_id = int(original_text.split("ID: [")[1].split("]")[0])

                if user_id in user_confirmation_messages:
                    try:
                        await context.bot.delete_message(
                            chat_id=user_id,
                            message_id=user_confirmation_messages[user_id]
                        )
                        del user_confirmation_messages[user_id]  
                    except Exception as e:
                        print(f"Couldn't delete message: {e}")

                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"رد الأدمن:\n{update.message.text}"
                )

            except Exception as e:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f"خطأ: {e}")
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text="لم يتم العثور على ID المستخدم.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.Chat(ADMIN_ID) & ~filters.COMMAND, handle_user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(ADMIN_ID), handle_admin_reply))
    app.run_polling()

if __name__ == '__main__':
    main()
