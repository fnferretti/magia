import os
import json
from cryptography.fernet import Fernet

KEY_FILE = "session_key.key"

def get_fernet():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    return Fernet(key)

def encrypt_credentials(credentials: dict) -> str:
    data_str = json.dumps(credentials)
    fernet = get_fernet()
    encrypted = fernet.encrypt(data_str.encode())
    return encrypted.decode()

def decrypt_credentials(encrypted_data: str) -> dict:
    fernet = get_fernet()
    decrypted = fernet.decrypt(encrypted_data.encode())
    return json.loads(decrypted.decode())
