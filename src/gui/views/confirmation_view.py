"""Order Confirmation View presenting activation keys, transaction summary, and proof of persistence."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from .base_view import BaseView
from ...domain.entities import Order
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
    safe_icon,
)
from ..components.footer import StoreFooterComponent


class OrderConfirmationView(BaseView):
    """Celebratory view presenting simulated activation keys, receipt, and JSON verification."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        order: Optional[Order] = None,
        notify_fn: Optional[Callable[[str, str], None]] = None
    ):
        super().__init__(page, navigate_fn)
        self._order = order
        self._notify = notify_fn

    def build(self) -> ft.Control:
        if not self._order:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(safe_icon("receipt_long"), size=64, color=TEXT_MUTED),
                        ft.Text("No hay información de orden activa.", size=18, color=TEXT_PRIMARY),
                        ft.FilledButton(
                            content=ft.Text("Volver a la Tienda"),
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

        # Header success banner
        success_header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(safe_icon("task_alt"), size=56, color="#4ADE80"),
                        bgcolor="#064E3B",
                        padding=18,
                        border_radius=50
                    ),
                    ft.Text(
                        "¡Compra Simulada Completada con Éxito!",
                        size=26,
                        weight=ft.FontWeight.W_900,
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        f"Identificador de Pedido: {self._order.id}",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ACCENT_CYAN
                    ),
                    ft.Text(
                        f"La transacción ha sido guardada en 'data/orders.json'. Se han generado las siguientes claves digitales para {self._order.customer_name}:",
                        size=13,
                        color=TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=24,
            alignment=ft.Alignment.CENTER
        )

        # Digital Keys List
        keys_controls = []
        for item in self._order.items:
            key_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(safe_icon("sports_esports"), color=ACCENT_PURPLE, size=24),
                                ft.Column(
                                    controls=[
                                        ft.Text(item.game_title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                        ft.Text(f"Precio pagado: ${item.price_paid:,.2f} USD", size=12, color=TEXT_MUTED)
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=12,
                            tight=True,
                            expand=True
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(safe_icon("vpn_key"), size=16, color=ACCENT_CYAN),
                                    ft.Text(
                                        item.digital_key,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color="#A5F3FC",
                                        font_family="Consolas"
                                    )
                                ],
                                spacing=8,
                                tight=True
                            ),
                            bgcolor="#082F49",
                            border=ft.Border.all(1, "#0284C7"),
                            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                            border_radius=8
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=16,
                bgcolor="#0F172A",
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=10,
                margin=ft.Margin(left=0, right=0, top=4, bottom=4)
            )
            keys_controls.append(key_card)

        keys_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Tus Claves de Activación Digital (Simuladas)", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Copia o registra tus códigos de activación para añadir los títulos a tu biblioteca simulada.", size=12, color=TEXT_SECONDARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Column(controls=keys_controls, spacing=6)
                ],
                spacing=10
            ),
            bgcolor=BG_SURFACE,
            padding=22,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        # Receipt Summary Card
        receipt_items = [
            ("Fecha y Hora (UTC)", self._order.created_at[:19].replace("T", " ")),
            ("Comprador", self._order.customer_name),
            ("Correo de Entrega", self._order.customer_email),
            ("Método de Pago", self._order.payment_method),
            ("Subtotal", f"${self._order.subtotal:,.2f} USD"),
            ("Ahorro Obtenido", f"-${self._order.total_discount:,.2f} USD"),
            ("Total Pagado", f"${self._order.total:,.2f} USD"),
            ("Estado", self._order.status)
        ]

        receipt_controls = []
        for label, val in receipt_items:
            is_total = label == "Total Pagado"
            receipt_controls.append(
                ft.Row(
                    controls=[
                        ft.Text(label, size=13, color=TEXT_PRIMARY if is_total else TEXT_MUTED),
                        ft.Text(
                            val,
                            size=14 if is_total else 13,
                            weight=ft.FontWeight.BOLD if is_total else ft.FontWeight.NORMAL,
                            color=ACCENT_CYAN if is_total else TEXT_PRIMARY
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        receipt_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Recibo de Simulación Académica", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Column(controls=receipt_controls, spacing=8)
                ],
                spacing=12
            ),
            bgcolor=BG_SURFACE,
            padding=22,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        # Action Buttons
        actions_row = ft.Row(
            controls=[
                ft.FilledButton(
                    content=ft.Text("Seguir Explorando la Tienda", size=14, weight=ft.FontWeight.BOLD),
                    icon=safe_icon("storefront"),
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT_PURPLE,
                        color="#FFFFFF",
                        padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=lambda _: self.navigate("home", None)
                ),
                ft.OutlinedButton(
                    content=ft.Text("Ver Historial de Pedidos", size=14),
                    icon=safe_icon("receipt_long"),
                    style=ft.ButtonStyle(
                        color=ACCENT_CYAN,
                        side=ft.BorderSide(1.5, ACCENT_CYAN),
                        padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=lambda _: self.navigate("orders", None)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16
        )

        return ft.ListView(
            controls=[
                ft.Container(height=10),
                success_header,
                keys_section,
                ft.Container(height=16),
                receipt_card,
                ft.Container(height=24),
                actions_row,
                StoreFooterComponent().build()
            ],
            spacing=0,
            padding=ft.Padding(left=32, right=32, top=16, bottom=20),
            expand=True
        )
