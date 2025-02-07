import flet as ft
from modules.ui.main_flow import MainFlow

async def main(page: ft.Page):
    flow = MainFlow(page)
    # print(page)
    await flow.run()

if __name__ == "__main__":
    ft.app(target=main)