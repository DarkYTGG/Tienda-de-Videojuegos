"""Concrete infrastructure repositories implementing JSON file persistence.

Thread-safe, robust against missing or corrupt files, adhering to domain ports.
"""
import json
import os
import threading
from typing import List, Optional

from ..domain.entities import Game, Order
from ..domain.ports import GameRepository, OrderRepository
from ..domain.exceptions import (
    ApiError,
    create_api_exception_from_status,
)
from .seed_data import SEED_GAMES
from .api_client import Progra2ApiClient


class ApiInMemoryGameRepository(GameRepository):
    """100% In-Memory Game Repository.
    
    Data exists ONLY in RAM (no JSON file reading/writing for catalog).
    Integrates live games from the Progra-2 API in memory and outputs HTTP telemetry to console.
    """

    def __init__(self, api_client: Optional[Progra2ApiClient] = None, initial_games: Optional[List[dict]] = None):
        self._api_client = api_client
        raw_base = initial_games if initial_games is not None else SEED_GAMES
        self._games_by_id: dict[str, Game] = {}
        for item in raw_base:
            try:
                g = Game.from_dict(item)
                self._games_by_id[g.id] = g
            except Exception:
                continue

        self._games: List[Game] = list(self._games_by_id.values())
        self._lock = threading.Lock()
        
        # In-memory API connection and exception telemetry
        self.last_status_code: int = 200
        self.last_status_message: str = "Inicializando catálogo en memoria RAM..."
        self.last_exception: Optional[ApiError] = None
        self.last_error_detail: Optional[str] = None
        self.is_live: bool = False

        if self._api_client is not None:
            self.sync_from_api(raise_on_error=False)

    def sync_from_api(
        self,
        genre: Optional[str] = None,
        override_key: Optional[str] = None,
        omit_key: bool = False,
        override_user: Optional[str] = None,
        raise_on_error: bool = False
    ) -> List[Game]:
        """Queries the API in real time, storing results exclusively in RAM.
        
        Logs HTTP status codes (200, 401, 403, 404, 405, 422, 500, 503) directly to console.
        """
        with self._lock:
            if not self._api_client:
                self.last_status_code = 200
                self.is_live = False
                return list(self._games_by_id.values())

            status_code, items, exc = self._api_client.fetch_games_with_status(
                genre=genre,
                override_key=override_key,
                omit_key=omit_key,
                override_user=override_user,
                raise_on_error=False
            )

            self.last_status_code = status_code
            self.last_exception = exc
            self.last_error_detail = self._api_client.last_error_detail
            self.last_status_message = self._api_client.last_status_message

            # Log HTTP Status exclusively to terminal console
            if status_code == 200:
                self.is_live = True
                print(f"[CONSOLA API HTTP] Estado: 200 OK | Endpoint: /api/v1/{override_user or self._api_client.username}/games | {len(items)} juego(s) recibido(s) de la API y fusionados en RAM.", flush=True)
                for item in items:
                    try:
                        rg = Game.from_dict(item)
                        # Keep requirements / demo if remote lacks them
                        if rg.id in self._games_by_id:
                            local_g = self._games_by_id[rg.id]
                            if not rg.demo_url and local_g.demo_url:
                                rg.demo_url = local_g.demo_url
                            if not rg.system_requirements and local_g.system_requirements:
                                rg.system_requirements = local_g.system_requirements
                        self._games_by_id[rg.id] = rg
                    except Exception as e:
                        print(f"[CONSOLA API] Error parseando juego remoto: {e}", flush=True)
                self._games = list(self._games_by_id.values())
                return self._games
            else:
                self.is_live = False
                exc_label = exc.__class__.__name__ if exc else "ApiError"
                print(f"[CONSOLA API HTTP ERROR] Estado: {status_code} | Excepción: {exc_label} | Mensaje: {self.last_status_message}", flush=True)
                if self.last_error_detail:
                    print(f"[CONSOLA API HTTP ERROR] Detalle del servidor: {self.last_error_detail}", flush=True)
                
                # Al fallar la API (ej: 401, 403, 404, etc.), vaciar la memoria RAM
                # para que no queden juegos cacheados y refleje fielmente la falla
                self._games_by_id.clear()
                self._games = []
                
                if raise_on_error and exc:
                    raise exc
                return self._games

    def get_all(self) -> List[Game]:
        """Returns games currently held in RAM memory."""
        with self._lock:
            return list(self._games_by_id.values())

    def get_by_id(self, game_id: str) -> Optional[Game]:
        """Retrieves game from RAM by ID."""
        for game in self.get_all():
            if game.id == game_id:
                return game
        return None

    def get_by_slug(self, slug: str) -> Optional[Game]:
        """Retrieves game from RAM by slug."""
        for game in self.get_all():
            if game.slug.lower() == slug.lower():
                return game
        return None

    def get_featured(self) -> List[Game]:
        return [g for g in self.get_all() if g.is_featured]

    def get_on_sale(self) -> List[Game]:
        return [g for g in self.get_all() if g.is_on_sale]

    def get_indie(self) -> List[Game]:
        return [g for g in self.get_all() if g.is_indie]

    def get_new_releases(self) -> List[Game]:
        return [g for g in self.get_all() if g.is_new]

    def get_genres(self) -> List[str]:
        genres = set(g.genre for g in self.get_all())
        return sorted(list(genres))


class JsonGameRepository(GameRepository):
    """Adapter reading Game entities from a local JSON file with live synchronization from Progra2 API."""

    def __init__(self, file_path: str, api_client: Optional[Progra2ApiClient] = None):
        self._file_path = file_path
        self._api_client = api_client
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

    def _write_data(self, data: List[dict]) -> None:
        """Atomically persists games list to the local JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(self._file_path)), exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_and_save_api_games(self, raise_on_error: bool = False) -> List[Game]:
        """Consumes games from the Progra2 API, merges them, and saves them locally into JSON storage."""
        if not self._api_client:
            return self.get_all()

        with self._lock:
            # 1. Fetch from remote API endpoint with strict error handling support
            remote_items = self._api_client.fetch_games(raise_on_error=raise_on_error)

            # 2. Read existing local data
            local_raw = self._read_data()
            games_by_id = {item["id"]: item for item in local_raw if isinstance(item, dict) and "id" in item}

            # 3. Merge remote records, preserving local assets (requirements, demos) if remote lacks them
            for r_item in remote_items:
                g_id = r_item.get("id")
                if not g_id:
                    continue
                if g_id in games_by_id:
                    local_record = games_by_id[g_id]
                    if not r_item.get("demo_url") and local_record.get("demo_url"):
                        r_item["demo_url"] = local_record["demo_url"]
                    if not r_item.get("system_requirements") and local_record.get("system_requirements"):
                        r_item["system_requirements"] = local_record["system_requirements"]
                games_by_id[g_id] = r_item

            # 4. Save and persist permanently in the local JSON system
            merged_list = list(games_by_id.values())
            self._write_data(merged_list)

            # 5. Return domain Game instances
            return [Game.from_dict(item) for item in merged_list]

    def get_all(self) -> List[Game]:
        """Retrieves all games from the local JSON storage merged with the live Progra2 API."""
        with self._lock:
            raw_list = self._read_data()
            games_by_id = {}

            # 1. Load local games
            for item in raw_list:
                try:
                    g = Game.from_dict(item)
                    games_by_id[g.id] = g
                except Exception:
                    continue

            # 2. Merge remote API games if client is present
            if self._api_client:
                try:
                    remote_items = self._api_client.fetch_games()
                    for r_item in remote_items:
                        try:
                            rg = Game.from_dict(r_item)
                            if rg.id in games_by_id:
                                local_g = games_by_id[rg.id]
                                if not rg.demo_url and local_g.demo_url:
                                    rg.demo_url = local_g.demo_url
                                if not rg.system_requirements and local_g.system_requirements:
                                    rg.system_requirements = local_g.system_requirements
                            games_by_id[rg.id] = rg
                        except Exception:
                            continue
                except Exception:
                    pass

            return list(games_by_id.values())

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
