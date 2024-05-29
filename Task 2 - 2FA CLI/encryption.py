from cryptography.fernet import Fernet


def encrypt_db():
    key = Fernet.generate_key()
    with open("Task 2 - 2FA CLI\\temp\key.key", "wb") as key_file:
        key_file.write(key)
    with open("Task 2 - 2FA CLI\\temp\key.key", "rb") as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    with open("Task 2 - 2FA CLI\data\\totp.db", "rb") as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open("Task 2 - 2FA CLI\data\\totp.db", "wb") as file:
        file.write(encrypted_data)


def decrypt_db():
    with open("Task 2 - 2FA CLI\\temp\key.key", "rb") as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    with open("Task 2 - 2FA CLI\data\\totp.db", "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open("Task 2 - 2FA CLI\data\\totp.db", "wb") as file:
        file.write(decrypted_data)
