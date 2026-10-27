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

    port = 8555
    # Si se pasa un puerto como argumento CLI, lo usamos
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    # Asegurar codificación UTF-8 en consolas Windows
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    is_desktop = "--desktop" in sys.argv
    is_sync_only = "--sync-only" in sys.argv
    is_test_exceptions = "--test-exceptions" in sys.argv
    app_view = ft.AppView.FLET_APP if is_desktop else ft.AppView.WEB_BROWSER
    modo_str = "Prueba de Excepciones HTTP en Consola" if is_test_exceptions else ("Sincronización CLI (Sin GUI)" if is_sync_only else ("Aplicación de Escritorio Nativa (Límites 1024x700)" if is_desktop else f"Aplicación Web en Navegador (http://127.0.0.1:{port})"))

    print("==================================================================", flush=True)
    print("[PIXELVAULT] TIENDA DIGITAL DE VIDEOJUEGOS (STEAM + ITCH.IO)", flush=True)
    print("IUT 'Antonio Jose de Sucre' -- Programacion IV", flush=True)
    print("Docente de Referencia: Prof. Yoher Alejandro Vazquez Salinas", flush=True)
    print(f"Modo: {modo_str}", flush=True)
    print("Persistencia: 100% en Memoria RAM (Dependiente de la API Progra-2)", flush=True)
    print("==================================================================", flush=True)

    if is_test_exceptions:
        _run_all_http_tests(app_controller)
        return

    # ------------------------------------------------------------------
    # CONSUMO DE LA API, CARGA EN RAM Y MANEJO DE EXCEPCIONES EN CONSOLA
    # ------------------------------------------------------------------
    print("\n[CONECTANDO CON LA API EXTERNA PROGRA-2...]", flush=True)
    try:
        from src.domain.exceptions import (
            ApiMissingKeyError,
            ApiForbiddenKeyError,
            ApiAuthenticationError,
            ApiNamespaceNotFoundError,
            ApiMethodNotAllowedError,
            ApiValidationError,
            ApiInternalServerError,
            ApiConnectionError,
            ApiResponseError,
            ApiError,
        )

        # 1. Comprobar salud del endpoint
        health = app_controller.api_client.check_health(raise_on_error=True)
        print(f" -> Estado Servidor: {health.get('status', 'OK').upper()} (Código HTTP: 200 OK)", flush=True)
        print(f" -> Namespace Estudiante: {health.get('user')}", flush=True)
        print(f" -> Nombre: {health.get('full_name', 'Abraham Ali Garcia Lozano')}", flush=True)
        print(f" -> Endpoint: {health.get('endpoint')}", flush=True)

        # 2. Consumir endpoint GET /api/v1/abraham/games y almacenar en memoria RAM
        print("\n[CONSUMIENDO GET /api/v1/abraham/games Y ALMACENANDO EN MEMORIA RAM...]", flush=True)
        ram_games = app_controller.game_repo.sync_from_api(raise_on_error=True)
        print(f" -> ¡Éxito! Total de videojuegos cargados en RAM: {len(ram_games)}", flush=True)

        # 3. Imprimir en pantalla los videojuegos consumidos
        print("\n" + "-" * 70, flush=True)
        print(f"{'ID':<12} | {'TÍTULO':<32} | {'PRECIO':<9} | {'GÉNERO'}", flush=True)
        print("-" * 70, flush=True)
        for g in ram_games[:8]:
            precio_str = f"${g.final_price:.2f}" if g.final_price > 0 else "GRATIS"
            print(f"{g.id:<12} | {g.title[:30]:<32} | {precio_str:<9} | {g.genre}", flush=True)
        if len(ram_games) > 8:
            print(f"... y {len(ram_games) - 8} títulos más en memoria RAM.", flush=True)
        print("-" * 70 + "\n", flush=True)

    except ApiMissingKeyError as e:
        print(f"\n[EXCEPCIÓN HTTP 401 UNAUTHORIZED]: {e.message}", flush=True)
        print(f"Detalles: {e.errors}", flush=True)
    except ApiForbiddenKeyError as e:
        print(f"\n[EXCEPCIÓN HTTP 403 FORBIDDEN]: {e.message}", flush=True)
        print(f"Detalles: {e.errors}", flush=True)
    except ApiNamespaceNotFoundError as e:
        print(f"\n[EXCEPCIÓN HTTP 404 NOT FOUND]: {e.message}", flush=True)
        print(f"Detalles: {e.errors}", flush=True)
    except ApiMethodNotAllowedError as e:
        print(f"\n[EXCEPCIÓN HTTP 405 METHOD NOT ALLOWED]: {e.message}", flush=True)
    except ApiValidationError as e:
        print(f"\n[EXCEPCIÓN HTTP 422 UNPROCESSABLE ENTITY]: {e.message}", flush=True)
    except ApiInternalServerError as e:
        print(f"\n[EXCEPCIÓN HTTP 500 INTERNAL SERVER ERROR]: {e.message}", flush=True)
    except ApiConnectionError as e:
        print(f"\n[EXCEPCIÓN HTTP 503 SERVICE UNAVAILABLE / TIMEOUT]: {e.message}", flush=True)
    except ApiError as e:
        print(f"\n[EXCEPCIÓN DE API (HTTP {e.status_code})]: {e.message}", flush=True)
    except Exception as e:
        print(f"\n[EXCEPCIÓN NO CONTROLADA]: {e}", flush=True)

    if is_sync_only:
        print("[SINCRONIZACIÓN FINALIZADA (--sync-only). Finalizando proceso]", flush=True)
        return

    # Ejecutar la aplicación Flet (en ventana de escritorio o navegador web)
    if is_desktop:
        ft.run(
            app_controller.main,
            view=ft.AppView.FLET_APP,
            port=0
        )
    else:
        ft.run(
            app_controller.main,
            view=ft.AppView.WEB_BROWSER,
            host="127.0.0.1",
            port=port
        )


def _run_all_http_tests(app_controller):
    """Demuestra en consola todas las respuestas y excepciones HTTP documentadas en la API."""
    import urllib.request
    import urllib.error

    print("\n" + "=" * 70, flush=True)
    print("DEMOSTRACIÓN DE ESTADOS Y EXCEPCIONES HTTP EN CONSOLA", flush=True)
    print("=" * 70, flush=True)

    # 1. HTTP 200 OK
    print("\n--- [TEST 1] HTTP 200 OK (Credenciales válidas) ---", flush=True)
    games = app_controller.game_repo.sync_from_api(raise_on_error=False)
    print(f"Resultado: {len(games)} juegos en memoria RAM.", flush=True)

    # 2. HTTP 401 Unauthorized (Sin cabecera X-API-Key)
    print("\n--- [TEST 2] HTTP 401 Unauthorized (Omitiendo cabecera X-API-Key) ---", flush=True)
    app_controller.game_repo.sync_from_api(omit_key=True, raise_on_error=False)

    # 3. HTTP 403 Forbidden (API Key inválida)
    print("\n--- [TEST 3] HTTP 403 Forbidden (API Key errónea) ---", flush=True)
    app_controller.game_repo.sync_from_api(override_key="sk_live_clave_invalida_xxx", raise_on_error=False)

    # 4. HTTP 404 Not Found (Namespace inexistente)
    print("\n--- [TEST 4] HTTP 404 Not Found (Namespace no registrado) ---", flush=True)
    app_controller.game_repo.sync_from_api(override_user="estudiante_inexistente_999", raise_on_error=False)

    # 5. HTTP 422 Unprocessable Entity (Parámetros inválidos)
    print("\n--- [TEST 5] HTTP 422 Unprocessable Entity (limit=-1) ---", flush=True)
    try:
        req = urllib.request.Request(
            f"{app_controller.api_client.base_url}/api/v1/{app_controller.api_client.username}/games?limit=-1",
            headers=app_controller.api_client._get_headers()
        )
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(f"[CONSOLA API HTTP ERROR] Estado: {e.code} | Excepción: ApiValidationError | Mensaje: Parámetros inválidos | Detalle: {e.read().decode('utf-8', errors='ignore')}", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("TODAS LAS PRUEBAS DE EXCEPCIONES HTTP EN CONSOLA COMPLETADAS CON ÉXITO", flush=True)
    print("=" * 70 + "\n", flush=True)


if __name__ == "__main__":
    main()
