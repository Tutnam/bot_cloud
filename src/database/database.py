import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "data/files.db"):
        self.db_path = db_path
        self._ensure_database_directory()
        self._migrate_old_database()
        self.init_database()

    def _ensure_database_directory(self):
        """Убедиться, что директория для БД существует"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _migrate_old_database(self):
        """Перенести базу данных из устаревшей папки logs при наличии"""
        old_path = Path("logs/files.db")
        new_path = Path(self.db_path)

        if new_path.exists() or not old_path.exists():
            return

        try:
            old_path.rename(new_path)
            logger.info(f"Перенесена база данных в {new_path}")
        except Exception as e:
            logger.error(f"Не удалось перенести базу данных из logs: {e}")
    
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
            
            # Создаем таблицу для ссылок на файлы
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS share_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    share_id TEXT UNIQUE NOT NULL,
                    file_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    record_id INTEGER NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (record_id) REFERENCES files (id) ON DELETE CASCADE
                )
            ''')
            
            # Создаем таблицу для пользовательских ссылок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    tags TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
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
        """Поиск файлов по названию, описанию, тегам или типу файла"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id 
                    FROM files 
                    WHERE user_id = ? AND (
                        file_name LIKE ? OR 
                        description LIKE ? OR 
                        tags LIKE ? OR 
                        file_type LIKE ?
                    )
                    ORDER BY upload_date DESC
                ''', (user_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
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
    
    async def add_share_link(self, share_id: str, file_id: str, user_id: int, record_id: int):
        """Добавить ссылку на файл"""
        try:
            from datetime import datetime, timedelta
            
            # Устанавливаем срок действия ссылки (24 часа)
            expires_date = datetime.now() + timedelta(hours=24)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO share_links (share_id, file_id, user_id, record_id, expires_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (share_id, file_id, user_id, record_id, expires_date))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении ссылки: {e}")
            return False
    
    async def get_share_link(self, share_id: str):
        """Получить информацию о ссылке"""
        try:
            from datetime import datetime
            
            logger.info(f"Ищем ссылку с share_id: {share_id}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT sl.share_id, sl.file_id, sl.user_id, sl.record_id, sl.created_date, sl.expires_date, sl.is_active,
                           f.file_name, f.file_size, f.file_type, f.category, f.description, f.tags
                    FROM share_links sl
                    JOIN files f ON sl.record_id = f.id
                    WHERE sl.share_id = ? AND sl.is_active = 1
                ''', (share_id,))
                result = cursor.fetchone()
                
                logger.info(f"Результат поиска ссылки: {result}")
                
                if result:
                    # Проверяем, не истекла ли ссылка
                    expires_date = datetime.fromisoformat(result[5])
                    logger.info(f"Срок действия ссылки: {expires_date}, текущее время: {datetime.now()}")
                    
                    if datetime.now() > expires_date:
                        logger.warning(f"Ссылка {share_id} истекла")
                        # Помечаем ссылку как неактивную
                        cursor.execute('UPDATE share_links SET is_active = 0 WHERE share_id = ?', (share_id,))
                        conn.commit()
                        return None
                    
                    logger.info(f"Ссылка {share_id} найдена и активна")
                    return result
                else:
                    logger.warning(f"Ссылка {share_id} не найдена")
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении ссылки: {e}")
            return None
    
    async def deactivate_share_link(self, share_id: str):
        """Деактивировать ссылку"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE share_links SET is_active = 0 WHERE share_id = ?
                ''', (share_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при деактивации ссылки: {e}")
            return False
    
    async def cleanup_expired_links(self):
        """Очистить истекшие ссылки"""
        try:
            from datetime import datetime
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE share_links SET is_active = 0 
                    WHERE expires_date < ? AND is_active = 1
                ''', (datetime.now(),))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Ошибка при очистке истекших ссылок: {e}")
            return 0
    
    # Методы для работы с пользовательскими ссылками
    async def check_link_exists(self, user_id: int, url: str):
        """Проверить, существует ли ссылка у пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, description, category, tags, created_date
                    FROM user_links 
                    WHERE user_id = ? AND url = ? AND is_active = 1
                ''', (user_id, url))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка при проверке существования ссылки: {e}")
            return None

    async def add_user_link(self, user_id: int, title: str, url: str, description: str = None, 
                           category: str = 'general', tags: str = None):
        """Добавить пользовательскую ссылку"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_links (user_id, title, url, description, category, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, title, url, description, category, tags))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при добавлении ссылки: {e}")
            return None
    
    async def get_user_links(self, user_id: int):
        """Получить все ссылки пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, description, category, tags, created_date
                    FROM user_links 
                    WHERE user_id = ? AND is_active = 1 
                    ORDER BY created_date DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении ссылок пользователя: {e}")
            return []
    
    async def get_user_links_by_category(self, user_id: int, category: str):
        """Получить ссылки пользователя по категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, description, category, tags, created_date
                    FROM user_links 
                    WHERE user_id = ? AND category = ? AND is_active = 1 
                    ORDER BY created_date DESC
                ''', (user_id, category))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении ссылок по категории: {e}")
            return []
    
    async def get_user_link_categories(self, user_id: int):
        """Получить категории ссылок пользователя с количеством"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT category, COUNT(*) as count
                    FROM user_links 
                    WHERE user_id = ? AND is_active = 1 
                    GROUP BY category 
                    ORDER BY count DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении категорий ссылок: {e}")
            return []
    
    async def get_user_link_by_id(self, link_id: int, user_id: int):
        """Получить ссылку по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, description, category, tags, created_date
                    FROM user_links 
                    WHERE id = ? AND user_id = ? AND is_active = 1
                ''', (link_id, user_id))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка при получении ссылки: {e}")
            return None
    
    async def delete_user_link(self, link_id: int, user_id: int):
        """Удалить ссылку пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE user_links SET is_active = 0 
                    WHERE id = ? AND user_id = ?
                ''', (link_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении ссылки: {e}")
            return False
    
    async def search_user_links(self, user_id: int, query: str):
        """Поиск ссылок пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, description, category, tags, created_date
                    FROM user_links 
                    WHERE user_id = ? AND is_active = 1 AND (
                        title LIKE ? OR 
                        description LIKE ? OR 
                        tags LIKE ? OR 
                        url LIKE ?
                    )
                    ORDER BY created_date DESC
                ''', (user_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при поиске ссылок: {e}")
            return []
    
    async def get_user_links_stats(self, user_id: int):
        """Получить статистику ссылок пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM user_links WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                result = cursor.fetchone()
                return {
                    'total_links': result[0] or 0
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики ссылок: {e}")
            return {'total_links': 0} 