"""Main Storefront view featuring Hero Banner, Curated Sections, and Deals."""
from typing import Callable, Optional, Dict, Any
import flet as ft

from .base_view import BaseView
from ...application.use_cases import ListGamesUseCase, ManageCartUseCase
from ...domain.entities import Game
from ..theme import (
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    ACCENT_GREEN,
    create_section_header,
    safe_icon,
)
from ..components.hero_banner import FeaturedHeroBannerComponent
from ..components.game_card import GameCardComponent
from ..components.footer import StoreFooterComponent


class StoreView(BaseView):
    """Primary storefront view combining Steam structure with itch.io indie spirit."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        list_games_uc: ListGamesUseCase,
        cart_manager: ManageCartUseCase,
        notify_fn: Optional[Callable[[str, str], None]] = None,
        notify: Optional[Callable[[str, str], None]] = None,
        **kwargs: Any
    ):
        super().__init__(page, navigate_fn)
        self._list_uc = list_games_uc
        self._cart_manager = cart_manager
        self._notify = notify_fn or notify
        self._on_cart_open = kwargs.get("on_cart_open") or kwargs.get("open_cart_drawer")

    def _on_detail(self, game: Game):
        self.navigate("detail", {"slug": game.slug})

    def _on_add_cart(self, game: Game):
        try:
            self._cart_manager.add_game(game)
            if self._notify:
                self._notify(f"¡'{game.title}' añadido al carrito de compras!", "success")
            if self._on_cart_open:
                self._on_cart_open()
            elif self.page:
                self.page.update()
        except Exception as e:
            if self._notify:
                self._notify(str(e), "warning")

    def _build_game_row(self, games, max_items: int = 4) -> ft.Row:
        cards = []
        for g in games[:max_items]:
            is_in_cart = self._cart_manager.has_game(g.id)
            card = GameCardComponent(
                game=g,
                on_detail=self._on_detail,
                on_add_cart=self._on_add_cart,
                is_in_cart=is_in_cart,
                width=275
            )
            cards.append(card.build())

        return ft.Row(
            controls=cards,
            spacing=16,
            wrap=True,
            alignment=ft.MainAxisAlignment.START
        )

    def build(self) -> ft.Control:
        featured_games = self._list_uc.get_featured()
        on_sale_games = self._list_uc.get_on_sale()
        new_releases = self._list_uc.get_new_releases()
        indie_games = self._list_uc.get_indie()

        controls = []

        # 1. Hero Promotional Banner
        if featured_games:
            main_hero = featured_games[0]
            is_hero_in_cart = self._cart_manager.has_game(main_hero.id)
            hero_component = FeaturedHeroBannerComponent(
                game=main_hero,
                on_detail=self._on_detail,
                on_add_cart=self._on_add_cart,
                is_in_cart=is_hero_in_cart
            )
            controls.append(hero_component.build())

        # 2. Key Value Proposition Bar
        value_items = [
            ("vpn_key", "#8B5CF6", "Claves Digitales", "Generación instantánea"),
            ("auto_awesome", "#06B6D4", "Curaduría Indie", "Espacio a creadores"),
            ("verified_user", "#10B981", "Simulación Segura", "Fines académicos"),
            ("storage", "#F59E0B", "Persistencia JSON", "Auditable en data/"),
        ]
        val_cards = []
        for icon_name, color, title, subtitle in value_items:
            val_cards.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(safe_icon(icon_name), size=20, color=color),
                                bgcolor="#0B132B",
                                padding=8,
                                border_radius=8,
                                border=ft.Border.all(1, color)
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                    ft.Text(subtitle, size=11, color=TEXT_SECONDARY)
                                ],
                                spacing=1
                            )
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    bgcolor="#111A2E",
                    border=ft.Border.all(1, "#22304A"),
                    border_radius=10,
                    padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                    expand=True
                )
            )
        val_bar = ft.Container(
            content=ft.Row(controls=val_cards, spacing=12),
            margin=ft.Margin(left=0, right=0, top=18, bottom=16)
        )
        controls.append(val_bar)

        # 3. Section: Demos Jugables Online en Navegador (Call of Duty Web Editions)
        demo_games = self._list_uc.get_demo_games()
        if demo_games:
            demo_header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(safe_icon("sports_esports"), size=15, color="#FFFFFF"),
                                            ft.Text("WEB PLAYABLE DEMOS", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF")
                                        ],
                                        spacing=5,
                                        tight=True
                                    ),
                                    bgcolor="#0284C7",
                                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                    border_radius=4
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text("Demos Jugables Online en Navegador", size=19, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                        ft.Text("Prueba estos títulos legendarios de Call of Duty directamente en tu navegador con un solo clic.", size=12, color=TEXT_SECONDARY)
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(safe_icon("wifi"), size=14, color=ACCENT_CYAN),
                                ft.Text("Sin descargas ni instalaciones requeridas", size=12, weight=ft.FontWeight.W_600, color=ACCENT_CYAN)
                            ],
                            spacing=4
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                gradient=ft.LinearGradient(
                    colors=["#082F49", "#0C1E38", "#0B1528"],
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT
                ),
                border=ft.Border.all(1.5, ACCENT_CYAN),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color="rgba(6, 182, 212, 0.25)", offset=ft.Offset(0, 4)),
                border_radius=12,
                margin=ft.Margin(left=0, right=0, top=12, bottom=16)
            )
            controls.append(demo_header)
            controls.append(self._build_game_row(demo_games, max_items=4))

        # 4. Section: Super Ofertas (Steam-style discount wall)
        if on_sale_games:
            controls.append(
                create_section_header(
                    title="Super Ofertas & Descuentos",
                    subtitle="Ahorra hasta un 70% en títulos seleccionados por tiempo limitado.",
                    icon="local_fire_department",
                    accent_color="#DC2626",
                    action_text="Ver todas las ofertas",
                    action_callback=lambda _: self.navigate("catalog", {"only_sales": True})
                )
            )
            controls.append(self._build_game_row(on_sale_games, max_items=4))

        # 3. Section: Novedades & Tendencias
        if new_releases:
            controls.append(
                create_section_header(
                    title="Novedades & Tendencias 2026",
                    subtitle="Los lanzamientos más recientes recién llegados a la plataforma.",
                    icon="auto_awesome",
                    accent_color=ACCENT_PURPLE,
                    action_text="Explorar novedades",
                    action_callback=lambda _: self.navigate("catalog", {"sort": "destacados"})
                )
            )
            controls.append(self._build_game_row(new_releases, max_items=4))

        # 4. Section: Rincón Indie & Experimental (itch.io inspiration)
        if indie_games:
            controls.append(
                create_section_header(
                    title="Rincón Indie & Experimental",
                    subtitle="Juegos innovadores y creativos creados por estudios y desarrolladores independientes.",
                    icon="sports_esports",
                    accent_color=ACCENT_CYAN,
                    action_text="Ver espacio indie",
                    action_callback=lambda _: self.navigate("catalog", {"only_indie": True})
                )
            )
            controls.append(self._build_game_row(indie_games, max_items=4))

        # 5. Section: Más Juegos Destacados
        other_featured = [g for g in featured_games if g.id != featured_games[0].id]
        if other_featured:
            controls.append(
                create_section_header(
                    title="Destacados de la Comunidad",
                    subtitle="Títulos altamente valorados por los usuarios de PixelVault.",
                    icon="thumb_up",
                    accent_color="#2563EB",
                    action_text="Ir al catálogo completo",
                    action_callback=lambda _: self.navigate("catalog", None)
                )
            )
            controls.append(self._build_game_row(other_featured, max_items=4))

        # 6. Call to Action Banner
        cta_banner = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("¿Buscas algo específico?", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text(
                                "Filtra por géneros, rangos de precio, valoraciones o busca directamente en nuestro catálogo de +18 títulos.",
                                size=13,
                                color=TEXT_SECONDARY
                            )
                        ],
                        spacing=4,
                        expand=True
                    ),
                    ft.FilledButton(
                        content=ft.Text("Abrir Catálogo Completo", size=14, weight=ft.FontWeight.BOLD),
                        icon=safe_icon("search"),
                        style=ft.ButtonStyle(
                            bgcolor=ACCENT_PURPLE,
                            color="#FFFFFF",
                            padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _: self.navigate("catalog", None)
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor="#162032",
            border_radius=12,
            border=ft.Border.all(1, "#22304A"),
            padding=24,
            margin=ft.Margin(left=0, right=0, top=28, bottom=20)
        )
        controls.append(cta_banner)

        # 7. Academic Footer
        controls.append(StoreFooterComponent().build())

        return ft.ListView(
            controls=controls,
            spacing=0,
            padding=ft.Padding(left=32, right=32, top=16, bottom=20),
            expand=True
        )
