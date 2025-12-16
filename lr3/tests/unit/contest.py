import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(engine, tables):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
async def user_repository(session):
    return UserRepository(session)


@pytest.fixture
async def product_repository(session):
    return ProductRepository(session)


@pytest.fixture
async def order_repository(session):
    return OrderRepository(session)


@pytest.fixture(autouse=True)
async def cleanup_database(session):
    yield

    try:
        from app.models import User, Product, Order, Address

        await session.execute(Order.__table__.delete())
        await session.execute(Product.__table__.delete())
        await session.execute(Address.__table__.delete())
        await session.execute(User.__table__.delete())

        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"Cleanup warning: {e}")