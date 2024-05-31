import sqlite3
import json
from encryption import decrypt_db, encrypt_db
import os


def remove_service(service, username, key):
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    DELETE FROM services WHERE service = ? AND username = ?
    """,
        (service, username),
    )
    conn.commit()
    conn.close()
    encrypt_db()
