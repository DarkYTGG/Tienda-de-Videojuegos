"""Web presentation layer: Controllers and Flask routes for PixelVault."""
import json
import os
from typing import Optional
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
    abort,
    current_app,
)

from ..domain.entities import ShoppingCart, Game
from ..domain.exceptions import GameNotFoundError
from ..application.dtos import GameFilterDTO, CheckoutRequestDTO
from ..application.use_cases import (
    ListGamesUseCase,
    SearchAndFilterGamesUseCase,
    GetGameDetailUseCase,
    CheckoutUseCase,
    GetOrdersUseCase,
)


class StoreWebController:
    """Object-Oriented Web Controller coordinating HTTP requests with Clean Architecture Use Cases."""

    def __init__(
        self,
        list_games_uc: ListGamesUseCase,
        search_filter_uc: SearchAndFilterGamesUseCase,
        get_game_uc: GetGameDetailUseCase,
        checkout_uc: CheckoutUseCase,
        get_orders_uc: GetOrdersUseCase,
    ):
        self._list_games_uc = list_games_uc
        self._search_filter_uc = search_filter_uc
        self._get_game_uc = get_game_uc
        self._checkout_uc = checkout_uc
        self._get_orders_uc = get_orders_uc

    def _get_cart(self) -> ShoppingCart:
        """Reconstructs the Domain ShoppingCart entity from the user's HTTP session."""
        cart = ShoppingCart()
        game_ids = session.get("cart", [])
        for gid in game_ids:
            try:
                game = self._get_game_uc.execute_by_id(gid)
                cart.add_game(game)
            except GameNotFoundError:
                continue
        return cart

    def _save_cart(self, cart: ShoppingCart) -> None:
        """Serializes current cart item IDs to the user's session."""
        session["cart"] = [item.game.id for item in cart.get_items()]
        session.modified = True

    # -------------------------------------------------------------
    # Page Endpoints
    # -------------------------------------------------------------
    def index(self):
        """Storefront homepage displaying Hero banner, Super Sales, Indie Highlights, and New Releases."""
        featured = self._list_games_uc.get_featured()
        hero_game = featured[0] if featured else None
        on_sale = self._list_games_uc.get_on_sale()
        indie_games = self._list_games_uc.get_indie()
        new_releases = self._list_games_uc.get_new_releases()
        demo_games = self._list_games_uc.get_demo_games()
        cart = self._get_cart()

        return render_template(
            "index.html",
            hero_game=hero_game,
            featured=featured,
            on_sale=on_sale,
            indie_games=indie_games,
            new_releases=new_releases,
            demo_games=demo_games,
            cart=cart,
        )

    def catalog(self):
        """Complete catalog with multi-criteria filtering, search, and sorting."""
        search = request.args.get("search", "").strip()
        genre = request.args.get("genre", "Todos")
        only_sales = request.args.get("only_sales", "").lower() in ("1", "true", "on")
        only_indie = request.args.get("only_indie", "").lower() in ("1", "true", "on")
        sort_by = request.args.get("sort", "destacados")

        filter_dto = GameFilterDTO(
            search_query=search,
            genre=genre,
            only_sales=only_sales,
            only_indie=only_indie,
            sort_by=sort_by,
        )

        games = self._search_filter_uc.execute(filter_dto)
        genres = self._list_games_uc.get_genres()
        cart = self._get_cart()

        return render_template(
            "catalog.html",
            games=games,
            genres=genres,
            active_filter=filter_dto,
            cart=cart,
            total_count=len(games),
        )

    def game_detail(self, slug: str):
        """Detailed game overview page featuring screenshots gallery, system requirements, and ratings."""
        try:
            game = self._get_game_uc.execute_by_slug(slug)
        except GameNotFoundError:
            abort(404)

        cart = self._get_cart()
        is_in_cart = cart.has_game(game.id)
        related_games = [g for g in self._list_games_uc.get_all() if g.genre == game.genre and g.id != game.id][:3]

        return render_template(
            "detail.html",
            game=game,
            is_in_cart=is_in_cart,
            related_games=related_games,
            cart=cart,
        )

    def cart_view(self):
        """Dedicated shopping cart review view."""
        cart = self._get_cart()
        return render_template("cart.html", cart=cart)

    def checkout_view(self):
        """Checkout checkout view with client validation and order total summary."""
        cart = self._get_cart()
        if cart.is_empty:
            flash("Tu carrito de compras está vacío. Agrega juegos antes de continuar.", "warning")
            return redirect(url_for("store.catalog"))

        return render_template("checkout.html", cart=cart, form_data={}, errors={})

    def process_checkout(self):
        """Handles POST checkout form submission executing business rules and JSON order persistence."""
        cart = self._get_cart()
        if cart.is_empty:
            flash("Tu carrito está vacío.", "danger")
            return redirect(url_for("store.catalog"))

        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        payment_method = request.form.get("payment_method", "Tarjeta de Crédito / Débito")
        accept_terms = bool(request.form.get("accept_terms"))

        request_dto = CheckoutRequestDTO(
            customer_name=customer_name,
            customer_email=customer_email,
            payment_method=payment_method,
            accept_terms=accept_terms,
        )

        response_dto = self._checkout_uc.execute(cart, request_dto)

        if not response_dto.success:
            for field, err_msg in response_dto.errors.items():
                flash(f"{field.capitalize()}: {err_msg}", "danger")
            return render_template(
                "checkout.html",
                cart=cart,
                form_data=request.form,
                errors=response_dto.errors,
            )

        # Clear session cart upon successful purchase
        session["cart"] = []
        session.modified = True

        flash("¡Compra procesada con éxito! Tus claves de activación han sido generadas.", "success")
        return redirect(url_for("store.order_confirmation", order_id=response_dto.order.id))

    def order_confirmation(self, order_id: str):
        """Order confirmation and activation key receipt screen."""
        order = self._get_orders_uc.get_by_id(order_id)
        if not order:
            flash("Orden no encontrada.", "warning")
            return redirect(url_for("store.index"))

        cart = self._get_cart()
        return render_template("confirmation.html", order=order, cart=cart)

    def orders_history(self):
        """Historical purchases list with raw JSON persistence inspector for academic grading."""
        orders = self._get_orders_uc.get_all()
        cart = self._get_cart()

        # Read raw JSON from persistence file for transparent verification
        orders_file = current_app.config.get("ORDERS_FILE")
        raw_json = "[]"
        if orders_file and os.path.exists(orders_file):
            try:
                with open(orders_file, "r", encoding="utf-8") as f:
                    raw_json = json.dumps(json.load(f), indent=2, ensure_ascii=False)
            except Exception:
                raw_json = "[]"

        return render_template(
            "orders.html",
            orders=orders,
            raw_json=raw_json,
            cart=cart,
            orders_count=len(orders),
        )

    # -------------------------------------------------------------
    # AJAX / REST API Endpoints for Reactive UI
    # -------------------------------------------------------------
    def api_cart_add(self, game_id: str):
        """AJAX endpoint adding a game to cart without page reload."""
        try:
            game = self._get_game_uc.execute_by_id(game_id)
            cart = self._get_cart()
            added = cart.add_game(game)
            self._save_cart(cart)
            return jsonify({
                "success": True,
                "added": added,
                "message": f"¡'{game.title}' añadido al carrito!" if added else f"'{game.title}' ya estaba en tu carrito.",
                "cart_count": cart.item_count,
                "subtotal": cart.subtotal,
                "total": cart.total,
                "game": {
                    "id": game.id,
                    "title": game.title,
                    "price": game.final_price,
                    "cover_image": game.cover_image,
                }
            })
        except GameNotFoundError:
            return jsonify({"success": False, "message": "Videojuego no encontrado."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    def api_cart_remove(self, game_id: str):
        """AJAX endpoint removing an item from cart."""
        cart = self._get_cart()
        removed = cart.remove_game(game_id)
        self._save_cart(cart)
        return jsonify({
            "success": removed,
            "cart_count": cart.item_count,
            "subtotal": cart.subtotal,
            "total_discount": cart.total_discount,
            "total": cart.total,
            "is_empty": cart.is_empty,
        })

    def api_cart_clear(self):
        """AJAX endpoint clearing the entire cart."""
        session["cart"] = []
        session.modified = True
        return jsonify({"success": True, "cart_count": 0, "total": 0.0})

    def api_cart_state(self):
        """AJAX endpoint returning current items in cart for the offcanvas drawer."""
        cart = self._get_cart()
        items = [
            {
                "id": item.game.id,
                "title": item.game.title,
                "slug": item.game.slug,
                "price": item.unit_price,
                "cover_image": item.game.cover_image,
                "genre": item.game.genre,
            }
            for item in cart.get_items()
        ]
        return jsonify({
            "count": cart.item_count,
            "subtotal": cart.subtotal,
            "total_discount": cart.total_discount,
            "total": cart.total,
            "items": items,
        })

    def api_filter_games(self):
        """AJAX endpoint returning filtered games JSON for instant catalog rendering."""
        search = request.args.get("search", "").strip()
        genre = request.args.get("genre", "Todos")
        only_sales = request.args.get("only_sales", "").lower() in ("1", "true", "on")
        only_indie = request.args.get("only_indie", "").lower() in ("1", "true", "on")
        sort_by = request.args.get("sort", "destacados")

        filter_dto = GameFilterDTO(
            search_query=search,
            genre=genre,
            only_sales=only_sales,
            only_indie=only_indie,
            sort_by=sort_by,
        )

        games = self._search_filter_uc.execute(filter_dto)
        cart = self._get_cart()

        games_data = [
            {
                "id": g.id,
                "title": g.title,
                "slug": g.slug,
                "developer": g.developer,
                "genre": g.genre,
                "price": g.price,
                "discount_percent": g.discount_percent,
                "final_price": g.final_price,
                "rating": g.rating,
                "reviews_count": g.reviews_count,
                "cover_image": g.cover_image,
                "is_featured": g.is_featured,
                "is_indie": g.is_indie,
                "is_on_sale": g.is_on_sale,
                "is_new": g.is_new,
                "tags": g.tags,
                "demo_url": g.demo_url,
                "in_cart": cart.has_game(g.id),
            }
            for g in games
        ]
        return jsonify({"count": len(games_data), "games": games_data})


def create_store_blueprint(controller: StoreWebController) -> Blueprint:
    """Builds and wires the Flask Blueprint connecting URLs to OOP Controller methods."""
    bp = Blueprint("store", __name__)

    # HTML Routes
    bp.add_url_rule("/", "index", controller.index, methods=["GET"])
    bp.add_url_rule("/catalog", "catalog", controller.catalog, methods=["GET"])
    bp.add_url_rule("/game/<slug>", "game_detail", controller.game_detail, methods=["GET"])
    bp.add_url_rule("/cart", "cart_view", controller.cart_view, methods=["GET"])
    bp.add_url_rule("/checkout", "checkout_view", controller.checkout_view, methods=["GET"])
    bp.add_url_rule("/checkout", "process_checkout", controller.process_checkout, methods=["POST"])
    bp.add_url_rule("/confirmation/<order_id>", "order_confirmation", controller.order_confirmation, methods=["GET"])
    bp.add_url_rule("/orders", "orders_history", controller.orders_history, methods=["GET"])

    # REST / AJAX Routes
    bp.add_url_rule("/api/cart/add/<game_id>", "api_cart_add", controller.api_cart_add, methods=["POST"])
    bp.add_url_rule("/api/cart/remove/<game_id>", "api_cart_remove", controller.api_cart_remove, methods=["POST"])
    bp.add_url_rule("/api/cart/clear", "api_cart_clear", controller.api_cart_clear, methods=["POST"])
    bp.add_url_rule("/api/cart/state", "api_cart_state", controller.api_cart_state, methods=["GET"])
    bp.add_url_rule("/api/games", "api_filter_games", controller.api_filter_games, methods=["GET"])

    return bp
