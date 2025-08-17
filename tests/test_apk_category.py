#!/usr/bin/env python3
"""
Тест для проверки новой категории APK файлов
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.utils import (
    get_file_category,
    get_category_icon,
    get_category_name,
    get_file_type_icon
)

def test_apk_category():
    """Тест: Проверяем категоризацию APK файлов"""
    print("🧪 Тестируем категоризацию APK файлов...")
    
    # Проверяем, что APK файлы попадают в правильную категорию
    apk_category = get_file_category('apk')
    assert apk_category == 'apk', f"APK файлы должны попадать в категорию 'apk', получили '{apk_category}'"
    
    # Проверяем APK в разных регистрах
    apk_upper_category = get_file_category('APK')
    assert apk_upper_category == 'apk', f"APK файлы в верхнем регистре должны попадать в категорию 'apk', получили '{apk_upper_category}'"
    
    print("✅ APK файлы корректно категоризируются!")

def test_apk_icon():
    """Тест: Проверяем иконку для категории APK"""
    print("🧪 Тестируем иконку категории APK...")
    
    # Проверяем иконку категории
    category_icon = get_category_icon('apk')
    assert category_icon == '📱', f"Иконка категории APK должна быть '📱', получили '{category_icon}'"
    
    # Проверяем иконку типа файла
    file_type_icon = get_file_type_icon('apk')
    assert file_type_icon == '📱', f"Иконка типа файла APK должна быть '📱', получили '{file_type_icon}'"
    
    print("✅ Иконки APK файлов корректны!")

def test_apk_name():
    """Тест: Проверяем название категории APK"""
    print("🧪 Тестируем название категории APK...")
    
    # Проверяем название категории на русском
    category_name = get_category_name('apk')
    expected_name = 'Android приложения'
    assert category_name == expected_name, f"Название категории APK должно быть '{expected_name}', получили '{category_name}'"
    
    print("✅ Название категории APK корректно!")

def test_other_categories_unchanged():
    """Тест: Проверяем, что другие категории не изменились"""
    print("🧪 Проверяем, что другие категории не изменились...")
    
    # Проверяем основные категории
    test_cases = [
        ('pdf', 'documents', '📄', 'Документы'),
        ('jpg', 'images', '🖼️', 'Изображения'),
        ('mp4', 'videos', '🎬', 'Видео'),
        ('mp3', 'audio', '🎵', 'Аудио'),
        ('zip', 'archives', '📦', 'Архивы'),
        ('txt', 'documents', '📄', 'Документы'),
    ]
    
    for file_type, expected_category, expected_icon, expected_name in test_cases:
        # Проверяем категорию
        category = get_file_category(file_type)
        assert category == expected_category, f"Файлы {file_type} должны быть в категории '{expected_category}', получили '{category}'"
        
        # Проверяем иконку категории
        icon = get_category_icon(category)
        assert icon == expected_icon, f"Иконка категории '{category}' должна быть '{expected_icon}', получили '{icon}'"
        
        # Проверяем название категории
        name = get_category_name(category)
        assert name == expected_name, f"Название категории '{category}' должно быть '{expected_name}', получили '{name}'"
    
    print("✅ Другие категории остались без изменений!")

def test_apk_vs_other_category():
    """Тест: Проверяем отличие APK от категории 'other'"""
    print("🧪 Проверяем отличие APK от категории 'other'...")
    
    # APK должен попадать в свою категорию, а не в 'other'
    apk_category = get_file_category('apk')
    assert apk_category != 'other', f"APK файлы НЕ должны попадать в категорию 'other'"
    
    # Проверяем, что неизвестные файлы все еще попадают в 'other'
    unknown_category = get_file_category('unknown_extension')
    assert unknown_category == 'other', f"Неизвестные файлы должны попадать в категорию 'other', получили '{unknown_category}'"
    
    # Проверяем, что иконка 'other' изменилась на папку
    other_icon = get_category_icon('other')
    assert other_icon == '📁', f"Иконка категории 'other' должна быть '📁', получили '{other_icon}'"
    
    print("✅ APK правильно отличается от категории 'other'!")

def test_mime_type_support():
    """Тест: Проверяем поддержку MIME типа для APK"""
    print("🧪 Проверяем поддержку MIME типа для APK...")
    
    # Проверяем, что MIME тип APK добавлен в маппинг
    from src.utils.utils import get_file_extension
    import inspect
    
    # Получаем исходный код функции для проверки
    source = inspect.getsource(get_file_extension)
    
    # Проверяем, что MIME тип для APK присутствует в коде
    apk_mime_present = 'application/vnd.android.package-archive' in source
    assert apk_mime_present, "MIME тип 'application/vnd.android.package-archive' должен быть в функции get_file_extension"
    
    # Проверяем, что он мапится на 'apk'
    apk_mapping_present = "'application/vnd.android.package-archive': 'apk'" in source
    assert apk_mapping_present, "MIME тип для APK должен мапиться на 'apk'"
    
    print("✅ MIME тип для APK поддерживается!")

def run_all_tests():
    """Запускаем все тесты"""
    print("🚀 Запускаем тесты новой категории APK...\n")
    
    try:
        test_apk_category()
        print()
        
        test_apk_icon()
        print()
        
        test_apk_name()
        print()
        
        test_other_categories_unchanged()
        print()
        
        test_apk_vs_other_category()
        print()
        
        test_mime_type_support()
        print()
        
        print("🎉 Все тесты пройдены успешно!")
        print("\n📋 Результаты проверки новой категории APK:")
        print("✅ APK файлы попадают в отдельную категорию 'apk'")
        print("✅ Иконка категории APK: 📱")
        print("✅ Название категории: 'Android приложения'")
        print("✅ Иконка типа файла APK: 📱")
        print("✅ MIME тип 'application/vnd.android.package-archive' поддерживается")
        print("✅ Другие категории остались без изменений")
        print("✅ Иконка категории 'other' изменена на 📁")
        
        return True
        
    except Exception as e:
        print(f"❌ Тест провален: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
