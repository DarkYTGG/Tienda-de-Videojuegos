"""Data Transfer Objects (DTOs) decoupling presentation and application layers."""
from dataclasses import dataclass, field
import re
from typing import Optional, Dict, Any

from ..domain.entities import Order


@dataclass
class GameFilterDTO:
    """Carries search, filter, and sorting parameters for catalog querying."""
    search_query: str = ""
    genre: str = "Todos"
    only_sales: bool = False
    only_indie: bool = False
    max_price: Optional[float] = None
    sort_by: str = "destacados"  # "destacados", "precio_menor", "precio_mayor", "valoracion", "nombre"


@dataclass
class CheckoutRequestDTO:
    """Contains payload submitted by the customer during simulated checkout."""
    customer_name: str
    customer_email: str
    payment_method: str = "Saldo PixelVault"

    def validate(self) -> Dict[str, str]:
        """Validates input before domain processing."""
        errors: Dict[str, str] = {}
        if not self.customer_name or len(self.customer_name.strip()) < 3:
            errors["customer_name"] = "El nombre completo debe tener al menos 3 caracteres."

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not self.customer_email or not re.match(email_pattern, self.customer_email.strip()):
            errors["customer_email"] = "Por favor ingresa un correo electrónico válido para recibir tus claves."

        if not self.payment_method:
            errors["payment_method"] = "Selecciona un método de simulación de pago."

        return errors


@dataclass
class CheckoutResponseDTO:
    """Result payload delivered back to presentation upon checkout completion."""
    success: bool
    message: str
    order: Optional[Order] = None
    errors: Dict[str, str] = field(default_factory=dict)
