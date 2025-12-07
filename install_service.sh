#!/bin/bash
# Скрипт для установки systemd сервиса для автозапуска бота

SERVICE_NAME="bot-cloud"
SERVICE_FILE="bot-cloud.service"
CURRENT_DIR=$(pwd)
SERVICE_PATH="$CURRENT_DIR/$SERVICE_FILE"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "🔧 Установка сервиса для автозапуска бота..."

# Проверяем наличие файла сервиса
if [ ! -f "$SERVICE_PATH" ]; then
    echo "❌ Ошибка: Файл $SERVICE_FILE не найден!"
    exit 1
fi

# Создаем директорию для user systemd сервисов
mkdir -p "$SYSTEMD_DIR"

# Копируем файл сервиса
cp "$SERVICE_PATH" "$SYSTEMD_DIR/$SERVICE_FILE"

# Обновляем пути в файле сервиса
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_DIR|g" "$SYSTEMD_DIR/$SERVICE_FILE"
sed -i "s|ExecStart=.*|ExecStart=$CURRENT_DIR/start_bot_screen.sh|g" "$SYSTEMD_DIR/$SERVICE_FILE"
sed -i "s|ExecStop=.*|ExecStop=$CURRENT_DIR/stop_bot_screen.sh|g" "$SYSTEMD_DIR/$SERVICE_FILE"

echo "✅ Файл сервиса скопирован в $SYSTEMD_DIR"

# Перезагружаем systemd
systemctl --user daemon-reload

# Включаем автозапуск
systemctl --user enable "$SERVICE_NAME.service"

echo "✅ Сервис установлен и включен для автозапуска"
echo ""
echo "📋 Полезные команды:"
echo "   Запустить сервис:    systemctl --user start $SERVICE_NAME"
echo "   Остановить сервис:   systemctl --user stop $SERVICE_NAME"
echo "   Статус сервиса:      systemctl --user status $SERVICE_NAME"
echo "   Логи сервиса:        journalctl --user -u $SERVICE_NAME -f"
echo "   Отключить автозапуск: systemctl --user disable $SERVICE_NAME"
echo ""
echo "⚠️  Важно: Для автозапуска после перезагрузки системы нужно включить linger:"
echo "   sudo loginctl enable-linger $USER"

