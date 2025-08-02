#!/usr/bin/env python3
"""
FileStorage Bot - Telegram файлохранилище
Запуск бота
"""

import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.main import main
import asyncio

if __name__ == "__main__":
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Ошибка: Файл .env не найден!")
        print("📝 Создайте файл .env и добавьте в него BOT_TOKEN=ваш_токен_бота")
        exit(1)
    
    # Создаем папку для логов если её нет
    os.makedirs('logs', exist_ok=True)
    
    # Запускаем бота
    asyncio.run(main()) 