import pyotp
from encryption import decrypt_db, encrypt_db
import sqlite3
import datetime


def fetch_seed(service):
    decrypt_db()
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    SELECT seed FROM services WHERE service = ?
    """,
        (service,),
    )
    seed = curser.fetchone()[0]
    conn.close()
    encrypt_db()
    return seed


def show_otp(seed):
    totp = pyotp.TOTP(seed)
    return (
        totp.now(),
        totp.interval - datetime.datetime.now().timestamp() % totp.interval,
    )
