from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload
from models import User, Address

connect_url = "postgresql://postgres:123@127.0.0.1:5432/lr2_db"
engine = create_engine(connect_url, echo=False)

session_factory = sessionmaker(bind=engine)

with session_factory() as session:
    stmt = select(User).options(selectinload(User.addresses))
    users = session.scalars(stmt).all()

    for user in users:
        print(f"Пользователь: {user.username} ({user.email})")
        if user.addresses:
            for addr in user.addresses:
                print(f"Адрес: {addr.street}, {addr.city}, {addr.country}")
        else:
            print("Адресов нет")
        print("-" * 20)