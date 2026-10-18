"""Sliding Offcanvas Cart Drawer component inspired by modern e-commerce and Steam/Flask."""
from typing import Callable, Optional
import flet as ft

from ...domain.entities import ShoppingCart
from ..theme import (
    BG_HEADER,
    BG_SURFACE,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_RED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    safe_icon,
)


class CartDrawerComponent:
    """Animated sliding cart drawer rendering offcanvas over the application."""

    def __init__(
        self,
        cart: ShoppingCart,
        is_open: bool,
        on_close: Callable[[], None],
        on_remove_item: Callable[[str], None],
        on_checkout: Callable[[], None],
        on_view_cart: Callable[[], None],
        on_catalog: Callable[[], None]
    ):
        self._cart = cart
        self._is_open = is_open
        self._on_close = on_close
        self._on_remove_item = on_remove_item
        self._on_checkout = on_checkout
        self._on_view_cart = on_view_cart
        self._on_catalog = on_catalog

    def build(self) -> Optional[ft.Control]:
        if not self._is_open:
            return None

        # 1. Header Row
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(safe_icon("shopping_cart"), color="#FFFFFF", size=18),
                                bgcolor=ACCENT_PURPLE,
                                padding=6,
                                border_radius=6,
                                shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="rgba(139, 92, 246, 0.4)")
                            ),
                            ft.Text("Tu Carrito Digital", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
                        ],
                        spacing=10,
                        tight=True
                    ),
                    ft.IconButton(
                        icon=safe_icon("close"),
                        icon_color=TEXT_SECONDARY,
                        tooltip="Cerrar carrito",
                        on_click=lambda _: self._on_close()
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.Padding(left=20, right=16, top=16, bottom=14),
            border=ft.Border(bottom=ft.BorderSide(1, "#1E293B"))
        )

        # 2. Cart Items or Empty state
        if self._cart.is_empty:
            body = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(safe_icon("shopping_cart_outlined"), size=52, color=TEXT_MUTED),
                        ft.Text("Tu carrito está vacío", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(
                            "Explora nuestro catálogo y agrega tus títulos favoritos.",
                            size=12,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.OutlinedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(safe_icon("grid_view"), size=15, color=ACCENT_CYAN),
                                    ft.Text("Explorar Catálogo", size=12, weight=ft.FontWeight.BOLD, color=ACCENT_CYAN),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                tight=True,
                                spacing=6
                            ),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1.5, ACCENT_CYAN),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(left=18, right=18, top=10, bottom=10)
                            ),
                            on_click=lambda _: self._on_catalog()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14
                ),
                padding=30,
                alignment=ft.Alignment.CENTER,
                expand=True
            )
        else:
            item_cards = []
            for item in self._cart.get_items():
                price_str = "Gratis" if item.unit_price <= 0 else f"${item.unit_price:,.2f} USD"
                item_cards.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Image(
                                    src=item.game.cover_image,
                                    width=64,
                                    height=40,
                                    fit=ft.BoxFit.COVER,
                                    border_radius=6,
                                    error_content=ft.Container(
                                        content=ft.Icon(safe_icon("videogame_asset"), size=20, color=ACCENT_PURPLE),
                                        alignment=ft.Alignment.CENTER,
                                        bgcolor="#1E1B4B"
                                    )
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(item.game.title, size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(item.game.genre, size=10, color=TEXT_MUTED),
                                        ft.Text(price_str, size=12, weight=ft.FontWeight.BOLD, color="#38BDF8")
                                    ],
                                    spacing=2,
                                    expand=True
                                ),
                                ft.IconButton(
                                    icon=safe_icon("delete_outline"),
                                    icon_color="#EF4444",
                                    icon_size=18,
                                    tooltip="Eliminar del carrito",
                                    on_click=lambda _, gid=item.game.id: self._on_remove_item(gid)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        padding=10,
                        bgcolor="#131D31",
                        border=ft.Border.all(1, "#22304A"),
                        border_radius=8
                    )
                )

            body = ft.Container(
                content=ft.ListView(
                    controls=item_cards,
                    spacing=8,
                    padding=ft.Padding(left=16, right=16, top=14, bottom=14)
                ),
                expand=True
            )

        # 3. Footer Summary & Action Buttons
        subtotal_str = f"${self._cart.subtotal:,.2f} USD"
        total_str = f"${self._cart.total:,.2f} USD"

        summary_rows = [
            ft.Row(
                controls=[
                    ft.Text("Subtotal", size=12, color=TEXT_SECONDARY),
                    ft.Text(subtotal_str, size=12, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ]

        if self._cart.total_discount > 0:
            summary_rows.append(
                ft.Row(
                    controls=[
                        ft.Text("Descuento Aplicado", size=12, color="#4ADE80"),
                        ft.Text(f"-${self._cart.total_discount:,.2f} USD", size=12, weight=ft.FontWeight.W_600, color="#4ADE80")
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        summary_rows.append(
            ft.Row(
                controls=[
                    ft.Text("Total a Pagar", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(total_str, size=18, weight=ft.FontWeight.W_900, color="#38BDF8")
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        checkout_btn = ft.FilledButton(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("credit_card"), size=17, color="#FFFFFF"),
                    ft.Text("Continuar a la Compra", size=13, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=8
            ),
            style=ft.ButtonStyle(
                bgcolor=ACCENT_PURPLE,
                color="#FFFFFF",
                padding=ft.Padding(left=16, right=16, top=13, bottom=13),
                shape=ft.RoundedRectangleBorder(radius=8),
                shadow_color="rgba(139, 92, 246, 0.4)",
                elevation=4
            ),
            disabled=self._cart.is_empty,
            on_click=lambda _: self._on_checkout(),
            expand=True
        )

        view_cart_btn = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("shopping_bag"), size=16, color=TEXT_PRIMARY),
                    ft.Text("Ver Carrito Detallado", size=12, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=8
            ),
            style=ft.ButtonStyle(
                color=TEXT_PRIMARY,
                side=ft.BorderSide(1, BORDER_COLOR),
                padding=ft.Padding(left=14, right=14, top=11, bottom=11),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self._on_view_cart(),
            expand=True
        )

        footer = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Column(controls=summary_rows, spacing=4),
                    ft.Divider(color="#1E293B", height=1),
                    ft.Row(controls=[checkout_btn]),
                    ft.Row(controls=[view_cart_btn])
                ],
                spacing=10
            ),
            padding=ft.Padding(left=20, right=20, top=14, bottom=20),
            border=ft.Border(top=ft.BorderSide(1, "#1E293B")),
            bgcolor="#0B101D"
        )

        # 4. Drawer Panel Container with smooth offcanvas shadow & border
        drawer_panel = ft.Container(
            content=ft.Column(
                controls=[header, body, footer],
                spacing=0,
                expand=True
            ),
            width=420,
            bgcolor="#0B101D",
            border=ft.Border(left=ft.BorderSide(1.5, "#334155")),
            shadow=ft.BoxShadow(spread_radius=6, blur_radius=50, color="rgba(0, 0, 0, 0.85)", offset=ft.Offset(-12, 0)),
        )

        # 5. Full overlay Stack with semi-transparent backdrop
        return ft.Stack(
            controls=[
                ft.Container(
                    bgcolor="rgba(0, 0, 0, 0.65)",
                    on_click=lambda _: self._on_close(),
                    expand=True
                ),
                ft.Row(
                    controls=[drawer_panel],
                    alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    expand=True
                )
            ],
            expand=True
        )
