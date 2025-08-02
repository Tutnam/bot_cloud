#!/usr/bin/env python3
"""
Утилита для управления ботом
"""

import sys
import os
import requests
import json

def get_bot_info_from_api(token):
    """Получение информации о боте через API"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"🤖 Информация о боте:")
                print(f"   Имя: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                print(f"   ID: {bot_info.get('id', 'N/A')}")
                print(f"   Поддерживает inline: {bot_info.get('supports_inline_queries', False)}")
                return True
            else:
                print(f"❌ Ошибка API: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при получении информации: {e}")
        return False

def reset_webhook_from_api(token):
    """Сброс webhook через API"""
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    params = {"drop_pending_updates": True}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Webhook сброшен успешно")
                
                # Получаем информацию о боте
                if get_bot_info_from_api(token):
                    # Проверяем статус webhook
                    webhook_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
                    webhook_response = requests.get(webhook_url)
                    if webhook_response.status_code == 200:
                        webhook_data = webhook_response.json()
                        if webhook_data.get('ok'):
                            webhook_info = webhook_data['result']
                            if webhook_info.get('url'):
                                print(f"🌐 Webhook URL: {webhook_info['url']}")
                            else:
                                print("🌐 Webhook не установлен")
                return True
            else:
                print(f"❌ Ошибка API: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при сбросе webhook: {e}")
        return False

def main():
    """Главная функция утилиты"""
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("📝 Создайте файл .env и добавьте в него BOT_TOKEN=ваш_токен_бота")
        return
    
    # Загружаем токен из .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        
        if not token or token == "your_bot_token_here":
            print("❌ Токен бота не найден в .env файле!")
            print("📝 Добавьте BOT_TOKEN=ваш_токен_бота в файл .env")
            return
    except ImportError:
        print("❌ python-dotenv не установлен!")
        print("📝 Установите: pip install python-dotenv")
        return
    except Exception as e:
        print(f"❌ Ошибка при загрузке .env: {e}")
        return
    
    if len(sys.argv) < 2:
        print("🔧 Утилиты для управления ботом:")
        print("   reset  - Сбросить webhook")
        print("   info   - Получить информацию о боте")
        print("\nПримеры:")
        print("   python reset_bot.py reset")
        print("   python reset_bot.py info")
        return
    
    command = sys.argv[1].lower()
    
    if command == "reset":
        print("🔄 Сброс webhook...")
        reset_webhook_from_api(token)
    elif command == "info":
        print("📊 Получение информации о боте...")
        get_bot_info_from_api(token)
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Доступные команды: reset, info")

if __name__ == "__main__":
    main() 