#!/usr/bin/env python3
"""
Тесты для проверки изменений в меню бота
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

# Добавляем src в путь для импортов
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.handlers.handlers import (
    cmd_start,
    callback_main_menu,
    show_link_categories,
    show_files_list,
    handle_url_message,
    is_valid_url,
    extract_title_from_url
)

class TestMenuChanges:
    """Тесты изменений в меню"""
    
    @pytest.fixture
    def mock_message(self):
        """Создаем мок сообщения"""
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 123456789
        message.chat.id = 123456789
        message.text = "/start"
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_callback(self):
        """Создаем мок callback query"""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = MagicMock(spec=User)
        callback.from_user.id = 123456789
        callback.message = MagicMock(spec=Message)
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        callback.data = "main_menu"
        return callback
    
    @pytest.fixture
    def mock_state(self):
        """Создаем мок состояния"""
        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value=None)
        state.update_data = AsyncMock()
        state.clear = AsyncMock()
        return state

    def test_main_menu_buttons_removed(self, mock_message):
        """Тест 1: Проверяем, что кнопки 'статистика' и 'экспорт' убраны из главного меню"""
        # Проверяем вызов cmd_start
        async def check_main_menu():
            await cmd_start(mock_message)
            
            # Проверяем, что answer был вызван
            assert mock_message.answer.called
            
            # Получаем аргументы вызова
            call_args = mock_message.answer.call_args
            reply_markup = call_args[1]['reply_markup']
            
            # Проверяем, что кнопки статистика и экспорт отсутствуют
            buttons_text = []
            for row in reply_markup.inline_keyboard:
                for button in row:
                    buttons_text.append(button.text)
            
            assert "📊 Статистика" not in buttons_text
            assert "📊 Экспорт" not in buttons_text
            assert "📤 Загрузить файл" not in buttons_text
            
            # Проверяем, что основные кнопки остались
            assert "📁 Мои файлы" in buttons_text
            assert "🔗 Ссылки" in buttons_text
        
        # Запускаем тест
        asyncio.run(check_main_menu())

    def test_search_button_in_main_menu_removed(self, mock_message):
        """Тест 2: Проверяем, что кнопка поиска убрана из главного меню"""
        async def check_search_removed():
            await cmd_start(mock_message)
            
            call_args = mock_message.answer.call_args
            reply_markup = call_args[1]['reply_markup']
            
            buttons_text = []
            for row in reply_markup.inline_keyboard:
                for button in row:
                    buttons_text.append(button.text)
            
            # Проверяем, что кнопка поиска файлов отсутствует в главном меню
            assert "🔍 Поиск" not in buttons_text
        
        asyncio.run(check_search_removed())

    def test_url_detection(self):
        """Тест 3: Проверяем функцию определения URL"""
        # Валидные URL
        assert is_valid_url("https://google.com") == True
        assert is_valid_url("http://example.org") == True
        assert is_valid_url("https://github.com/user/repo") == True
        assert is_valid_url("http://localhost:8080") == True
        
        # Невалидные URL
        assert is_valid_url("просто текст") == False
        assert is_valid_url("google.com") == False  # нет протокола
        assert is_valid_url("ftp://example.com") == False  # не http/https
        assert is_valid_url("") == False

    def test_title_extraction(self):
        """Тест 4: Проверяем извлечение названия из URL"""
        assert extract_title_from_url("https://google.com") == "Google"
        assert extract_title_from_url("https://github.com/user/repo") == "Github"
        assert extract_title_from_url("http://stackoverflow.com/questions") == "Stackoverflow"
        assert extract_title_from_url("https://www.example.org") == "Example"
        assert extract_title_from_url("http://localhost:3000") == "Localhost"

    def test_url_message_handling(self, mock_message, mock_state):
        """Тест 5: Проверяем обработку URL сообщений"""
        async def check_url_handling():
            mock_message.text = "https://example.com"
            
            await handle_url_message(mock_message, mock_state)
            
            # Проверяем, что answer был вызван с предложением добавить ссылку
            assert mock_message.answer.called
            call_args = mock_message.answer.call_args
            text = call_args[0][0]
            
            assert "🔗 **Обнаружена ссылка!**" in text
            assert "https://example.com" in text
            assert "Example" in text  # проверяем извлеченное название
            
            # Проверяем наличие кнопок подтверждения
            reply_markup = call_args[1]['reply_markup']
            buttons_text = []
            for row in reply_markup.inline_keyboard:
                for button in row:
                    buttons_text.append(button.text)
            
            assert "✅ Да, добавить" in buttons_text
            assert "❌ Нет, отменить" in buttons_text
        
        asyncio.run(check_url_handling())

def test_files_list_has_back_button():
    """Тест 6: Проверяем наличие кнопки 'назад' в списке файлов"""
    # Создаем мок данных для файлов
    mock_files = [
        (1, "file1", "test.txt", 1024, "txt", "document", 123456789, "2023-01-01T10:00:00", "desc", "tags", 1, 123456789)
    ]
    
    async def check_back_button():
        mock_message = MagicMock(spec=Message)
        mock_message.answer = AsyncMock()
        
        await show_files_list(mock_message, mock_files, "Тест файлы")
        
        # Проверяем наличие кнопки "Назад к категориям"
        call_args = mock_message.answer.call_args
        reply_markup = call_args[1]['reply_markup']
        
        buttons_text = []
        for row in reply_markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert "🔙 Назад к категориям" in buttons_text
        assert "🏠 Главное меню" in buttons_text
        # Проверяем, что кнопка поиска убрана из списка файлов
        assert "🔍 Поиск" not in buttons_text
    
    asyncio.run(check_back_button())

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
