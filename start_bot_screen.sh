#!/bin/bash
# Скрипт для запуска бота в screen сессии

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SCREEN_SESSION="bot-cloud"
PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# Проверяем наличие screen
if ! command -v screen &> /dev/null; then
    echo "❌ Ошибка: screen не установлен!"
    exit 1
fi

# Проверяем наличие Python
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Ошибка: Python не найден в $PYTHON_BIN"
    exit 1
fi

# Проверяем наличие main.py
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "❌ Ошибка: main.py не найден!"
    exit 1
fi

# Проверяем, не запущен ли уже бот в этой сессии
if screen -list | grep -q "$SCREEN_SESSION"; then
    echo "⚠️  Сессия $SCREEN_SESSION уже существует"
    echo "   Используйте: screen -r $SCREEN_SESSION для подключения"
    exit 1
fi

# Запускаем бота в screen сессии
screen -dmS "$SCREEN_SESSION" "$PYTHON_BIN" "$MAIN_SCRIPT"

# Даем немного времени на запуск
sleep 1

# Проверяем, что сессия создана
if screen -list | grep -q "$SCREEN_SESSION"; then
    echo "✅ Бот запущен в screen сессии: $SCREEN_SESSION"
    echo "   Подключиться: screen -r $SCREEN_SESSION"
    exit 0
else
    echo "❌ Ошибка: Не удалось создать screen сессию" >&2
    exit 1
fi

