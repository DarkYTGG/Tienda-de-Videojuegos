"""Top application bar and navigation header component."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from ..theme import (
    BG_HEADER,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    ACCENT_GREEN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    BORDER_COLOR,
    BG_INPUT,
    safe_icon,
)


class StoreHeaderComponent:
    """Header bar providing brand identity, section routing, quick search, and cart counter."""

    def __init__(
        self,
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        cart_count: int = 0,
        current_route: str = "home",
        on_search_submit: Optional[Callable[[str], None]] = None,
        on_cart_click: Optional[Callable[[], None]] = None
    ):
        self._navigate = navigate_fn
        self._cart_count = cart_count
        self._current_route = current_route
        self._on_search_submit = on_search_submit
        self._on_cart_click = on_cart_click
        self._search_field = ft.TextField(
            hint_text="Buscar juegos, géneros o desarrolladores...",
            text_size=12,
            height=38,
            content_padding=ft.Padding(left=12, right=12, top=0, bottom=0),
            border_radius=8,
            border_color="#1F293D",
            bgcolor="#0D1322",
            color=TEXT_PRIMARY,
            hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            prefix_icon=ft.Icons.SEARCH,
            on_submit=self._handle_search,
            expand=True
        )

    def _handle_search(self, e):
        query = self._search_field.value or ""
        if self._on_search_submit:
            self._on_search_submit(query)
        else:
            self._navigate("catalog", {"search": query})

    def _build_nav_link(self, label: str, route_name: str, params: Optional[Dict[str, Any]] = None, icon: Optional[str] = None) -> ft.Control:
        is_active = self._current_route == route_name and not params
        text_color = "#38BDF8" if is_active else TEXT_SECONDARY
        font_weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500

        controls = []
        if icon:
            controls.append(ft.Icon(safe_icon(icon), size=16, color=text_color))
        controls.append(ft.Text(label, size=13, weight=font_weight, color=text_color))

        return ft.Container(
            content=ft.Row(controls=controls, spacing=6, tight=True),
            padding=ft.Padding(left=12, right=12, top=7, bottom=7),
            border_radius=6,
            bgcolor="rgba(6, 182, 212, 0.12)" if is_active else ft.Colors.TRANSPARENT,
            border=ft.Border.all(1, "rgba(6, 182, 212, 0.35)") if is_active else None,
            on_click=lambda _: self._navigate(route_name, params),
            ink=True
        )

    def build(self) -> ft.Container:
        # Brand Logo
        logo = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(safe_icon("sports_esports"), color="#FFFFFF", size=20),
                        bgcolor=ACCENT_PURPLE,
                        padding=6,
                        border_radius=8,
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="rgba(139, 92, 246, 0.45)")
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("PIXEL", size=22, weight=ft.FontWeight.W_900, color=TEXT_PRIMARY),
                            ft.Text("VAULT", size=22, weight=ft.FontWeight.W_900, color=ACCENT_PURPLE),
                        ],
                        spacing=0,
                        tight=True
                    )
                ],
                spacing=8,
                tight=True
            ),
            on_click=lambda _: self._navigate("home", None),
            ink=True
        )

        # Nav links
        nav_links = ft.Row(
            controls=[
                self._build_nav_link("Tienda", "home", icon="storefront"),
                self._build_nav_link("Catálogo Completo", "catalog", icon="grid_view"),
                self._build_nav_link("Zona Indie", "catalog", {"only_indie": True}, icon="auto_awesome"),
                self._build_nav_link("Mis Pedidos", "orders", icon="receipt_long"),
            ],
            spacing=4,
            tight=True
        )

        # Search bar container
        search_container = ft.Container(
            content=self._search_field,
            width=280
        )

        # Cart Button with dynamic badge
        badge_text = str(self._cart_count)
        cart_click_handler = self._on_cart_click if self._on_cart_click else (lambda: self._navigate("cart", None))

        cart_button = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("shopping_cart"), color="#FFFFFF", size=18),
                    ft.Text("Carrito", size=13, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Container(
                        content=ft.Text(badge_text, size=11, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                        bgcolor=ACCENT_GREEN if self._cart_count > 0 else "#475569",
                        padding=ft.Padding(left=7, right=7, top=2, bottom=2),
                        border_radius=10,
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="rgba(16, 185, 129, 0.4)") if self._cart_count > 0 else None
                    )
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            bgcolor=ACCENT_PURPLE,
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            border_radius=8,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="rgba(139, 92, 246, 0.4)"),
            on_click=lambda _: cart_click_handler(),
            ink=True
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    logo,
                    nav_links,
                    ft.Row(
                        controls=[
                            search_container,
                            cart_button
                        ],
                        spacing=12,
                        tight=True
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor="#0B101D",
            padding=ft.Padding(left=32, right=32, top=12, bottom=12),
            border=ft.Border(bottom=ft.BorderSide(1, "rgba(255, 255, 255, 0.08)"))
        )
