from ..core.state import LoginState
from ..core.exceptions import AuthError

class AuthManager:
    def __init__(self, state: LoginState):
        self.state = state

    async def validate_credentials(self, credentials: dict):
        # Validación más flexible
        if not credentials.get("email") or not credentials.get("password"):
            raise AuthError("Todos los campos son requeridos")
            
        if "@" not in credentials["email"]:  # Validación básica de email
            raise AuthError("Formato de email inválido")