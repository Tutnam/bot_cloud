import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    # Telegram Bot Token
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token_here')
    
    # Максимальный размер файла в байтах (50MB по умолчанию)
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))
    
    # Redis настройки
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PREFIX = os.getenv('REDIS_PREFIX', 'filestorage_bot')
    
    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Информация о боте (будет установлена при запуске)
    BOT_USERNAME = None
    
    @classmethod
    async def get_bot_info(cls, bot):
        """Получить информацию о боте"""
        try:
            bot_info = await bot.get_me()
            cls.BOT_USERNAME = bot_info.username
            return bot_info
        except Exception as e:
            print(f"❌ Ошибка при получении информации о боте: {e}")
            return None 