import argparse
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

my_token = '*:*'
my_key = '*'

open("chatid.txt", "w")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class EmailToBot:

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Hello, I can help you to check email!")


    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=update.message.text)


    async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = 'use \'/join key\' to join the session\n\
        so I will send to email to you\n\
        use \'/leave\' to leave the session\n\
        so I will not send email to you\
        '
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=help_text)

    async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text_caps: str = ' '.join(context.args)
        if text_caps == my_key:
            with open("chatid.txt", "r") as file:
                all_chat_id = file.read()

            if str(update.effective_chat.id) not in all_chat_id:
                with open("chatid.txt", "a") as file:
                    file.write(str(update.effective_chat.id)+'\n')

            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Congratulations, you successfully join the session!')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Sorry, the password is incorrect, please try again.')

    async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
        with open("chatid.txt", "r") as file:
            all_chat_id = file.read()
        if str(update.effective_chat.id) not in all_chat_id:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='You have not joined the session.')
        else:
            now_chat_id = all_chat_id.replace(str(update.effective_chat.id)+'\n', "")

            with open("chatid.txt", "w") as file:
                file.write(now_chat_id)

            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Byebye, you successfully leave the session!')

    async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='description of your program')
    parser.add_argument('-t', '--token', help='your bot token')
    parser.add_argument('-k', '--key', help='a key to manage')

    args = parser.parse_args()
    my_token = args.token
    my_key = args.key

    application = ApplicationBuilder().token(my_token).build()

    start_handler = CommandHandler('start', EmailToBot.start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), EmailToBot.echo)
    help_handler = CommandHandler('help', EmailToBot.help)
    join_handler = CommandHandler('join', EmailToBot.join)
    leave_handler = CommandHandler('leave', EmailToBot.leave)
    unknown_handler = MessageHandler(filters.COMMAND, EmailToBot.unknown)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(help_handler)
    application.add_handler(join_handler)
    application.add_handler(leave_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
