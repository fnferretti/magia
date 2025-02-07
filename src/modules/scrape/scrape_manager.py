from dataclasses import dataclass
import requests
from datetime import datetime
from modules.core.state import LoginState

@dataclass
class ScrapeConfig:
    secret_key_url: str = "https://docs.tpr.com.ar:2001/DocUXApi/api/RegistroEntidad/getSecretKey?param=459"
    auth_url: str = "https://docs.tpr.com.ar:2001/CommonApi/api/Usuarios/authenticate"
    management_url: str = "https://docs.tpr.com.ar:2001/DocUXApi/api/DocumentacionesRequeridas/getGestionDocsRequeridas"

class ScrapeManager:
    def __init__(self, login_state: LoginState, config: ScrapeConfig = None): # type: ignore
        self.login_state = login_state
        self.config = config if config is not None else ScrapeConfig()
        self.headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"
        }

    def fetch_secret_key(self, url: str = None) -> str: # type: ignore
        url = url or self.config.secret_key_url
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            secret_key_data = response.json()
            secret_key = secret_key_data.get("Valor")
            print("Retrieved Secret Key:", secret_key)
            return secret_key
        else:
            print(f"Failed to retrieve secretKey. Status Code: {response.status_code}")
            print("Response Text:", response.text)
            exit()

    def authenticate(self, auth_url: str = None, secret_key_url: str = None) -> dict: # type: ignore
        # If token is already stored, reuse it
        if self.login_state.token is not None:
            print("Using cached token.")
            return {
                "Token": self.login_state.token,
                "EntidadesContacto": [{"EntidadId": self.login_state.entity_id}]
            }
        auth_url = auth_url or self.config.auth_url
        secret_key_url = secret_key_url or self.config.secret_key_url
        auth_data = {
            "Denominacion": self.login_state.credentials.get("email"),
            "Clave": self.login_state.credentials.get("password"),
            "secretKey": self.fetch_secret_key(secret_key_url)
        }
        auth_response = requests.post(auth_url, headers=self.headers, json=auth_data)
        if auth_response.status_code == 200:
            auth_response_data = auth_response.json()
            print("Login Successful!")
            print("Response:", auth_response_data)
            # Cache the token and entity id in state
            self.login_state.token = auth_response_data.get("Token")
            self.login_state.entity_id = auth_response_data.get("EntidadesContacto")[0].get("EntidadId")  # type: ignore
            return auth_response_data
        else:
            print(f"Login failed with status code {auth_response.status_code}")
            print("Response Text:", auth_response.text)
            raise Exception("Authentication failed")

    def fetch_management_data(
        self,
        token: str,
        month: int,
        year: int,
        entity: int,
        incl_approved_doc: bool = True,
        management_url: str = None # type: ignore
    ) -> dict:
        management_url = management_url or self.config.management_url
        self.headers["Authorization"] = f"Bearer {token}"
        management_data = {
            "Periodo": {
                "Mes": month,
                "A\u00f1o": year,
                "EntidadId": entity
            },
            "IncluirDocumentacionAprobada": incl_approved_doc
        }
        response = requests.post(management_url, headers=self.headers, json=management_data)
        return response.json()

    def scrape(self, management_url: str = None): # type: ignore
        auth_data = self.authenticate()
        entity = auth_data.get("EntidadesContacto")[0].get("EntidadId")  # type: ignore
        print("Entity ID:", entity)
        return self.fetch_management_data(
            token=auth_data.get("Token"),  # type: ignore
            month=datetime.now().month,
            year=datetime.now().year,
            entity=entity,
            management_url=management_url
        )

# Usage example:
if __name__ == "__main__":
    # Create a LoginState instance and set the credentials
    from modules.core.state import LoginState
    state = LoginState()
    state.credentials["email"] = "my_username"
    state.credentials["password"] = "my_password"
    
    # Create an instance of ScrapeManager with the state and (optionally) a custom config
    manager = ScrapeManager(login_state=state)
    result = manager.scrape()
    print(result)
