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
        tf.write("Username:[]\n")
        tf.write("Seed:[]")
        tf.flush()
        try:
            subprocess.call(
                [
                    editor,
                    tf.name,
                ]
            )
        except:
            print("Invalid editor. Please set a valid editor.")
        tf.seek(0)
        # print(tf.readlines())
        lines = tf.readlines()
        try:
            service = lines[1].split(":")[1].strip("\n").strip("[").strip("]")
            username = lines[2].split(":")[1].strip("\n").strip("[").strip("]")
            seed = lines[3].split(":")[1].strip("[").strip("]")
        except:
            print("Invalid input format. Please fill in the [] fields.")
    os.remove(tf.name)
    return service, username, seed


def set_editor(editor):
    os.environ["EDITOR"] = editor
    print("EDITOR set successfully")


def init_database():
    if os.path.exists("Task 2 - 2FA CLI\data\\totp.db"):
        pass
    else:
        conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
        curser = conn.cursor()
        curser.execute(
            """
        CREATE TABLE IF NOT EXISTS services(
            service TEXT,
            username TEXT,
            seed TEXT PRIMARY KEY
        )
            """
        )
        conn.commit()
        conn.close()
        encrypt_db()


def set_service(key):
    service, username, seed = set_seed()
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    INSERT INTO services(service, username, seed) VALUES(?, ?, ?)
    """,
        (service, username, seed),
    )
    conn.commit()
    conn.close()
    encrypt_db()
