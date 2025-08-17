#!/usr/bin/env python3
"""
Тест для проверки удаления кнопок поиска ссылок
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_search_links_buttons_removed():
    """Проверяем, что кнопки поиска ссылок удалены везде кроме основного меню ссылок"""
    print("🧪 Проверяем удаление кнопок поиска ссылок...")
    
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Подсчитываем количество кнопок поиска ссылок
    search_links_button_count = content.count('text="🔍 Поиск ссылок"')
    search_new_button_count = content.count('text="🔍 Новый поиск"')
    
    print(f"Найдено {search_links_button_count} кнопок 'Поиск ссылок'")
    print(f"Найдено {search_new_button_count} кнопок 'Новый поиск'")
    
    # Должна остаться только одна кнопка поиска ссылок в основном меню
    assert search_links_button_count == 1, f"Ожидалась 1 кнопка 'Поиск ссылок', найдено {search_links_button_count}"
    
    # Проверяем кнопки "Новый поиск" более детально
    search_new_files_count = content.count('text="🔍 Новый поиск", callback_data="search_files"')
    search_new_links_count = content.count('text="🔍 Новый поиск", callback_data="search_links"')
    
    print(f"Найдено {search_new_files_count} кнопок 'Новый поиск' для файлов")
    print(f"Найдено {search_new_links_count} кнопок 'Новый поиск' для ссылок")
    
    # Кнопки "Новый поиск" для ссылок должны быть удалены
    assert search_new_links_count == 0, f"Кнопки 'Новый поиск' для ссылок должны быть удалены, найдено {search_new_links_count}"
    
    # Проверяем, что callback_data="search_links" остался только в двух местах:
    # 1. В кнопке основного меню
    # 2. В определении обработчика
    search_links_callback_count = content.count('callback_data="search_links"')
    
    print(f"Найдено {search_links_callback_count} использований callback_data='search_links'")
    
    assert search_links_callback_count == 1, f"Ожидалось 1 использование callback_data='search_links', найдено {search_links_callback_count}"
    
    # Проверяем, что обработчик остался
    handler_count = content.count('@router.callback_query(F.data == "search_links")')
    assert handler_count == 1, f"Обработчик search_links должен остаться, найдено {handler_count}"
    
    print("✅ Кнопки поиска ссылок корректно удалены!")

def test_main_links_menu_still_has_search():
    """Проверяем, что в основном меню ссылок кнопка поиска осталась"""
    print("🧪 Проверяем наличие поиска в основном меню ссылок...")
    
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем функцию show_link_categories
    show_link_categories_start = content.find('async def show_link_categories(')
    assert show_link_categories_start != -1, "Функция show_link_categories не найдена"
    
    # Найдем конец функции
    next_function_start = content.find('\n@router.callback_query', show_link_categories_start)
    if next_function_start == -1:
        next_function_start = show_link_categories_start + 1000
    
    function_section = content[show_link_categories_start:next_function_start]
    
    print(f"Участок функции show_link_categories: {len(function_section)} символов")
    
    # В этой функции должна быть кнопка поиска ссылок
    has_search_button = 'text="🔍 Поиск ссылок"' in function_section
    has_search_callback = 'callback_data="search_links"' in function_section
    
    print(f"Есть кнопка поиска: {has_search_button}")
    print(f"Есть callback поиска: {has_search_callback}")
    
    assert has_search_button, "В основном меню ссылок должна остаться кнопка поиска"
    assert has_search_callback, "В основном меню ссылок должен остаться callback поиска"
    
    print("✅ В основном меню ссылок кнопка поиска присутствует!")

def test_links_list_no_search():
    """Проверяем, что в списке ссылок нет кнопки поиска"""
    print("🧪 Проверяем отсутствие поиска в списке ссылок...")
    
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем функцию show_links_list
    show_links_list_start = content.find('async def show_links_list(')
    assert show_links_list_start != -1, "Функция show_links_list не найдена"
    
    # Берем участок функции (примерно 1000 символов)
    show_links_list_end = content.find('\n@router.callback_query', show_links_list_start)
    if show_links_list_end == -1:
        show_links_list_end = show_links_list_start + 1000
    
    function_section = content[show_links_list_start:show_links_list_end]
    
    # В этой функции НЕ должно быть кнопки поиска ссылок
    assert 'text="🔍 Поиск ссылок"' not in function_section, "В списке ссылок НЕ должно быть кнопки поиска"
    
    print("✅ В списке ссылок кнопка поиска отсутствует!")

def test_search_results_no_new_search():
    """Проверяем, что в результатах поиска нет кнопки 'Новый поиск'"""
    print("🧪 Проверяем отсутствие кнопки 'Новый поиск' в результатах поиска...")
    
    with open('/home/boss/cursor_project/bot_cloud/src/handlers/handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем функцию handle_link_search_query
    search_handler_start = content.find('async def handle_link_search_query(')
    assert search_handler_start != -1, "Функция handle_link_search_query не найдена"
    
    # Берем участок функции
    search_handler_end = content.find('\n@router.message()', search_handler_start)
    if search_handler_end == -1:
        search_handler_end = search_handler_start + 1000
    
    function_section = content[search_handler_start:search_handler_end]
    
    # В этой функции НЕ должно быть кнопки "Новый поиск"
    assert 'text="🔍 Новый поиск"' not in function_section, "В результатах поиска НЕ должно быть кнопки 'Новый поиск'"
    
    print("✅ В результатах поиска кнопка 'Новый поиск' отсутствует!")

def run_all_tests():
    """Запускаем все тесты"""
    print("🚀 Запускаем тесты удаления кнопок поиска ссылок...\n")
    
    try:
        test_search_links_buttons_removed()
        print()
        
        test_main_links_menu_still_has_search()
        print()
        
        test_links_list_no_search()
        print()
        
        test_search_results_no_new_search()
        print()
        
        print("🎉 Все тесты пройдены успешно!")
        print("\n📋 Результаты проверки:")
        print("✅ Кнопка 'Поиск ссылок' осталась только в основном меню ссылок")
        print("✅ Кнопка 'Поиск ссылок' удалена из списка ссылок")
        print("✅ Кнопка 'Новый поиск' удалена из результатов поиска")
        print("✅ Обработчик поиска ссылок сохранен")
        
        return True
        
    except Exception as e:
        print(f"❌ Тест провален: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
