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
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_add_file(self):
        """Тест добавления файла"""
        async def run_test():
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
        
        asyncio.run(run_test())
    
    def test_get_user_files(self):
        """Тест получения файлов пользователя"""
        async def run_test():
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
        
        asyncio.run(run_test())
    
    def test_add_share_link(self):
        """Тест добавления ссылки на файл"""
        async def run_test():
            # Сначала добавляем файл
            record_id = await self.db.add_file(
                file_id="test_file_id",
                file_name="test.pdf",
                file_size=1024,
                file_type="pdf",
                category="documents",
                user_id=12345
            )
            
            # Добавляем ссылку
            success = await self.db.add_share_link(
                share_id="test_share_123",
                file_id="test_file_id",
                user_id=12345,
                record_id=record_id
            )
            
            self.assertTrue(success)
        
        asyncio.run(run_test())
    
    def test_get_share_link(self):
        """Тест получения ссылки на файл"""
        async def run_test():
            # Добавляем файл и ссылку
            record_id = await self.db.add_file(
                file_id="test_file_id",
                file_name="test.pdf",
                file_size=1024,
                file_type="pdf",
                category="documents",
                user_id=12345
            )
            
            await self.db.add_share_link(
                share_id="test_share_123",
                file_id="test_file_id",
                user_id=12345,
                record_id=record_id
            )
            
            # Получаем ссылку
            share_data = await self.db.get_share_link("test_share_123")
            
            self.assertIsNotNone(share_data)
            self.assertEqual(share_data[0], "test_share_123")  # share_id
            self.assertEqual(share_data[7], "test.pdf")  # file_name
        
        asyncio.run(run_test())
    
    def test_deactivate_share_link(self):
        """Тест деактивации ссылки"""
        async def run_test():
            # Добавляем файл и ссылку
            record_id = await self.db.add_file(
                file_id="test_file_id",
                file_name="test.pdf",
                file_size=1024,
                file_type="pdf",
                category="documents",
                user_id=12345
            )
            
            await self.db.add_share_link(
                share_id="test_share_123",
                file_id="test_file_id",
                user_id=12345,
                record_id=record_id
            )
            
            # Деактивируем ссылку
            success = await self.db.deactivate_share_link("test_share_123")
            
            self.assertTrue(success)
            
            # Проверяем, что ссылка больше не активна
            share_data = await self.db.get_share_link("test_share_123")
            self.assertIsNone(share_data)
        
        asyncio.run(run_test())

    def test_get_bot_share_url(self):
        """Тест генерации ссылки с именем бота"""
        from src.handlers.handlers import get_bot_share_url
        
        # Тестируем с заглушкой (когда имя бота не установлено)
        share_id = "test123"
        url = get_bot_share_url(share_id)
        self.assertEqual(url, "https://t.me/your_bot_username?start=file_test123")
        
        # Тестируем с установленным именем бота
        from src.config.config import Config
        Config.BOT_USERNAME = "test_bot"
        url = get_bot_share_url(share_id)
        self.assertEqual(url, "https://t.me/test_bot?start=file_test123")

if __name__ == '__main__':
    unittest.main() 