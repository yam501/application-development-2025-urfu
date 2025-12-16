class EmailService:
    async def send_order_shipped(
        self, email: str, order_id: int, username: str
    ) -> bool:
        print(f"Sending shipping email to {email} for order {order_id}")
        return True
