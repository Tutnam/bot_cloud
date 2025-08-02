import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    # Telegram Bot Token
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token_here')
    
    # Максимальный размер файла в байтах (50MB по умолчанию)
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))
    
    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO') 