"""Web presentation layer using Flask adhering to Hexagonal/Layered Architecture."""
from .app import create_app

__all__ = ["create_app"]
