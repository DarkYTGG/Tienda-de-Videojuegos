"""Unit tests for Domain Entities and Invariants (OOP Encapsulation & Validation)."""
import unittest
from src.domain.entities import (
    Game,
    CartItem,
    ShoppingCart,
    OrderItem,
    Order,
    generate_digital_key,
)
from src.domain.exceptions import (
    InvalidGameDataError,
    GameAlreadyInCartError,
    GameNotInCartError,
    InvalidOrderError,
)


class TestGameEntity(unittest.TestCase):
    """Verifies Game domain entity logic, price discounts, and invariants."""

    def test_game_creation_and_discount_calculation(self):
        game = Game(
            id="g1",
            title="Cyber Adventure",
            slug="cyber-adventure",
            developer="Neon Devs",
            publisher="PixelVault",
            release_date="2026-01-01",
            genre="Acción",
            price=60.0,
            discount_percent=25,
            rating=4.8,
            reviews_count=500
        )
        self.assertEqual(game.final_price, 45.0)
        self.assertEqual(game.savings, 15.0)
        self.assertTrue(game.is_on_sale)
        self.assertEqual(game.discount_badge, "-25%")
        self.assertEqual(game.formatted_original_price, "$60.00 USD")
        self.assertEqual(game.formatted_final_price, "$45.00 USD")
        self.assertIn("Extremadamente positivas", game.rating_summary)

    def test_free_game_pricing(self):
        free_game = Game(
            id="g2",
            title="Free Open Arena",
            slug="free-open-arena",
            developer="Indie Dev",
            publisher="Indie Dev",
            release_date="2026-02-01",
            genre="Indie",
            price=0.0,
            discount_percent=0
        )
        self.assertEqual(free_game.final_price, 0.0)
        self.assertEqual(free_game.formatted_final_price, "Gratis")
        self.assertFalse(free_game.is_on_sale)

    def test_game_validation_invalid_title(self):
        with self.assertRaises(InvalidGameDataError):
            Game(
                id="g3",
                title="   ",
                slug="empty-title",
                developer="Dev",
                publisher="Pub",
                release_date="2026-01-01",
                genre="Acción",
                price=20.0
            )

    def test_game_validation_negative_price(self):
        with self.assertRaises(InvalidGameDataError):
            Game(
                id="g4",
                title="Negative Price Game",
                slug="neg-price",
                developer="Dev",
                publisher="Pub",
                release_date="2026-01-01",
                genre="Acción",
                price=-10.0
            )

    def test_game_validation_invalid_discount(self):
        with self.assertRaises(InvalidGameDataError):
            Game(
                id="g5",
                title="Over Discounted Game",
                slug="over-disc",
                developer="Dev",
                publisher="Pub",
                release_date="2026-01-01",
                genre="Acción",
                price=50.0,
                discount_percent=150
            )

    def test_game_serialization_roundtrip(self):
        original = Game(
            id="g6",
            title="Roundtrip Title",
            slug="roundtrip-title",
            developer="Studio",
            publisher="Publisher",
            release_date="2026-03-01",
            genre="Terror",
            tags=["Terror", "Misterio"],
            price=29.99,
            discount_percent=10,
            rating=4.5,
            reviews_count=200
        )
        data = original.to_dict()
        reconstituted = Game.from_dict(data)
        self.assertEqual(reconstituted.id, original.id)
        self.assertEqual(reconstituted.title, original.title)
        self.assertEqual(reconstituted.final_price, original.final_price)
        self.assertEqual(reconstituted.tags, original.tags)


class TestShoppingCartEntity(unittest.TestCase):
    """Verifies ShoppingCart business logic, duplicate prevention, and totals calculation."""

    def setUp(self):
        self.game1 = Game(
            id="g1",
            title="Game One",
            slug="game-one",
            developer="Dev 1",
            publisher="Pub 1",
            release_date="2026-01-01",
            genre="Acción",
            price=50.0,
            discount_percent=20  # final: 40.0, savings: 10.0
        )
        self.game2 = Game(
            id="g2",
            title="Game Two",
            slug="game-two",
            developer="Dev 2",
            publisher="Pub 2",
            release_date="2026-01-01",
            genre="Rol / RPG",
            price=30.0,
            discount_percent=0  # final: 30.0, savings: 0.0
        )

    def test_cart_add_and_duplicate_prevention(self):
        cart = ShoppingCart()
        self.assertTrue(cart.is_empty)
        self.assertEqual(cart.item_count, 0)

        # Add first game
        cart.add_game(self.game1)
        self.assertEqual(cart.item_count, 1)
        self.assertTrue(cart.has_game("g1"))

        # Attempt to add same game again must raise GameAlreadyInCartError
        with self.assertRaises(GameAlreadyInCartError):
            cart.add_game(self.game1)

        self.assertEqual(cart.item_count, 1)

    def test_cart_remove_and_clear(self):
        cart = ShoppingCart()
        cart.add_game(self.game1)
        cart.add_game(self.game2)
        self.assertEqual(cart.item_count, 2)

        removed = cart.remove_game("g1")
        self.assertEqual(removed.game.id, "g1")
        self.assertEqual(cart.item_count, 1)
        self.assertFalse(cart.has_game("g1"))

        # Removing non-existent game raises GameNotInCartError
        with self.assertRaises(GameNotInCartError):
            cart.remove_game("g1")

        cart.clear()
        self.assertTrue(cart.is_empty)
        self.assertEqual(cart.item_count, 0)

    def test_cart_totals_calculation(self):
        cart = ShoppingCart()
        cart.add_game(self.game1)  # 50.0 original, 40.0 final, 10.0 discount
        cart.add_game(self.game2)  # 30.0 original, 30.0 final, 0.0 discount

        self.assertEqual(cart.subtotal, 80.0)
        self.assertEqual(cart.total_discount, 10.0)
        self.assertEqual(cart.total, 70.0)
        self.assertEqual(cart.formatted_total, "$70.00 USD")


class TestOrderEntity(unittest.TestCase):
    """Verifies Order entity, activation key generation, and validation."""

    def test_digital_key_format(self):
        key = generate_digital_key()
        self.assertTrue(key.startswith("PIXEL-"))
        parts = key.split("-")
        self.assertEqual(len(parts), 5)

    def test_order_validation_success(self):
        item = OrderItem(game_id="g1", game_title="Game One", price_paid=40.0)
        order = Order(
            id="PV-TEST-1234",
            customer_name="Estudiante Universitario",
            customer_email="estudiante@universidad.edu",
            payment_method="Saldo PixelVault",
            items=[item],
            subtotal=50.0,
            total_discount=10.0,
            total=40.0
        )
        order.validate()
        self.assertEqual(len(order.items), 1)

    def test_order_validation_invalid_name(self):
        item = OrderItem(game_id="g1", game_title="Game One", price_paid=40.0)
        order = Order(
            id="PV-TEST-1234",
            customer_name="AB",  # < 3 chars
            customer_email="estudiante@universidad.edu",
            payment_method="Saldo PixelVault",
            items=[item],
            subtotal=50.0,
            total_discount=10.0,
            total=40.0
        )
        with self.assertRaises(InvalidOrderError):
            order.validate()

    def test_order_validation_invalid_email(self):
        item = OrderItem(game_id="g1", game_title="Game One", price_paid=40.0)
        order = Order(
            id="PV-TEST-1234",
            customer_name="Estudiante Universitario",
            customer_email="not-an-email",
            payment_method="Saldo PixelVault",
            items=[item],
            subtotal=50.0,
            total_discount=10.0,
            total=40.0
        )
        with self.assertRaises(InvalidOrderError):
            order.validate()

    def test_order_validation_empty_items(self):
        order = Order(
            id="PV-TEST-1234",
            customer_name="Estudiante Universitario",
            customer_email="estudiante@universidad.edu",
            payment_method="Saldo PixelVault",
            items=[],
            subtotal=0.0,
            total_discount=0.0,
            total=0.0
        )
        with self.assertRaises(InvalidOrderError):
            order.validate()


if __name__ == "__main__":
    unittest.main()
