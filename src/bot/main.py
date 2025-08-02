import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src.config.config import Config
from src.handlers.handlers import router

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
    # Инициализируем бота и диспетчер
    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутеры
    dp.include_router(router)
    
    logger.info("🤖 FileStorage Bot запускается...")
    
    try:
        # Запускаем бота
        await dp.start_polling(bot)
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
