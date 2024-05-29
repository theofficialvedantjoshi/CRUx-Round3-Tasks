# import totp
import time
import os
import tempfile
import subprocess
import sqlite3

from encryption import encrypt_db, decrypt_db


def set_seed():
    editor = os.getenv("EDITOR", "notepad")
    path = "D:\\CODE\\CRUx-Round3-Tasks\\Task 2 - 2FA CLI\\temp"
    with tempfile.NamedTemporaryFile(
        mode="w+", dir=path, delete=False, suffix=".txt"
    ) as tf:
        tf.write("ENTER TOTP SEED BELOW\n")
        tf.write("Service:[]\n")
        tf.write("Seed:[]")
        tf.flush()
        subprocess.call(
            [
                editor,
                tf.name,
            ]
        )
        tf.seek(0)
        # print(tf.readlines())
        lines = tf.readlines()
        service = lines[1].split(":")[1].strip("\n").strip("[").strip("]")
        seed = lines[2].split(":")[1].strip("[").strip("]")
    os.remove(tf.name)
    return service, seed


def set_editor():
    editor = input("Enter your preferred text editor: ")
    os.environ["EDITOR"] = editor
    print("EDITOR set successfully")


def init_database():
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    CREATE TABLE IF NOT EXISTS services(
        seed TEXT PRIMARY KEY,
        service TEXT NOT NULL
    )
        """
    )
    conn.commit()
    conn.close()


def add_service():
    service, seed = set_seed()
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    INSERT INTO services(seed, service) VALUES(?, ?)
    """,
        (seed, service),
    )
    conn.commit()
    conn.close()
    encrypt_db()
    print("Service added successfully")
