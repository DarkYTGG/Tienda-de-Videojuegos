"""Domain ports defining abstract contracts for repositories (Dependency Inversion Principle)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import Game, Order


class GameRepository(ABC):
    """Abstract port for querying and managing video game catalog data."""

    @abstractmethod
    def get_all(self) -> List[Game]:
        """Retrieve all games available in the catalog."""
        pass

    @abstractmethod
    def get_by_id(self, game_id: str) -> Optional[Game]:
        """Retrieve a specific game by its unique ID."""
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Game]:
        """Retrieve a specific game by its URL slug."""
        pass

    @abstractmethod
    def get_featured(self) -> List[Game]:
        """Retrieve games marked as featured."""
        pass

    @abstractmethod
    def get_on_sale(self) -> List[Game]:
        """Retrieve games with active promotional discounts."""
        pass

    @abstractmethod
    def get_indie(self) -> List[Game]:
        """Retrieve independent / indie showcase games."""
        pass

    @abstractmethod
    def get_new_releases(self) -> List[Game]:
        """Retrieve recently released games."""
        pass

    @abstractmethod
    def get_genres(self) -> List[str]:
        """Retrieve all unique genre categories present in the catalog."""
        pass


class OrderRepository(ABC):
    """Abstract port for persisting and querying customer simulated purchases."""

    @abstractmethod
    def save(self, order: Order) -> Order:
        """Persist a newly completed simulated order."""
        pass

    @abstractmethod
    def get_all(self) -> List[Order]:
        """Retrieve all past simulated orders."""
        pass

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Retrieve an order by its unique identifier."""
        pass
