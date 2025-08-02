#!/usr/bin/env python3
"""
Тесты для модуля базы данных
"""

import asyncio
import unittest
import tempfile
import os
import sys

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database.database import Database

class TestDatabase(unittest.TestCase):
    """Тесты для класса Database"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную базу данных
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную базу данных
        self.temp_db.close()
        os.unlink(self.temp_db.name)
    
    def test_init_database(self):
        """Тест инициализации базы данных"""
        # Проверяем, что таблица создана
        with self.db.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    async def test_add_file(self):
        """Тест добавления файла"""
        result = await self.db.add_file(
            file_id="test_file_id",
            file_name="test.pdf",
            file_size=1024,
            file_type="pdf",
            category="documents",
            user_id=12345,
            description="Test file",
            tags="test,document"
        )
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
    
    async def test_get_user_files(self):
        """Тест получения файлов пользователя"""
        # Добавляем тестовый файл
        await self.db.add_file(
            file_id="test_file_id",
            file_name="test.pdf",
            file_size=1024,
            file_type="pdf",
            category="documents",
            user_id=12345
        )
        
        # Получаем файлы
        files = await self.db.get_user_files(12345)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][2], "test.pdf")  # file_name

if __name__ == '__main__':
    unittest.main() 