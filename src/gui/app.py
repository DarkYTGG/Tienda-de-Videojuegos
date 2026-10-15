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
from .components.header import StoreHeaderComponent
from .components.cart_drawer import CartDrawerComponent
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
        self.drawer_container = ft.Container(visible=False, expand=True)
        self.root_stack: Optional[ft.Stack] = None
        self.is_cart_drawer_open: bool = False
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

    def _refresh_header(self) -> None:
        """Rebuilds the custom cyberpunk top navigation bar with dynamic counters and active route."""
        header_comp = StoreHeaderComponent(
            navigate_fn=self.navigate,
            cart_count=self.cart.item_count,
            current_route=self.current_route,
            on_search_submit=self._handle_header_search,
            on_cart_click=self.toggle_cart_drawer
        )
        self.header_container.content = header_comp.build()

    def _build_cart_drawer(self) -> Optional[ft.Control]:
        """Builds the offcanvas sliding drawer component."""
        drawer_comp = CartDrawerComponent(
            cart=self.cart,
            is_open=self.is_cart_drawer_open,
            on_close=self.close_cart_drawer,
            on_remove_item=self.remove_from_cart,
            on_checkout=self._handle_drawer_checkout,
            on_view_cart=self._handle_drawer_view_cart,
            on_catalog=self._handle_drawer_catalog
        )
        return drawer_comp.build()

    def open_cart_drawer(self) -> None:
        """Slides open the offcanvas cart drawer overlay."""
        self.is_cart_drawer_open = True
        self.drawer_container.visible = True
        self.drawer_container.content = self._build_cart_drawer()
        self._refresh_header()
        if self.page:
            self.page.update()

    def close_cart_drawer(self) -> None:
        """Closes the offcanvas cart drawer overlay."""
        self.is_cart_drawer_open = False
        self.drawer_container.visible = False
        self.drawer_container.content = None
        self._refresh_header()
        if self.page:
            self.page.update()

    def toggle_cart_drawer(self) -> None:
        """Toggles the visibility state of the offcanvas cart drawer."""
        if self.is_cart_drawer_open:
            self.close_cart_drawer()
        else:
            self.open_cart_drawer()

    def remove_from_cart(self, game_id: str) -> None:
        """Removes a video game line item, updating drawer, header badge, and underlying view."""
        try:
            self.cart_manager.remove_game(game_id)
            self.notify("Videojuego eliminado del carrito", "info")
            # Refresh drawer contents
            self.drawer_container.content = self._build_cart_drawer()
            # Refresh header cart counter
            self._refresh_header()
            # Refresh underlying view so card buttons reflect removed status
            view_instance = self._create_view(self.current_route, self.route_params)
            if view_instance:
                self.content_container.content = view_instance.build()
            if self.page:
                self.page.update()
        except Exception as e:
            self.notify(str(e), "warning")

    def _handle_drawer_checkout(self) -> None:
        """Navigates from drawer directly to checkout."""
        self.close_cart_drawer()
        self.navigate("checkout")

    def _handle_drawer_view_cart(self) -> None:
        """Navigates from drawer to the full-page detailed cart view."""
        self.close_cart_drawer()
        self.navigate("cart")

    def _handle_drawer_catalog(self) -> None:
        """Navigates from empty drawer to the full catalog."""
        self.close_cart_drawer()
        self.navigate("catalog")

    def _handle_header_search(self, query: str) -> None:
        """Routes header search queries directly to the catalog view."""
        self.navigate("catalog", {"search": query})

    def _create_view(self, route_name: str, params: Dict[str, Any]):
        """Polymorphic factory instantiating the view for the requested route."""
        if route_name == "home":
            return StoreView(
                self.page,
                self.navigate,
                self.list_games_uc,
                self.cart_manager,
                notify_fn=self.notify,
                on_cart_open=self.open_cart_drawer
            )
        elif route_name == "catalog":
            return CatalogView(
                self.page,
                self.navigate,
                self.search_filter_uc,
                self.list_games_uc,
                self.cart_manager,
                initial_params=params,
                notify_fn=self.notify,
                on_cart_open=self.open_cart_drawer
            )
        elif route_name == "detail":
            slug = params.get("slug", "")
            return GameDetailView(
                self.page,
                self.navigate,
                self.get_game_uc,
                self.cart_manager,
                game_slug=slug,
                notify_fn=self.notify,
                on_cart_open=self.open_cart_drawer
            )
        elif route_name == "cart":
            return CartView(
                self.page,
                self.navigate,
                self.cart_manager,
                self.notify
            )
        elif route_name == "checkout":
            return CheckoutView(
                self.page,
                self.navigate,
                self.cart_manager,
                self.checkout_uc,
                self.notify
            )
        elif route_name == "confirmation":
            order = params.get("order")
            return OrderConfirmationView(
                self.page,
                self.navigate,
                order=order,
                notify_fn=self.notify
            )
        elif route_name == "orders":
            return OrdersHistoryView(
                self.page,
                self.navigate,
                self.get_orders_uc,
                self.notify
            )
        return None

    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Centralized reactive navigation router implementing polymorphism across views."""
        self.current_route = route_name
        self.route_params = params or {}

        # 1. Update Custom Header with current route & cart counter
        self._refresh_header()

        # 2. Polymorphic View Instantiation
        view_instance = self._create_view(route_name, self.route_params)

        # 3. Mount view content
        if view_instance:
            self.content_container.content = view_instance.build()

        # 4. If drawer is currently open, re-render its content
        if self.is_cart_drawer_open:
            self.drawer_container.content = self._build_cart_drawer()

        if self.page:
            self.page.update()

    def main(self, page: ft.Page) -> None:
        """Flet session initialization callback."""
        self.page = page
        self.page.title = "PixelVault — Tienda Digital de Videojuegos | Programación IV"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = BG_DARK
        self.page.padding = 0

        # Construct primary application layout: Custom Header + View Content Container
        main_column = ft.Column(
            controls=[
                self.header_container,
                self.content_container,
            ],
            spacing=0,
            expand=True
        )

        # Root Stack hosting base layout and sliding offcanvas drawer overlay
        self.root_stack = ft.Stack(
            controls=[
                main_column,
                self.drawer_container,
            ],
            expand=True
        )

        # Attach Root Stack to Page
        self.page.add(self.root_stack)

        # Navigate to initial view
        self.navigate("home")
