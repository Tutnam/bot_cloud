#!/usr/bin/env python3
"""
Тест для проверки поддержки всех Android форматов файлов
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

def test_all_android_formats():
    """Тест всех Android форматов"""
    android_formats = {
        'apk': 'Android Package',
        'aab': 'Android App Bundle', 
        'xapk': 'Extended APK',
        'apks': 'APK Set',
        'apkm': 'APK Mirror Bundle',
        'obb': 'Android OBB Data'
    }
    
    print("🧪 Тестируем все Android форматы...")
    
    for format_ext, format_name in android_formats.items():
        category = get_file_category(format_ext)
        icon = get_file_type_icon(format_ext)
        
        print(f"  {icon} {format_ext.upper()} ({format_name}) → категория: {category}")
        
        assert category == 'apk', f"{format_ext} должен быть в категории 'apk', получили '{category}'"
        assert icon == '📱', f"{format_ext} должен иметь иконку 📱, получили '{icon}'"
    
    print("✅ Все Android форматы поддерживаются!")

def test_android_category_properties():
    """Тест свойств категории Android приложений"""
    print("\n🧪 Тестируем свойства категории Android...")
    
    # Проверяем иконку категории
    category_icon = get_category_icon('apk')
    assert category_icon == '📱', f"Иконка категории должна быть 📱, получили '{category_icon}'"
    print(f"  📱 Иконка категории: {category_icon} ✅")
    
    # Проверяем название категории
    category_name = get_category_name('apk')
    assert category_name == 'Android приложения', f"Название должно быть 'Android приложения', получили '{category_name}'"
    print(f"  📝 Название категории: {category_name} ✅")

def test_case_insensitive():
    """Тест нечувствительности к регистру"""
    print("\n🧪 Тестируем нечувствительность к регистру...")
    
    test_cases = [
        ('APK', 'apk'),
        ('aab', 'apk'), 
        ('XaPk', 'apk'),
        ('APKS', 'apk'),
        ('Obb', 'apk')
    ]
    
    for format_ext, expected_category in test_cases:
        category = get_file_category(format_ext)
        assert category == expected_category, f"{format_ext} должен быть в категории '{expected_category}', получили '{category}'"
        print(f"  📱 {format_ext} → {category} ✅")

def test_android_vs_other_categories():
    """Тест что Android форматы не смешиваются с другими"""
    print("\n🧪 Тестируем разделение Android и других форматов...")
    
    # Не Android форматы
    other_formats = {
        'pdf': 'documents',
        'jpg': 'images', 
        'mp4': 'videos',
        'mp3': 'audio',
        'zip': 'archives',
        'txt': 'documents'
    }
    
    for format_ext, expected_category in other_formats.items():
        category = get_file_category(format_ext)
        assert category == expected_category, f"{format_ext} должен быть в категории '{expected_category}', получили '{category}'"
        assert category != 'apk', f"{format_ext} НЕ должен быть в категории 'apk'"
        print(f"  📄 {format_ext} → {category} (НЕ Android) ✅")

def run_all_tests():
    """Запускаем все тесты Android форматов"""
    print("🚀 Запускаем полный тест Android форматов...\n")
    
    try:
        test_all_android_formats()
        test_android_category_properties()
        test_case_insensitive()
        test_android_vs_other_categories()
        
        print("\n🎉 Все тесты Android форматов пройдены успешно!")
        print("\n📋 Результаты проверки поддержки Android форматов:")
        print("✅ APK - Android Package")
        print("✅ AAB - Android App Bundle") 
        print("✅ XAPK - Extended APK")
        print("✅ APKS - APK Set")
        print("✅ APKM - APK Mirror Bundle")
        print("✅ OBB - Android OBB Data")
        print("✅ Все форматы используют иконку 📱")
        print("✅ Все форматы попадают в категорию 'Android приложения'")
        print("✅ Поддержка нечувствительности к регистру")
        print("✅ Корректное разделение с другими категориями")
        
        return True
        
    except Exception as e:
        print(f"❌ Тест провален: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n🎯 Все Android форматы готовы к работе в боте!")
    else:
        print("\n💥 Обнаружены проблемы, требуется исправление")
        sys.exit(1)
