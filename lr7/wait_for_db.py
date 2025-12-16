import os
import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def wait_for_db():
    database_url = os.getenv("postgresql+asyncpg://postgres:123@postgres:5432/lr7_db")
    if not database_url:
        print("Ошибка: переменная окружения DATABASE_URL не установлена", file=sys.stderr)
        sys.exit(1)

    sync_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")

    print("Ожидание подключения к базе данных...")
    for i in range(30):
        try:
            engine = create_engine(sync_url)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ База данных доступна!")
            return
        except OperationalError as e:
            print(f"Попытка {i + 1}/30: БД недоступна — {e}")
            time.sleep(2)
    print("Не удалось подключиться к базе данных за 60 секунд", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()