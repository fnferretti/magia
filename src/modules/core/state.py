# state.py
import asyncio

class LoginState:
    def __init__(self):
        self.credentials = {
            "email": None,
            "password": None,
            "keep_logged_in": False
        }
        self.token = None         # token obtained after authentication
        self.entity_id = None     # entity id from authentication
        self.event = asyncio.Event()
        self.error = None
