"""Unit and integration tests for the PixelVault Flask Web presentation layer."""
import os
import unittest
from src.web.app import create_app


class TestPixelVaultFlaskWeb(unittest.TestCase):
    """Verifies that the Flask web layer routes, templates, and API endpoints work properly."""

    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.games_file = os.path.join(base_dir, "data", "games.json")
        self.orders_file = os.path.join(base_dir, "data", "orders.json")

        self.app = create_app({
            "TESTING": True,
            "GAMES_FILE": self.games_file,
            "ORDERS_FILE": self.orders_file,
            "SECRET_KEY": "test-secret-key",
        })
        self.client = self.app.test_client()

    def test_homepage_renders_ok(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("PIXEL", html)
        self.assertIn("VAULT", html)
        self.assertIn("Destacado de la Semana", html)

    def test_catalog_renders_and_filters(self):
        response = self.client.get("/catalog?genre=Acción")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Catálogo de Videojuegos", html)

    def test_game_detail_valid_and_invalid(self):
        # Valid slug
        response = self.client.get("/game/cyber-odyssey-neo-veridia")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Cyber Odyssey: Neo-Veridia", html)
        self.assertIn("Requisitos del Sistema", html)

        # Invalid slug
        response_404 = self.client.get("/game/non-existent-game-slug-404")
        self.assertEqual(response_404.status_code, 404)

    def test_api_cart_operations(self):
        # 1. Add game to cart via AJAX API
        add_res = self.client.post("/api/cart/add/pv-cyber-odyssey")
        self.assertEqual(add_res.status_code, 200)
        data = add_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["cart_count"], 1)

        # 2. Check cart state API
        state_res = self.client.get("/api/cart/state")
        self.assertEqual(state_res.status_code, 200)
        state_data = state_res.get_json()
        self.assertEqual(state_data["count"], 1)
        self.assertEqual(len(state_data["items"]), 1)

        # 3. View cart page
        cart_page = self.client.get("/cart")
        self.assertEqual(cart_page.status_code, 200)

        # 4. Remove game
        rem_res = self.client.post("/api/cart/remove/pv-cyber-odyssey")
        self.assertEqual(rem_res.status_code, 200)
        rem_data = rem_res.get_json()
        self.assertEqual(rem_data["cart_count"], 0)

    def test_api_filter_games_endpoint(self):
        res = self.client.get("/api/games?search=Cyber")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["count"], 0)
        self.assertIn("Cyber", data["games"][0]["title"])

    def test_orders_history_page(self):
        res = self.client.get("/orders")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Historial de Pedidos", html)
        self.assertIn("Inspector de Persistencia Local JSON", html)

    def test_cod_games_and_online_demos(self):
        # 1. Homepage showcases online demos section and links
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Demos Jugables Online en Navegador", html)
        self.assertIn("https://vel.gg/bo1z", html)
        self.assertIn("https://vibeslops.luckeysystems.com", html)
        self.assertIn("https://cheese-cube.pages.dev", html)
        self.assertIn("https://ovz-game-production.up.railway.app", html)
        self.assertIn("Probar Demo Online", html)

        # 2. Detail pages for COD titles
        cod_slugs = [
            ("cod-black-ops-zombies", "https://vel.gg/bo1z"),
            ("cod-black-ops-2", "https://vibeslops.luckeysystems.com"),
            ("cod-black-ops-3-zombies-cheese-cube", "https://cheese-cube.pages.dev"),
            ("cod-modern-warfare-2", "https://ovz-game-production.up.railway.app"),
        ]
        for slug, expected_url in cod_slugs:
            detail_res = self.client.get(f"/game/{slug}")
            self.assertEqual(detail_res.status_code, 200)
            detail_html = detail_res.data.decode("utf-8")
            self.assertIn(expected_url, detail_html)
            self.assertIn("¡Demo Web Online Disponible!", detail_html)
            self.assertIn("Probar Demo Online", detail_html)

    def test_process_checkout_flow(self):
        # 1. Add game to cart
        self.client.post("/api/cart/add/pv-cyber-odyssey")

        # 2. View checkout page
        checkout_page = self.client.get("/checkout")
        self.assertEqual(checkout_page.status_code, 200)

        # 3. Post checkout form with accept_terms
        res = self.client.post(
            "/checkout",
            data={
                "customer_name": "Estudiante Prueba",
                "customer_email": "estudiante@ejemplo.com",
                "payment_method": "Tarjeta de Crédito / Débito",
                "accept_terms": "on"
            },
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("¡Gracias por tu compra!", html)
        self.assertIn("Tus Claves de Activación Digitales", html)
        self.assertIn("data/orders.json", html)


if __name__ == "__main__":
    unittest.main()


