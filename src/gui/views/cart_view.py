"""Shopping Cart View managing selected items, pricing breakdowns, and checkout routing."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from .base_view import BaseView
from ...application.use_cases import ManageCartUseCase
from ...domain.entities import CartItem
from ..theme import (
    BG_SURFACE,
    ACCENT_PURPLE,
    ACCENT_GREEN,
    ACCENT_CYAN,
    ACCENT_RED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    create_badge,
    safe_icon,
)
from ..components.footer import StoreFooterComponent


class CartView(BaseView):
    """Shopping cart view enforcing unique games and business rule totals."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        cart_manager: ManageCartUseCase,
        notify_fn: Optional[Callable[[str, str], None]] = None,
        notify: Optional[Callable[[str, str], None]] = None,
        **kwargs: Any
    ):
        super().__init__(page, navigate_fn)
        self._cart_manager = cart_manager
        self._notify = notify_fn or notify

    def _on_remove_item(self, game_id: str, title: str):
        try:
            self._cart_manager.remove_game(game_id)
            if self._notify:
                self._notify(f"'{title}' eliminado del carrito.", "info")
            if self.page:
                self.page.update()
        except Exception as e:
            if self._notify:
                self._notify(str(e), "warning")

    def _on_clear_cart(self):
        self._cart_manager.clear()
        if self._notify:
            self._notify("Carrito de compras vaciado.", "info")
        if self.page:
            self.page.update()

    def _build_item_card(self, item: CartItem) -> ft.Container:
        game = item.game

        thumbnail = ft.Container(
            content=ft.Image(
                src=game.cover_image,
                width=110,
                height=65,
                fit=ft.BoxFit.COVER,
                border_radius=8,
                error_content=ft.Container(
                    content=ft.Icon(safe_icon("videogame_asset"), size=24, color=ACCENT_PURPLE),
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#1E1B4B"
                )
            ),
            border_radius=8,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        title_col = ft.Column(
            controls=[
                ft.Text(game.title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Row(
                    controls=[
                        create_badge(game.genre, bg_color="#1E293B", text_color=ACCENT_CYAN, font_size=10),
                        ft.Text(f"por {game.developer}", size=12, color=TEXT_MUTED)
                    ],
                    spacing=8
                )
            ],
            spacing=4,
            expand=True
        )

        # Price info
        price_controls = []
        if game.is_on_sale:
            price_controls.append(
                create_badge(f"-{game.discount_percent}%", bg_color="#064E3B", text_color="#4ADE80", font_size=11)
            )
            price_controls.append(
                ft.Text(
                    f"${game.price:,.2f}",
                    size=12,
                    color=TEXT_MUTED,
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color=TEXT_MUTED)
                )
            )

        final_label = "Gratis" if game.final_price <= 0 else f"${game.final_price:,.2f} USD"
        price_controls.append(
            ft.Text(final_label, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
        )

        price_row = ft.Row(controls=price_controls, spacing=8, alignment=ft.MainAxisAlignment.END, tight=True)

        remove_btn = ft.IconButton(
            icon=safe_icon("delete_outline"),
            icon_color=ACCENT_RED,
            tooltip="Eliminar del carrito",
            on_click=lambda _: self._on_remove_item(game.id, game.title)
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    thumbnail,
                    title_col,
                    price_row,
                    remove_btn
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16
            ),
            padding=14,
            bgcolor=BG_SURFACE,
            border_radius=10,
            border=ft.Border.all(1, BORDER_COLOR),
            margin=ft.Margin(left=0, right=0, top=4, bottom=6)
        )

    def build(self) -> ft.Control:
        cart = self._cart_manager.cart

        if cart.is_empty:
            empty_state = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(safe_icon("shopping_cart_outlined"), size=64, color=TEXT_MUTED),
                            bgcolor="#162032",
                            padding=24,
                            border_radius=50
                        ),
                        ft.Text("Tu carrito de compras está vacío", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(
                            "Parece que aún no has agregado ningún videojuego a tu carrito.",
                            size=14,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.FilledButton(
                            content=ft.Text("Explorar la Tienda", size=14, weight=ft.FontWeight.BOLD),
                            icon=safe_icon("storefront"),
                            style=ft.ButtonStyle(
                                bgcolor=ACCENT_PURPLE,
                                color="#FFFFFF",
                                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=lambda _: self.navigate("home", None)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16
                ),
                padding=60,
                alignment=ft.Alignment.CENTER,
                expand=True
            )

            return ft.ListView(
                controls=[
                    ft.Container(height=30),
                    empty_state,
                    StoreFooterComponent().build()
                ],
                spacing=0,
                padding=ft.Padding(left=32, right=32, top=16, bottom=20),
                expand=True
            )

        # Header Title
        title_banner = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(safe_icon("shopping_cart"), color="#FFFFFF", size=22),
                            bgcolor=ACCENT_PURPLE,
                            padding=8,
                            border_radius=8
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Carrito de Compras", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text(f"Tienes {cart.item_count} videojuego{'s' if cart.item_count != 1 else ''} seleccionado{'s' if cart.item_count != 1 else ''}", size=13, color=TEXT_SECONDARY)
                            ],
                            spacing=2
                        )
                    ],
                    spacing=12,
                    tight=True
                ),
                ft.OutlinedButton(
                    content=ft.Text("Vaciar Carrito", size=12, weight=ft.FontWeight.W_600),
                    icon=safe_icon("remove_shopping_cart"),
                    style=ft.ButtonStyle(
                        color=ACCENT_RED,
                        side=ft.BorderSide(1, ACCENT_RED),
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=lambda _: self._on_clear_cart()
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Left: Items list
        items_controls = [self._build_item_card(item) for item in cart.get_items()]
        items_column = ft.Column(controls=items_controls, spacing=8, expand=2)

        # Right: Totals summary card
        subtotal_row = ft.Row(
            controls=[
                ft.Text("Precio Base:", size=13, color=TEXT_SECONDARY),
                ft.Text(cart.formatted_subtotal, size=13, color=TEXT_PRIMARY)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        discount_row = ft.Row(
            controls=[
                ft.Text("Ahorro por Ofertas:", size=13, color=TEXT_SECONDARY),
                ft.Text(f"-${cart.total_discount:,.2f} USD", size=13, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        total_row = ft.Row(
            controls=[
                ft.Text("Total Estimado:", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(cart.formatted_total, size=20, weight=ft.FontWeight.W_900, color=ACCENT_CYAN)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        checkout_btn = ft.FilledButton(
            content=ft.Text("Continuar a la Compra Simulada", size=14, weight=ft.FontWeight.BOLD),
            icon=safe_icon("lock"),
            style=ft.ButtonStyle(
                bgcolor=ACCENT_GREEN,
                color="#FFFFFF",
                padding=ft.Padding(left=18, right=18, top=14, bottom=14),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self.navigate("checkout", None)
        )

        keep_shopping_btn = ft.OutlinedButton(
            content=ft.Text("Seguir Explorando Juegos", size=13),
            icon=safe_icon("storefront"),
            style=ft.ButtonStyle(
                color=TEXT_PRIMARY,
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self.navigate("catalog", None)
        )

        disclaimer = ft.Container(
            content=ft.Text(
                "ℹ️ Simulación Académica: No se procesa dinero real. Podrás confirmar o cancelar en la siguiente pantalla.",
                size=11,
                color=TEXT_MUTED,
                text_align=ft.TextAlign.CENTER
            ),
            bgcolor="#0B0F19",
            padding=10,
            border_radius=8
        )

        summary_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Resumen de tu Compra", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    subtotal_row,
                    discount_row,
                    ft.Divider(color=BORDER_COLOR, height=1),
                    total_row,
                    ft.Container(height=8),
                    checkout_btn,
                    keep_shopping_btn,
                    disclaimer
                ],
                spacing=12
            ),
            bgcolor=BG_SURFACE,
            padding=22,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR),
            width=360
        )

        body_layout = ft.Row(
            controls=[items_column, summary_card],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=24
        )

        return ft.ListView(
            controls=[
                ft.Container(height=10),
                title_banner,
                ft.Container(height=16),
                body_layout,
                StoreFooterComponent().build()
            ],
            spacing=0,
            padding=ft.Padding(left=32, right=32, top=16, bottom=20),
            expand=True
        )
