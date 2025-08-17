#!/usr/bin/env python3
"""
Интеграционный тест для проверки работы категории APK в боте
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock
from src.utils.utils import get_file_category, get_category_icon, get_category_name, get_file_extension

def test_apk_file_processing():
    """Тест: Проверяем полную обработку APK файла как в боте"""
    print("🧪 Тестируем полную обработку APK файла...")
    
    # Имитируем APK файл с правильным расширением
    mock_document = MagicMock()
    mock_document.file_name = "my_app.apk"
    mock_document.mime_type = "application/vnd.android.package-archive"
    
    # Шаг 1: Получаем расширение файла
    file_extension = get_file_extension(mock_document)
    print(f"Расширение файла: {file_extension}")
    assert file_extension == 'apk', f"Расширение должно быть 'apk', получили '{file_extension}'"
    
    # Шаг 2: Определяем категорию
    category = get_file_category(file_extension)
    print(f"Категория файла: {category}")
    assert category == 'apk', f"Категория должна быть 'apk', получили '{category}'"
    
    # Шаг 3: Получаем иконку категории
    category_icon = get_category_icon(category)
    print(f"Иконка категории: {category_icon}")
    assert category_icon == '📱', f"Иконка должна быть '📱', получили '{category_icon}'"
    
    # Шаг 4: Получаем название категории
    category_name = get_category_name(category)
    print(f"Название категории: {category_name}")
    assert category_name == 'Android приложения', f"Название должно быть 'Android приложения', получили '{category_name}'"
    
    print("✅ APK файл корректно обрабатывается на всех этапах!")

def test_different_apk_files():
    """Тест: Проверяем обработку разных APK файлов"""
    print("🧪 Тестируем обработку разных APK файлов...")
    
    apk_files = [
        "telegram.apk",
        "WhatsApp.APK",  # верхний регистр
        "my-game-v2.3.apk",
        "com.example.app.apk"
    ]
    
    for apk_file in apk_files:
        mock_document = MagicMock()
        mock_document.file_name = apk_file
        
        # Получаем расширение
        extension = get_file_extension(mock_document)
        print(f"Файл: {apk_file} -> расширение: {extension}")
        
        # Проверяем категорию
        category = get_file_category(extension)
        assert category == 'apk', f"Файл {apk_file} должен быть в категории 'apk', получили '{category}'"
    
    print("✅ Все варианты APK файлов обрабатываются корректно!")

def test_apk_vs_other_files():
    """Тест: Проверяем, что APK не путается с другими файлами"""
    print("🧪 Проверяем отличие APK от других файлов...")
    
    test_files = [
        ("document.pdf", "documents"),
        ("image.jpg", "images"),
        ("video.mp4", "videos"),
        ("music.mp3", "audio"),
        ("archive.zip", "archives"),
        ("my_app.apk", "apk"),  # наш APK
        ("unknown.xyz", "other")
    ]
    
    for filename, expected_category in test_files:
        mock_document = MagicMock()
        mock_document.file_name = filename
        
        extension = get_file_extension(mock_document)
        category = get_file_category(extension)
        
        print(f"Файл: {filename} -> категория: {category}")
        assert category == expected_category, f"Файл {filename} должен быть в категории '{expected_category}', получили '{category}'"
    
    print("✅ APK корректно отличается от других типов файлов!")

def test_apk_display_info():
    """Тест: Проверяем отображение информации о APK файлах"""
    print("🧪 Проверяем отображение информации о APK файлах...")
    
    # Имитируем данные как они будут в боте
    apk_category_info = {
        'category': 'apk',
        'icon': get_category_icon('apk'),
        'name': get_category_name('apk'),
        'count': 5,
        'total_size': 150 * 1024 * 1024  # 150 MB
    }
    
    print(f"Информация о категории APK:")
    print(f"  Иконка: {apk_category_info['icon']}")
    print(f"  Название: {apk_category_info['name']}")
    print(f"  Количество файлов: {apk_category_info['count']}")
    print(f"  Общий размер: {apk_category_info['total_size'] / (1024*1024):.1f} MB")
    
    # Проверяем правильность отображения
    assert apk_category_info['icon'] == '📱'
    assert apk_category_info['name'] == 'Android приложения'
    
    # Имитируем отображение в меню как в боте
    menu_text = f"{apk_category_info['icon']} **{apk_category_info['name']}** - {apk_category_info['count']} файлов ({apk_category_info['total_size'] / (1024*1024):.1f} MB)"
    expected_text = "📱 **Android приложения** - 5 файлов (150.0 MB)"
    
    assert menu_text == expected_text, f"Отображение в меню должно быть '{expected_text}', получили '{menu_text}'"
    
    print("✅ Информация о APK файлах отображается корректно!")

def run_all_tests():
    """Запускаем все интеграционные тесты"""
    print("🚀 Запускаем интеграционные тесты категории APK...\n")
    
    try:
        test_apk_file_processing()
        print()
        
        test_different_apk_files()
        print()
        
        test_apk_vs_other_files()
        print()
        
        test_apk_display_info()
        print()
        
        print("🎉 Все интеграционные тесты пройдены успешно!")
        print("\n📋 Интеграционная проверка завершена:")
        print("✅ APK файлы корректно обрабатываются на всех этапах")
        print("✅ Различные форматы имен APK файлов поддерживаются")
        print("✅ APK файлы не путаются с другими типами файлов")
        print("✅ Информация о APK файлах корректно отображается в интерфейсе")
        print("\n🎯 Категория APK готова к использованию в боте!")
        
        return True
        
    except Exception as e:
        print(f"❌ Интеграционный тест провален: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
