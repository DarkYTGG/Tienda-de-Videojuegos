"""Academic and store footer component."""
import flet as ft

from ..theme import (
    BG_HEADER,
    ACCENT_PURPLE,
    ACCENT_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER_COLOR,
    create_badge,
    safe_icon,
)


class StoreFooterComponent:
    """Footer acknowledging university course context, teacher reference, and tech stack."""

    def build(self) -> ft.Container:
        brand_col = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(safe_icon("sports_esports"), color=ACCENT_PURPLE, size=20),
                        ft.Text("PIXELVAULT", size=16, weight=ft.FontWeight.W_900, color=TEXT_PRIMARY),
                    ],
                    spacing=6,
                    tight=True
                ),
                ft.Text(
                    "Tienda digital de videojuegos simulada con diseño híbrido Steam e itch.io.",
                    size=12,
                    color=TEXT_SECONDARY
                ),
                ft.Text(
                    "Proyecto Académico — Programación IV",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ACCENT_CYAN
                )
            ],
            spacing=4,
            expand=True
        )

        academic_col = ft.Column(
            controls=[
                ft.Text("Referencia Académica", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text("IUT 'Antonio José de Sucre'", size=12, color=TEXT_SECONDARY),
                ft.Text("Docente: Prof. Yoher Alejandro Vazquez Salinas", size=12, color=TEXT_SECONDARY),
                ft.Text("Arquitectura en Capas & Programación Orientada a Objetos", size=11, color=TEXT_MUTED)
            ],
            spacing=3,
            expand=True
        )

        tech_col = ft.Column(
            controls=[
                ft.Text("Tecnologías Utilizadas", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Row(
                    controls=[
                        create_badge("Python 3.14", bg_color="#1E293B", text_color="#38BDF8", font_size=11),
                        create_badge("Flet 1.0", bg_color="#1E293B", text_color="#A78BFA", font_size=11),
                        create_badge("uv package manager", bg_color="#1E293B", text_color="#34D399", font_size=11),
                        create_badge("JSON Persistence", bg_color="#1E293B", text_color="#FBBF24", font_size=11),
                    ],
                    wrap=True,
                    spacing=6
                )
            ],
            spacing=6,
            expand=True
        )

        content_row = ft.Row(
            controls=[brand_col, academic_col, tech_col],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20
        )

        copyright_text = ft.Text(
            "© 2026 PixelVault — Trabajo práctico con fines educativos. Todos los nombres ficticios y referencias pertenecen a sus respectivos autores.",
            size=11,
            color=TEXT_MUTED,
            text_align=ft.TextAlign.CENTER
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    content_row,
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Container(content=copyright_text, alignment=ft.Alignment.CENTER)
                ],
                spacing=16
            ),
            bgcolor=BG_HEADER,
            padding=ft.Padding(left=28, right=28, top=24, bottom=20),
            border=ft.Border(top=ft.BorderSide(1, BORDER_COLOR)),
            margin=ft.Margin(left=0, right=0, top=30, bottom=0)
        )
