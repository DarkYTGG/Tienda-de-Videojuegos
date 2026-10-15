"""Unit tests for Infrastructure Repositories (JSON file storage, thread safety, fault tolerance)."""
import json
import os
import tempfile
import unittest

from src.domain.entities import Order, OrderItem
from src.infrastructure.repositories import JsonGameRepository, JsonOrderRepository


class TestJsonRepositories(unittest.TestCase):
    """Verifies persistence, file recovery, and repository operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.games_file = os.path.join(self.temp_dir.name, "games.json")
        self.orders_file = os.path.join(self.temp_dir.name, "orders.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_game_repository_creates_seed_file_when_missing(self):
        self.assertFalse(os.path.exists(self.games_file))
        repo = JsonGameRepository(self.games_file)
        self.assertTrue(os.path.exists(self.games_file))

        games = repo.get_all()
        self.assertGreaterEqual(len(games), 15)

        # Check genres
        genres = repo.get_genres()
        self.assertIn("Acción", genres)
        self.assertIn("Rol / RPG", genres)

        # Check lookup
        first = games[0]
        found = repo.get_by_id(first.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, first.title)

        found_slug = repo.get_by_slug(first.slug)
        self.assertIsNotNone(found_slug)
        self.assertEqual(found_slug.id, first.id)

    def test_game_repository_handles_corrupted_json(self):
        # Write corrupted JSON
        with open(self.games_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json corrupted text ]]]")

        repo = JsonGameRepository(self.games_file)
        # Should fall back to SEED_GAMES instead of crashing
        games = repo.get_all()
        self.assertGreaterEqual(len(games), 15)

    def test_order_repository_persistence_and_retrieval(self):
        self.assertFalse(os.path.exists(self.orders_file))
        repo = JsonOrderRepository(self.orders_file)
        self.assertTrue(os.path.exists(self.orders_file))

        # Initially empty
        self.assertEqual(len(repo.get_all()), 0)

        # Save order
        item = OrderItem(game_id="g1", game_title="Title One", price_paid=25.0)
        order = Order(
            id="PV-TEST-ORDER-1",
            customer_name="Juan Perez",
            customer_email="juan@correo.com",
            payment_method="Saldo PixelVault",
            items=[item],
            subtotal=30.0,
            total_discount=5.0,
            total=25.0
        )
        saved = repo.save(order)
        self.assertEqual(saved.id, "PV-TEST-ORDER-1")

        # Read back
        orders = repo.get_all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].customer_name, "Juan Perez")
        self.assertEqual(orders[0].items[0].game_title, "Title One")

        # Find by ID
        found = repo.get_by_id("PV-TEST-ORDER-1")
        self.assertIsNotNone(found)
        self.assertEqual(found.customer_email, "juan@correo.com")

        not_found = repo.get_by_id("NON-EXISTENT")
        self.assertIsNone(not_found)

    def test_order_repository_handles_corrupt_file(self):
        with open(self.orders_file, "w", encoding="utf-8") as f:
            f.write("corrupted content")

        repo = JsonOrderRepository(self.orders_file)
        self.assertEqual(repo.get_all(), [])


if __name__ == "__main__":
    unittest.main()
