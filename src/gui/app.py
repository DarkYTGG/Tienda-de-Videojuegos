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
from .theme import (
    BG_DARK,
    BG_HEADER,
    ACCENT_PURPLE,
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    safe_icon,
)
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
                        safe_icon("check_circle") if message_type == "success" else safe_icon("info"),
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

    def _build_appbar(self) -> ft.AppBar:
        """Constructs Flutter Web native AppBar with branding, section navigation, search, and dynamic cart badge."""
        cart_badge_text = str(self.cart.item_count)

        return ft.AppBar(
            leading=ft.Container(
                content=ft.Icon(safe_icon("sports_esports"), color=ACCENT_PURPLE, size=24),
                padding=ft.Padding(left=12, right=0, top=0, bottom=0),
                on_click=lambda _: self.navigate("home"),
            ),
            title=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("PIXEL", size=20, weight=ft.FontWeight.W_900, color=TEXT_PRIMARY),
                        ft.Text("VAULT", size=20, weight=ft.FontWeight.W_900, color=ACCENT_PURPLE),
                    ],
                    spacing=0,
                    tight=True
                ),
                on_click=lambda _: self.navigate("home"),
                ink=True
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text(
                        "Tienda",
                        size=13,
                        weight=ft.FontWeight.BOLD if self.current_route == "home" else ft.FontWeight.W_500,
                        color=ACCENT_CYAN if self.current_route == "home" else TEXT_SECONDARY
                    ),
                    on_click=lambda _: self.navigate("home")
                ),
                ft.TextButton(
                    content=ft.Text(
                        "Catálogo Completo",
                        size=13,
                        weight=ft.FontWeight.BOLD if self.current_route == "catalog" and not self.route_params.get("only_indie") else ft.FontWeight.W_500,
                        color=ACCENT_CYAN if self.current_route == "catalog" and not self.route_params.get("only_indie") else TEXT_SECONDARY
                    ),
                    on_click=lambda _: self.navigate("catalog")
                ),
                ft.TextButton(
                    content=ft.Text(
                        "Zona Indie",
                        size=13,
                        weight=ft.FontWeight.BOLD if self.current_route == "catalog" and self.route_params.get("only_indie") else ft.FontWeight.W_500,
                        color=ACCENT_CYAN if self.current_route == "catalog" and self.route_params.get("only_indie") else TEXT_SECONDARY
                    ),
                    on_click=lambda _: self.navigate("catalog", {"only_indie": True})
                ),
                ft.TextButton(
                    content=ft.Text(
                        "Mis Pedidos",
                        size=13,
                        weight=ft.FontWeight.BOLD if self.current_route == "orders" else ft.FontWeight.W_500,
                        color=ACCENT_CYAN if self.current_route == "orders" else TEXT_SECONDARY
                    ),
                    on_click=lambda _: self.navigate("orders")
                ),
                ft.IconButton(
                    icon=safe_icon("search"),
                    icon_color=TEXT_SECONDARY,
                    tooltip="Buscar en catálogo",
                    on_click=lambda _: self.navigate("catalog")
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(safe_icon("shopping_cart"), size=18, color="#FFFFFF"),
                            ft.Text("Carrito", size=13, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            ft.Container(
                                content=ft.Text(cart_badge_text, size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                bgcolor=ACCENT_GREEN if self.cart.item_count > 0 else "#475569",
                                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                border_radius=10
                            )
                        ],
                        spacing=6,
                        tight=True
                    ),
                    bgcolor=ACCENT_PURPLE,
                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                    border_radius=8,
                    margin=ft.Margin(left=4, right=16, top=0, bottom=0),
                    on_click=lambda _: self.navigate("cart"),
                    ink=True
                )
            ],
            bgcolor=BG_HEADER,
            center_title=False
        )

    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Centralized reactive navigation router implementing polymorphism across views."""
        self.current_route = route_name
        self.route_params = params or {}

        # 1. Update AppBar with current route & cart counter
        if self.page:
            self.page.appbar = self._build_appbar()

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

        # Attach AppBar
        self.page.appbar = self._build_appbar()

        # Attach dynamic content area directly to page
        self.page.add(self.content_container)

        # Navigate to initial view
        self.navigate("home")
