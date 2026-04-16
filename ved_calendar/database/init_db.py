"""
Скрипт инициализации базы данных
Запускается автоматически при деплое на Railway
"""
import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db


async def main():
    """Инициализация БД"""
    try:
        print("Начало инициализации базы данных...")
        await init_db()
        print("База данных успешно инициализирована!")
        return True
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
