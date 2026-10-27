"""API Client and service adapter for the Progra-2 Students API evaluation.

Connects to https://progra-2-krw5.onrender.com/api/v1/abraham using the student's API Key.
"""
import json
import logging
import os
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional

from ..domain.exceptions import (
    ApiError,
    ApiAuthenticationError,
    ApiConnectionError,
    ApiResponseError,
    create_api_exception_from_status,
)

logger = logging.getLogger(__name__)

DEFAULT_API_BASE_URL = "https://progra-2-krw5.onrender.com"
DEFAULT_USER = "abraham"


def _load_env_file() -> None:
    """Load key-value pairs from .env if present without external dependencies."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.is_file():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("\"'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception as e:
            logger.debug("Failed reading .env file: %s", e)


# Attempt loading .env upon import
_load_env_file()


class Progra2ApiClient:
    """Client for consuming student endpoints on the Progra-2 Students API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 8
    ):
        _load_env_file()
        self.base_url = (base_url or os.environ.get("PROGRA2_API_URL") or DEFAULT_API_BASE_URL).rstrip("/")
        self.username = username or os.environ.get("PROGRA2_API_USER") or DEFAULT_USER
        self.api_key = api_key or os.environ.get("PROGRA2_API_KEY") or ""
        self.timeout = timeout

        # Active telemetry & last response state
        self.last_status_code: int = 200
        self.last_status_message: str = "Esperando primera consulta..."
        self.last_error_detail: Optional[str] = None
        self.last_exception: Optional[ApiError] = None

    def _get_headers(self, override_key: Optional[str] = None, omit_key: bool = False) -> Dict[str, str]:
        headers = {
            "User-Agent": "PixelVault-Client/1.0",
            "Accept": "application/json",
        }
        if not omit_key:
            headers["X-API-Key"] = override_key if override_key is not None else self.api_key
        return headers

    def check_health(self, raise_on_error: bool = False) -> Dict[str, Any]:
        """Checks the namespace health endpoint (/api/v1/{user}/health)."""
        url = f"{self.base_url}/api/v1/{self.username}/health"
        req = urllib.request.Request(url, headers=self._get_headers())
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self.last_status_code = resp.status
                self.last_status_message = f"HTTP {resp.status} OK: Conexión exitosa a la API"
                self.last_exception = None
                self.last_error_detail = None
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "online": True,
                    "status_code": resp.status,
                    "status": data.get("status", "healthy"),
                    "user": data.get("user", self.username),
                    "full_name": data.get("full_name", "Abraham Ali Garcia Lozano"),
                    "is_active": data.get("is_active", True),
                    "endpoint": url
                }
        except urllib.error.HTTPError as e:
            self.last_status_code = e.code
            detail = ""
            try:
                raw_err = e.read().decode("utf-8")
                err_json = json.loads(raw_err)
                detail = err_json.get("detail") or err_json.get("message") or raw_err
            except Exception:
                detail = str(e.reason)
            self.last_error_detail = detail
            exc = create_api_exception_from_status(e.code, detail=detail)
            self.last_exception = exc
            self.last_status_message = f"HTTP {e.code}: {exc.message}"
            if raise_on_error:
                raise exc from e
            return {"online": False, "status_code": e.code, "error": exc.message, "user": self.username, "endpoint": url}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            self.last_status_code = 503
            exc = ApiConnectionError(f"Fallo de conexión o timeout con la API: {e}")
            self.last_exception = exc
            self.last_status_message = f"HTTP 503: {exc.message}"
            if raise_on_error:
                raise exc from e
            return {"online": False, "status_code": 503, "error": str(e), "user": self.username, "endpoint": url}
        except Exception as e:
            self.last_status_code = 500
            exc = ApiError(f"Error inesperado al consultar health: {e}", status_code=500)
            self.last_exception = exc
            self.last_status_message = f"HTTP 500: {exc.message}"
            if raise_on_error:
                raise exc from e
            return {"online": False, "status_code": 500, "error": str(e), "user": self.username, "endpoint": url}

    def fetch_games_with_status(
        self,
        genre: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        override_key: Optional[str] = None,
        omit_key: bool = False,
        override_user: Optional[str] = None,
        raise_on_error: bool = False
    ) -> tuple[int, List[Dict[str, Any]], Optional[ApiError]]:
        """Queries the games endpoint and returns (status_code, items_list, exception_or_none)."""
        target_user = override_user if override_user is not None else self.username
        url = f"{self.base_url}/api/v1/{target_user}/games?limit={limit}&offset={offset}"
        if genre and genre.strip().lower() != "todos":
            url += f"&genre={urllib.parse.quote(genre.strip())}"

        req = urllib.request.Request(url, headers=self._get_headers(override_key=override_key, omit_key=omit_key))
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self.last_status_code = resp.status
                self.last_status_message = f"HTTP {resp.status} OK: Juegos obtenidos exitosamente desde la API en RAM"
                self.last_exception = None
                self.last_error_detail = None
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                return resp.status, (items if isinstance(items, list) else []), None
        except urllib.error.HTTPError as e:
            self.last_status_code = e.code
            detail = ""
            try:
                raw_err = e.read().decode("utf-8")
                err_json = json.loads(raw_err)
                detail = err_json.get("detail") or err_json.get("message") or raw_err
            except Exception:
                detail = str(e.reason)
            self.last_error_detail = detail
            exc = create_api_exception_from_status(e.code, detail=detail)
            self.last_exception = exc
            self.last_status_message = f"HTTP {e.code}: {exc.message}"
            if raise_on_error:
                raise exc from e
            return e.code, [], exc
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            self.last_status_code = 503
            exc = ApiConnectionError(f"HTTP 503: Servidor inalcanzable ({e})")
            self.last_exception = exc
            self.last_status_message = f"HTTP 503: {exc.message}"
            if raise_on_error:
                raise exc from e
            return 503, [], exc
        except Exception as e:
            self.last_status_code = 500
            exc = ApiError(f"HTTP 500: Error procesando respuesta: {e}", status_code=500)
            self.last_exception = exc
            self.last_status_message = f"HTTP 500: {exc.message}"
            if raise_on_error:
                raise exc from e
            return 500, [], exc

    def fetch_games(self, genre: Optional[str] = None, limit: int = 50, offset: int = 0, raise_on_error: bool = False) -> List[Dict[str, Any]]:
        """Backwards compatible method returning purely the list of items."""
        code, items, exc = self.fetch_games_with_status(genre=genre, limit=limit, offset=offset, raise_on_error=raise_on_error)
        return items
