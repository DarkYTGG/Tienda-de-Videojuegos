"""Main GUI Controller and Application Container in Flet adhering to OOP principles."""
import os
from typing import Optional, Dict, Any
import flet as ft

from ..infrastructure.repositories import JsonGameRepository, JsonOrderRepository
from ..domain.entities import ShoppingCart
from ..application.use_cases import (
    ListGamesUseCase,
    SearchAndFilterGamesUseCase,
    GetGameDetailUseCase,
    ManageCartUseCase,
    CheckoutUseCase,
    GetOrdersUseCase,
)
from .theme import BG_DARK, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_RED
from .components.header import StoreHeaderComponent
from .views.store_view import StoreView
from .views.catalog_view import CatalogView
from .views.detail_view import GameDetailView
from .views.cart_view import CartView
from .views.checkout_view import CheckoutView
from .views.confirmation_view import OrderConfirmationView
from .views.orders_view import OrdersHistoryView


class PixelVaultApp:
    """Encapsulates the state, navigation, lifecycle, and dependency injection of the PixelVault Web GUI."""

    def __init__(self, games_file: str, orders_file: str):
        # 1. Infrastructure Repositories
        self.game_repo = JsonGameRepository(games_file)
        self.order_repo = JsonOrderRepository(orders_file)

        # 2. Domain Entities
        self.cart = ShoppingCart()

        # 3. Application Use Cases
        self.list_games_uc = ListGamesUseCase(self.game_repo)
        self.search_filter_uc = SearchAndFilterGamesUseCase(self.game_repo)
        self.get_game_uc = GetGameDetailUseCase(self.game_repo)
        self.cart_manager = ManageCartUseCase(self.cart)
        self.checkout_uc = CheckoutUseCase(self.order_repo)
        self.get_orders_uc = GetOrdersUseCase(self.order_repo)

        # 4. GUI & Routing State
        self.page: Optional[ft.Page] = None
        self.header_container = ft.Container()
        self.content_container = ft.Container(expand=True)
        self.current_route: str = "home"
        self.route_params: Dict[str, Any] = {}

    def notify(self, message: str, message_type: str = "info") -> None:
        """Displays responsive feedback snackbar messages."""
        if not self.page:
            return

        bg_color = {
            "success": "#065F46",
            "warning": "#9A3412",
            "error": "#991B1B",
            "info": "#1E293B"
        }.get(message_type, "#1E293B")

        snack = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        "check_circle" if message_type == "success" else "info",
                        color="#FFFFFF",
                        size=20
                    ),
                    ft.Text(message, size=13, weight=ft.FontWeight.W_500, color="#FFFFFF")
                ],
                spacing=8
            ),
            bgcolor=bg_color,
            duration=3500,
            behavior=ft.SnackBarBehavior.FLOATING
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    def _update_header(self) -> None:
        """Refreshes the top header bar with current route and cart badge counter."""
        header_comp = StoreHeaderComponent(
            navigate_fn=self.navigate,
            cart_count=self.cart.item_count,
            current_route=self.current_route,
            on_search_submit=lambda q: self.navigate("catalog", {"search": q})
        )
        self.header_container.content = header_comp.build()

    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Centralized reactive navigation router implementing polymorphism across views."""
        self.current_route = route_name
        self.route_params = params or {}

        # 1. Update header with current route & cart count
        self._update_header()

        # 2. Polymorphic View Instantiation
        view_instance = None
        if route_name == "home":
            view_instance = StoreView(
                self.page,
                self.navigate,
                self.list_games_uc,
                self.cart_manager,
                self.notify
            )
        elif route_name == "catalog":
            view_instance = CatalogView(
                self.page,
                self.navigate,
                self.search_filter_uc,
                self.list_games_uc,
                self.cart_manager,
                initial_params=self.route_params,
                notify=self.notify
            )
        elif route_name == "detail":
            slug = self.route_params.get("slug", "")
            view_instance = GameDetailView(
                self.page,
                self.navigate,
                self.get_game_uc,
                self.cart_manager,
                game_slug=slug,
                notify_fn=self.notify
            )
        elif route_name == "cart":
            view_instance = CartView(
                self.page,
                self.navigate,
                self.cart_manager,
                self.notify
            )
        elif route_name == "checkout":
            view_instance = CheckoutView(
                self.page,
                self.navigate,
                self.cart_manager,
                self.checkout_uc,
                self.notify
            )
        elif route_name == "confirmation":
            order = self.route_params.get("order")
            view_instance = OrderConfirmationView(
                self.page,
                self.navigate,
                order=order,
                notify_fn=self.notify
            )
        elif route_name == "orders":
            view_instance = OrdersHistoryView(
                self.page,
                self.navigate,
                self.get_orders_uc,
                self.notify
            )

        # 3. Mount view content
        if view_instance:
            self.content_container.content = view_instance.build()
            if self.page:
                self.page.update()

    def main(self, page: ft.Page) -> None:
        """Flet session initialization callback."""
        self.page = page
        self.page.title = "PixelVault — Tienda Digital de Videojuegos | Programación IV"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = BG_DARK
        self.page.padding = 0

        # Build app layout
        self._update_header()

        layout = ft.Column(
            controls=[
                self.header_container,
                self.content_container
            ],
            spacing=0,
            expand=True
        )

        self.page.add(layout)
        self.navigate("home")
