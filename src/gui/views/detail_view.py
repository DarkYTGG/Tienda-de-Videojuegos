"""Detailed Game View presenting screenshots, specs, reviews, and purchasing options."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from .base_view import BaseView
from ...application.use_cases import GetGameDetailUseCase, ManageCartUseCase
from ...domain.entities import Game
from ...domain.exceptions import GameNotFoundError
from ..theme import (
    BG_SURFACE,
    BG_HEADER,
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
from ..components.footer import StoreFooterComponent


class GameDetailView(BaseView):
    """Rich game overview page presenting full media, specifications, reviews, and cart actions."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        get_game_uc: GetGameDetailUseCase,
        cart_manager: ManageCartUseCase,
        game_slug: str,
        notify_fn: Optional[Callable[[str, str], None]] = None
    ):
        super().__init__(page, navigate_fn)
        self._get_game_uc = get_game_uc
        self._cart_manager = cart_manager
        self._slug = game_slug
        self._notify = notify_fn

    def _on_add_cart(self, game: Game):
        try:
            self._cart_manager.add_game(game)
            if self._notify:
                self._notify(f"¡'{game.title}' añadido al carrito de compras!", "success")
            if self.page:
                self.page.update()
        except Exception as e:
            if self._notify:
                self._notify(str(e), "warning")

    def _on_buy_now(self, game: Game):
        try:
            if not self._cart_manager.has_game(game.id):
                self._cart_manager.add_game(game)
            self.navigate("checkout", None)
        except Exception as e:
            if self._notify:
                self._notify(str(e), "warning")

    def build(self) -> ft.Control:
        try:
            game = self._get_game_uc.execute_by_slug(self._slug)
        except GameNotFoundError:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(safe_icon("error_outline"), size=64, color="#EF4444"),
                        ft.Text("Videojuego no encontrado", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.FilledButton(
                            content=ft.Text("Volver a la Tienda"),
                            on_click=lambda _: self.navigate("home", None)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16
                ),
                padding=60,
                alignment=ft.Alignment.CENTER
            )

        is_in_cart = self._cart_manager.has_game(game.id)

        # Back Navigation Row
        back_row = ft.Row(
            controls=[
                ft.OutlinedButton(
                    content=ft.Text("← Volver a la Tienda", size=13, weight=ft.FontWeight.W_600),
                    style=ft.ButtonStyle(
                        color=TEXT_PRIMARY,
                        side=ft.BorderSide(1, BORDER_COLOR),
                        shape=ft.RoundedRectangleBorder(radius=6)
                    ),
                    on_click=lambda _: self.navigate("home", None)
                ),
                ft.Text(" / ", size=13, color=TEXT_MUTED),
                ft.Text(game.genre, size=13, color=ACCENT_CYAN),
                ft.Text(" / ", size=13, color=TEXT_MUTED),
                ft.Text(game.title, size=13, color=TEXT_SECONDARY)
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # --- Left Column: Media & Story & Specs ---
        banner_img = ft.Container(
            content=ft.Image(
                src=game.banner_image or game.cover_image,
                width=720,
                height=340,
                fit=ft.BoxFit.COVER,
                border_radius=12,
                error_content=ft.Container(
                    content=ft.Icon(safe_icon("videogame_asset"), size=80, color=ACCENT_PURPLE),
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#1E1B4B"
                )
            ),
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        # Tags row
        tags_controls = [create_badge(game.genre, bg_color="#1E293B", text_color=ACCENT_CYAN, font_size=11)]
        for tag in game.tags:
            tags_controls.append(create_badge(tag, bg_color="#0F172A", text_color=TEXT_SECONDARY, font_size=11))

        tags_row = ft.Row(controls=tags_controls, wrap=True, spacing=6)

        # Description Card
        desc_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Acerca de este juego", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Text(game.full_description, size=14, color=TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Text("Características Principales", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(safe_icon("check_circle"), size=16, color=ACCENT_GREEN),
                                    ft.Text(feat, size=13, color=TEXT_SECONDARY)
                                ],
                                spacing=8
                            )
                            for feat in game.features
                        ],
                        spacing=6
                    )
                ],
                spacing=12
            ),
            bgcolor=BG_SURFACE,
            padding=22,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        # Technical Requirements Card
        specs_rows = []
        for k, v in game.system_requirements.items():
            specs_rows.append(
                ft.Row(
                    controls=[
                        ft.Text(f"{k}:", size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, width=120),
                        ft.Text(v, size=12, color=TEXT_SECONDARY, expand=True)
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            )

        specs_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Requisitos del Sistema (PC)", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Column(controls=specs_rows, spacing=8)
                ],
                spacing=10
            ),
            bgcolor=BG_SURFACE,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        left_column = ft.Column(
            controls=[
                banner_img,
                tags_row,
                desc_card,
                specs_card
            ],
            spacing=18,
            expand=2
        )

        # --- Right Column: Buy Box Sidebar ---
        cover_thumbnail = ft.Container(
            content=ft.Image(
                src=game.cover_image,
                width=340,
                height=180,
                fit=ft.BoxFit.COVER,
                border_radius=10,
                error_content=ft.Container(
                    content=ft.Icon(safe_icon("image"), size=48, color=TEXT_MUTED),
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#1E1B4B"
                )
            ),
            border_radius=10,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        # Reviews summary box
        reviews_box = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon("star"), color=ACCENT_AMBER, size=24),
                    ft.Column(
                        controls=[
                            ft.Text(f"Valoración: {game.rating:.1f} / 5.0", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text(game.rating_summary, size=11, color=ACCENT_CYAN)
                        ],
                        spacing=1
                    )
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor="#0F172A",
            padding=12,
            border_radius=8,
            border=ft.Border.all(1, BORDER_COLOR)
        )

        # Metadata table
        meta_items = [
            ("Desarrollador", game.developer),
            ("Editor", game.publisher),
            ("Fecha de estreno", game.release_date),
            ("Plataforma", "Windows PC"),
            ("Licencia", "Digital PixelVault Key")
        ]
        meta_controls = []
        for label, val in meta_items:
            meta_controls.append(
                ft.Row(
                    controls=[
                        ft.Text(label, size=12, color=TEXT_MUTED, width=110),
                        ft.Text(val, size=12, weight=ft.FontWeight.W_500, color=TEXT_PRIMARY, expand=True)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        # Price Display Box
        price_display_box = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Comprar {game.title}", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row(
                        controls=[
                            create_price_display(
                                price=game.price,
                                discount_percent=game.discount_percent,
                                final_price=game.final_price,
                                show_badge=True
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                spacing=8
            ),
            bgcolor="#1E293B",
            padding=14,
            border_radius=8
        )

        # Action Buttons
        if is_in_cart:
            add_cart_btn = ft.FilledButton(
                content=ft.Text("En el Carrito ✓", size=14, weight=ft.FontWeight.BOLD),
                icon=safe_icon("check"),
                style=ft.ButtonStyle(
                    bgcolor=ACCENT_GREEN,
                    color="#FFFFFF",
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(left=16, right=16, top=14, bottom=14)
                ),
                disabled=True
            )
        else:
            add_cart_btn = ft.FilledButton(
                content=ft.Text("Añadir al Carrito", size=14, weight=ft.FontWeight.BOLD),
                icon=safe_icon("add_shopping_cart"),
                style=ft.ButtonStyle(
                    bgcolor=ACCENT_PURPLE,
                    color="#FFFFFF",
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(left=16, right=16, top=14, bottom=14)
                ),
                on_click=lambda _: self._on_add_cart(game)
            )

        buy_now_btn = ft.OutlinedButton(
            content=ft.Text("Comprar Ahora (Simulación)", size=13, weight=ft.FontWeight.BOLD),
            icon=safe_icon("bolt"),
            style=ft.ButtonStyle(
                color=ACCENT_CYAN,
                side=ft.BorderSide(1.5, ACCENT_CYAN),
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12)
            ),
            on_click=lambda _: self._on_buy_now(game)
        )

        academic_pill = ft.Container(
            content=ft.Text(
                "🎮 Simulación de tienda académica. Al comprar se genera una clave de activación.",
                size=11,
                color=TEXT_MUTED,
                text_align=ft.TextAlign.CENTER
            ),
            bgcolor="#0B0F19",
            padding=8,
            border_radius=6
        )

        right_column = ft.Container(
            content=ft.Column(
                controls=[
                    cover_thumbnail,
                    reviews_box,
                    ft.Column(controls=meta_controls, spacing=6),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    price_display_box,
                    add_cart_btn,
                    buy_now_btn,
                    academic_pill
                ],
                spacing=14
            ),
            bgcolor=BG_SURFACE,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR),
            width=360
        )

        body_layout = ft.Row(
            controls=[left_column, right_column],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=24
        )

        return ft.ListView(
            controls=[
                ft.Container(height=10),
                back_row,
                ft.Container(height=12),
                body_layout,
                StoreFooterComponent().build()
            ],
            spacing=0,
            padding=ft.Padding(left=32, right=32, top=16, bottom=20),
            expand=True
        )
