"""Flask application factory and dependency injection configuration for PixelVault."""
import os
from flask import Flask, render_template

from ..infrastructure.repositories import JsonGameRepository, JsonOrderRepository
from ..application.use_cases import (
    ListGamesUseCase,
    SearchAndFilterGamesUseCase,
    GetGameDetailUseCase,
    CheckoutUseCase,
    GetOrdersUseCase,
)
from .routes import StoreWebController, create_store_blueprint


def create_app(test_config: dict | None = None) -> Flask:
    """Creates and configures the Flask application adhering to Clean/Layered Architecture."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "pixelvault-academic-secret-key-2026-sucre"),
        GAMES_FILE=os.path.join(data_dir, "games.json"),
        ORDERS_FILE=os.path.join(data_dir, "orders.json")
    )

    if test_config:
        app.config.update(test_config)

    # 1. Instantiate Infrastructure Adapters (100% RAM Memory persistence for games + External API)
    from ..infrastructure.api_client import Progra2ApiClient
    from ..infrastructure.repositories import ApiInMemoryGameRepository
    api_client = test_config.get("API_CLIENT") if (test_config and "API_CLIENT" in test_config) else Progra2ApiClient()

    # Games live exclusively in RAM via live API connection
    game_repo = test_config.get("GAME_REPO") if (test_config and "GAME_REPO" in test_config) else ApiInMemoryGameRepository(api_client=api_client)
    order_repo = JsonOrderRepository(app.config["ORDERS_FILE"])

    # 2. Instantiate Application Use Cases (Injecting ports)
    list_games_uc = ListGamesUseCase(game_repo)
    search_filter_uc = SearchAndFilterGamesUseCase(game_repo)
    get_game_uc = GetGameDetailUseCase(game_repo)
    checkout_uc = CheckoutUseCase(order_repo)
    get_orders_uc = GetOrdersUseCase(order_repo)

    # 3. Instantiate Web Presentation Controller (Injecting use cases, api_client and game_repo)
    controller = StoreWebController(
        list_games_uc=list_games_uc,
        search_filter_uc=search_filter_uc,
        get_game_uc=get_game_uc,
        checkout_uc=checkout_uc,
        get_orders_uc=get_orders_uc,
        api_client=api_client,
        game_repo=game_repo,
    )

    # 4. Register Blueprint
    bp = create_store_blueprint(controller)
    app.register_blueprint(bp)

    @app.context_processor
    def inject_api_context():
        """Provides Progra-2 API connection metadata and exception telemetry to all Jinja templates."""
        status_code = getattr(game_repo, "last_status_code", 200) if game_repo else 200
        status_msg = getattr(game_repo, "last_status_message", "") if game_repo else ""
        exc = getattr(game_repo, "last_exception", None) if game_repo else None
        exc_name = exc.__class__.__name__ if exc else ("OK" if status_code == 200 else "ApiError")
        detail = getattr(game_repo, "last_error_detail", "") if game_repo else ""

        return {
            "progra2_api": {
                "base_url": api_client.base_url if api_client else "https://progra-2-krw5.onrender.com",
                "user": api_client.username if api_client else "abraham",
                "api_key_masked": f"{api_client.api_key[:8]}...{api_client.api_key[-4:]}" if (api_client and api_client.api_key) else "",
                "status_code": status_code,
                "status_message": status_msg,
                "exception_name": exc_name,
                "error_detail": detail,
                "is_live": getattr(game_repo, "is_live", False) if game_repo else False,
            }
        }

    # 5. Custom Jinja Template Filters
    @app.template_filter("currency")
    def currency_filter(value) -> str:
        """Formats numbers into standard store currency string."""
        if value is None:
            return "$0.00 USD"
        try:
            val = float(value)
            if val == 0:
                return "Gratis"
            return f"${val:.2f} USD"
        except (ValueError, TypeError):
            return "$0.00 USD"

    # 6. Global Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    return app
