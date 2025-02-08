import json
import os
from cryptography.fernet import Fernet

# Retrieve your encryption key from an environment variable.
# If not set, generate one (and make sure to persist it securely for future runs).
key = os.getenv("SESSION_ENCRYPTION_KEY")
if not key:
    key = Fernet.generate_key()
    # In production, store this key securely rather than regenerating it.
fernet = Fernet(key)

def encrypt_credentials(credentials: dict) -> str:
    """Encrypts the credentials dictionary into a string."""
    data_str = json.dumps(credentials)
    encrypted_data = fernet.encrypt(data_str.encode())
    return encrypted_data.decode()

def decrypt_credentials(encrypted_data: str) -> dict:
    """Decrypts the encrypted string back into a credentials dictionary."""
    decrypted_data = fernet.decrypt(encrypted_data.encode())
    return json.loads(decrypted_data.decode())
