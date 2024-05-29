import pyotp
from encryption import decrypt_db, encrypt_db
import sqlite3
import datetime
from qrcode import QRCode


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


def show_qr(service, seed):
    totp = pyotp.TOTP(seed)
    qr = QRCode()
    qr.add_data(totp.provisioning_uri(service))
    qr.print_ascii(invert=True)
