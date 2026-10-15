"""Unit tests for Application Layer Use Cases."""
import tempfile
import os
import unittest
from typing import List, Optional

from src.domain.entities import Game, ShoppingCart
from src.domain.ports import GameRepository, OrderRepository
from src.domain.exceptions import GameNotFoundError, GameAlreadyInCartError
from src.application.dtos import GameFilterDTO, CheckoutRequestDTO
from src.application.use_cases import (
    ListGamesUseCase,
    SearchAndFilterGamesUseCase,
    GetGameDetailUseCase,
    ManageCartUseCase,
    CheckoutUseCase,
    GetOrdersUseCase,
)
from src.infrastructure.repositories import JsonOrderRepository


class MockGameRepository(GameRepository):
    """In-memory mock repository implementing the GameRepository port for testing."""

    def __init__(self, games: List[Game]):
        self._games = games

    def get_all(self) -> List[Game]:
        return list(self._games)

    def get_by_id(self, game_id: str) -> Optional[Game]:
        for g in self._games:
            if g.id == game_id:
                return g
        return None

    def get_by_slug(self, slug: str) -> Optional[Game]:
        for g in self._games:
            if g.slug.lower() == slug.lower():
                return g
        return None

    def get_featured(self) -> List[Game]:
        return [g for g in self._games if g.is_featured]

    def get_on_sale(self) -> List[Game]:
        return [g for g in self._games if g.is_on_sale]

    def get_indie(self) -> List[Game]:
        return [g for g in self._games if g.is_indie]

    def get_new_releases(self) -> List[Game]:
        return [g for g in self._games if g.is_new]

    def get_genres(self) -> List[str]:
        return sorted(list(set(g.genre for g in self._games)))


class TestUseCases(unittest.TestCase):
    """Tests all application use cases using decoupled mock and temporary repositories."""

    def setUp(self):
        self.sample_games = [
            Game(
                id="g1",
                title="Neon Cyberpunk",
                slug="neon-cyberpunk",
                developer="Neon Dev",
                publisher="Pub A",
                release_date="2026-01-01",
                genre="Rol / RPG",
                tags=["Cyberpunk", "RPG"],
                price=50.0,
                discount_percent=20,  # final 40.0
                rating=4.8,
                reviews_count=1000,
                is_featured=True,
                is_new=True,
                is_indie=False
            ),
            Game(
                id="g2",
                title="Hollow Depths",
                slug="hollow-depths",
                developer="Ghost Dev",
                publisher="Pub B",
                release_date="2025-10-01",
                genre="Terror",
                tags=["Terror", "Misterio"],
                price=20.0,
                discount_percent=50,  # final 10.0
                rating=4.5,
                reviews_count=400,
                is_featured=False,
                is_new=False,
                is_indie=True
            ),
            Game(
                id="g3",
                title="Aetheria Islands",
                slug="aetheria-islands",
                developer="Cloud Dev",
                publisher="Pub C",
                release_date="2026-02-01",
                genre="Aventura",
                tags=["Aventura", "Exploración"],
                price=30.0,
                discount_percent=0,  # final 30.0
                rating=4.9,
                reviews_count=2000,
                is_featured=True,
                is_new=True,
                is_indie=True
            )
        ]
        self.mock_repo = MockGameRepository(self.sample_games)
        self.list_uc = ListGamesUseCase(self.mock_repo)
        self.search_filter_uc = SearchAndFilterGamesUseCase(self.mock_repo)
        self.detail_uc = GetGameDetailUseCase(self.mock_repo)

        # Temp order repo for checkout tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_orders_path = os.path.join(self.temp_dir.name, "orders.json")
        self.order_repo = JsonOrderRepository(self.temp_orders_path)
        self.checkout_uc = CheckoutUseCase(self.order_repo)
        self.get_orders_uc = GetOrdersUseCase(self.order_repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_games_sections(self):
        all_games = self.list_uc.get_all()
        self.assertEqual(len(all_games), 3)

        featured = self.list_uc.get_featured()
        self.assertEqual(len(featured), 2)

        on_sale = self.list_uc.get_on_sale()
        self.assertEqual(len(on_sale), 2)

        indie = self.list_uc.get_indie()
        self.assertEqual(len(indie), 2)

        genres = self.list_uc.get_genres()
        self.assertEqual(genres, ["Aventura", "Rol / RPG", "Terror"])

    def test_search_and_filter_by_title(self):
        # Match title
        results = self.search_filter_uc.execute(GameFilterDTO(search_query="Cyber"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Neon Cyberpunk")

        # Match tag
        results = self.search_filter_uc.execute(GameFilterDTO(search_query="Misterio"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Hollow Depths")

    def test_filter_by_genre_and_sales(self):
        results = self.search_filter_uc.execute(GameFilterDTO(genre="Terror"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].genre, "Terror")

        # Only sales
        sales_results = self.search_filter_uc.execute(GameFilterDTO(only_sales=True))
        self.assertEqual(len(sales_results), 2)
        for g in sales_results:
            self.assertTrue(g.is_on_sale)

    def test_filter_by_price_and_sorting(self):
        # Max price 25
        cheap_results = self.search_filter_uc.execute(GameFilterDTO(max_price=25.0))
        self.assertEqual(len(cheap_results), 1)
        self.assertEqual(cheap_results[0].id, "g2")  # Hollow depths final price is 10.0

        # Sort price asc
        sorted_asc = self.search_filter_uc.execute(GameFilterDTO(sort_by="precio_menor"))
        self.assertEqual(sorted_asc[0].id, "g2")  # 10.0
        self.assertEqual(sorted_asc[-1].id, "g1")  # 40.0

        # Sort price desc
        sorted_desc = self.search_filter_uc.execute(GameFilterDTO(sort_by="precio_mayor"))
        self.assertEqual(sorted_desc[0].id, "g1")  # 40.0
        self.assertEqual(sorted_desc[-1].id, "g2")  # 10.0

    def test_get_game_detail(self):
        game = self.detail_uc.execute_by_slug("neon-cyberpunk")
        self.assertEqual(game.id, "g1")

        game_by_id = self.detail_uc.execute_by_id("g2")
        self.assertEqual(game_by_id.slug, "hollow-depths")

        with self.assertRaises(GameNotFoundError):
            self.detail_uc.execute_by_slug("non-existent-game")

    def test_manage_cart_use_case(self):
        cart = ShoppingCart()
        cart_uc = ManageCartUseCase(cart)

        cart_uc.add_game(self.sample_games[0])
        self.assertTrue(cart_uc.has_game("g1"))
        self.assertEqual(cart_uc.cart.item_count, 1)

        # Duplicate
        with self.assertRaises(GameAlreadyInCartError):
            cart_uc.add_game(self.sample_games[0])

        cart_uc.remove_game("g1")
        self.assertFalse(cart_uc.has_game("g1"))
        self.assertEqual(cart_uc.cart.item_count, 0)

    def test_checkout_use_case_success(self):
        cart = ShoppingCart()
        cart.add_game(self.sample_games[0])  # final 40.0
        cart.add_game(self.sample_games[1])  # final 10.0

        req = CheckoutRequestDTO(
            customer_name="Estudiante Yoher",
            customer_email="estudiante@universidad.edu",
            payment_method="Saldo PixelVault"
        )

        response = self.checkout_uc.execute(cart, req)
        self.assertTrue(response.success)
        self.assertIsNotNone(response.order)
        self.assertEqual(response.order.total, 50.0)
        self.assertEqual(len(response.order.items), 2)
        self.assertTrue(response.order.items[0].digital_key.startswith("PIXEL-"))

        # Cart must be cleared after checkout
        self.assertTrue(cart.is_empty)

        # Order must be persisted
        saved_orders = self.get_orders_uc.get_all()
        self.assertEqual(len(saved_orders), 1)
        self.assertEqual(saved_orders[0].id, response.order.id)

    def test_checkout_use_case_empty_cart(self):
        empty_cart = ShoppingCart()
        req = CheckoutRequestDTO(
            customer_name="Estudiante",
            customer_email="estudiante@correo.com"
        )
        response = self.checkout_uc.execute(empty_cart, req)
        self.assertFalse(response.success)
        self.assertIn("vacío", response.message.lower())

    def test_checkout_use_case_invalid_data(self):
        cart = ShoppingCart()
        cart.add_game(self.sample_games[0])
        req = CheckoutRequestDTO(
            customer_name="A",  # too short
            customer_email="invalid-email"
        )
        response = self.checkout_uc.execute(cart, req)
        self.assertFalse(response.success)
        self.assertIn("customer_name", response.errors)
        self.assertIn("customer_email", response.errors)


if __name__ == "__main__":
    unittest.main()
