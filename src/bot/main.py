import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src.config.config import Config
from src.handlers.handlers import router, init_database

# Создаем директорию для логов, если её нет
os.makedirs('logs', exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    # Initialize database first
    init_database()
    
    # Инициализируем бота и диспетчер
    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Временно используем MemoryStorage для отладки
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()
    logger.info("✅ Используется MemoryStorage для хранения состояний")
    
    dp = Dispatcher(storage=storage)
    
    # Получаем информацию о боте
    bot_info = await Config.get_bot_info(bot)
    if bot_info:
        logger.info(f"🤖 Бот @{bot_info.username} ({bot_info.first_name}) запускается...")
        logger.info(f"📝 Имя бота установлено: @{Config.BOT_USERNAME}")
    else:
        logger.warning("⚠️ Не удалось получить информацию о боте")
        logger.warning("🔧 Бот будет использовать 'your_bot_username' в ссылках")
    
    # Регистрируем роутеры
    dp.include_router(router)
    
    logger.info("🤖 FileStorage Bot запускается...")
    
    try:
        # Запускаем бота с настройками для избежания конфликтов
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        logger.info("🛑 Бот запущен")
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    # Проверяем токен бота
    if Config.BOT_TOKEN == "your_bot_token_here":
        print("❌ Ошибка: Не установлен токен бота!")
        print("📝 Создайте файл .env и добавьте в него BOT_TOKEN=ваш_токен_бота")
        exit(1)

    # Запускаем бота
    asyncio.run(main()) 
