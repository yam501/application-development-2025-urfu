from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Integer

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)  # ----------
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    addresses = relationship("Address", back_populates="user")


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
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
    __tablename__ = 'products'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey('addresses.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User")
    address = relationship("Address")
    product = relationship("Product")