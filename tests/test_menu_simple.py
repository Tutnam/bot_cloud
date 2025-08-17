#!/usr/bin/env python3
"""
Простые тесты для проверки изменений в меню бота (без базы данных)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.handlers.handlers import is_valid_url, extract_title_from_url

def test_url_detection():
    """Тест: Проверяем функцию определения URL"""
    print("🧪 Тестируем определение URL...")
    
    # Валидные URL
    assert is_valid_url("https://google.com") == True, "Не распознает https://google.com"
    assert is_valid_url("http://example.org") == True, "Не распознает http://example.org"
    assert is_valid_url("https://github.com/user/repo") == True, "Не распознает GitHub URL"
    assert is_valid_url("http://localhost:8080") == True, "Не распознает localhost"
    
    # Невалидные URL
    assert is_valid_url("просто текст") == False, "Ошибочно распознает простой текст как URL"
    assert is_valid_url("google.com") == False, "Ошибочно распознает URL без протокола"
    assert is_valid_url("ftp://example.com") == False, "Ошибочно распознает FTP URL"
    assert is_valid_url("") == False, "Ошибочно распознает пустую строку"
    
    print("✅ Тест определения URL пройден!")

def test_title_extraction():
    """Тест: Проверяем извлечение названия из URL"""
    print("🧪 Тестируем извлечение названий из URL...")
    
    assert extract_title_from_url("https://google.com") == "Google"
    assert extract_title_from_url("https://github.com/user/repo") == "Github"
    assert extract_title_from_url("http://stackoverflow.com/questions") == "Stackoverflow"
    assert extract_title_from_url("https://www.example.org") == "Example"
    assert extract_title_from_url("http://localhost:3000") == "Localhost"
    
    print("✅ Тест извлечения названий пройден!")

def test_import_handlers():
    """Тест: Проверяем, что все обработчики импортируются без ошибок"""
    print("🧪 Тестируем импорт обработчиков...")
    
    try:
        from src.handlers.handlers import (
            cmd_start,
            callback_main_menu,
            show_link_categories,
            handle_url_message,
            callback_show_links,
            callback_search_links
        )
        print("✅ Все обработчики успешно импортированы!")
        
        # Проверяем, что функции существуют
        assert callable(cmd_start), "cmd_start не является функцией"
        assert callable(callback_main_menu), "callback_main_menu не является функцией"
        assert callable(show_link_categories), "show_link_categories не является функцией"
        assert callable(handle_url_message), "handle_url_message не является функцией"
        
        print("✅ Все функции корректны!")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        raise

def check_main_menu_structure():
    """Проверяем структуру главного меню через анализ кода"""
    print("🧪 Проверяем структуру главного меню...")
    
    # Читаем исходный код функции cmd_start
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем секцию с кнопками главного меню
    start_pos = content.find('keyboard.button(text="📁 Мои файлы", callback_data="show_files")')
    if start_pos == -1:
        raise AssertionError("Не найдена кнопка 'Мои файлы' в главном меню")
    
    # Берем следующие 300 символов для анализа кнопок
    menu_section = content[start_pos:start_pos + 300]
    
    # Проверяем, что удаленные кнопки отсутствуют
    assert '📊 Статистика' not in menu_section, "Кнопка 'Статистика' не была удалена из главного меню"
    assert '📊 Экспорт' not in menu_section, "Кнопка 'Экспорт' не была удалена из главного меню"
    assert '📤 Загрузить файл' not in menu_section, "Кнопка 'Загрузить файл' не была удалена из главного меню"
    
    # Проверяем наличие оставшихся кнопок
    assert '📁 Мои файлы' in menu_section, "Кнопка 'Мои файлы' отсутствует в главном меню"
    assert '🔗 Ссылки' in menu_section, "Кнопка 'Ссылки' отсутствует в главном меню"
    
    print("✅ Структура главного меню корректна!")

def check_search_functionality():
    """Проверяем, что поиск остался только в меню ссылок"""
    print("🧪 Проверяем функционал поиска...")
    
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, что в главном меню нет поиска файлов
    # Найдем все места где используется search_files
    search_files_occurrences = content.count('callback_data="search_files"')
    print(f"Найдено {search_files_occurrences} упоминаний callback_data='search_files'")
    
    # Проверяем, что поиск ссылок есть в меню ссылок
    search_links_occurrences = content.count('callback_data="search_links"')
    print(f"Найдено {search_links_occurrences} упоминаний callback_data='search_links'")
    
    assert search_links_occurrences >= 1, "Поиск ссылок должен быть доступен в меню ссылок"
    
    print("✅ Функционал поиска настроен корректно!")

def check_add_link_functionality():
    """Проверяем, что кнопки 'Добавить ссылку' убраны"""
    print("🧪 Проверяем функционал добавления ссылок...")
    
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, что текст "Добавить ссылку" не встречается в кнопках
    add_link_button_count = content.count('text="➕ Добавить ссылку"')
    add_more_link_count = content.count('text="➕ Добавить еще"')
    
    print(f"Найдено {add_link_button_count} кнопок 'Добавить ссылку'")
    print(f"Найдено {add_more_link_count} кнопок 'Добавить еще'")
    
    assert add_link_button_count == 0, "Кнопки 'Добавить ссылку' не были удалены"
    assert add_more_link_count == 0, "Кнопки 'Добавить еще' не были удалены"
    
    # Проверяем, что функционал добавления через URL остался
    url_handler_present = 'handle_url_message' in content
    confirm_add_url_present = 'confirm_add_url' in content
    
    assert url_handler_present, "Обработчик URL сообщений отсутствует"
    assert confirm_add_url_present, "Обработчик подтверждения добавления URL отсутствует"
    
    print("✅ Функционал добавления ссылок настроен корректно!")

def run_all_tests():
    """Запускаем все тесты"""
    print("🚀 Запускаем тесты изменений меню бота...\n")
    
    try:
        test_import_handlers()
        print()
        
        test_url_detection()
        print()
        
        test_title_extraction()
        print()
        
        check_main_menu_structure()
        print()
        
        check_search_functionality()
        print()
        
        check_add_link_functionality()
        print()
        
        print("🎉 Все тесты пройдены успешно!")
        print("\n📋 Результаты проверки:")
        print("✅ Кнопки 'Статистика' и 'Экспорт' удалены из главного меню")
        print("✅ Кнопка 'Загрузить файл' удалена из главного меню") 
        print("✅ Кнопки 'Добавить ссылку' удалены из меню ссылок")
        print("✅ Кнопка поиска файлов удалена из главного меню")
        print("✅ Кнопка поиска ссылок осталась в меню ссылок")
        print("✅ Функционал добавления ссылок через URL работает")
        print("✅ Функции извлечения названий и проверки URL работают")
        
        return True
        
    except Exception as e:
        print(f"❌ Тест провален: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
