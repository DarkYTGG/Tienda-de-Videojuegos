"""Domain entities adhering strictly to Object-Oriented Programming (OOP) principles.

Encapsulation, business logic invariants, data validation, and serialization.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import secrets
from typing import List, Dict, Any, Optional
import uuid

from .exceptions import (
    InvalidGameDataError,
    GameAlreadyInCartError,
    GameNotInCartError,
    InvalidOrderError,
)


@dataclass
class Game:
    """Represents a video game in the PixelVault digital catalog."""
    id: str
    title: str
    slug: str
    developer: str
    publisher: str
    release_date: str
    genre: str
    tags: List[str] = field(default_factory=list)
    price: float = 0.0
    discount_percent: int = 0
    rating: float = 4.5
    reviews_count: int = 0
    is_featured: bool = False
    is_new: bool = False
    is_indie: bool = False
    short_description: str = ""
    full_description: str = ""
    cover_image: str = ""
    banner_image: str = ""
    features: List[str] = field(default_factory=list)
    system_requirements: Dict[str, str] = field(default_factory=dict)
    demo_url: Optional[str] = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Validates domain invariants for game integrity."""
        errors: Dict[str, str] = {}
        if not self.title or not self.title.strip():
            errors["title"] = "El título del videojuego no puede estar vacío."
        if self.price < 0:
            errors["price"] = "El precio base no puede ser negativo."
        if self.discount_percent < 0 or self.discount_percent > 100:
            errors["discount_percent"] = "El porcentaje de descuento debe estar entre 0 y 100."
        if self.rating < 0.0 or self.rating > 5.0:
            errors["rating"] = "La valoración debe estar entre 0.0 y 5.0."
        if errors:
            raise InvalidGameDataError("Invariante de videojuego inválida.", errors=errors)

    @property
    def final_price(self) -> float:
        """Calculates effective selling price after applying promotional discount."""
        if self.discount_percent <= 0:
            return round(self.price, 2)
        factor = 1.0 - (self.discount_percent / 100.0)
        return round(self.price * factor, 2)

    @property
    def is_on_sale(self) -> bool:
        """Indicates whether this title currently has an active promotional discount."""
        return self.discount_percent > 0

    @property
    def savings(self) -> float:
        """Monetary savings if game is bought under discount."""
        return round(self.price - self.final_price, 2)

    @property
    def formatted_original_price(self) -> str:
        """Formatted original price in USD."""
        if self.price <= 0:
            return "Gratis"
        return f"${self.price:,.2f} USD"

    @property
    def formatted_final_price(self) -> str:
        """Formatted final price in USD."""
        if self.final_price <= 0:
            return "Gratis"
        return f"${self.final_price:,.2f} USD"

    @property
    def discount_badge(self) -> str:
        """Percentage badge string, e.g. -50%."""
        return f"-{self.discount_percent}%"

    @property
    def rating_summary(self) -> str:
        """Qualitative description of user reviews inspired by Steam/itch.io."""
        if self.rating >= 4.7:
            return f"Extremadamente positivas ({self.reviews_count:,} reseñas)"
        if self.rating >= 4.2:
            return f"Muy positivas ({self.reviews_count:,} reseñas)"
        if self.rating >= 3.5:
            return f"Mayormente positivas ({self.reviews_count:,} reseñas)"
        return f"Variadas ({self.reviews_count:,} reseñas)"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Game":
        """Factory method reconstituting a Game entity from a dictionary."""
        return cls(
            id=str(data.get("id", str(uuid.uuid4()))),
            title=str(data.get("title", "")),
            slug=str(data.get("slug", "")),
            developer=str(data.get("developer", "PixelVault Studios")),
            publisher=str(data.get("publisher", "PixelVault Publishing")),
            release_date=str(data.get("release_date", "2026-01-01")),
            genre=str(data.get("genre", "Acción")),
            tags=list(data.get("tags", [])),
            price=float(data.get("price", 0.0)),
            discount_percent=int(data.get("discount_percent", 0)),
            rating=float(data.get("rating", 4.5)),
            reviews_count=int(data.get("reviews_count", 100)),
            is_featured=bool(data.get("is_featured", False)),
            is_new=bool(data.get("is_new", False)),
            is_indie=bool(data.get("is_indie", False)),
            short_description=str(data.get("short_description", "")),
            full_description=str(data.get("full_description", "")),
            cover_image=str(data.get("cover_image", "")),
            banner_image=str(data.get("banner_image", "")),
            features=list(data.get("features", [])),
            system_requirements=dict(data.get("system_requirements", {})),
            demo_url=data.get("demo_url")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Game entity into a dictionary structure."""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "developer": self.developer,
            "publisher": self.publisher,
            "release_date": self.release_date,
            "genre": self.genre,
            "tags": self.tags,
            "price": self.price,
            "discount_percent": self.discount_percent,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "is_featured": self.is_featured,
            "is_new": self.is_new,
            "is_indie": self.is_indie,
            "short_description": self.short_description,
            "full_description": self.full_description,
            "cover_image": self.cover_image,
            "banner_image": self.banner_image,
            "features": self.features,
            "system_requirements": self.system_requirements,
            "demo_url": self.demo_url
        }


@dataclass
class CartItem:
    """Represents a unique game entry in the shopping cart."""
    game: Game
    added_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def unit_price(self) -> float:
        """Final price to be charged for this item."""
        return self.game.final_price

    @property
    def original_price(self) -> float:
        """Original undiscounted price."""
        return self.game.price

    @property
    def savings(self) -> float:
        """Amount saved on this title."""
        return self.game.savings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game": self.game.to_dict(),
            "added_at": self.added_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CartItem":
        return cls(
            game=Game.from_dict(data["game"]),
            added_at=data.get("added_at", datetime.now(timezone.utc).isoformat())
        )


class ShoppingCart:
    """Encapsulates the shopping cart state and business calculations.

    Guarantees that a game cannot appear duplicated as multiple line items.
    """

    def __init__(self, initial_items: Optional[List[CartItem]] = None):
        # Mapped by game.id to guarantee uniqueness (digital licensing constraint)
        self._items: Dict[str, CartItem] = {}
        if initial_items:
            for item in initial_items:
                self._items[item.game.id] = item

    def add_game(self, game: Game) -> CartItem:
        """Adds a video game to the cart. Raises GameAlreadyInCartError if already added."""
        if game.id in self._items:
            raise GameAlreadyInCartError(game.title)
        item = CartItem(game=game)
        self._items[game.id] = item
        return item

    def remove_game(self, game_id: str) -> CartItem:
        """Removes a video game by ID. Raises GameNotInCartError if not present."""
        if game_id not in self._items:
            raise GameNotInCartError(game_id)
        return self._items.pop(game_id)

    def has_game(self, game_id: str) -> bool:
        """Checks if a game is already in the cart."""
        return game_id in self._items

    def clear(self) -> None:
        """Empties all items from the shopping cart."""
        self._items.clear()

    def get_items(self) -> List[CartItem]:
        """Returns a snapshot list of current items in the cart."""
        return list(self._items.values())

    @property
    def item_count(self) -> int:
        """Total distinct video games in the cart."""
        return len(self._items)

    @property
    def is_empty(self) -> bool:
        """Indicates whether the cart has 0 games."""
        return len(self._items) == 0

    @property
    def subtotal(self) -> float:
        """Calculates total undiscounted cost of all games."""
        return round(sum(item.original_price for item in self._items.values()), 2)

    @property
    def total_discount(self) -> float:
        """Calculates total savings across all discounted games."""
        return round(sum(item.savings for item in self._items.values()), 2)

    @property
    def total(self) -> float:
        """Calculates net amount to pay."""
        return round(sum(item.unit_price for item in self._items.values()), 2)

    @property
    def formatted_subtotal(self) -> str:
        return f"${self.subtotal:,.2f} USD"

    @property
    def formatted_total_discount(self) -> str:
        return f"-${self.total_discount:,.2f} USD"

    @property
    def formatted_total(self) -> str:
        return f"${self.total:,.2f} USD"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self._items.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShoppingCart":
        raw_items = data.get("items", [])
        items = [CartItem.from_dict(i) for i in raw_items]
        return cls(initial_items=items)


def generate_digital_key() -> str:
    """Generates a realistic 16-character digital game activation key."""
    blocks = [secrets.token_hex(2).upper() for _ in range(4)]
    return f"PIXEL-{'-'.join(blocks)}"


@dataclass
class OrderItem:
    """Represents a fulfilled item within a digital purchase order."""
    game_id: str
    game_title: str
    price_paid: float
    digital_key: str = field(default_factory=generate_digital_key)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self.game_id,
            "game_title": self.game_title,
            "price_paid": self.price_paid,
            "digital_key": self.digital_key
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderItem":
        return cls(
            game_id=str(data.get("game_id", "")),
            game_title=str(data.get("game_title", "")),
            price_paid=float(data.get("price_paid", 0.0)),
            digital_key=str(data.get("digital_key", generate_digital_key()))
        )


@dataclass
class Order:
    """Order domain entity representing a completed simulated purchase."""
    id: str
    customer_name: str
    customer_email: str
    payment_method: str
    items: List[OrderItem]
    subtotal: float
    total_discount: float
    total: float
    status: str = "Completada (Simulación de Compra)"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        """Enforces domain validation invariants for an order."""
        errors: Dict[str, str] = {}
        if not self.customer_name or len(self.customer_name.strip()) < 3:
            errors["customer_name"] = "El nombre del comprador debe contener al menos 3 caracteres."

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not self.customer_email or not re.match(email_pattern, self.customer_email.strip()):
            errors["customer_email"] = "Por favor ingresa un correo electrónico válido para recibir las claves digitales."

        if not self.items:
            errors["items"] = "La orden debe contener al menos un videojuego."

        if self.total < 0:
            errors["total"] = "El total de la orden no puede ser negativo."

        if errors:
            raise InvalidOrderError("Error en la validación de la orden de compra.", errors=errors)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Order entity to JSON-friendly dictionary."""
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "payment_method": self.payment_method,
            "items": [item.to_dict() for item in self.items],
            "subtotal": self.subtotal,
            "total_discount": self.total_discount,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        """Reconstitutes an Order entity from a dictionary."""
        raw_items = data.get("items", [])
        parsed_items = [OrderItem.from_dict(it) for it in raw_items]
        return cls(
            id=str(data.get("id", f"PV-{secrets.token_hex(4).upper()}")),
            customer_name=str(data.get("customer_name", "")),
            customer_email=str(data.get("customer_email", "")),
            payment_method=str(data.get("payment_method", "Saldo PixelVault")),
            items=parsed_items,
            subtotal=float(data.get("subtotal", 0.0)),
            total_discount=float(data.get("total_discount", 0.0)),
            total=float(data.get("total", 0.0)),
            status=str(data.get("status", "Completada (Simulación de Compra)")),
            created_at=str(data.get("created_at", datetime.now(timezone.utc).isoformat()))
        )
