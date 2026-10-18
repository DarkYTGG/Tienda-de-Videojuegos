"""Interactive catalog filter, search, and sorting bar component."""
from typing import Callable, List, Optional
import flet as ft

from ...application.dtos import GameFilterDTO
from ..theme import (
    BG_SURFACE,
    BG_INPUT,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    BORDER_COLOR,
    safe_icon,
)


class FilterBarComponent:
    """Provides UI controls for searching, filtering by genre/sales/indie, and sorting."""

    def __init__(
        self,
        current_filter: GameFilterDTO,
        available_genres: List[str],
        on_filter_changed: Callable[[GameFilterDTO], None],
        on_reset: Callable[[], None]
    ):
        self._filter = current_filter
        self._genres = ["Todos"] + available_genres
        self._on_filter_changed = on_filter_changed
        self._on_reset = on_reset

    def _trigger_change(self):
        self._on_filter_changed(self._filter)

    def _on_search_change(self, e):
        self._filter.search_query = e.control.value or ""
        self._trigger_change()

    def _on_genre_change(self, e):
        self._filter.genre = e.control.value or "Todos"
        self._trigger_change()

    def _on_sales_toggle(self, e):
        self._filter.only_sales = bool(e.control.value)
        self._trigger_change()

    def _on_indie_toggle(self, e):
        self._filter.only_indie = bool(e.control.value)
        self._trigger_change()

    def _on_sort_change(self, e):
        self._filter.sort_by = e.control.value or "destacados"
        self._trigger_change()

    def build(self) -> ft.Container:
        # Search input
        search_field = ft.TextField(
            value=self._filter.search_query,
            hint_text="Buscar por título, desarrollador o etiqueta...",
            text_size=13,
            height=42,
            content_padding=ft.Padding(left=12, right=12, top=0, bottom=0),
            bgcolor=BG_INPUT,
            color=TEXT_PRIMARY,
            hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            prefix_icon=safe_icon("search"),
            on_change=self._on_search_change,
            expand=True
        )

        # Genre dropdown
        genre_options = [
            ft.dropdown.Option(key=g, text=f"Género: {g}" if g != "Todos" else "Todos los géneros")
            for g in self._genres
        ]
        genre_dropdown = ft.Dropdown(
            options=genre_options,
            value=self._filter.genre,
            text_size=12,
            height=42,
            content_padding=ft.Padding(left=10, right=10, top=0, bottom=0),
            bgcolor=BG_INPUT,
            color=TEXT_PRIMARY,
            width=200,
            on_select=self._on_genre_change
        )

        # Sort dropdown
        sort_options = [
            ft.dropdown.Option(key="destacados", text="Destacados y Populares"),
            ft.dropdown.Option(key="precio_menor", text="Precio: Menor a Mayor"),
            ft.dropdown.Option(key="precio_mayor", text="Precio: Mayor a Menor"),
            ft.dropdown.Option(key="valoracion", text="Mejor Valorados"),
            ft.dropdown.Option(key="nombre", text="Alfabético A-Z"),
        ]
        sort_dropdown = ft.Dropdown(
            options=sort_options,
            value=self._filter.sort_by,
            text_size=12,
            height=42,
            content_padding=ft.Padding(left=10, right=10, top=0, bottom=0),
            bgcolor=BG_INPUT,
            color=TEXT_PRIMARY,
            width=210,
            on_select=self._on_sort_change
        )

        # Toggle switches
        sales_switch = ft.Switch(
            label="Solo Ofertas 🔥",
            value=self._filter.only_sales,
            active_color="#10B981",
            label_text_style=ft.TextStyle(color=TEXT_PRIMARY, size=12, weight=ft.FontWeight.W_600),
            on_change=self._on_sales_toggle
        )

        indie_switch = ft.Switch(
            label="Solo Indies 👾",
            value=self._filter.only_indie,
            active_color=ACCENT_CYAN,
            label_text_style=ft.TextStyle(color=TEXT_PRIMARY, size=12, weight=ft.FontWeight.W_600),
            on_change=self._on_indie_toggle
        )

        # Reset button
        reset_button = ft.OutlinedButton(
            content=ft.Text("Restablecer", size=12),
            icon=safe_icon("filter_alt_off"),
            style=ft.ButtonStyle(
                color=TEXT_SECONDARY,
                side=ft.BorderSide(1, BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            on_click=lambda _: self._on_reset()
        )

        # Row 1: Search + Dropdowns
        row1 = ft.Row(
            controls=[
                search_field,
                genre_dropdown,
                sort_dropdown
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Row 2: Toggles + Reset
        row2 = ft.Row(
            controls=[
                ft.Row(controls=[sales_switch, indie_switch], spacing=16, tight=True),
                reset_button
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        return ft.Container(
            content=ft.Column(
                controls=[row1, row2],
                spacing=12
            ),
            padding=16,
            bgcolor=BG_SURFACE,
            border_radius=12,
            border=ft.Border.all(1, BORDER_COLOR),
            margin=ft.Margin(left=0, right=0, top=10, bottom=20)
        )
