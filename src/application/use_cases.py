"""Application use cases coordinating domain entities, invariants, and ports."""
import secrets
from typing import List, Optional, Dict
from ..domain.entities import (
    Game,
    ShoppingCart,
    Order,
    OrderItem,
    generate_digital_key,
)
from ..domain.ports import GameRepository, OrderRepository
from ..domain.exceptions import (
    GameNotFoundError,
    EmptyCartCheckoutError,
    InvalidOrderError,
)
from .dtos import (
    GameFilterDTO,
    CheckoutRequestDTO,
    CheckoutResponseDTO,
)


class ListGamesUseCase:
    """Retrieves games for various storefront sections."""

    def __init__(self, game_repo: GameRepository):
        self._game_repo = game_repo

    def get_all(self) -> List[Game]:
        return self._game_repo.get_all()

    def get_featured(self) -> List[Game]:
        return self._game_repo.get_featured()

    def get_on_sale(self) -> List[Game]:
        return self._game_repo.get_on_sale()

    def get_indie(self) -> List[Game]:
        return self._game_repo.get_indie()

    def get_new_releases(self) -> List[Game]:
        return self._game_repo.get_new_releases()

    def get_genres(self) -> List[str]:
        return self._game_repo.get_genres()


class SearchAndFilterGamesUseCase:
    """Executes dynamic filtering, text search, price limits, and sorting."""

    def __init__(self, game_repo: GameRepository):
        self._game_repo = game_repo

    def execute(self, filters: GameFilterDTO) -> List[Game]:
        games = self._game_repo.get_all()

        # 1. Search query (matches title, developer, or tags)
        if filters.search_query and filters.search_query.strip():
            query = filters.search_query.strip().lower()
            games = [
                g for g in games
                if query in g.title.lower()
                or query in g.developer.lower()
                or any(query in tag.lower() for tag in g.tags)
            ]

        # 2. Genre filter
        if filters.genre and filters.genre != "Todos":
            games = [g for g in games if g.genre.lower() == filters.genre.lower()]

        # 3. Only sales
        if filters.only_sales:
            games = [g for g in games if g.is_on_sale]

        # 4. Only indie
        if filters.only_indie:
            games = [g for g in games if g.is_indie]

        # 5. Max price threshold
        if filters.max_price is not None and filters.max_price > 0:
            games = [g for g in games if g.final_price <= filters.max_price]

        # 6. Sorting
        if filters.sort_by == "precio_menor":
            games.sort(key=lambda g: g.final_price)
        elif filters.sort_by == "precio_mayor":
            games.sort(key=lambda g: g.final_price, reverse=True)
        elif filters.sort_by == "valoracion":
            games.sort(key=lambda g: (g.rating, g.reviews_count), reverse=True)
        elif filters.sort_by == "nombre":
            games.sort(key=lambda g: g.title.lower())
        else:
            # "destacados": featured first, then sales, then rating
            games.sort(key=lambda g: (g.is_featured, g.is_on_sale, g.rating), reverse=True)

        return games


class GetGameDetailUseCase:
    """Fetches full game details by slug or ID."""

    def __init__(self, game_repo: GameRepository):
        self._game_repo = game_repo

    def execute_by_slug(self, slug: str) -> Game:
        game = self._game_repo.get_by_slug(slug)
        if not game:
            raise GameNotFoundError(slug)
        return game

    def execute_by_id(self, game_id: str) -> Game:
        game = self._game_repo.get_by_id(game_id)
        if not game:
            raise GameNotFoundError(game_id)
        return game


class ManageCartUseCase:
    """Encapsulates business operations on the shopping cart."""

    def __init__(self, cart: ShoppingCart):
        self._cart = cart

    @property
    def cart(self) -> ShoppingCart:
        return self._cart

    def add_game(self, game: Game):
        """Adds a game to the cart. Ensures non-duplication through domain entity."""
        return self._cart.add_game(game)

    def remove_game(self, game_id: str):
        """Removes a game from the cart."""
        return self._cart.remove_game(game_id)

    def has_game(self, game_id: str) -> bool:
        """Checks whether a game is in the cart."""
        return self._cart.has_game(game_id)

    def clear(self):
        """Empties the shopping cart."""
        self._cart.clear()


class CheckoutUseCase:
    """Coordinates the simulated checkout transaction.

    Validates payload, enforces cart non-emptiness, computes totals,
    generates simulated activation keys, creates order, persists via repository,
    and clears the cart.
    """

    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    def execute(self, cart: ShoppingCart, request_dto: CheckoutRequestDTO) -> CheckoutResponseDTO:
        # Step 1: Validate cart is not empty
        if cart.is_empty:
            return CheckoutResponseDTO(
                success=False,
                message="El carrito está vacío. Agrega videojuegos antes de comprar.",
                errors={"cart": "Carrito vacío"}
            )

        # Step 2: Validate customer inputs
        validation_errors = request_dto.validate()
        if validation_errors:
            return CheckoutResponseDTO(
                success=False,
                message="Por favor revisa los datos ingresados.",
                errors=validation_errors
            )

        # Step 3: Build order items with unique digital activation keys
        order_items: List[OrderItem] = []
        for item in cart.get_items():
            order_items.append(
                OrderItem(
                    game_id=item.game.id,
                    game_title=item.game.title,
                    price_paid=item.unit_price,
                    digital_key=generate_digital_key()
                )
            )

        # Step 4: Create Order domain entity
        order_id = f"PV-2026-{secrets.token_hex(3).upper()}"
        order = Order(
            id=order_id,
            customer_name=request_dto.customer_name.strip(),
            customer_email=request_dto.customer_email.strip().lower(),
            payment_method=request_dto.payment_method,
            items=order_items,
            subtotal=cart.subtotal,
            total_discount=cart.total_discount,
            total=cart.total,
            status="Completada (Simulación Académica)"
        )

        try:
            order.validate()
        except InvalidOrderError as err:
            return CheckoutResponseDTO(
                success=False,
                message=str(err),
                errors=err.errors
            )

        # Step 5: Persist through port
        persisted_order = self._order_repo.save(order)

        # Step 6: Clear cart upon successful transaction
        cart.clear()

        return CheckoutResponseDTO(
            success=True,
            message="¡Compra simulada completada exitosamente! Tus claves de activación están listas.",
            order=persisted_order
        )


class GetOrdersUseCase:
    """Retrieves past simulated purchase orders."""

    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    def get_all(self) -> List[Order]:
        return self._order_repo.get_all()

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._order_repo.get_by_id(order_id)
