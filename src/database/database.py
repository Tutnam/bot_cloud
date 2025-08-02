import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "logs/files.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    tags TEXT,
                    message_id INTEGER,
                    chat_id INTEGER
                )
            ''')
            conn.commit()
    
    async def add_file(self, file_id: str, file_name: str, file_size: int, 
                       file_type: str, category: str, user_id: int, description: str = None, tags: str = None,
                       message_id: int = None, chat_id: int = None):
        """Добавить файл в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO files (file_id, file_name, file_size, file_type, category, user_id, description, tags, message_id, chat_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (file_id, file_name, file_size, file_type, category, user_id, description, tags, message_id, chat_id))
                conn.commit()
                return cursor.lastrowid  # Возвращаем ID записи
        except Exception as e:
            logger.error(f"Ошибка при добавлении файла: {e}")
            return "error"  # Возвращаем код ошибки
    
    async def get_user_files(self, user_id: int):
        """Получить все файлы пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id 
                    FROM files WHERE user_id = ? ORDER BY upload_date DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении файлов пользователя: {e}")
            return []
    
    async def get_user_files_by_category(self, user_id: int, category: str):
        """Получить файлы пользователя по категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id 
                    FROM files WHERE user_id = ? AND category = ? ORDER BY upload_date DESC
                ''', (user_id, category))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении файлов по категории: {e}")
            return []
    
    async def get_user_categories(self, user_id: int):
        """Получить категории пользователя с количеством файлов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT category, COUNT(*) as count, SUM(file_size) as total_size
                    FROM files WHERE user_id = ? GROUP BY category ORDER BY count DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении категорий пользователя: {e}")
            return []
    
    async def get_file_by_id(self, file_id: str):
        """Получить файл по file_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id 
                    FROM files WHERE file_id = ?
                ''', (file_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка при получении файла: {e}")
            return None
    
    async def check_file_exists(self, file_id: str, user_id: int):
        """Проверить, существует ли файл у пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT file_name, file_size FROM files 
                    WHERE file_id = ? AND user_id = ?
                ''', (file_id, user_id))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка при проверке существования файла: {e}")
            return None
    
    async def get_file_by_record_id(self, record_id):
        """Получить файл по ID записи"""
        try:
            # Преобразуем record_id в int, если он строка
            if isinstance(record_id, str):
                record_id = int(record_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id 
                    FROM files WHERE id = ?
                ''', (record_id,))
                result = cursor.fetchone()
                logger.info(f"Поиск файла с record_id {record_id}: {result}")
                return result
        except Exception as e:
            logger.error(f"Ошибка при получении файла по ID записи: {e}")
            return None
    
    async def delete_file(self, file_id: str, user_id: int):
        """Удалить файл из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM files WHERE file_id = ? AND user_id = ?
                ''', (file_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении файла: {e}")
            return False
    
    async def delete_file_by_record_id(self, record_id: int, user_id: int):
        """Удалить файл из базы данных по ID записи"""
        try:
            # Преобразуем record_id в int, если он строка
            if isinstance(record_id, str):
                record_id = int(record_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM files WHERE id = ? AND user_id = ?
                ''', (record_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении файла по record_id: {e}")
            return False
    
    async def search_files(self, user_id: int, query: str):
        """Поиск файлов по названию или описанию"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id 
                    FROM files 
                    WHERE user_id = ? AND (file_name LIKE ? OR description LIKE ?)
                    ORDER BY upload_date DESC
                ''', (user_id, f"%{query}%", f"%{query}%"))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при поиске файлов: {e}")
            return []
    
    async def get_file_stats(self, user_id: int):
        """Получить статистику файлов пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*), SUM(file_size) FROM files WHERE user_id = ?
                ''', (user_id,))
                result = cursor.fetchone()
                return {
                    'total_files': result[0] or 0,
                    'total_size': result[1] or 0
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return {'total_files': 0, 'total_size': 0} 