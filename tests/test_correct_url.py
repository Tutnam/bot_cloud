#!/usr/bin/env python3
"""
Скрипт для генерации правильной ссылки с реальным именем бота
"""

import asyncio
import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.config import Config
from src.handlers.handlers import get_bot_share_url

async def test_correct_url():
    """Тест генерации правильной ссылки"""
    print("🔗 Генерируем правильную ссылку...")
    
    try:
        # Получаем информацию о боте
        from aiogram import Bot
        bot = Bot(token=Config.BOT_TOKEN)
        bot_info = await Config.get_bot_info(bot)
        await bot.session.close()
        
        if bot_info:
            print(f"✅ Информация о боте получена:")
            print(f"   Имя: {bot_info.first_name}")
            print(f"   Username: @{bot_info.username}")
            print(f"   BOT_USERNAME в конфиге: {Config.BOT_USERNAME}")
            
            # Генерируем ссылку с реальным именем бота
            share_id = "14a41458311c"  # Реальная ссылка из базы данных
            full_url = get_bot_share_url(share_id)
            print(f"\n🔗 Правильная ссылка: {full_url}")
            
            print(f"\n📝 Для тестирования:")
            print(f"1. Скопируйте ссылку выше")
            print(f"2. Откройте её в браузере или Telegram")
            print(f"3. Проверьте, что бот показывает информацию о файле")
            
        else:
            print("❌ Не удалось получить информацию о боте")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_correct_url()) 