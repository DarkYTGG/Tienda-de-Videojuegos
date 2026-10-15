"""Domain package containing core entities, value objects, exceptions, and ports."""
from .entities import (
    Game,
    CartItem,
    ShoppingCart,
    OrderItem,
    Order,
    generate_digital_key,
)
from .exceptions import (
    PixelVaultDomainException,
    GameNotFoundError,
    GameAlreadyInCartError,
    GameNotInCartError,
    EmptyCartCheckoutError,
    InvalidOrderError,
    InvalidGameDataError,
)
from .ports import GameRepository, OrderRepository

__all__ = [
    "Game",
    "CartItem",
    "ShoppingCart",
    "OrderItem",
    "Order",
    "generate_digital_key",
    "PixelVaultDomainException",
    "GameNotFoundError",
    "GameAlreadyInCartError",
    "GameNotInCartError",
    "EmptyCartCheckoutError",
    "InvalidOrderError",
    "InvalidGameDataError",
    "GameRepository",
    "OrderRepository",
]
