from decimal import Decimal
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.exceptions.python_exceptions import (
    CartItemNotFoundException,
    ProductNotFoundException,
)
from app.domains.cart_items.schemas import (
    CartItemPublic,
    CartItemUpdate,
    CartPublic,
    CartItemCreate,
)
from app.models import Product, Category, User, CartItem


class CartItemsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _check_if_product_exists(self, product_id: int) -> Product:
        product = await self.session.scalar(
            select(Product)
            .join(Product.category)
            .join(Product.seller)
            .where(
                Product.id == product_id,
                Product.is_active,
                Category.is_active,
                User.is_active,
            )
        )
        if not product:
            raise ProductNotFoundException

        return product

    async def _get_cart_item(self, user_id: int, product_id: int) -> CartItem | None:
        cart_item = await self.session.scalar(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        )

        return cart_item

    async def get_cart(self, user_id: int) -> CartPublic:

        cart = await self.session.scalars(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        )
        items = cart.all()
        total_quantity = sum(item.quantity for item in items)

        price_items = (
            Decimal(item.quantity)
            * (item.product.price if item.product.price is not None else Decimal("0"))
            for item in items
        )
        total_price_decimal = sum(price_items, Decimal("0.00"))

        return CartPublic(
            user_id=user_id,
            items=items,
            total_quantity=total_quantity,
            total_price=total_price_decimal,
        )

    async def add_item_to_cart(
        self, create_cart_item: CartItemCreate, user_id: int
    ) -> CartItemPublic:
        product = await self._check_if_product_exists(create_cart_item.product_id)

        if create_cart_item.quantity > product.stock:
            create_cart_item.quantity = product.stock

        cart_item = await self._get_cart_item(user_id, create_cart_item.product_id)

        if cart_item:
            if cart_item.quantity + create_cart_item.quantity > product.stock:
                cart_item.quantity = product.stock
            else:
                cart_item.quantity += create_cart_item.quantity

        else:
            cart_item = CartItem(**create_cart_item.model_dump(), user_id=user_id)
            self.session.add(cart_item)

        updated_item = await self._get_cart_item(user_id, create_cart_item.product_id)
        return CartItemPublic.model_validate(updated_item)

    async def update_cart_item(
        self, product_id: int, update_cart_item: CartItemUpdate, user_id: int
    ) -> CartItemPublic:
        product = await self._check_if_product_exists(product_id)

        if update_cart_item.quantity > product.stock:
            update_cart_item.quantity = product.stock

        cart_item = await self._get_cart_item(user_id, product_id)

        if not cart_item:
            raise CartItemNotFoundException

        cart_item.quantity = update_cart_item.quantity
        await self.session.flush()

        updated_item = await self._get_cart_item(
            user_id,
            product_id,
        )

        return CartItemPublic.model_validate(updated_item)

    async def delete_cart_item(self, product_id: int, user_id: int) -> None:

        cart_item = await self._get_cart_item(user_id, product_id)

        if not cart_item:
            raise CartItemNotFoundException

        await self.session.delete(cart_item)
        await self.session.flush()

    async def clear_cart(self, user_id: int) -> None:

        await self.session.execute(delete(CartItem).where(CartItem.user_id == user_id))
        await self.session.flush()
