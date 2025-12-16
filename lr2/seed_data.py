from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Address
import uuid

connect_url = "postgresql://postgres:123@127.0.0.1:5432/lr2_db"

engine = create_engine(connect_url, echo=True)

session_factory = sessionmaker(bind=engine)

with session_factory() as session:
    users_data = [
        {"username": "john_doe", "email": "john.doe@example.com"},
        {"username": "jane_smith", "email": "jane.smith@example.com"},
        {"username": "alex_wilson", "email": "alex.wilson@example.com"},
        {"username": "maria_garcia", "email": "maria.garcia@example.com"},
        {"username": "li_wei", "email": "li.wei@example.com"},
    ]

    users = []
    for data in users_data:
        user = User(username=data["username"], email=data["email"])
        session.add(user)
        users.append(user)

    session.commit()

    addresses_data = [
        {"user_id": users[0].id, "street": "123 Main St", "city": "New York", "country": "USA"},
        {"user_id": users[1].id, "street": "456 Oak Ave", "city": "Los Angeles", "country": "USA"},
        {"user_id": users[2].id, "street": "789 Pine Rd", "city": "Chicago", "country": "USA"},
        {"user_id": users[3].id, "street": "101 Maple Ln", "city": "Madrid", "country": "Spain"},
        {"user_id": users[4].id, "street": "202 Bamboo St", "city": "Beijing", "country": "China"},
    ]

    for data in addresses_data:
        address = Address(
            user_id=data["user_id"],
            street=data["street"],
            city=data["city"],
            country=data["country"]
        )
        session.add(address)

    session.commit()