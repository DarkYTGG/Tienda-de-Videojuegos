"""Unit and integration tests for the Progra-2 Students API client adapter."""
import unittest
from unittest.mock import patch, MagicMock
import io
import json

from src.infrastructure.api_client import Progra2ApiClient
from src.infrastructure.repositories import JsonGameRepository


class TestProgra2ApiClient(unittest.TestCase):
    """Verifies authentication, endpoint formation, and error resilience."""

    def setUp(self):
        self.client = Progra2ApiClient(
            base_url="https://progra-2-krw5.onrender.com",
            username="abraham",
            api_key="sk_live_abr_8f2d91a4c03b7e615f8e02d9"
        )

    def test_headers_include_api_key(self):
        headers = self.client._get_headers()
        self.assertEqual(headers["X-API-Key"], "sk_live_abr_8f2d91a4c03b7e615f8e02d9")
        self.assertEqual(headers["Accept"], "application/json")

    @patch("urllib.request.urlopen")
    def test_check_health_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "status": "healthy",
            "user": "abraham",
            "full_name": "Abraham Ali Garcia Lozano",
            "is_active": True
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        health = self.client.check_health()
        self.assertTrue(health["online"])
        self.assertEqual(health["user"], "abraham")
        self.assertEqual(health["status"], "healthy")

    @patch("urllib.request.urlopen")
    def test_check_health_failure_resilience(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection timeout")
        health = self.client.check_health()
        self.assertFalse(health["online"])
        self.assertIn("Connection timeout", health.get("error", ""))

    @patch("urllib.request.urlopen")
    def test_fetch_games_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "items": [
                {
                    "id": "game-001",
                    "title": "Cyber Odyssey: Neo-Veridia",
                    "slug": "cyber-odyssey-neo-veridia",
                    "price": 59.99,
                    "discount_percent": 15,
                    "rating": 4.8,
                    "reviews_count": 1420
                }
            ],
            "total": 1
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        games = self.client.fetch_games()
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["id"], "game-001")
        self.assertEqual(games[0]["title"], "Cyber Odyssey: Neo-Veridia")

    @patch("urllib.request.urlopen")
    def test_repository_merges_api_games(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "items": [
                {
                    "id": "remote-game-999",
                    "title": "Test Remote Game",
                    "slug": "test-remote-game",
                    "price": 29.99,
                    "discount_percent": 10,
                    "rating": 4.5,
                    "reviews_count": 50,
                    "genre": "Indie"
                }
            ],
            "total": 1
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        repo = JsonGameRepository("data/games.json", api_client=self.client)
        all_games = repo.get_all()
        ids = [g.id for g in all_games]
        self.assertIn("remote-game-999", ids)

    @patch("urllib.request.urlopen")
    def test_authentication_error_raised(self, mock_urlopen):
        from urllib.error import HTTPError
        from src.domain.exceptions import ApiAuthenticationError

        err = HTTPError(url="https://...", code=401, msg="Unauthorized", hdrs={}, fp=io.BytesIO(b"{}"))
        mock_urlopen.side_effect = err

        with self.assertRaises(ApiAuthenticationError):
            self.client.check_health(raise_on_error=True)

    @patch("urllib.request.urlopen")
    def test_connection_error_raised(self, mock_urlopen):
        from src.domain.exceptions import ApiConnectionError

        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        with self.assertRaises(ApiConnectionError):
            self.client.check_health(raise_on_error=True)

    @patch("urllib.request.urlopen")
    def test_sync_and_save_api_games(self, mock_urlopen):
        import tempfile
        import os
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "items": [
                {
                    "id": "persisted-game-101",
                    "title": "Saved Game",
                    "slug": "saved-game",
                    "price": 19.99,
                    "discount_percent": 0,
                    "genre": "Aventura"
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            repo = JsonGameRepository(temp_path, api_client=self.client)
            saved_games = repo.sync_and_save_api_games(raise_on_error=True)
            saved_ids = [g.id for g in saved_games]
            self.assertIn("persisted-game-101", saved_ids)

            # Verificar que físicamente quedó escrito en el archivo JSON
            with open(temp_path, "r", encoding="utf-8") as f:
                disk_data = json.load(f)
                disk_ids = [item["id"] for item in disk_data]
                self.assertIn("persisted-game-101", disk_ids)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
