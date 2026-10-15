"""Abstract base view for all presentation views (OOP Abstraction and Polymorphism)."""
from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any
import flet as ft


class BaseView(ABC):
    """Abstract Base View defining the contract for all UI views in PixelVault."""

    def __init__(
        self,
        page: Optional[ft.Page],
        navigate_fn: Callable[[str, Optional[Dict[str, Any]]], None]
    ):
        self.page = page
        self.navigate = navigate_fn

    @abstractmethod
    def build(self) -> ft.Control:
        """Constructs and returns the Flet control hierarchy for this view."""
        pass
