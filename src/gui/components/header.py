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
    """Header bar providing brand identity, section routing, quick search, and cart counter.
    Dynamically adapts between single-row desktop layout and 2-tier responsive mobile/tablet layout.
    """

    def __init__(
        self,
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        cart_count: int = 0,
        current_route: str = "home",
        on_search_submit: Optional[Callable[[str], None]] = None,
        on_cart_click: Optional[Callable[[], None]] = None,
        page_width: Optional[int] = None,
        search_query: str = ""
    ):
        self._navigate = navigate_fn
        self._cart_count = cart_count
        self._current_route = current_route
        self._on_search_submit = on_search_submit
        self._on_cart_click = on_cart_click
        self._page_width = page_width if page_width is not None else 1280
        self._search_field = ft.TextField(
            value=search_query,
            hint_text="Buscar juegos...",
            text_size=12,
            height=36,
            content_padding=ft.Padding(left=10, right=10, top=0, bottom=0),
            border_radius=8,
            border_color="#1F293D",
            bgcolor="#0D1322",
            color=TEXT_PRIMARY,
            hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=11),
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
            controls.append(ft.Icon(safe_icon(icon), size=15, color=text_color))
        controls.append(ft.Text(label, size=12, weight=font_weight, color=text_color))

        return ft.Container(
            content=ft.Row(controls=controls, spacing=5, tight=True),
            padding=ft.Padding(left=9, right=9, top=6, bottom=6),
            border_radius=6,
            bgcolor="rgba(6, 182, 212, 0.12)" if is_active else ft.Colors.TRANSPARENT,
            border=ft.Border.all(1, "rgba(6, 182, 212, 0.35)") if is_active else None,
            on_click=lambda _: self._navigate(route_name, params),
            ink=True
        )

    def build(self) -> ft.Container:
        is_compact = self._page_width < 960
        is_mobile = self._page_width < 600

        # Brand Logo (Compact & crisp)
        logo = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(safe_icon("sports_esports"), color="#FFFFFF", size=18),
                        bgcolor=ACCENT_PURPLE,
                        padding=5,
                        border_radius=7,
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="rgba(139, 92, 246, 0.45)")
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("PIXEL", size=18 if is_compact else 20, weight=ft.FontWeight.W_900, color=TEXT_PRIMARY),
                            ft.Text("VAULT", size=18 if is_compact else 20, weight=ft.FontWeight.W_900, color=ACCENT_PURPLE),
                        ],
                        spacing=0,
                        tight=True
                    )
                ],
                spacing=7,
                tight=True
            ),
            on_click=lambda _: self._navigate("home", None),
            ink=True
        )

        # Nav links in an expandable, adaptive-scroll container
        nav_links = ft.Row(
            controls=[
                self._build_nav_link("Tienda", "home", icon="storefront"),
                self._build_nav_link("Catálogo", "catalog", icon="grid_view"),
                self._build_nav_link("Zona Indie", "catalog", {"only_indie": True}, icon="auto_awesome"),
                self._build_nav_link("Mis Pedidos", "orders", icon="receipt_long"),
            ],
            spacing=4,
            tight=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Search bar container
        search_width = 120 if is_mobile else (140 if is_compact else 160)
        search_container = ft.Container(
            content=self._search_field,
            width=search_width
        )

        # Cart Button with dynamic badge
        badge_text = str(self._cart_count)
        cart_click_handler = self._on_cart_click if self._on_cart_click else (lambda: self._navigate("cart", None))

        cart_content_controls = [
            ft.Icon(safe_icon("shopping_cart"), color="#FFFFFF", size=16),
        ]
        if not is_mobile:
            cart_content_controls.append(
                ft.Text("Carrito", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF")
            )
        cart_content_controls.append(
            ft.Container(
                content=ft.Text(badge_text, size=10, weight=ft.FontWeight.W_900, color="#FFFFFF"),
                bgcolor=ACCENT_GREEN if self._cart_count > 0 else "#475569",
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                border_radius=10,
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="rgba(16, 185, 129, 0.4)") if self._cart_count > 0 else None
            )
        )

        cart_button = ft.Container(
            content=ft.Row(
                controls=cart_content_controls,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            bgcolor=ACCENT_PURPLE,
            padding=ft.Padding(left=10, right=10, top=7, bottom=7),
            border_radius=8,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="rgba(139, 92, 246, 0.4)"),
            on_click=lambda _: cart_click_handler(),
            ink=True
        )

        # Right actions group (Search + Cart)
        right_actions = ft.Row(
            controls=[
                search_container,
                cart_button
            ],
            spacing=8,
            tight=True
        )

        if is_compact:
            # 2-Tier Responsive Layout for Tablet / Narrow Windows:
            # Tier 1: Brand Logo on Left, Search + Cart pinned to Right (NEVER cut off)
            top_tier = ft.Row(
                controls=[
                    logo,
                    right_actions
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
            # Tier 2: Navigation Links centered or horizontally scrollable
            nav_tier = ft.Container(
                content=nav_links,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding(top=2, bottom=2, left=0, right=0)
            )
            header_layout = ft.Column(
                controls=[
                    top_tier,
                    nav_tier
                ],
                spacing=6,
                tight=True
            )
            padding_top_bottom = 6
        else:
            # Single-Row Desktop Layout (>= 960px):
            # Middle nav is expandable with adaptive horizontal scrolling and bounded clipping
            nav_container = ft.Container(
                content=nav_links,
                expand=True,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding(left=6, right=6, top=0, bottom=0),
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
            header_layout = ft.Row(
                controls=[
                    logo,
                    nav_container,
                    right_actions
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            )
            padding_top_bottom = 8

        return ft.Container(
            content=header_layout,
            bgcolor="#0B101D",
            padding=ft.Padding(left=16, right=16, top=padding_top_bottom, bottom=padding_top_bottom),
            border=ft.Border(bottom=ft.BorderSide(1, "rgba(255, 255, 255, 0.08)"))
        )
