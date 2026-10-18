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

    # 1. Instantiate Infrastructure Adapters (Repositories with JSON persistence)
    game_repo = JsonGameRepository(app.config["GAMES_FILE"])
    order_repo = JsonOrderRepository(app.config["ORDERS_FILE"])

    # 2. Instantiate Application Use Cases (Injecting ports)
    list_games_uc = ListGamesUseCase(game_repo)
    search_filter_uc = SearchAndFilterGamesUseCase(game_repo)
    get_game_uc = GetGameDetailUseCase(game_repo)
    checkout_uc = CheckoutUseCase(order_repo)
    get_orders_uc = GetOrdersUseCase(order_repo)

    # 3. Instantiate Web Presentation Controller (Injecting use cases)
    controller = StoreWebController(
        list_games_uc=list_games_uc,
        search_filter_uc=search_filter_uc,
        get_game_uc=get_game_uc,
        checkout_uc=checkout_uc,
        get_orders_uc=get_orders_uc,
    )

    # 4. Register Blueprint
    bp = create_store_blueprint(controller)
    app.register_blueprint(bp)

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
