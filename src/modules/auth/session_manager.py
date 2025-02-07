import asyncio
from flet import Page
from ..core.exceptions import SessionError

class SessionManager:
    def __init__(self, page: Page):
        self.page = page
        
    async def load_session(self) -> dict:
        try:
            return {
                "email": await self.page.client_storage.get_async("email"),
                "password": await self.page.client_storage.get_async("password"),
                "keep_logged_in": await self.page.client_storage.get_async("keep_logged_in")
            }
        except Exception as e:
            print(f"Error loading session: {e}")
            return {}

    async def save_session(self, credentials: dict):
        try:
            if credentials["keep_logged_in"]:
                await self.page.client_storage.set_async("email", credentials["email"])
                await self.page.client_storage.set_async("password", credentials["password"])
                await self.page.client_stachent_storage.set_async("keep_logged_in", True) # type: ignore
            else:
                await self.clear_session()
        except Exception as e:
            raise SessionError(f"Failed to save session: {str(e)}")

    async def clear_session(self):
        await self.page.client_storage.clear_async()