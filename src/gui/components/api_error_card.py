"""Visual Exception and Error Display component for PixelVault GUI when API fails.

Renders modern cyberpunk glassmorphism card detailing the HTTP Status Code,
Exception Class, Reason, and Recovery action.
"""
from typing import Callable, Optional
import flet as ft

from ..theme import (
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_GREEN,
    ACCENT_PURPLE,
    safe_icon,
)


class ApiErrorCardComponent:
    """Displays a full-view visual exception card when the in-memory API repository encounters an HTTP error."""

    def __init__(
        self,
        status_code: int,
        status_message: str,
        exception_name: Optional[str] = None,
        error_detail: Optional[str] = None,
        on_retry: Optional[Callable[[], None]] = None,
    ):
        self.status_code = status_code
        self.status_message = status_message
        self.exception_name = exception_name or "ApiError"
        self.error_detail = error_detail or "No se pudo completar la sincronización con la API."
        self.on_retry = on_retry

    def build(self) -> ft.Container:
        border_color = "#DC2626" if self.status_code in (401, 403, 500) else "#EA580C"

        card_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(safe_icon("error_outline"), size=36, color="#EF4444"),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    f"Error de Conexión con la API (HTTP {self.status_code})",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"
                                ),
                                ft.Text(
                                    f"Tipo de Error: {self.exception_name}",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color="#F87171"
                                )
                            ],
                            spacing=2
                        )
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Divider(height=24, color="#334155"),
                ft.Text(
                    "Ocurrió un inconveniente al conectar con la API de videojuegos. "
                    "Si el problema persiste, por favor escribe al soporte técnico.",
                    size=14,
                    color=TEXT_PRIMARY
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("RESPUESTA DETALLADA DEL SERVIDOR:", size=11, weight=ft.FontWeight.BOLD, color="#94A3B8"),
                            ft.Text(
                                f"{self.status_message}\nDetalle: {self.error_detail}",
                                size=12,
                                color="#FCA5A5",
                                font_family="monospace"
                            )
                        ],
                        spacing=4
                    ),
                    bgcolor="#0F172A",
                    border=ft.Border.all(1, "#1E293B"),
                    border_radius=8,
                    padding=12
                ),
                ft.Container(height=14),
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            content=ft.Text("Reintentar Conexión", size=13, weight=ft.FontWeight.BOLD),
                            icon=safe_icon("refresh"),
                            style=ft.ButtonStyle(
                                bgcolor=ACCENT_GREEN,
                                color="#FFFFFF",
                                padding=ft.Padding(left=18, right=18, top=12, bottom=12),
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=lambda _: self.on_retry() if self.on_retry else None
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Escribir a Soporte", size=13, weight=ft.FontWeight.BOLD),
                            icon=safe_icon("support_agent"),
                            style=ft.ButtonStyle(
                                color="#E2E8F0",
                                side=ft.BorderSide(1, "#334155"),
                                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=lambda _: None
                        )
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.START
                )
            ],
            spacing=6
        )

        return ft.Container(
            content=card_content,
            bgcolor="#1E1B2E",
            border=ft.Border.all(2, border_color),
            border_radius=12,
            padding=28,
            margin=ft.Margin(left=0, right=0, top=20, bottom=20),
        )
