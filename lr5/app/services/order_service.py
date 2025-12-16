from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID


class OrderService:
    def __init__(
        self,
        order_repository,
        product_repository=None,
        user_repository=None,
        email_service=None,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository
        self.email_service = email_service

    async def update_order_status(self, order_id: int, new_status: str):
        print(
            f"DEBUG: update_order_status called with order_id={order_id}, status={new_status}"
        )

        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        print(
            f"DEBUG: Order found: {order.id}, user: {getattr(order, 'user', 'No user')}"
        )

        updated_order = await self.order_repository.update_status(order_id, new_status)

        if new_status == "shipped" and self.email_service:
            print("DEBUG: Attempting to send shipping email")
            try:
                user_email = (
                    getattr(order.user, "email", None)
                    if hasattr(order, "user")
                    else None
                )
                username = (
                    getattr(order.user, "username", "Customer")
                    if hasattr(order, "user")
                    else "Customer"
                )

                if user_email:
                    await self.email_service.send_order_shipped(
                        email=user_email, order_id=order_id, username=username
                    )
                    print("DEBUG: Email sent successfully")
                else:
                    print("DEBUG: No user email found")

            except Exception as e:
                print(f"DEBUG: Failed to send shipping email: {e}")

        return updated_order

    async def create_order(self, order_data: Dict) -> Dict:
        user_id = order_data["user_id"]
        items = order_data["items"]

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        total_amount = 0
        product_items = []

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            if product.stock_quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for product {product.name}. Available: {product.stock_quantity}, requested: {quantity}"
                )

            item_total = product.price * quantity
            total_amount += item_total

            product_items.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "price_at_time": product.price,
                }
            )

        order = await self.order_repository.create(
            user_id=user_id,
            address_id=user_id,
            product_items=product_items,
            total_amount=total_amount,
        )

        return {
            "order_id": order.id,
            "total_amount": total_amount,
            "status": order.status,
            "items_count": len(items),
        }

    async def get_order(self, order_id: UUID) -> Dict:
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        return {
            "order_id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
        }

    async def create_order(self, order_data: Dict[str, Any]):
        if not order_data.get("items"):
            raise ValueError("Order must contain at least one item")

        for item in order_data["items"]:
            quantity = item.get("quantity", 0)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")

        user_id = order_data["user_id"]
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        total_amount = Decimal("0")
        for item in order_data["items"]:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            if product.stock_quantity < quantity:
                raise ValueError(f"Insufficient stock for product {product.name}")

            item_price = Decimal(str(product.price))
            total_amount += item_price * quantity

            item["price_at_time"] = float(item_price)

        order = await self.order_repository.create(
            user_id=user_id,
            product_items=order_data["items"],
            total_amount=float(total_amount),
        )

        for item in order_data["items"]:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product = await self.product_repository.get_by_id(product_id)
            new_stock = product.stock_quantity - quantity
            await self.product_repository.update_stock(product_id, new_stock)

        return order
