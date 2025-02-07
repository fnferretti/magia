import datetime
import flet as ft
import pprint
import asyncio

from modules.auth import AuthManager, SessionManager
from modules.core.state import LoginState
from modules.ui_helpers import show_error, loading_indicator
from modules.scrape.scrape_manager import ScrapeManager

class MainFlow:
    def __init__(self, page: ft.Page):  # Asegurar tipo Page
        self.page = page
        self.state = LoginState()
        self.session_manager = SessionManager(page)
        self.auth_manager = AuthManager(self.state)
        
        # Configurar página (no async)
        self.page.title = "Mi App"
        self.page.window_width = 800  # type: ignore
        self.page.window_height = 600  # type: ignore
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    async def run(self):
        try:
            # Cargar y validar sesión
            session = await self.session_manager.load_session()
            await self.auth_manager.validate_credentials(session)
            print(session)
            # Cargar contenido principal
            self._load_main_content()
        except Exception as e:
            # Mostrar login si falla
            await self._show_login_form()

    async def _show_login_form(self):
        """Muestra el formulario de login"""
        self.page.clean()
        email_field = ft.TextField(label="Email")
        password_field = ft.TextField(label="Contraseña", password=True)
        stay_logged_in = ft.Checkbox(label="Mantenerse conectado")
        async def on_login_click(e):
            await self._on_login(email_field.value, password_field.value)  # type: ignore
        login_btn = ft.ElevatedButton("Ingresar", on_click=on_login_click)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Inicio de sesión", size=24),
                    email_field,
                    password_field,
                    stay_logged_in,
                    login_btn
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=400
            )
        )
        self.page.update()

    async def _on_login(self, email: str, password: str):
        """Manejador de login"""
        try:
            loading_indicator(self.page, "Validando...")
            self.state.credentials.update({"email": email, "password": password})
            await self.auth_manager.validate_credentials(self.state.credentials)
            scrape_manager = ScrapeManager(self.state)
            scrape_result = scrape_manager.scrape()  # synchronous call
            pprint.pp(scrape_result)  # type: ignore
            self._load_main_content(scrape_data=scrape_result)
        except Exception as e:
            show_error(self.page, str(e))
            await self._show_login_form()

    # Define the sort order for Estado values.
    SORT_ORDER = {
        "Vencido": 0,
        "Pendiente": 1,
        "Esperando aprobación": 2,
        "Aprobado": 3,
    }

    # sort_key remains as before.
    def sort_key(self, rec):
        archivo = rec.get("Archivo", {})
        estado = archivo.get("EstadoDenominacion", "")
        base_order = self.SORT_ORDER.get(estado, 99)
        if estado == "Aprobado":
            fecha_str = archivo.get("FechaVencimiento", "")
            try:
                fecha_str = fecha_str.strip()
                if "T" in fecha_str:
                    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S%z").date()
                else:
                    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                days_left = (fecha - datetime.date.today()).days
            except Exception:
                days_left = float("inf")
            return (base_order, days_left)
        else:
            return (base_order, 0)

    def _build_custom_table_rows(self, scrape_data):
        # Header row with five columns:
        # 1) Estado, 2) Denominación, 3) Patente, 4) Documento, 5) Servicio.
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Estado", weight="bold", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    ft.Text("Denominación", weight="bold", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    ft.Text("Patente", weight="bold", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    ft.Text("Documento", weight="bold", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    ft.Text("Servicio", weight="bold", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=10,
            bgcolor=ft.colors.GREY_900,
            border=ft.border.all(1, ft.colors.GREY),
        )
        rows = []
        for record in scrape_data:
            # Top-level fields.
            documento = str(record.get("DocumentacionDenominacion", ""))
            servicio = str(record.get("ServicioDenominacion", ""))
            denominacion = str(record.get("DenominacionEnte", ""))
            # Compute "Patente" if DenominacionEnte is one of the given values.
            if denominacion.upper() in ["AUTOMOVIL", "CHASIS", "ACOPLADO"]:
                patente_value = record.get("VehiculoPatente", "")
            else:
                patente_value = ""
            # Nested fields from "Archivo".
            archivo = record.get("Archivo", {})
            estado_val = archivo.get("EstadoDenominacion", "")
            
            # Build cells for Denominación, Documento, Servicio.
            denominacion_cell = ft.Text(denominacion, width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
            patente_cell = ft.Text(patente_value, width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
            documento_cell = ft.Text(documento, width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
            servicio_cell = ft.Text(servicio, width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
            
            # Build the Estado cell based on its value.
            if estado_val == "Pendiente":
                estado_cell = ft.Container(
                    content=ft.Text("Pendiente", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    bgcolor=ft.colors.AMBER_700,
                    width=200,
                )
            elif estado_val == "Aprobado":
                fecha_str = archivo.get("FechaVencimiento", None)
                if fecha_str:
                    try:
                        fecha_str = fecha_str.strip()
                        if "T" in fecha_str:
                            fecha_venc = datetime.datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S%z").date()
                        else:
                            fecha_venc = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                        days_left = (fecha_venc - datetime.date.today()).days
                        estado_text = f"{days_left} días"
                    except Exception:
                        estado_text = "N/A"
                else:
                    estado_text = "N/A"
                estado_cell = ft.Container(
                    content=ft.Text(estado_text, width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    bgcolor=ft.colors.GREEN_800,  # Dark green for "Aprobado"
                    width=200,
                )
            elif estado_val == "Vencido":
                estado_cell = ft.Container(
                    content=ft.Text("Vencido", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    bgcolor=ft.colors.ORANGE_800,  # Dark orange for "Vencido"
                    width=200,
                )
            elif estado_val == "Esperando aprobación":
                estado_cell = ft.Container(
                    content=ft.Text("Esperando aprobación", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE),
                    bgcolor=ft.colors.BLUE_800,  # Dark blue for "Esperando aprobación"
                    width=200,
                )
            else:
                estado_cell = ft.Text("", width=200, text_align=ft.TextAlign.CENTER, color=ft.colors.WHITE)
            
            # Combine cells into a row with the following column order:
            # Estado, Denominación, Patente, Documento, Servicio.
            row = ft.Container(
                content=ft.Row(
                    controls=[
                        estado_cell,
                        denominacion_cell,
                        patente_cell,
                        documento_cell,
                        servicio_cell,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=8,
                bgcolor=ft.colors.GREY_800,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY)),
            )
            rows.append(row)
        return [header] + rows

    def _load_main_content(self, scrape_data=None):
        """Display a welcome message and, if scrape_data is provided, a custom-styled table that scrolls
        only within the table area. The table is sorted by Estado in the order:
        Vencido, Pendiente, Esperando aprobación, and then Aprobado (sorted by days left ascending)."""
        self.page.controls.clear()
        content_controls = [ft.Text("¡Bienvenido!", size=30, weight="bold")]

        if scrape_data:
            # Sort the data using the instance method self.sort_key.
            scrape_data.sort(key=self.sort_key)
            table_rows = self._build_custom_table_rows(scrape_data)
            scrollable_table = ft.ListView(
                controls=table_rows,
                height=1000,  # Fixed height for the table scroll area.
                spacing=0
            )
            content_controls.append(scrollable_table)

        self.page.add(
            ft.Column(
                controls=content_controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        self.page.update()