import asyncio
import logging
from aiogram import Bot
from config import Config

async def reset_webhook():
    """Сброс webhook и запуск бота"""
    bot = Bot(token=Config.BOT_TOKEN)
    
    try:
        # Сбрасываем webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook сброшен успешно")
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"🤖 Бот: @{bot_info.username}")
        
    except Exception as e:
        print(f"❌ Ошибка при сбросе webhook: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(reset_webhook()) 