import flet as ft

def show_error(page: ft.Page, message: str):
    if not page.controls:  # Si la página está vacía
        page.add(ft.Container())  # Agregar contenedor temporal
    
    page.snack_bar = ft.SnackBar( # type: ignore
        content=ft.Text(message, color="#fefefe"),
        bgcolor = "#101010"
    )
    page.snack_bar.open = True # type: ignore
    page.overlay.append(page.snack_bar) # type: ignore
    page.update()

def loading_indicator(page: ft.Page, text: str = "Cargando..."):
    # page.controls.clear() # type: ignore
    page.add(
        ft.Column(
            [
                ft.ProgressRing(width=50, height=50, color="#00cc00"),
                ft.Text(text, size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()