"""Entrypoint for running the PixelVault Flask Web Storefront.

Evaluación Práctica - Programación IV
Instituto Universitario de Tecnología "Antonio José de Sucre"
Docente de Referencia: Prof. Yoher Alejandro Vázquez Salinas
"""
import os
from src.web.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 66)
    print("[PIXELVAULT] TIENDA DIGITAL DE VIDEOJUEGOS (FLASK + HTML5/CSS3)")
    print("IUT 'Antonio Jose de Sucre' -- Programacion IV")
    print("Docente de Referencia: Prof. Yoher Alejandro Vazquez Salinas")
    print(f"Servidor Web interactivo iniciado en: http://127.0.0.1:{port}")
    print("Persistencia: Archivos JSON locales en data/ (games.json y orders.json)")
    print("=" * 66)
    app.run(host="127.0.0.1", port=port, debug=True)
