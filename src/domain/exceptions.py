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


class ApiError(PixelVaultDomainException):
    """Base exception for all external API integration failures."""

    def __init__(self, message: str = "Error en la comunicación con la API externa.", status_code: int = 500, errors: Optional[Dict[str, str]] = None):
        super().__init__(message, errors=errors)
        self.status_code = status_code
        self.message = message


class ApiAuthenticationError(ApiError):
    """Base exception for all authentication/authorization API errors (401 / 403)."""

    def __init__(self, message: str = "Error de autenticación con la API.", status_code: int = 401, detail: Optional[str] = None):
        super().__init__(message, status_code=status_code, errors={"auth": detail or message})


class ApiMissingKeyError(ApiAuthenticationError):
    """HTTP 401 - Falta cabecera X-API-Key."""

    def __init__(self, message: str = "HTTP 401 Unauthorized: Falta la cabecera 'X-API-Key'.", detail: Optional[str] = None):
        super().__init__(message, status_code=401, detail=detail or "Falta cabecera X-API-Key")


class ApiForbiddenKeyError(ApiAuthenticationError):
    """HTTP 403 - API Key inválida para este namespace."""

    def __init__(self, message: str = "HTTP 403 Forbidden: API Key inválida para este namespace.", detail: Optional[str] = None):
        super().__init__(message, status_code=403, detail=detail or "API Key inválida para este namespace")


class ApiNamespaceNotFoundError(ApiError):
    """HTTP 404 - Namespace de usuario no encontrado."""

    def __init__(self, message: str = "HTTP 404 Not Found: Namespace de usuario no encontrado en la API.", detail: Optional[str] = None):
        super().__init__(message, status_code=404, errors={"error": "Namespace de usuario no encontrado", "detail": detail or ""})


class ApiMethodNotAllowedError(ApiError):
    """HTTP 405 - Método HTTP no permitido."""

    def __init__(self, message: str = "HTTP 405 Method Not Allowed: Método HTTP no admitido por este endpoint.", detail: Optional[str] = None):
        super().__init__(message, status_code=405, errors={"error": "Método no permitido", "detail": detail or ""})


class ApiValidationError(ApiError):
    """HTTP 422 - Error de validación en parámetros."""

    def __init__(self, message: str = "HTTP 422 Unprocessable Entity: Error de validación en los parámetros enviados a la API.", detail: Optional[str] = None):
        super().__init__(message, status_code=422, errors={"error": "Validation Error", "detail": detail or ""})


class ApiInternalServerError(ApiError):
    """HTTP 500 - Error interno del servidor en la API."""

    def __init__(self, message: str = "HTTP 500 Internal Server Error: Error interno en el servidor de Render.", detail: Optional[str] = None):
        super().__init__(message, status_code=500, errors={"error": "Error interno del servidor", "detail": detail or ""})


class ApiConnectionError(ApiError):
    """HTTP 503 / Network - Fallo de red, timeout o servidor inalcanzable."""

    def __init__(self, message: str = "HTTP 503 Service Unavailable: No fue posible conectar con el servidor de la API.", errors: Optional[Dict[str, str]] = None):
        super().__init__(message, status_code=503, errors=errors or {"network": "Servidor inalcanzable o timeout"})


class ApiResponseError(ApiError):
    """Respuesta con formato no reconocido o código inesperado."""

    def __init__(self, message: str = "Respuesta inválida recibida desde la API.", status_code: int = 502, errors: Optional[Dict[str, str]] = None):
        super().__init__(message, status_code=status_code, errors=errors or {"api": "Formato de datos no reconocido"})


def create_api_exception_from_status(status_code: int, detail: Optional[str] = None) -> ApiError:
    """Factory creating exact domain exception matching OpenAPI specification status codes."""
    if status_code == 401:
        return ApiMissingKeyError(detail=detail)
    elif status_code == 403:
        return ApiForbiddenKeyError(detail=detail)
    elif status_code == 404:
        return ApiNamespaceNotFoundError(detail=detail)
    elif status_code == 405:
        return ApiMethodNotAllowedError(detail=detail)
    elif status_code == 422:
        return ApiValidationError(detail=detail)
    elif status_code == 500:
        return ApiInternalServerError(detail=detail)
    elif status_code in (502, 503, 504):
        return ApiConnectionError(f"HTTP {status_code}: Servidor no disponible o timeout de puerta de enlace.")
    else:
        return ApiError(f"HTTP {status_code}: Error devuelto por la API.", status_code=status_code, errors={"detail": detail or ""})
