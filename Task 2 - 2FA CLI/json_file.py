import sqlite3
import json
from encryption import decrypt_db, encrypt_db
import pyminizip
import os


def export_db(key, password):
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    curser.execute(
        """
    SELECT * FROM services
    """
    )
    data = curser.fetchall()
    conn.close()
    for i in data:
        with open(f"Task 2 - 2FA CLI\data\\{i[0]}-{i[1]}.json", "w") as f:
            json.dump({"service": i[0], "username": i[1], "seed": i[2]}, f)

    encrypt_db()
    json_files = [
        "Task 2 - 2FA CLI\data\\" + f
        for f in os.listdir("Task 2 - 2FA CLI\data")
        if f.endswith(".json")
    ]
    pyminizip.compress_multiple(
        json_files, [], "Task 2 - 2FA CLI\data\\data.zip", password, 5
    )
    for file in json_files:
        os.remove(file)


def import_db_json(key, file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    data = json.loads(data)
    decrypt_db(key)
    conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
    curser = conn.cursor()
    try:
        curser.execute(
            """
    INSERT INTO services(service, username, seed) VALUES(?, ?, ?)
    """,
            (data["service"], data["username"], data["seed"]),
        )
    except:
        print("Invalid data or duplicate entry")
    conn.commit()
    conn.close()
    encrypt_db()


def import_db_zip(key, password, file_path):
    try:
        pyminizip.uncompress(file_path, password, "Task 2 - 2FA CLI\data", 0)
    except:
        print("Invalid password or file")
        return
    json_files = [
        "Task 2 - 2FA CLI\data\\" + f
        for f in os.listdir("Task 2 - 2FA CLI\data")
        if f.endswith(".json")
    ]
    decrypt_db(key)
    for file in json_files:
        with open(file, "rb") as f:
            data = f.read()
        data = json.loads(data)
        conn = sqlite3.connect("Task 2 - 2FA CLI\data\\totp.db")
        curser = conn.cursor()
        try:
            curser.execute(
                """
        INSERT INTO services(service, username, seed) VALUES(?, ?, ?)
        """,
                (data["service"], data["username"], data["seed"]),
            )
        except:
            print("Invalid data or duplicate entry")
        conn.commit()
        conn.close()
        os.remove(file)
    encrypt_db()
