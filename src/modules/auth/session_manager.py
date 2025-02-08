import json
import os

class SessionManager:
    def __init__(self, page):
        self.page = page
        self.session_file = "session.json"  # Adjust path as needed

    async def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                encrypted = f.read()
            # Decrypt the stored session.
            from modules.auth.encryption import decrypt_credentials  # adjust import as needed
            session = decrypt_credentials(encrypted)
            return session
        return None

    def save_session(self, session):
        # Encrypt the session before saving.
        from modules.auth.encryption import encrypt_credentials  # adjust import as needed
        encrypted = encrypt_credentials(session)
        with open(self.session_file, "w") as f:
            f.write(encrypted)
