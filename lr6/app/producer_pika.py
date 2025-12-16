import pika
import json
import uuid
from datetime import datetime

connection_params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    virtual_host='local',
    credentials=pika.PlainCredentials('guest', 'guest')
)

def send_message(queue_name: str, message: dict):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message, ensure_ascii=False, indent=2),
        properties=pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2,
        )
    )
    print(f"Сообщение отправлено в очередь '{queue_name}':\n{json.dumps(message, indent=2)}\n")
    connection.close()


def send_products():
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Монитор 27\" 4K",
            "price": 349.99,
            "description": "Цветопередача sRGB 100%, HDR10",
            "available": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Механическая клавиатура",
            "price": 129.99,
            "description": "RGB-подсветка, переключатели Cherry MX Blue",
            "available": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Внешний SSD 1TB",
            "price": 89.99,
            "description": "Скорость до 1050 МБ/с, компактный корпус",
            "available": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Веб-камера Full HD",
            "price": 69.99,
            "description": "Автофокус, шторка приватности",
            "available": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "USB-хаб с портами питания",
            "price": 34.99,
            "description": "7 портов, поддержка быстрой зарядки",
            "available": True
        }
    ]

    for product in products:
        send_message("product", product)


def send_orders():
    user_id = str(uuid.uuid4())
    address_id = str(uuid.uuid4())

    orders = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "address_id": address_id,
            "items": [
                {"product_id": "123e4567-e89b-12d3-a456-426614174000", "quantity": 1}
            ],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "address_id": address_id,
            "items": [
                {"product_id": "123e4567-e89b-12d3-a456-426614174001", "quantity": 2}
            ],
            "status": "shipped",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "address_id": address_id,
            "items": [
                {"product_id": "123e4567-e89b-12d3-a456-426614174002", "quantity": 1}
            ],
            "status": "delivered",
            "created_at": datetime.now().isoformat()
        }
    ]

    for order in orders:
        send_message("order", order)


if __name__ == "__main__":
    print("Запуск продюсера на pika...\n")
    send_products()
    send_orders()
    print("Все сообщения отправлены!")
