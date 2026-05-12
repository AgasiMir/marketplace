from decimal import Decimal
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.orders.schemas import OrderListPublic, OrderPublic
from app.exceptions.python_exceptions import (
    CartIsEmptyException,
    FailedToLoadOrderException,
    OrderNotFoundException,
    ProductIsOutOfStockException,
    ProductIsUnavailableException,
    ProductWithNoPriceException,
)
from app.models import Order, OrderItem, CartItem


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _load_order_with_items(self, order_id: int) -> Order | None:
        result = await self.session.scalars(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
            )
            .where(Order.id == order_id)
        )
        return result.first()

    async def checkout_order(self, user_id: int):

        # получаем текущее состояние корзины
        cart_result = await self.session.scalars(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        )
        cart_items = cart_result.all()

        # проверяем, что корзина не пуста
        if not cart_items:
            raise CartIsEmptyException

        # создаём заказ и проходим по позициям
        order = Order(user_id=user_id)
        total_amount = Decimal("0")

        for cart_item in cart_items:
            product = cart_item.product
            # Валидируем доступность товара, проверяем два условия:
            # товар активен и остатков достаточно для заказа
            if not product or not product.is_active:
                raise ProductIsUnavailableException(product_id=cart_item.product_id)

            if product.stock < cart_item.quantity:
                raise ProductIsOutOfStockException(product_name=product.name)

            # unit_price берётся из текущего состояния товара, но сохраняется в OrderItem.
            # Даже если цена потом изменится, то в заказе останется старая.
            # фиксируем цену и считаем сумму заказа:
            unit_price = product.price

            if unit_price is None:
                raise ProductWithNoPriceException(product_name=product.name)

            total_price = unit_price * cart_item.quantity
            total_amount += total_price

            # создаём позицию заказа и уменьшаем остатки:
            order_item = OrderItem(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
            order.items.append(order_item)

            product.stock -= cart_item.quantity

        # сохраняем заказ и очищаем корзину:
        order.total_amount = total_amount
        self.session.add(order)

        await self.session.execute(delete(CartItem).where(CartItem.user_id == user_id))
        await self.session.flush()

        # перезагружаем заказ с полными данными:
        created_order = await self._load_order_with_items(order.id)
        if not created_order:
            raise FailedToLoadOrderException

        return OrderPublic.model_validate(created_order)

    async def get_orders(
        self, page: int, page_size: int, user_id: int
    ) -> OrderListPublic:
        """
        Возвращает заказы текущего пользователя с простой пагинацией.
        """

        total = await self.session.scalar(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )

        orders = await self.session.scalars(
            select(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .where(Order.user_id == user_id)
            .order_by(Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        orders = orders.all()

        return OrderListPublic(
            items=orders, total=total or 0, page=page, page_size=page_size
        )

    async def get_order(self, order_id: int, user_id: int) -> OrderPublic:
        """
        Возвращает детальную информацию по заказу, если он принадлежит пользователю.
        """

        order = await self._load_order_with_items(order_id)

        if not order or order.user_id != user_id:
            raise OrderNotFoundException

        return OrderPublic.model_validate(order)
