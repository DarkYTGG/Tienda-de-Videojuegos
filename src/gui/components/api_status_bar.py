"""Interactive API Status and Exception Handling Bar for PixelVault GUI.

Visualizes HTTP Status Codes (200, 401, 403, 404, 405, 422, 500, 503)
and permits testing different exception scenarios in real time.
"""
from typing import Callable, Optional
import flet as ft

from ..theme import (
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_PURPLE,
    safe_icon,
)


class ApiStatusBarComponent:
    """Renders a responsive cyberpunk control bar for inspecting API status and triggering HTTP exception simulations."""

    def __init__(
        self,
        status_code: int,
        status_message: str,
        exception_name: Optional[str] = None,
        error_detail: Optional[str] = None,
        on_test_status: Optional[Callable[[str], None]] = None,
        on_refresh: Optional[Callable[[], None]] = None,
    ):
        self.status_code = status_code
        self.status_message = status_message
        self.exception_name = exception_name
        self.error_detail = error_detail
        self.on_test_status = on_test_status
        self.on_refresh = on_refresh

    def _get_badge_colors(self) -> tuple[str, str, str]:
        """Returns (background_color, text_color, border_color) based on HTTP status code."""
        if self.status_code == 200:
            return ("#064E3B", "#34D399", "#059669")  # Emerald
        elif self.status_code in (401, 403):
            return ("#7F1D1D", "#F87171", "#DC2626")  # Red
        elif self.status_code == 404:
            return ("#7C2D12", "#FDBA74", "#EA580C")  # Orange
        elif self.status_code in (405, 422):
            return ("#4C1D95", "#C084FC", "#9333EA")  # Purple
        else:
            return ("#881337", "#FDA4AF", "#E11D48")  # Rose / 500

    def build(self) -> ft.Container:
        bg, fg, border = self._get_badge_colors()
        is_ok = self.status_code == 200

        icon_name = "check_circle" if is_ok else "warning"

        status_chip = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(safe_icon(icon_name), size=16, color=fg),
                    ft.Text(f"HTTP {self.status_code}", size=13, weight=ft.FontWeight.BOLD, color=fg),
                    ft.Container(
                        content=ft.Text(
                            "EN RAM (LIVE)" if is_ok else (self.exception_name or "EXCEPCIÓN"),
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF"
                        ),
                        bgcolor=border,
                        border_radius=4,
                        padding=ft.Padding(left=6, right=6, top=2, bottom=2)
                    )
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor=bg,
            border=ft.Border.all(1, border),
            border_radius=6,
            padding=ft.Padding(left=10, right=10, top=5, bottom=5)
        )

        message_text = ft.Text(
            self.status_message,
            size=12,
            color=TEXT_PRIMARY if is_ok else "#FCA5A5",
            weight=ft.FontWeight.W_500,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
            expand=True
        )

        # Simulation and testing buttons to verify HTTP status codes visually
        def make_test_btn(label: str, code_key: str, btn_color: str) -> ft.TextButton:
            return ft.TextButton(
                content=ft.Text(label, size=11, weight=ft.FontWeight.BOLD),
                style=ft.ButtonStyle(
                    color=btn_color,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                    shape=ft.RoundedRectangleBorder(radius=4)
                ),
                on_click=lambda _: self.on_test_status(code_key) if self.on_test_status else None
            )

        test_buttons = ft.Row(
            controls=[
                ft.Text("Probar Respuestas API:", size=11, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                make_test_btn("200 OK", "200", "#10B981"),
                make_test_btn("401 Sin Key", "401", "#EF4444"),
                make_test_btn("403 Key Mala", "403", "#F87171"),
                make_test_btn("404 Not Found", "404", "#FB923C"),
                make_test_btn("422 Validation", "422", "#C084FC"),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.END,
            scroll=ft.ScrollMode.ADAPTIVE
        )

        row_content = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[status_chip, message_text],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                        expand=True
                    ),
                    col={"sm": 12, "md": 6, "lg": 6}
                ),
                ft.Container(
                    content=test_buttons,
                    alignment=ft.Alignment.CENTER_RIGHT,
                    col={"sm": 12, "md": 6, "lg": 6}
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        return ft.Container(
            content=row_content,
            bgcolor="#0F172A",
            border=ft.Border(bottom=ft.BorderSide(1, border if not is_ok else "#1E293B")),
            padding=ft.Padding(left=24, right=24, top=6, bottom=6),
        )
