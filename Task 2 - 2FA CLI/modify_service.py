import sqlite3
from encryption import encrypt_db, decrypt_db


def modify_service(service_from, service_to, key):
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    UPDATE services SET service = ? WHERE service = ?
    """,
        (service_to, service_from),
    )
    conn.commit()
    conn.close()
    encrypt_db()


def modify_username(service, username_from, username_to, key):
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    UPDATE services SET username = ? WHERE service = ? AND username = ?
    """,
        (username_to, service, username_from),
    )
    conn.commit()
    conn.close()
    encrypt_db()


def modify_seed(service, username, seed, key):
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    UPDATE services SET seed = ? WHERE service = ? AND username = ?
    """,
        (seed, service, username),
    )
    conn.commit()
    conn.close()
    encrypt_db()
