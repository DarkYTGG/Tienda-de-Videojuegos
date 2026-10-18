"""Domain exceptions representing business rule violations and domain errors."""
from typing import Dict, Optional


class PixelVaultDomainException(Exception):
    """Base exception for all domain-specific errors in PixelVault."""

    def __init__(self, message: str, errors: Optional[Dict[str, str]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or {}


class GameNotFoundError(PixelVaultDomainException):
    """Raised when a requested game does not exist in the repository."""

    def __init__(self, identifier: str):
        super().__init__(
            f"El videojuego con identificador '{identifier}' no fue encontrado en el catálogo.",
            errors={"game": f"Juego '{identifier}' no encontrado"}
        )
        self.identifier = identifier


class GameAlreadyInCartError(PixelVaultDomainException):
    """Raised when attempting to add a game that is already present in the shopping cart."""

    def __init__(self, game_title: str):
        super().__init__(
            f"'{game_title}' ya se encuentra en tu carrito de compras.",
            errors={"cart": f"'{game_title}' ya está en el carrito"}
        )
        self.game_title = game_title


class GameNotInCartError(PixelVaultDomainException):
    """Raised when attempting to remove a game not present in the shopping cart."""

    def __init__(self, game_id: str):
        super().__init__(
            f"El videojuego '{game_id}' no está presente en el carrito.",
            errors={"cart": "El producto no se encuentra en el carrito"}
        )
        self.game_id = game_id


class EmptyCartCheckoutError(PixelVaultDomainException):
    """Raised when attempting to checkout with an empty shopping cart."""

    def __init__(self):
        super().__init__(
            "No se puede procesar la compra porque el carrito está vacío.",
            errors={"cart": "El carrito no contiene ningún videojuego"}
        )


class InvalidOrderError(PixelVaultDomainException):
    """Raised when checkout order validation fails against business rules."""

    def __init__(self, message: str = "Datos de compra inválidos.", errors: Optional[Dict[str, str]] = None):
        super().__init__(message, errors=errors)


class InvalidGameDataError(PixelVaultDomainException):
    """Raised when game domain validation invariants fail."""

    def __init__(self, message: str = "Datos de videojuego inválidos.", errors: Optional[Dict[str, str]] = None):
        super().__init__(message, errors=errors)
