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
    TEXT_MUTED,
    create_badge,
    safe_icon,
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
                ft.Icon(safe_icon("star"), size=18, color=ACCENT_AMBER),
                ft.Text(f"{self._game.rating:.1f}", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text("/ 5.0", size=12, color=TEXT_MUTED),
                ft.Text("•", size=12, color=TEXT_MUTED),
                ft.Icon(safe_icon("favorite"), size=14, color="#F43F5E"),
                ft.Text(f"Extremadamente positivas ({self._game.reviews_count:,} reseñas)", size=12, color="#E2E8F0")
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
            ft.Text(final_price_label, size=26, weight=ft.FontWeight.W_900, color=TEXT_PRIMARY)
        )

        price_row = ft.Row(
            controls=price_row_controls,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Action Buttons
        detail_btn = ft.FilledButton(
            content=ft.Text("Ver Detalles Completos", size=13, weight=ft.FontWeight.BOLD),
            icon=safe_icon("visibility"),
            style=ft.ButtonStyle(
                bgcolor=ACCENT_PURPLE,
                color="#FFFFFF",
                padding=ft.Padding(left=18, right=18, top=14, bottom=14),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self._on_detail(self._game)
        )

        if self._is_in_cart:
            cart_btn = ft.OutlinedButton(
                content=ft.Text("En Carrito ✓", size=13, weight=ft.FontWeight.BOLD),
                icon=safe_icon("check"),
                style=ft.ButtonStyle(
                    color=ACCENT_GREEN,
                    side=ft.BorderSide(1.5, ACCENT_GREEN),
                    padding=ft.Padding(left=18, right=18, top=14, bottom=14),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                disabled=True
            )
        else:
            cart_btn = ft.OutlinedButton(
                content=ft.Text("Añadir al Carrito", size=13, weight=ft.FontWeight.BOLD),
                icon=safe_icon("add_shopping_cart"),
                style=ft.ButtonStyle(
                    color="#FFFFFF",
                    side=ft.BorderSide(1.5, ACCENT_PURPLE),
                    padding=ft.Padding(left=18, right=18, top=14, bottom=14),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=lambda _: self._on_add_cart(self._game)
            )
        action_controls = [detail_btn]
        if self._game.demo_url:
            demo_hero_btn = ft.FilledButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(safe_icon("play_circle_filled"), size=16, color="#38BDF8"),
                        ft.Text("Probar Demo Online", size=13, weight=ft.FontWeight.BOLD, color="#38BDF8")
                    ],
                    tight=True,
                    spacing=6
                ),
                url=self._game.demo_url,
                style=ft.ButtonStyle(
                    bgcolor="#082F49",
                    side=ft.BorderSide(1.5, ACCENT_CYAN),
                    padding=ft.Padding(left=16, right=16, top=14, bottom=14),
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            )
            action_controls.append(demo_hero_btn)
        action_controls.append(cart_btn)

        actions_row = ft.Row(
            controls=action_controls,
            spacing=12,
            wrap=True
        )

        left_column = ft.Column(
            controls=[
                ft.Row(controls=badges, spacing=8),
                title_text,
                desc_text,
                reviews_row,
                ft.Container(height=4),
                price_row,
                actions_row
            ],
            spacing=12,
            expand=True
        )

        # Right Image Showcase
        right_image = ft.Container(
            content=ft.Image(
                src=self._game.cover_image,
                width=420,
                height=250,
                fit=ft.BoxFit.COVER,
                border_radius=14,
                error_content=ft.Container(
                    content=ft.Icon(safe_icon("sports_esports"), size=64, color=ACCENT_PURPLE),
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#1E1B4B"
                )
            ),
            border_radius=14,
            border=ft.Border.all(2, "#4F46E5"),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color="rgba(79, 70, 229, 0.35)", offset=ft.Offset(0, 4))
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    left_column,
                    right_image
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=28
            ),
            padding=28,
            border_radius=16,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1E1B4B", "#101935", "#0F172A"]
            ),
            border=ft.Border.all(1.5, "#4F46E5"),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=30, color="rgba(79, 70, 229, 0.25)", offset=ft.Offset(0, 4)),
            margin=ft.Margin(left=0, right=0, top=10, bottom=22)
        )
