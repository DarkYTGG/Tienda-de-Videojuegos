"""Design system tokens and styling helpers for PixelVault (Steam + itch.io aesthetics)."""
from typing import Optional, Any
import flet as ft


# --- Palette Tokens ---
BG_DARK = "#0B0E14"          # Deep cosmic charcoal
BG_HEADER = "#101726"        # Header & Navigation bar
BG_SURFACE = "#162032"       # Primary cards & panels
BG_SURFACE_HOVER = "#1E2C44" # Hover state
BG_INPUT = "#0D131F"         # Text fields & dropdown inputs

ACCENT_PURPLE = "#8B5CF6"      # Electric violet (Primary brand)
ACCENT_PURPLE_DARK = "#7C3AED" # Deep violet
ACCENT_CYAN = "#06B6D4"        # Neon cyan (itch.io highlight)
ACCENT_GREEN = "#10B981"       # Steam discount green
ACCENT_GREEN_BG = "#064E3B"    # Dark emerald for discount badge background
ACCENT_AMBER = "#F59E0B"       # Star ratings & awards
ACCENT_RED = "#EF4444"         # Deletions & errors

TEXT_PRIMARY = "#F8FAFC"       # Clean crisp white
TEXT_SECONDARY = "#94A3B8"     # Secondary muted slate
TEXT_MUTED = "#64748B"         # Low-contrast captions
BORDER_COLOR = "#22304A"       # Subtle card borders
BORDER_LIGHT = "#334155"       # Divider lines


# --- Icon Safety Helper ---
ICON_MAPPING = {
    "star": ft.Icons.STAR,
    "sports_esports": ft.Icons.SPORTS_ESPORTS,
    "storefront": ft.Icons.STOREFRONT,
    "grid_view": ft.Icons.GRID_VIEW,
    "auto_awesome": ft.Icons.AUTO_AWESOME,
    "receipt_long": ft.Icons.RECEIPT_LONG,
    "shopping_cart": ft.Icons.SHOPPING_CART,
    "shopping_cart_outlined": ft.Icons.SHOPPING_CART_OUTLINED,
    "search": ft.Icons.SEARCH,
    "visibility": ft.Icons.VISIBILITY,
    "add_shopping_cart": ft.Icons.ADD_SHOPPING_CART,
    "check": ft.Icons.CHECK,
    "check_circle": ft.Icons.CHECK_CIRCLE,
    "local_fire_department": ft.Icons.LOCAL_FIRE_DEPARTMENT,
    "thumb_up": ft.Icons.THUMB_UP,
    "business": ft.Icons.BUSINESS,
    "error_outline": ft.Icons.ERROR_OUTLINE,
    "videogame_asset": ft.Icons.VIDEOGAME_ASSET,
    "vpn_key": ft.Icons.VPN_KEY,
    "history_toggle_off": ft.Icons.HISTORY_TOGGLE_OFF,
    "verified_user": ft.Icons.VERIFIED_USER,
    "info": ft.Icons.INFO,
    "search_off": ft.Icons.SEARCH_OFF,
    "image": ft.Icons.IMAGE,
    "arrow_back": ft.Icons.ARROW_BACK,
    "arrow_forward": ft.Icons.ARROW_FORWARD,
    "delete_outline": ft.Icons.DELETE_OUTLINE,
    "delete_sweep": ft.Icons.DELETE_SWEEP,
    "filter_list": ft.Icons.FILTER_LIST,
    "filter_alt_off": ft.Icons.FILTER_ALT_OFF,
    "lock": ft.Icons.LOCK,
    "credit_card": ft.Icons.CREDIT_CARD,
    "attach_money": ft.Icons.ATTACH_MONEY,
    "account_balance_wallet": ft.Icons.ACCOUNT_BALANCE_WALLET,
    "swap_horiz": ft.Icons.SWAP_HORIZ,
    "sort": ft.Icons.SORT,
    "task_alt": ft.Icons.TASK_ALT,
    "launch": ft.Icons.LAUNCH,
    "download": ft.Icons.DOWNLOAD,
    "close": ft.Icons.CLOSE,
}


def safe_icon(name: Optional[str]) -> Any:
    """Safely converts string or enum icon representations to ft.Icons enum.
    
    Prevents Flutter Web WASM runtime type exceptions when rendering icons.
    """
    if name is None:
        return None
    if not isinstance(name, str):
        return name

    clean = name.strip().lower().replace("-", "_").replace(" ", "_")
    if clean in ICON_MAPPING:
        return ICON_MAPPING[clean]

    clean_upper = clean.upper()
    if hasattr(ft.Icons, clean_upper):
        return getattr(ft.Icons, clean_upper)
    clean_outlined = f"{clean_upper}_OUTLINED"
    if hasattr(ft.Icons, clean_outlined):
        return getattr(ft.Icons, clean_outlined)

    return ft.Icons.CIRCLE


# --- UI Helper Components ---
def create_badge(
    text: str,
    bg_color: str = ACCENT_PURPLE,
    text_color: str = "#FFFFFF",
    font_size: int = 11,
    weight: ft.FontWeight = ft.FontWeight.BOLD,
    icon: Optional[str] = None
) -> ft.Container:
    """Creates a compact, stylized badge for categories, tags, or promos."""
    content_controls = []
    if icon:
        content_controls.append(ft.Icon(safe_icon(icon), size=font_size + 2, color=text_color))
    content_controls.append(
        ft.Text(text, size=font_size, weight=weight, color=text_color)
    )

    return ft.Container(
        content=ft.Row(
            controls=content_controls,
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True
        ),
        bgcolor=bg_color,
        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
        border_radius=6
    )


def create_price_display(
    price: float,
    discount_percent: int,
    final_price: float,
    show_badge: bool = True
) -> ft.Row:
    """Renders Steam-style pricing block with discount badge, crossed-out original, and final price."""
    controls = []

    if discount_percent > 0 and show_badge:
        controls.append(
            ft.Container(
                content=ft.Text(
                    f"-{discount_percent}%",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color="#4ADE80"
                ),
                bgcolor=ACCENT_GREEN_BG,
                padding=ft.Padding(left=6, right=6, top=3, bottom=3),
                border_radius=4,
                border=ft.Border.all(1, "#059669")
            )
        )

    price_column = []
    if discount_percent > 0:
        price_column.append(
            ft.Text(
                f"${price:,.2f}",
                size=11,
                color=TEXT_MUTED,
                style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, color=TEXT_MUTED)
            )
        )

    final_text = "Gratis" if final_price <= 0 else f"${final_price:,.2f} USD"
    price_column.append(
        ft.Text(
            final_text,
            size=14,
            weight=ft.FontWeight.BOLD,
            color=TEXT_PRIMARY
        )
    )

    controls.append(
        ft.Column(
            controls=price_column,
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

    return ft.Row(
        controls=controls,
        spacing=8,
        alignment=ft.MainAxisAlignment.END,
        tight=True
    )


def create_section_header(
    title: str,
    subtitle: str,
    icon: str = "local_fire_department",
    accent_color: str = ACCENT_PURPLE,
    action_text: Optional[str] = None,
    action_callback = None
) -> ft.Container:
    """Renders a section header with an icon, title, subtitle, and optional 'Ver todo' link."""
    left_side = ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(safe_icon(icon), color="#FFFFFF", size=20),
                bgcolor=accent_color,
                padding=8,
                border_radius=8
            ),
            ft.Column(
                controls=[
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(subtitle, size=12, color=TEXT_SECONDARY)
                ],
                spacing=2
            )
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
        tight=True
    )

    row_controls = [left_side]

    if action_text and action_callback:
        row_controls.append(
            ft.OutlinedButton(
                content=ft.Text(action_text, size=12, weight=ft.FontWeight.W_600),
                icon=safe_icon("arrow_forward"),
                style=ft.ButtonStyle(
                    color=ACCENT_CYAN,
                    side=ft.BorderSide(1, ACCENT_CYAN),
                    shape=ft.RoundedRectangleBorder(radius=6)
                ),
                on_click=action_callback
            )
        )

    return ft.Container(
        content=ft.Row(
            controls=row_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        margin=ft.Margin(left=0, right=0, top=20, bottom=12)
    )
