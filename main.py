"""Punto de entrada principal para el Aplicativo Web GUI en Flet con POO.

Proyecto: PixelVault — Tienda Digital de Videojuegos
Evaluación Práctica — Programación IV
Instituto Universitario de Tecnología "Antonio José de Sucre"
Docente de Referencia: Prof. Yoher Alejandro Vazquez Salinas
"""
import os
import sys
import flet as ft
from src.gui.app import PixelVaultApp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_FILE = os.path.join(BASE_DIR, "data", "games.json")
ORDERS_FILE = os.path.join(BASE_DIR, "data", "orders.json")


def main():
    # Instanciamos la aplicación orientada a objetos (POO)
    app_controller = PixelVaultApp(
        games_file=GAMES_FILE,
        orders_file=ORDERS_FILE
    )

    port = 8550
    # Si se pasa un puerto como argumento CLI, lo usamos
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    # Asegurar codificación UTF-8 en consolas Windows
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("==================================================================", flush=True)
    print("[PIXELVAULT] TIENDA DIGITAL DE VIDEOJUEGOS (STEAM + ITCH.IO)", flush=True)
    print("IUT 'Antonio Jose de Sucre' -- Programacion IV", flush=True)
    print("Docente de Referencia: Prof. Yoher Alejandro Vazquez Salinas", flush=True)
    print(f"Modo: Aplicacion Web en Navegador (http://127.0.0.1:{port})", flush=True)
    print("Persistencia: Archivos JSON locales en data/", flush=True)
    print("Gestion de Entorno: uv (uv run python main.py)", flush=True)
    print("==================================================================", flush=True)

    # Ejecutar la aplicación Flet directamente en el navegador web
    ft.run(
        app_controller.main,
        view=ft.AppView.WEB_BROWSER,
        host="127.0.0.1",
        port=port
    )


if __name__ == "__main__":
    main()
