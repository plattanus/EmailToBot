# Copyright 2014-2021 The aiosmtpd Developers
# SPDX-License-Identifier: Apache-2.0

import sqlite3
from argon2 import PasswordHasher
from pathlib import Path
from typing import Dict

DB_FILE = "mail.db"
USER_AND_PASSWORD: Dict[str, str] = {
    "sender@example.com": "password",
    "recipient@example.com": "password",
    "test@example.com": "password",
    "admin@example.com": "password",
    "from@example.com": "password",
    "to@example.com": "password",
    "user@example.com": "password",
    "sender": "password",
    "recipient": "password",
    "test": "password",
    "admin": "password",
    "from": "password",
    "to": "password",
    "user": "password",
}

if __name__ == '__main__':
    dbfp = Path(DB_FILE).absolute()
    if dbfp.exists():
        dbfp.unlink()
    conn = sqlite3.connect(DB_FILE)
    curs = conn.cursor()
    curs.execute("CREATE TABLE userauth (username text, hashpass text)")
    ph = PasswordHasher()
    insert_up = "INSERT INTO userauth VALUES (?, ?)"
    for u, p in USER_AND_PASSWORD.items():
        print(u,p)
        h = ph.hash(p)
        print(h)
        curs.execute(insert_up, (u, h))
    conn.commit()
    conn.close()
    assert dbfp.exists()
    print(f"database created at {dbfp}")