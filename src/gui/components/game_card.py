"""Reusable game card component presenting game cover, details, pricing, and actions."""
from typing import Callable, Optional
import flet as ft

from ...domain.entities import Game
from ..theme import (
    BG_SURFACE,
    BG_SURFACE_HOVER,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_GREEN_BG,
    ACCENT_AMBER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    create_badge,
    create_price_display,
    safe_icon,
)


class GameCardComponent:
    """Component rendering an individual game card with Steam/itch.io presentation."""

    def __init__(
        self,
        game: Game,
        on_detail: Callable[[Game], None],
        on_add_cart: Callable[[Game], None],
        is_in_cart: bool = False,
        width: int = 280
    ):
        self._game = game
        self._on_detail = on_detail
        self._on_add_cart = on_add_cart
        self._is_in_cart = is_in_cart
        self._width = width

    def _build_image_fallback(self) -> ft.Container:
        """Fallback container shown if image fails to load or offline."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(safe_icon("videogame_asset"), size=48, color=ACCENT_PURPLE),
                    ft.Text(self._game.genre, size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_600)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1E1B4B", "#0F172A"]
            ),
            alignment=ft.Alignment.CENTER,
            expand=True
        )

    def build(self) -> ft.Container:
        # Badges stack on image
        top_badges = []
        if self._game.is_on_sale:
            top_badges.append(
                create_badge(
                    self._game.discount_badge,
                    bg_color=ACCENT_GREEN_BG,
                    text_color="#4ADE80",
                    font_size=11
                )
            )
        if self._game.is_new:
            top_badges.append(
                create_badge("NUEVO", bg_color="#B45309", text_color="#FDE68A", font_size=10)
            )
        if self._game.is_indie:
            top_badges.append(
                create_badge("INDIE", bg_color="#0E7490", text_color="#A5F3FC", font_size=10)
            )

        # Image cover
        image_cover = ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src=self._game.cover_image,
                        width=self._width,
                        height=160,
                        fit=ft.BoxFit.COVER,
                        border_radius=ft.BorderRadius(top_left=12, top_right=12, bottom_left=0, bottom_right=0),
                        error_content=self._build_image_fallback()
                    ),
                    ft.Container(
                        content=ft.Row(controls=top_badges, spacing=4, tight=True),
                        left=8,
                        top=8
                    )
                ]
            ),
            height=160
        )

        # Content details
        title_text = ft.Text(
            self._game.title,
            size=15,
            weight=ft.FontWeight.BOLD,
            color=TEXT_PRIMARY,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS
        )

        dev_row = ft.Row(
            controls=[
                ft.Icon(safe_icon("business"), size=13, color=TEXT_MUTED),
                ft.Text(
                    self._game.developer,
                    size=12,
                    color=TEXT_SECONDARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True
                )
            ],
            spacing=4,
            tight=True
        )

        rating_row = ft.Row(
            controls=[
                ft.Icon(safe_icon("star"), size=14, color=ACCENT_AMBER),
                ft.Text(f"{self._game.rating:.1f}", size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(f"({self._game.reviews_count:,})", size=11, color=TEXT_MUTED),
                create_badge(self._game.genre, bg_color="#1E293B", text_color=ACCENT_CYAN, font_size=10)
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Price block
        pricing = create_price_display(
            price=self._game.price,
            discount_percent=self._game.discount_percent,
            final_price=self._game.final_price,
            show_badge=True
        )

        # Action Buttons
        detail_btn = ft.OutlinedButton(
            content=ft.Text("Detalles", size=12, weight=ft.FontWeight.W_600),
            style=ft.ButtonStyle(
                color=TEXT_PRIMARY,
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.Padding(left=10, right=10, top=6, bottom=6)
            ),
            on_click=lambda _: self._on_detail(self._game),
            expand=True
        )

        if self._is_in_cart:
            cart_btn = ft.FilledButton(
                content=ft.Text("En Carrito ✓", size=12, weight=ft.FontWeight.BOLD),
                icon=safe_icon("check"),
                style=ft.ButtonStyle(
                    bgcolor=ACCENT_GREEN,
                    color="#FFFFFF",
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.Padding(left=8, right=8, top=6, bottom=6)
                ),
                disabled=True,
                expand=True
            )
        else:
            cart_btn = ft.FilledButton(
                content=ft.Text("Añadir", size=12, weight=ft.FontWeight.BOLD),
                icon=safe_icon("add_shopping_cart"),
                style=ft.ButtonStyle(
                    bgcolor=ACCENT_PURPLE,
                    color="#FFFFFF",
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.Padding(left=8, right=8, top=6, bottom=6)
                ),
                on_click=lambda _: self._on_add_cart(self._game),
                expand=True
            )

        actions_row = ft.Row(
            controls=[detail_btn, cart_btn],
            spacing=8
        )

        card_body = ft.Container(
            content=ft.Column(
                controls=[
                    title_text,
                    dev_row,
                    rating_row,
                    ft.Divider(color="#22304A", height=1),
                    pricing,
                    actions_row
                ],
                spacing=10
            ),
            padding=14
        )

        return ft.Container(
            content=ft.Column(
                controls=[image_cover, card_body],
                spacing=0
            ),
            width=self._width,
            bgcolor=BG_SURFACE,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR),
            ink=False
        )
