#!/usr/bin/env python3
"""
Тестовый скрипт для симуляции команды start с параметрами
"""

import asyncio
import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.handlers import cmd_start
from src.database.database import Database

# Создаем мок объект Message для тестирования
class MockMessage:
    def __init__(self, text, user_id=12345):
        self.text = text
        self.from_user = MockUser(user_id)
    
    async def answer(self, text, reply_markup=None):
        print(f"📤 Бот отвечает: {text}")
        if reply_markup:
            print(f"⌨️ Клавиатура: {reply_markup}")

class MockUser:
    def __init__(self, user_id):
        self.id = user_id

async def test_start_command():
    """Тест обработки команды start с параметрами"""
    print("🧪 Тестируем обработку команды start...")
    
    # Создаем тестовую базу данных
    db = Database("test_start.db")
    
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
        
        # 3. Тестируем команду start без параметров
        print("\n📝 Тестируем /start без параметров...")
        message = MockMessage("/start")
        await cmd_start(message)
        
        # 4. Тестируем команду start с параметром файла
        print("\n📝 Тестируем /start с параметром файла...")
        message_with_file = MockMessage(f"/start file_{share_id}")
        await cmd_start(message_with_file)
        
        print("\n🎉 Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Удаляем тестовую базу данных
        if os.path.exists("test_start.db"):
            os.remove("test_start.db")
            print("🗑️ Тестовая база данных удалена")

if __name__ == "__main__":
    asyncio.run(test_start_command()) 