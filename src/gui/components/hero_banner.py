"""High-impact promotional Hero Banner component inspired by Steam and itch.io."""
from typing import Callable, Optional
import flet as ft

from ...domain.entities import Game
from ..theme import (
    ACCENT_PURPLE,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_GREEN_BG,
    ACCENT_AMBER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    create_badge,
)


class FeaturedHeroBannerComponent:
    """Hero banner showcasing the main featured title with description, badges, and quick buy."""

    def __init__(
        self,
        game: Game,
        on_detail: Callable[[Game], None],
        on_add_cart: Callable[[Game], None],
        is_in_cart: bool = False
    ):
        self._game = game
        self._on_detail = on_detail
        self._on_add_cart = on_add_cart
        self._is_in_cart = is_in_cart

    def build(self) -> ft.Container:
        # Badges list
        badges = [
            create_badge("⭐ DESTACADO DE LA SEMANA", bg_color=ACCENT_PURPLE, text_color="#FFFFFF", font_size=11),
            create_badge(self._game.genre, bg_color="#1E293B", text_color=ACCENT_CYAN, font_size=11),
        ]
        if self._game.is_on_sale:
            badges.append(
                create_badge(
                    f"OFERTA ESPECIAL {self._game.discount_badge}",
                    bg_color=ACCENT_GREEN_BG,
                    text_color="#4ADE80",
                    font_size=11
                )
            )

        # Left Info Column
        title_text = ft.Text(
            self._game.title,
            size=30,
            weight=ft.FontWeight.W_900,
            color=TEXT_PRIMARY
        )

        desc_text = ft.Text(
            self._game.short_description,
            size=14,
            color=TEXT_SECONDARY,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS
        )

        reviews_row = ft.Row(
            controls=[
                ft.Icon("star", size=18, color=ACCENT_AMBER),
                ft.Text(f"{self._game.rating:.1f}/5.0", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(f"— {self._game.rating_summary}", size=13, color="#A5F3FC")
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Price and Actions
        price_row_controls = []
        if self._game.discount_percent > 0:
            price_row_controls.append(
                ft.Container(
                    content=ft.Text(self._game.discount_badge, size=18, weight=ft.FontWeight.W_900, color="#4ADE80"),
                    bgcolor=ACCENT_GREEN_BG,
                    padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                    border_radius=6,
                    border=ft.Border.all(1, "#059669")
                )
            )
            price_row_controls.append(
                ft.Text(
                    f"${self._game.price:,.2f}",
                    size=16,
                    color="#64748B",
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color="#64748B")
                )
            )

        final_price_label = "Gratis" if self._game.final_price <= 0 else f"${self._game.final_price:,.2f} USD"
        price_row_controls.append(
            ft.Text(final_price_label, size=24, weight=ft.FontWeight.W_900, color=TEXT_PRIMARY)
        )

        price_row = ft.Row(
            controls=price_row_controls,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Action Buttons
        detail_btn = ft.FilledButton(
            content=ft.Text("Ver Detalles Completos", size=14, weight=ft.FontWeight.BOLD),
            icon="visibility",
            style=ft.ButtonStyle(
                bgcolor=ACCENT_PURPLE,
                color="#FFFFFF",
                padding=ft.Padding(left=18, right=18, top=12, bottom=12),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self._on_detail(self._game)
        )

        if self._is_in_cart:
            cart_btn = ft.OutlinedButton(
                content=ft.Text("En Carrito ✓", size=14, weight=ft.FontWeight.BOLD),
                icon="check",
                style=ft.ButtonStyle(
                    color=ACCENT_GREEN,
                    side=ft.BorderSide(1.5, ACCENT_GREEN),
                    padding=ft.Padding(left=18, right=18, top=12, bottom=12),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                disabled=True
            )
        else:
            cart_btn = ft.OutlinedButton(
                content=ft.Text("Añadir al Carrito", size=14, weight=ft.FontWeight.BOLD),
                icon="add_shopping_cart",
                style=ft.ButtonStyle(
                    color="#FFFFFF",
                    side=ft.BorderSide(1.5, ACCENT_PURPLE),
                    padding=ft.Padding(left=18, right=18, top=12, bottom=12),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=lambda _: self._on_add_cart(self._game)
            )

        actions_row = ft.Row(
            controls=[detail_btn, cart_btn],
            spacing=12
        )

        left_column = ft.Column(
            controls=[
                ft.Row(controls=badges, spacing=8),
                title_text,
                desc_text,
                reviews_row,
                ft.Container(height=6),
                price_row,
                actions_row
            ],
            spacing=10,
            expand=True
        )

        # Right Image Showcase
        right_image = ft.Container(
            content=ft.Image(
                src=self._game.cover_image,
                width=340,
                height=220,
                fit=ft.BoxFit.COVER,
                border_radius=12,
                error_content=ft.Container(
                    content=ft.Icon("sports_esports", size=64, color=ACCENT_PURPLE),
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#1E1B4B"
                )
            ),
            border_radius=12,
            border=ft.Border.all(2, "#312E81")
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    left_column,
                    right_image
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24
            ),
            padding=28,
            border_radius=16,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1E1B4B", "#0F172A", "#111827"]
            ),
            border=ft.Border.all(1, "#3730A3"),
            margin=ft.Margin(left=0, right=0, top=10, bottom=20)
        )
