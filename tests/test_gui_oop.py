"""Unit tests verifying Object-Oriented Programming (OOP) structure of GUI views and components."""
import os
import unittest

from src.infrastructure.repositories import JsonGameRepository, JsonOrderRepository
from src.domain.entities import ShoppingCart, Order, OrderItem
from src.application.use_cases import (
    ListGamesUseCase,
    SearchAndFilterGamesUseCase,
    GetGameDetailUseCase,
    ManageCartUseCase,
    CheckoutUseCase,
    GetOrdersUseCase,
)
from src.gui.components import (
    GameCardComponent,
    FeaturedHeroBannerComponent,
    FilterBarComponent,
    StoreHeaderComponent,
    StoreFooterComponent,
)
from src.gui.views import (
    BaseView,
    StoreView,
    CatalogView,
    GameDetailView,
    CartView,
    CheckoutView,
    OrderConfirmationView,
    OrdersHistoryView,
)
from src.gui.app import PixelVaultApp


class TestFletGUIOOPStructure(unittest.TestCase):
    """Verifies that all GUI components and views follow OOP principles, inheritance, and clean DI."""

    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.games_file = os.path.join(base_dir, "data", "games.json")
        self.orders_file = os.path.join(base_dir, "data", "orders.json")

        self.game_repo = JsonGameRepository(self.games_file)
        self.order_repo = JsonOrderRepository(self.orders_file)

        self.cart = ShoppingCart()

        self.list_uc = ListGamesUseCase(self.game_repo)
        self.search_filter_uc = SearchAndFilterGamesUseCase(self.game_repo)
        self.get_game_uc = GetGameDetailUseCase(self.game_repo)
        self.cart_manager = ManageCartUseCase(self.cart)
        self.checkout_uc = CheckoutUseCase(self.order_repo)
        self.get_orders_uc = GetOrdersUseCase(self.order_repo)

        self.games = self.list_uc.get_all()

    def test_components_build(self):
        game = self.games[0]

        # 1. GameCardComponent
        card_comp = GameCardComponent(
            game=game,
            on_detail=lambda g: None,
            on_add_cart=lambda g: None,
            is_in_cart=False
        )
        card_control = card_comp.build()
        self.assertIsNotNone(card_control)

        # 2. FeaturedHeroBannerComponent
        hero_comp = FeaturedHeroBannerComponent(
            game=game,
            on_detail=lambda g: None,
            on_add_cart=lambda g: None,
            is_in_cart=False
        )
        hero_control = hero_comp.build()
        self.assertIsNotNone(hero_control)

        # 3. StoreHeaderComponent
        header_comp = StoreHeaderComponent(
            navigate_fn=lambda r, p: None,
            cart_count=2,
            current_route="home"
        )
        header_control = header_comp.build()
        self.assertIsNotNone(header_control)

        # 4. StoreFooterComponent
        footer_comp = StoreFooterComponent()
        footer_control = footer_comp.build()
        self.assertIsNotNone(footer_control)

    def test_views_inheritance_and_polymorphic_build(self):
        # 1. StoreView
        store_view = StoreView(
            page=None,
            navigate_fn=lambda r, p: None,
            list_games_uc=self.list_uc,
            cart_manager=self.cart_manager
        )
        self.assertIsInstance(store_view, BaseView)
        self.assertIsNotNone(store_view.build())

        # 2. CatalogView
        catalog_view = CatalogView(
            page=None,
            navigate_fn=lambda r, p: None,
            search_filter_uc=self.search_filter_uc,
            list_games_uc=self.list_uc,
            cart_manager=self.cart_manager
        )
        self.assertIsInstance(catalog_view, BaseView)
        self.assertIsNotNone(catalog_view.build())

        # 3. GameDetailView (Valid slug)
        detail_view = GameDetailView(
            page=None,
            navigate_fn=lambda r, p: None,
            get_game_uc=self.get_game_uc,
            cart_manager=self.cart_manager,
            game_slug=self.games[0].slug
        )
        self.assertIsInstance(detail_view, BaseView)
        self.assertIsNotNone(detail_view.build())

        # 4. GameDetailView (Non-existent slug)
        invalid_detail = GameDetailView(
            page=None,
            navigate_fn=lambda r, p: None,
            get_game_uc=self.get_game_uc,
            cart_manager=self.cart_manager,
            game_slug="non-existent-game-slug"
        )
        self.assertIsNotNone(invalid_detail.build())

        # 5. CartView (Empty state)
        cart_view_empty = CartView(
            page=None,
            navigate_fn=lambda r, p: None,
            cart_manager=self.cart_manager
        )
        self.assertIsInstance(cart_view_empty, BaseView)
        self.assertIsNotNone(cart_view_empty.build())

        # 6. CartView (With items)
        self.cart_manager.add_game(self.games[0])
        cart_view_items = CartView(
            page=None,
            navigate_fn=lambda r, p: None,
            cart_manager=self.cart_manager
        )
        self.assertIsNotNone(cart_view_items.build())

        # 7. CheckoutView
        checkout_view = CheckoutView(
            page=None,
            navigate_fn=lambda r, p: None,
            cart_manager=self.cart_manager,
            checkout_uc=self.checkout_uc
        )
        self.assertIsInstance(checkout_view, BaseView)
        self.assertIsNotNone(checkout_view.build())

        # 8. OrderConfirmationView
        mock_order = Order(
            id="PV-CONFIRM-TEST",
            customer_name="Test Student",
            customer_email="student@univ.edu",
            payment_method="Saldo PixelVault",
            items=[OrderItem(game_id="g1", game_title="Game 1", price_paid=19.99)],
            subtotal=29.99,
            total_discount=10.0,
            total=19.99
        )
        confirm_view = OrderConfirmationView(
            page=None,
            navigate_fn=lambda r, p: None,
            order=mock_order
        )
        self.assertIsInstance(confirm_view, BaseView)
        self.assertIsNotNone(confirm_view.build())

        # 9. OrdersHistoryView
        orders_view = OrdersHistoryView(
            page=None,
            navigate_fn=lambda r, p: None,
            get_orders_uc=self.get_orders_uc
        )
        self.assertIsInstance(orders_view, BaseView)
        self.assertIsNotNone(orders_view.build())

    def test_app_controller_initialization(self):
        app = PixelVaultApp(
            games_file=self.games_file,
            orders_file=self.orders_file
        )
        self.assertEqual(app.current_route, "home")
        self.assertEqual(app.cart.item_count, 0)
        self.assertIsNotNone(app.game_repo)
        self.assertIsNotNone(app.order_repo)


if __name__ == "__main__":
    unittest.main()
