#!/usr/bin/env python3
"""
Тест для проверки обработки команды start с параметрами
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

async def test_start_with_params():
    """Тест обработки команды start с параметрами"""
    print("🧪 Тестируем обработку команды start с параметрами...")
    
    # Используем реальную базу данных
    from src.database.database import Database
    db = Database("logs/files.db")
    
    try:
        # Тестируем команду start с параметром файла
        print("\n📝 Тестируем /start с параметром файла...")
        message_with_file = MockMessage("/start file_14a41458311c")
        await cmd_start(message_with_file)
        
        print("\n📝 Тестируем /start без параметров...")
        message_normal = MockMessage("/start")
        await cmd_start(message_normal)
        
        print("\n🎉 Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_start_with_params()) 