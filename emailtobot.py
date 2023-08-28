import argparse
import logging
from functools import lru_cache
from typing import Dict

import dns.resolver
import telebot
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from argon2 import PasswordHasher
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)

my_token = "*:*"
my_key = "*"
all_chat_id = set()
USER_AND_PASSWORD: Dict[str, str] = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class Authenticator:
    def __call__(self, server, session, envelope, mechanism, auth_data):
        fail_nothandled = AuthResult(success=False, handled=False)
        if mechanism not in ("LOGIN", "PLAIN"):
            return fail_nothandled
        if not isinstance(auth_data, LoginPassword):
            return fail_nothandled
        username_str = auth_data.login.decode("utf-8")
        password_str = auth_data.password.decode("utf-8")
        if not PasswordHasher().verify(USER_AND_PASSWORD[username_str], password_str):
            return fail_nothandled
        return AuthResult(success=True)


@lru_cache(maxsize=256)
def get_mx(domain):
    records = dns.resolver.resolve(domain, "MX")
    if not records:
        return None
    records = sorted(records, key=lambda r: r.preference)
    return str(records[0].exchange)


async def snedtobot(sender, recipient, body):
    contents = f"From: {sender}\nTo: {recipient}\nMessage data: {body}"
    bot = telebot.TeleBot(my_token)
    for now_chat_id in all_chat_id:
        bot.send_message(now_chat_id, contents)


class RelayHandler:
    async def handle_MAIL(self, server, session, envelope, address, mail_options):
        envelope.mail_from = address
        return "250 OK"

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        mx_rcpt = {}
        for rcpt in envelope.rcpt_tos:
            _, _, domain = rcpt.partition("@")
            mx = get_mx(domain)
            if mx is None:
                continue
            mx_rcpt.setdefault(mx, []).append(rcpt)
        for mx, rcpts in mx_rcpt.items():
            print(
                f"from_addr: {envelope.mail_from}\n"
                f"to_addrs: {rcpts}\n"
                f"message: {envelope.original_content}\n"
            )
            await snedtobot(envelope.mail_from, rcpts, envelope.original_content)
        return "250 Message accepted for delivery"


# noinspection PyShadowingNames
def amain(my_port):
    controller = Controller(
        RelayHandler(),
        hostname="0.0.0.0",
        port=my_port,
        authenticator=Authenticator(),
        auth_require_tls=False,
    )
    try:
        controller.start()
    except Exception as e:
        print(e)
        controller.stop()


def createuser(my_username, my_password):
    USER_AND_PASSWORD[my_username] = PasswordHasher().hash(my_password)


# Forward mail to telegram bot
class EmailToBot:
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello, I can help you to check email!",
        )

    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=update.message.text
        )

    async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = "use '/join key' to join the session\n\
        so I will send to email to you\n\
        use '/leave' to leave the session\n\
        so I will not send email to you\
        "
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

    async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text_caps: str = " ".join(context.args)
        if text_caps == my_key:
            if update.effective_chat.id not in all_chat_id:
                all_chat_id.add(update.effective_chat.id)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Congratulations, you successfully join the session!",
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Oh, you already join the session!",
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, the password is incorrect, please try again.",
            )

    async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id not in all_chat_id:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You have not joined the session.",
            )
        else:
            all_chat_id.remove(update.effective_chat.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Byebye, you successfully leave the session!",
            )

    async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="description of your program")
    parser.add_argument("-t", "--token", help="your bot token")
    parser.add_argument("-k", "--key", help="a key to manage")
    parser.add_argument("-u", "--username", help="a user to login")
    parser.add_argument("-p", "--password", help="a password for user")
    parser.add_argument("-P", "--port", help="email bind port")
    args = parser.parse_args()
    my_token = args.token
    my_key = args.key
    my_username = args.username
    my_password = args.password
    my_port = args.port

    createuser(my_username, my_password)
    print("start server")
    amain(my_port)

    application = ApplicationBuilder().token(my_token).build()

    start_handler = CommandHandler("start", EmailToBot.start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), EmailToBot.echo)
    help_handler = CommandHandler("help", EmailToBot.help)
    join_handler = CommandHandler("join", EmailToBot.join)
    leave_handler = CommandHandler("leave", EmailToBot.leave)
    unknown_handler = MessageHandler(filters.COMMAND, EmailToBot.unknown)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(help_handler)
    application.add_handler(join_handler)
    application.add_handler(leave_handler)
    application.add_handler(unknown_handler)
    print("start tobot")
    application.run_polling()
    print("stop all")
