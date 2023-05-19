import argparse
import asyncio
import os
import ssl
import subprocess
import dns.resolver
import sqlite3
import sys
import telebot
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from argon2 import PasswordHasher
from functools import lru_cache
from pathlib import Path

DB_AUTH = Path("mail.db")
my_token = '*:*'

class Authenticator:
    def __init__(self, auth_database):
        self.auth_db = Path(auth_database)

    def __call__(self, server, session, envelope, mechanism, auth_data):
        fail_nothandled = AuthResult(success=False, handled=False)
        if mechanism not in ("LOGIN", "PLAIN"):
            return fail_nothandled
        if not isinstance(auth_data, LoginPassword):
            return fail_nothandled
        username_str = auth_data.login.decode('utf-8')
        password_str = auth_data.password.decode('utf-8')
        conn = sqlite3.connect(self.auth_db)
        curs = conn.execute(
            "SELECT hashpass FROM userauth WHERE username=?", (username_str,)
        )
        hash_db = curs.fetchone()
        conn.close()
        if not hash_db:
            return fail_nothandled
        if not PasswordHasher().verify(hash_db[0], password_str):
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
    with open("chatid.txt", "r") as file:
        all_chat_id = file.read()
    contents = f'From: {sender}\nTo: {recipient}\nMessage data: {body}'
    bot = telebot.TeleBot(my_token)
    all_chat_id2 = all_chat_id.split('\n')
    for now_chat_id in all_chat_id2:
        if len(now_chat_id) > 5:
            bot.send_message(int(now_chat_id), contents)

class RelayHandler:
    async def handle_MAIL(self, server, session, envelope, address, mail_options):
        # address 发送人给出已解析电子邮件地址
        # print(address)
        envelope.mail_from = address
        return '250 OK'
    
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # address 接收人给出已解析电子邮件地址
        # print(address)
        envelope.rcpt_tos.append(address)
        return '250 OK'
    
    async def handle_DATA(self, server, session, envelope):
        mx_rcpt = {}
        for rcpt in envelope.rcpt_tos:
            _, _, domain = rcpt.partition("@")
            mx = get_mx(domain)
            if mx is None:
                continue
            mx_rcpt.setdefault(mx, []).append(rcpt)

        for mx, rcpts in mx_rcpt.items():
            # with SMTPCLient(mx, 25) as client:
            #     client.sendmail(
            #         from_addr=envelope.mail_from,
            #         to_addrs=rcpts,
            #         msg=envelope.original_content
            #     )
            print(
                f"from_addr: {envelope.mail_from}\n"
                f"to_addrs: {rcpts}\n"
                f"message: {envelope.original_content}\n"
            )

            await snedtobot(envelope.mail_from, rcpts, envelope.original_content)
        return '250 Message accepted for delivery'

# noinspection PyShadowingNames
async def amain():
    handler = RelayHandler()
    if not os.path.exists('cert.cert') and not os.path.exists('key.key'):
        subprocess.call("openssl req -x509 -newkey rsa:4096 -keyout key.key -out cert.cert -days 365 -nodes -subj '/CN=localhost'",shell=True)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('cert.cert', 'key.key')
    controller = Controller(
        handler,
        hostname='127.0.0.1',
        port=18025,
        authenticator=Authenticator(DB_AUTH),
        auth_require_tls=False,
        tls_context=context, 
        require_starttls=True,
    )
    try:
        controller.start()
    except Exception as e:
        print(e)
        controller.stop()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='description of your program')
    parser.add_argument('-t', '--token', help='your bot token')

    args = parser.parse_args()
    my_token = args.token
    
    if not DB_AUTH.exists():
        print(f"Please create {DB_AUTH} first using makeuser.py")
        sys.exit(1)
    # logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(amain())
    try:
        loop.run_forever()
    except Exception as e:
        loop.stop()
        print("Stop:", e)