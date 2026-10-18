"""Presentation views package."""
from .base_view import BaseView
from .store_view import StoreView
from .catalog_view import CatalogView
from .detail_view import GameDetailView
from .cart_view import CartView
from .checkout_view import CheckoutView
from .confirmation_view import OrderConfirmationView
from .orders_view import OrdersHistoryView

__all__ = [
    "BaseView",
    "StoreView",
    "CatalogView",
    "GameDetailView",
    "CartView",
    "CheckoutView",
    "OrderConfirmationView",
    "OrdersHistoryView",
]
