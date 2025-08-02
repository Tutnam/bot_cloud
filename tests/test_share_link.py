#!/usr/bin/env python3
"""
Тестовый скрипт для проверки создания и использования ссылки
"""

import asyncio
import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import Database
from src.handlers.handlers import get_bot_share_url

async def test_share_link():
    """Тест создания и получения ссылки"""
    print("🧪 Тестируем создание и получение ссылки...")
    
    # Создаем временную базу данных
    db = Database("test_share.db")
    
    try:
        # 1. Добавляем тестовый файл
        print("📁 Добавляем тестовый файл...")
        record_id = await db.add_file(
            file_id="test_file_123",
            file_name="test_document.pdf",
            file_size=1024 * 1024,  # 1MB
            file_type="pdf",
            category="documents",
            user_id=12345,
            description="Тестовый документ",
            tags="тест,документ"
        )
        print(f"✅ Файл добавлен с record_id: {record_id}")
        
        # 2. Создаем ссылку
        print("🔗 Создаем ссылку...")
        share_id = "test_share_123"
        success = await db.add_share_link(
            share_id=share_id,
            file_id="test_file_123",
            user_id=12345,
            record_id=record_id
        )
        print(f"✅ Ссылка создана: {success}")
        
        # 3. Получаем ссылку
        print("📥 Получаем ссылку...")
        share_data = await db.get_share_link(share_id)
        print(f"✅ Данные ссылки: {share_data}")
        
        if share_data:
            share_id, file_id, user_id, record_id, created_date, expires_date, is_active, file_name, file_size, file_type, category, description, tags = share_data
            print(f"📄 Файл: {file_name}")
            print(f"📏 Размер: {file_size / (1024 * 1024):.2f} MB")
            print(f"📁 Тип: {file_type}")
            print(f"📅 Создана: {created_date}")
            print(f"⏰ Истекает: {expires_date}")
        
        # 4. Генерируем полную ссылку
        print("🔗 Генерируем полную ссылку...")
        full_url = get_bot_share_url(share_id)
        print(f"✅ Полная ссылка: {full_url}")
        
        # 5. Проверяем, что ссылка работает
        print("🔄 Проверяем повторное получение ссылки...")
        share_data_again = await db.get_share_link(share_id)
        print(f"✅ Ссылка все еще активна: {share_data_again is not None}")
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Удаляем тестовую базу данных
        if os.path.exists("test_share.db"):
            os.remove("test_share.db")
            print("🗑️ Тестовая база данных удалена")

if __name__ == "__main__":
    asyncio.run(test_share_link()) 