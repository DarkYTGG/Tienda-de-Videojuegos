"""Concrete infrastructure repositories implementing JSON file persistence.

Thread-safe, robust against missing or corrupt files, adhering to domain ports.
"""
import json
import os
import threading
from typing import List, Optional

from ..domain.entities import Game, Order
from ..domain.ports import GameRepository, OrderRepository
from .seed_data import SEED_GAMES


class JsonGameRepository(GameRepository):
    """Adapter reading Game entities from a local JSON file."""

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Initializes directory and writes seed data if the file is missing or empty."""
        os.makedirs(os.path.dirname(os.path.abspath(self._file_path)), exist_ok=True)
        if not os.path.exists(self._file_path) or os.path.getsize(self._file_path) == 0:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(SEED_GAMES, f, indent=2, ensure_ascii=False)

    def _read_data(self) -> List[dict]:
        """Safely reads the JSON file, recovering with seed data if file is corrupt."""
        if not os.path.exists(self._file_path):
            return SEED_GAMES
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else SEED_GAMES
        except (json.JSONDecodeError, IOError):
            return SEED_GAMES

    def get_all(self) -> List[Game]:
        """Retrieves all games from the JSON database."""
        with self._lock:
            raw_list = self._read_data()
            games: List[Game] = []
            for item in raw_list:
                try:
                    games.append(Game.from_dict(item))
                except Exception:
                    continue
            return games

    def get_by_id(self, game_id: str) -> Optional[Game]:
        """Retrieves a single game by its unique ID."""
        for game in self.get_all():
            if game.id == game_id:
                return game
        return None

    def get_by_slug(self, slug: str) -> Optional[Game]:
        """Retrieves a single game by its slug."""
        for game in self.get_all():
            if game.slug.lower() == slug.lower():
                return game
        return None

    def get_featured(self) -> List[Game]:
        """Returns games flagged as featured."""
        return [g for g in self.get_all() if g.is_featured]

    def get_on_sale(self) -> List[Game]:
        """Returns games with active promotional discounts."""
        return [g for g in self.get_all() if g.is_on_sale]

    def get_indie(self) -> List[Game]:
        """Returns independent developer games."""
        return [g for g in self.get_all() if g.is_indie]

    def get_new_releases(self) -> List[Game]:
        """Returns new release games."""
        return [g for g in self.get_all() if g.is_new]

    def get_genres(self) -> List[str]:
        """Returns a sorted list of unique genres present in the catalog."""
        genres = set(g.genre for g in self.get_all())
        return sorted(list(genres))


class JsonOrderRepository(OrderRepository):
    """Adapter persisting and querying Order entities to/from a local JSON file."""

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Guarantees target directory and initial empty JSON array file exist."""
        os.makedirs(os.path.dirname(os.path.abspath(self._file_path)), exist_ok=True)
        if not os.path.exists(self._file_path) or os.path.getsize(self._file_path) == 0:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _read_data(self) -> List[dict]:
        """Reads raw order records from JSON."""
        if not os.path.exists(self._file_path):
            return []
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    def _write_data(self, data: List[dict]) -> None:
        """Safely writes data to the JSON file."""
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self, order: Order) -> Order:
        """Appends or updates an Order in the JSON storage."""
        with self._lock:
            records = self._read_data()
            updated = False
            for i, rec in enumerate(records):
                if rec.get("id") == order.id:
                    records[i] = order.to_dict()
                    updated = True
                    break
            if not updated:
                records.insert(0, order.to_dict())  # Newest order first
            self._write_data(records)
            return order

    def get_all(self) -> List[Order]:
        """Retrieves all past orders sorted newest first."""
        with self._lock:
            records = self._read_data()
            orders: List[Order] = []
            for item in records:
                try:
                    orders.append(Order.from_dict(item))
                except Exception:
                    continue
            return orders

    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Retrieves a specific order by its identifier."""
        with self._lock:
            records = self._read_data()
            for rec in records:
                if rec.get("id") == order_id:
                    return Order.from_dict(rec)
            return None
