"""Full Catalog View with interactive search, category filters, and sorting."""
from typing import Callable, Optional, Dict, Any, List
import flet as ft

from .base_view import BaseView
from ...application.use_cases import (
    SearchAndFilterGamesUseCase,
    ListGamesUseCase,
    ManageCartUseCase,
)
from ...application.dtos import GameFilterDTO
from ...domain.entities import Game
from ..theme import (
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    BORDER_COLOR,
    create_badge,
    safe_icon,
)
from ..components.filter_bar import FilterBarComponent
from ..components.game_card import GameCardComponent
from ..components.footer import StoreFooterComponent


class CatalogView(BaseView):
    """Interactive catalog view with instant live filtering, sorting, and responsive layout."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None],
        search_filter_uc: SearchAndFilterGamesUseCase,
        list_games_uc: ListGamesUseCase,
        cart_manager: ManageCartUseCase,
        initial_params: Optional[Dict[str, Any]] = None,
        notify_fn: Optional[Callable[[str, str], None]] = None,
        notify: Optional[Callable[[str, str], None]] = None,
        **kwargs: Any
    ):
        super().__init__(page, navigate_fn)
        self._search_filter_uc = search_filter_uc
        self._list_uc = list_games_uc
        self._cart_manager = cart_manager
        self._notify = notify_fn or notify

        params = initial_params or {}
        self._current_filter = GameFilterDTO(
            search_query=params.get("search", ""),
            genre=params.get("genre", "Todos"),
            only_sales=bool(params.get("only_sales", False)),
            only_indie=bool(params.get("only_indie", False)),
            sort_by=params.get("sort", "destacados")
        )

        self._cards_container = ft.Row(
            controls=[],
            spacing=16,
            wrap=True,
            alignment=ft.MainAxisAlignment.START
        )
        self._counter_text = ft.Text("", size=14, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500)

    def _on_detail(self, game: Game):
        self.navigate("detail", {"slug": game.slug})

    def _on_add_cart(self, game: Game):
        try:
            self._cart_manager.add_game(game)
            if self._notify:
                self._notify(f"¡'{game.title}' añadido al carrito!", "success")
            self._refresh_cards()
            if self.page:
                self.page.update()
        except Exception as e:
            if self._notify:
                self._notify(str(e), "warning")

    def _refresh_cards(self):
        games = self._search_filter_uc.execute(self._current_filter)
        self._counter_text.value = f"Mostrando {len(games)} videojuego{'s' if len(games) != 1 else ''}"

        if not games:
            empty_view = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(safe_icon("search_off"), size=64, color=TEXT_MUTED),
                        ft.Text(
                            "No se encontraron videojuegos",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY
                        ),
                        ft.Text(
                            "Intenta modificar los términos de búsqueda o restablecer los filtros aplicados.",
                            size=13,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.FilledButton(
                            content=ft.Text("Restablecer Filtros", size=13),
                            icon=safe_icon("restart_alt"),
                            style=ft.ButtonStyle(bgcolor=ACCENT_PURPLE, color="#FFFFFF"),
                            on_click=lambda _: self._reset_filters()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=60,
                alignment=ft.Alignment.CENTER,
                expand=True
            )
            self._cards_container.controls = [empty_view]
        else:
            cards = []
            for g in games:
                is_in_cart = self._cart_manager.has_game(g.id)
                card = GameCardComponent(
                    game=g,
                    on_detail=self._on_detail,
                    on_add_cart=self._on_add_cart,
                    is_in_cart=is_in_cart,
                    width=275
                )
                cards.append(card.build())
            self._cards_container.controls = cards

    def _on_filter_changed(self, new_filter: GameFilterDTO):
        self._current_filter = new_filter
        self._refresh_cards()
        if self.page:
            self.page.update()

    def _reset_filters(self):
        self._current_filter = GameFilterDTO()
        self._refresh_cards()
        if self._notify:
            self._notify("Filtros restablecidos al valor predeterminado.", "info")
        if self.page:
            self.page.update()

    def build(self) -> ft.Control:
        available_genres = self._list_uc.get_genres()

        # Title header
        title_banner = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(safe_icon("grid_view"), color="#FFFFFF", size=22),
                            bgcolor=ACCENT_PURPLE,
                            padding=8,
                            border_radius=8
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Catálogo de Videojuegos", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text("Explora nuestra colección completa con filtros avanzados y ordenamiento.", size=13, color=TEXT_SECONDARY)
                            ],
                            spacing=2
                        )
                    ],
                    spacing=12,
                    tight=True
                ),
                ft.Container(
                    content=self._counter_text,
                    bgcolor="#162032",
                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                    border_radius=8,
                    border=ft.Border.all(1, BORDER_COLOR)
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        filter_bar = FilterBarComponent(
            current_filter=self._current_filter,
            available_genres=available_genres,
            on_filter_changed=self._on_filter_changed,
            on_reset=self._reset_filters
        )

        # Initial populate
        self._refresh_cards()

        return ft.ListView(
            controls=[
                ft.Container(height=10),
                title_banner,
                filter_bar.build(),
                self._cards_container,
                StoreFooterComponent().build()
            ],
            spacing=0,
            padding=ft.Padding(left=32, right=32, top=16, bottom=20),
            expand=True
        )
