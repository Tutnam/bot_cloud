# Реорганизация тестов

## Перемещение тестовых файлов

Все тестовые файлы были перемещены в папку `tests/` для лучшей организации проекта.

### Перемещенные файлы:

- `test_safe_share.py` → `tests/test_safe_share.py`
- `test_share_format.py` → `tests/test_share_format.py`
- `test_share_functionality.py` → `tests/test_share_functionality.py`
- `test_real_share.py` → `tests/test_real_share.py`
- `test_bot_info.py` → `tests/test_bot_info.py`
- `test_direct_share.py` → `tests/test_direct_share.py`
- `test_correct_url.py` → `tests/test_correct_url.py`
- `test_start_command.py` → `tests/test_start_command.py`
- `test_start_with_params.py` → `tests/test_start_with_params.py`
- `test_share_link.py` → `tests/test_share_link.py`

### Исправления импортов:

1. **Пути импорта** - обновлены для работы из папки `tests/`
2. **Импорты модулей** - убран префикс `src.` для корректной работы
3. **Структура проекта** - теперь соответствует стандартам Python

### Обновленные файлы:

#### src/handlers/handlers.py
- Исправлены импорты: `from src.config.config` → `from config.config`
- Исправлены импорты: `from src.database.database` → `from database.database`
- Исправлены импорты: `from src.utils.utils` → `from utils.utils`

#### tests/*.py
- Обновлены пути: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))`
- Исправлены импорты: `from src.handlers.handlers` → `from handlers.handlers`
- Исправлены импорты: `from src.config.config` → `from config.config`

### Запуск тестов:

```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск отдельных тестов
python tests/test_safe_share.py
python tests/test_share_format.py
python tests/test_bot_info.py
```

### Преимущества реорганизации:

1. **Лучшая структура** - тесты отделены от основного кода
2. **Стандарты Python** - соответствует PEP 8 и лучшим практикам
3. **Удобство разработки** - легко найти и запустить нужные тесты
4. **Чистота проекта** - корневая папка не засорена тестами

### Проверка работоспособности:

✅ Все тесты успешно перемещены и работают
✅ Импорты исправлены
✅ Структура проекта улучшена
✅ Соответствует стандартам Python 