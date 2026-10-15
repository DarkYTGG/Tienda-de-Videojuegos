"""Orders History View displaying all simulated orders persisted in data/orders.json."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from .base_view import BaseView
from ...application.use_cases import GetOrdersUseCase
from ..theme import (
    BG_SURFACE,
    ACCENT_PURPLE,
    ACCENT_GREEN,
    ACCENT_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    create_badge,
)
from ..components.footer import StoreFooterComponent


class OrdersHistoryView(BaseView):
    """View allowing the student and teacher to verify JSON order persistence and digital keys."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        get_orders_uc: GetOrdersUseCase,
        notify_fn: Optional[Callable[[str, str], None]] = None
    ):
        super().__init__(page, navigate_fn)
        self._get_orders_uc = get_orders_uc
        self._notify = notify_fn

    def build(self) -> ft.Control:
        orders = self._get_orders_uc.get_all()

        title_banner = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon("receipt_long", color="#FFFFFF", size=22),
                            bgcolor=ACCENT_PURPLE,
                            padding=8,
                            border_radius=8
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Historial de Compras Simuladas", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text("Registro de pedidos persistidos en 'data/orders.json' con sus claves digitales generadas.", size=13, color=TEXT_SECONDARY)
                            ],
                            spacing=2
                        )
                    ],
                    spacing=12,
                    tight=True
                ),
                ft.OutlinedButton(
                    content=ft.Text("Ir a la Tienda", size=13),
                    icon="storefront",
                    style=ft.ButtonStyle(
                        color=TEXT_PRIMARY,
                        side=ft.BorderSide(1, BORDER_COLOR),
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=lambda _: self.navigate("home", None)
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        if not orders:
            empty_state = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon("history_toggle_off", size=64, color=TEXT_MUTED),
                        ft.Text("Aún no hay compras simuladas registradas", size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(
                            "Realiza una compra simulada desde el carrito para ver el registro guardado en JSON.",
                            size=13,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.FilledButton(
                            content=ft.Text("Comenzar a Comprar"),
                            style=ft.ButtonStyle(bgcolor=ACCENT_PURPLE, color="#FFFFFF"),
                            on_click=lambda _: self.navigate("home", None)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=60,
                alignment=ft.Alignment.CENTER
            )

            return ft.ListView(
                controls=[
                    ft.Container(height=10),
                    title_banner,
                    ft.Container(height=20),
                    empty_state,
                    StoreFooterComponent().build()
                ],
                spacing=0,
                padding=ft.Padding(left=32, right=32, top=16, bottom=20),
                expand=True
            )

        # Order cards
        order_cards = []
        for ord_item in orders:
            # Items inside this order
            items_controls = []
            for item in ord_item.items:
                items_controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon("sports_esports", size=18, color=ACCENT_PURPLE),
                                        ft.Text(item.game_title, size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                        ft.Text(f"(${item.price_paid:,.2f} USD)", size=12, color=TEXT_MUTED)
                                    ],
                                    spacing=8,
                                    tight=True
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon("vpn_key", size=13, color=ACCENT_CYAN),
                                            ft.Text(item.digital_key, size=12, weight=ft.FontWeight.BOLD, color="#A5F3FC", font_family="Consolas")
                                        ],
                                        spacing=6,
                                        tight=True
                                    ),
                                    bgcolor="#082F49",
                                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                    border_radius=6
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor="#0F172A",
                        padding=10,
                        border_radius=8,
                        margin=ft.Margin(left=0, right=0, top=2, bottom=2)
                    )
                )

            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        create_badge(ord_item.id, bg_color=ACCENT_PURPLE, text_color="#FFFFFF", font_size=12),
                                        create_badge(ord_item.status, bg_color="#064E3B", text_color="#4ADE80", font_size=11),
                                    ],
                                    spacing=8,
                                    tight=True
                                ),
                                ft.Text(
                                    f"Total: ${ord_item.total:,.2f} USD",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ACCENT_CYAN
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Divider(color=BORDER_COLOR, height=1),
                        ft.Row(
                            controls=[
                                ft.Text(f"Comprador: {ord_item.customer_name} ({ord_item.customer_email})", size=12, color=TEXT_SECONDARY),
                                ft.Text(f"Fecha: {ord_item.created_at[:19].replace('T', ' ')} UTC", size=12, color=TEXT_MUTED)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Container(height=4),
                        ft.Text("Juegos y Claves Digitales Asignadas:", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Column(controls=items_controls, spacing=4)
                    ],
                    spacing=8
                ),
                bgcolor=BG_SURFACE,
                padding=20,
                border_radius=12,
                border=ft.Border.all(1, BORDER_COLOR),
                margin=ft.Margin(left=0, right=0, top=6, bottom=12)
            )
            order_cards.append(card)

        return ft.ListView(
            controls=[
                ft.Container(height=10),
                title_banner,
                ft.Container(height=16),
                ft.Column(controls=order_cards, spacing=8),
                StoreFooterComponent().build()
            ],
            spacing=0,
            padding=ft.Padding(left=32, right=32, top=16, bottom=20),
            expand=True
        )
