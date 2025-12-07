# Автозапуск бота после перезагрузки

Бот запускается через утилиту `screen` в фоновом режиме.

## Быстрая установка

1. Запустите скрипт установки:
```bash
./install_service.sh
```

2. Включите linger для автозапуска после перезагрузки (требует sudo):
```bash
sudo loginctl enable-linger $USER
```

3. Запустите сервис:
```bash
systemctl --user start bot-cloud
```

## Ручной запуск через screen

Если хотите запустить бота вручную без systemd:

```bash
# Запуск
./start_bot_screen.sh

# Подключение к сессии
screen -r bot-cloud

# Отключение от сессии (остается работать в фоне)
# Нажмите: Ctrl+A, затем D

# Остановка
./stop_bot_screen.sh
```

## Управление сервисом

### Запуск/остановка
```bash
# Запустить
systemctl --user start bot-cloud

# Остановить
systemctl --user stop bot-cloud

# Перезапустить
systemctl --user restart bot-cloud
```

### Просмотр статуса
```bash
systemctl --user status bot-cloud
```

### Просмотр логов

Бот запущен в screen сессии, поэтому логи можно смотреть двумя способами:

**Через screen:**
```bash
# Подключиться к сессии и смотреть вывод
screen -r bot-cloud

# Список всех screen сессий
screen -ls
```

**Через systemd (если запущен через сервис):**
```bash
# Все логи
journalctl --user -u bot-cloud

# Последние 50 строк
journalctl --user -u bot-cloud -n 50

# Логи в реальном времени
journalctl --user -u bot-cloud -f
```

**Логи бота в файле:**
```bash
tail -f logs/bot.log
```

### Включение/отключение автозапуска
```bash
# Включить автозапуск
systemctl --user enable bot-cloud

# Отключить автозапуск
systemctl --user disable bot-cloud
```

### Работа со screen сессией

Бот запускается в screen сессии с именем `bot-cloud`. Вы можете подключиться к ней в любой момент:

```bash
# Подключиться к сессии
screen -r bot-cloud

# Отключиться от сессии (бот продолжит работать)
# Нажмите: Ctrl+A, затем D

# Список всех screen сессий
screen -ls

# Если сессия "attached", можно принудительно подключиться
screen -dr bot-cloud
```

**Важно:** Если бот упадет внутри screen сессии, вы увидите ошибку при подключении к сессии. Systemd не будет автоматически перезапускать бота при падении, так как он работает внутри screen. Для перезапуска используйте:
```bash
systemctl --user restart bot-cloud
```

## Удаление сервиса

```bash
systemctl --user stop bot-cloud
systemctl --user disable bot-cloud
rm ~/.config/systemd/user/bot-cloud.service
systemctl --user daemon-reload
```

