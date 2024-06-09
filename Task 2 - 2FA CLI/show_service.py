import pyotp
from encryption import decrypt_db, encrypt_db
import sqlite3
import datetime
from qrcode import QRCode


def fetch_seed(service, key):
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    try:
        curser.execute(
            """
        SELECT seed FROM services WHERE service = ?
        """,
            (service,),
        )
    except:
        print("Invalid service")
    seed = curser.fetchone()[0]
    conn.close()
    encrypt_db()
    return seed


def show_otp(seed):
    try:
        totp = pyotp.TOTP(seed)
    except:
        print("Invalid seed, please remove and re-add the service.")
    return (
        totp.now(),
        totp.interval - datetime.datetime.now().timestamp() % totp.interval,
    )


def show_qr(service, seed):
    totp = pyotp.TOTP(seed)
    qr = QRCode()
    qr.add_data(totp.provisioning_uri(service))
    qr.print_ascii(invert=True)
