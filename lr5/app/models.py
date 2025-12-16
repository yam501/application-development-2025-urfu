import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

order_product_association = Table(
    "order_products",
    Base.metadata,
    Column("order_id", UUID(as_uuid=True), ForeignKey("orders.id"), primary_key=True),
    Column(
        "product_id", UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True
    ),
    Column("quantity", Integer, nullable=False),
    Column("price_at_time", Numeric(10, 2), nullable=False),
)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    user = relationship("User", back_populates="addresses")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String)
    stock_quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    orders = relationship(
        "Order", secondary=order_product_association, back_populates="products"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)
    status = Column(String, default="pending")
    total_amount = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="orders")
    address = relationship("Address")
    products = relationship(
        "Product", secondary=order_product_association, back_populates="orders"
    )
