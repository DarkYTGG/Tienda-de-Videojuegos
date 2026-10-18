"""Simulated Checkout View validating customer info, applying business logic, and creating orders."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from .base_view import BaseView
from ...application.use_cases import ManageCartUseCase, CheckoutUseCase
from ...application.dtos import CheckoutRequestDTO
from ..theme import (
    BG_SURFACE,
    BG_INPUT,
    ACCENT_PURPLE,
    ACCENT_GREEN,
    ACCENT_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    BORDER_LIGHT,
    safe_icon,
)
from ..components.footer import StoreFooterComponent


class CheckoutView(BaseView):
    """Simulated checkout page verifying minimal inputs, disclaimer, and order generation."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        cart_manager: ManageCartUseCase,
        checkout_uc: CheckoutUseCase,
        notify_fn: Optional[Callable[[str, str], None]] = None,
        notify: Optional[Callable[[str, str], None]] = None,
        **kwargs: Any
    ):
        super().__init__(page, navigate_fn)
        self._cart_manager = cart_manager
        self._checkout_uc = checkout_uc
        self._notify = notify_fn or notify

        # Form Controls
        self._name_field = ft.TextField(
            label="Nombre Completo del Comprador",
            hint_text="Ej. Carlos Mendoza",
            text_size=13,
            border_radius=8,
            border_color=BORDER_COLOR,
            bgcolor=BG_INPUT,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            prefix_icon=safe_icon("person"),
            autofocus=True
        )

        self._email_field = ft.TextField(
            label="Correo Electrónico (para entrega de claves)",
            hint_text="carlos@ejemplo.com",
            text_size=13,
            border_radius=8,
            border_color=BORDER_COLOR,
            bgcolor=BG_INPUT,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            prefix_icon=safe_icon("email")
        )

        self._payment_dropdown = ft.Dropdown(
            label="Método de Pago Simulado",
            options=[
                ft.dropdown.Option("Saldo PixelVault (Simulado)"),
                ft.dropdown.Option("Tarjeta Virtual de Prueba (Simulado)"),
                ft.dropdown.Option("Transferencia de Demostración"),
            ],
            value="Saldo PixelVault (Simulado)",
            text_size=13,
            border_radius=8,
            border_color=BORDER_COLOR,
            bgcolor=BG_INPUT,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12)
        )

        self._error_text = ft.Text("", size=12, color="#EF4444", visible=False)

    def _on_confirm_checkout(self):
        # Reset error messages
        self._name_field.error_text = None
        self._email_field.error_text = None
        self._error_text.visible = False

        req = CheckoutRequestDTO(
            customer_name=self._name_field.value or "",
            customer_email=self._email_field.value or "",
            payment_method=self._payment_dropdown.value or "Saldo PixelVault (Simulado)"
        )

        response = self._checkout_uc.execute(self._cart_manager.cart, req)

        if not response.success:
            if "customer_name" in response.errors:
                self._name_field.error_text = response.errors["customer_name"]
            if "customer_email" in response.errors:
                self._email_field.error_text = response.errors["customer_email"]
            if "cart" in response.errors:
                self._error_text.value = response.errors["cart"]
                self._error_text.visible = True
            if self._notify:
                self._notify(response.message, "warning")
            if self.page:
                self.page.update()
            return

        # Transaction succeeded
        if self._notify:
            self._notify("¡Compra simulada completada exitosamente!", "success")

        # Navigate to confirmation screen passing the created order
        self.navigate("confirmation", {"order": response.order})

    def build(self) -> ft.Control:
        cart = self._cart_manager.cart
        if cart.is_empty:
            # If opened with empty cart, redirect back
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(safe_icon("shopping_cart_outlined"), size=48, color=TEXT_MUTED),
                        ft.Text("El carrito está vacío. Agrega juegos antes de confirmar.", size=16, color=TEXT_PRIMARY),
                        ft.FilledButton(
                            content=ft.Text("Ir a la Tienda"),
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

        # Header Title
        title_banner = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(safe_icon("verified_user"), color="#FFFFFF", size=22),
                            bgcolor=ACCENT_GREEN,
                            padding=8,
                            border_radius=8
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Confirmación de Compra Digital", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text("Revisa tus videojuegos y completa los datos requeridos para la simulación de compra.", size=13, color=TEXT_SECONDARY)
                            ],
                            spacing=2
                        )
                    ],
                    spacing=12,
                    tight=True
                )
            ]
        )

        # Left Column: Form and Purchase Simulation Disclaimer
        disclaimer_banner = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("info"), color="#FBBF24", size=24),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "SIMULACIÓN DE COMPRA DIGITAL — ENTORNO SEGURO",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color="#FDE68A"
                            ),
                            ft.Text(
                                "Esta operación es 100% una simulación de compra digital. No se solicitará información financiera sensible, números de tarjeta reales ni se procesará cobro bancario alguno. Al confirmar se generarán claves de activación únicas para cada videojuego persistidas localmente.",
                                size=12,
                                color="#FEF3C7"
                            )
                        ],
                        spacing=2,
                        expand=True
                    )
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            bgcolor="#451A03",
            border=ft.Border.all(1, "#B45309"),
            border_radius=10,
            padding=16
        )

        form_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Datos del Comprador", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Las claves digitales se asociarán a estos datos simulados.", size=12, color=TEXT_SECONDARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    self._name_field,
                    self._email_field,
                    self._payment_dropdown,
                    self._error_text
                ],
                spacing=14
            ),
            bgcolor=BG_SURFACE,
            padding=22,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        left_column = ft.Container(
            content=ft.Column(
                controls=[
                    disclaimer_banner,
                    form_card
                ],
                spacing=16
            ),
            col={"sm": 12, "lg": 7, "xl": 8}
        )

        # Right Column: Order summary and Actions
        items_summary_controls = []
        for it in cart.get_items():
            items_summary_controls.append(
                ft.Row(
                    controls=[
                        ft.Text(it.game.title, size=13, color=TEXT_PRIMARY, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"${it.unit_price:,.2f} USD", size=13, weight=ft.FontWeight.BOLD, color=ACCENT_CYAN)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        confirm_btn = ft.FilledButton(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("task_alt"), size=18, color="#FFFFFF"),
                    ft.Text("Confirmar Simulación de Compra", size=14, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=8
            ),
            style=ft.ButtonStyle(
                bgcolor=ACCENT_GREEN,
                color="#FFFFFF",
                padding=ft.Padding(left=18, right=18, top=14, bottom=14),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self._on_confirm_checkout(),
            expand=True
        )

        cancel_btn = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("arrow_back"), size=16, color=TEXT_PRIMARY),
                    ft.Text("Cancelar y Volver al Carrito", size=13, color=TEXT_PRIMARY),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=8
            ),
            style=ft.ButtonStyle(
                color=TEXT_PRIMARY,
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12)
            ),
            on_click=lambda _: self.navigate("cart", None),
            expand=True
        )

        right_summary = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Detalle del Pedido", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Column(controls=items_summary_controls, spacing=8),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Row(
                        controls=[
                            ft.Text("Subtotal:", size=13, color=TEXT_SECONDARY),
                            ft.Text(cart.formatted_subtotal, size=13, color=TEXT_PRIMARY)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Descuentos:", size=13, color=TEXT_SECONDARY),
                            ft.Text(f"-${cart.total_discount:,.2f} USD", size=13, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Row(
                        controls=[
                            ft.Text("Total Final:", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text(cart.formatted_total, size=20, weight=ft.FontWeight.W_900, color=ACCENT_CYAN)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=6),
                    ft.Row(controls=[confirm_btn]),
                    ft.Row(controls=[cancel_btn])
                ],
                spacing=12
            ),
            bgcolor=BG_SURFACE,
            padding=22,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR),
            col={"sm": 12, "lg": 5, "xl": 4}
        )

        body_layout = ft.ResponsiveRow(
            controls=[left_column, right_summary],
            spacing=24,
            run_spacing=24,
            vertical_alignment=ft.CrossAxisAlignment.START
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
