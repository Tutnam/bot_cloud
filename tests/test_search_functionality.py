#!/usr/bin/env python3
"""
Тест функциональности поиска файлов
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import Database
from src.config.config import Config

async def test_search_functionality():
    """Тест функциональности поиска"""
    print("🔍 Тестирование функциональности поиска...")
    
    # Инициализируем базу данных
    db = Database()
    # База данных инициализируется автоматически в конструкторе
    
    # Тестовый пользователь
    test_user_id = 12345
    
    # Добавляем тестовые файлы
    test_files = [
        {
            'file_id': 'test_file_1',
            'file_name': 'документ.pdf',
            'file_size': 1024 * 1024,  # 1MB
            'file_type': 'pdf',
            'category': 'document',
            'description': 'Важный документ',
            'tags': 'важный, документ'
        },
        {
            'file_id': 'test_file_2',
            'file_name': 'фото.jpg',
            'file_size': 2048 * 1024,  # 2MB
            'file_type': 'jpg',
            'category': 'image',
            'description': 'Красивое фото',
            'tags': 'фото, красивый'
        },
        {
            'file_id': 'test_file_3',
            'file_name': 'музыка.mp3',
            'file_size': 512 * 1024,  # 512KB
            'file_type': 'mp3',
            'category': 'audio',
            'description': 'Любимая песня',
            'tags': 'музыка, любимая'
        }
    ]
    
    print("📁 Добавляем тестовые файлы...")
    for file_data in test_files:
        result = await db.add_file(
            file_id=file_data['file_id'],
            file_name=file_data['file_name'],
            file_size=file_data['file_size'],
            file_type=file_data['file_type'],
            category=file_data['category'],
            user_id=test_user_id,
            description=file_data['description'],
            tags=file_data['tags'],
            message_id=1,
            chat_id=1
        )
        if isinstance(result, int):
            print(f"✅ Добавлен файл: {file_data['file_name']}")
        else:
            print(f"❌ Ошибка добавления файла: {file_data['file_name']}")
    
    # Тестируем поиск
    print("\n🔍 Тестируем поиск...")
    
    # Тест 1: Поиск по названию
    print("Тест 1: Поиск по названию 'документ'")
    results = await db.search_files(test_user_id, "документ")
    print(f"Найдено файлов: {len(results)}")
    for file_data in results:
        print(f"  - {file_data[2]}")  # file_name
    
    # Тест 2: Поиск по описанию
    print("\nТест 2: Поиск по описанию 'красивое'")
    results = await db.search_files(test_user_id, "красивое")
    print(f"Найдено файлов: {len(results)}")
    for file_data in results:
        print(f"  - {file_data[2]}")  # file_name
    
    # Тест 3: Поиск по тегам
    print("\nТест 3: Поиск по тегам 'любимая'")
    results = await db.search_files(test_user_id, "любимая")
    print(f"Найдено файлов: {len(results)}")
    for file_data in results:
        print(f"  - {file_data[2]}")  # file_name
    
    # Тест 4: Поиск несуществующего
    print("\nТест 4: Поиск несуществующего 'несуществующий'")
    results = await db.search_files(test_user_id, "несуществующий")
    print(f"Найдено файлов: {len(results)}")
    
    # Тест 5: Поиск по типу файла
    print("\nТест 5: Поиск по типу 'pdf'")
    results = await db.search_files(test_user_id, "pdf")
    print(f"Найдено файлов: {len(results)}")
    for file_data in results:
        print(f"  - {file_data[2]}")  # file_name
    
    # Очищаем тестовые данные
    print("\n🧹 Очищаем тестовые данные...")
    for file_data in test_files:
        # Получаем record_id для удаления
        files = await db.get_user_files(test_user_id)
        for file_record in files:
            if file_record[1] == file_data['file_id']:  # file_id
                await db.delete_file_by_record_id(file_record[0], test_user_id)  # record_id
                print(f"🗑️ Удален файл: {file_data['file_name']}")
                break
    
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_search_functionality()) 