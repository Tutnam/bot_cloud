#!/bin/bash
# Скрипт для остановки бота из screen сессии

SCREEN_SESSION="bot-cloud"

# Проверяем наличие screen
if ! command -v screen &> /dev/null; then
    echo "❌ Ошибка: screen не установлен!"
    exit 1
fi

# Проверяем, существует ли сессия
if ! screen -list | grep -q "$SCREEN_SESSION"; then
    echo "⚠️  Сессия $SCREEN_SESSION не найдена"
    exit 1
fi

# Останавливаем сессию (отправляем Ctrl+C)
screen -S "$SCREEN_SESSION" -X stuff $'\003'

# Ждем немного
sleep 2

# Если сессия все еще существует, убиваем её
if screen -list | grep -q "$SCREEN_SESSION"; then
    screen -S "$SCREEN_SESSION" -X quit
    echo "✅ Сессия $SCREEN_SESSION остановлена"
else
    echo "✅ Бот остановлен"
fi

