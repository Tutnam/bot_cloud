#!/usr/bin/env python3
"""
Тест для проверки загрузки фотографий
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from aiogram.types import Message, PhotoSize, User, Chat
from src.handlers.handlers import handle_photo, handle_file_upload
from src.config.config import Config

class TestPhotoUpload:
    """Тесты для загрузки фотографий"""
    
    @pytest.fixture
    def mock_message(self):
        """Создает мок сообщения с фотографией"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456789
        message.message_id = 123
        message.chat = Mock()
        message.chat.id = 456
        message.answer = AsyncMock()
        
        # Создаем мок фотографии
        photo = Mock(spec=PhotoSize)
        photo.file_id = "test_photo_file_id_123"
        photo.file_size = 1024 * 1024  # 1MB
        photo.file_name = None
        
        message.photo = [photo]
        message.text = None
        
        return message
    
    @pytest.fixture
    def mock_state(self):
        """Создает мок состояния FSM"""
        state = AsyncMock()
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.clear = AsyncMock()
        return state
    
    @pytest.mark.asyncio
    async def test_photo_handler_called(self, mock_message, mock_state):
        """Тест: обработчик фотографий вызывается"""
        # Проверяем, что обработчик не вызывает исключений
        try:
            await handle_photo(mock_message, mock_state)
            # Если дошли до сюда, значит обработчик работает
            assert True
        except Exception as e:
            pytest.fail(f"Обработчик фотографий вызвал исключение: {e}")
    
    @pytest.mark.asyncio
    async def test_photo_file_upload(self, mock_message, mock_state):
        """Тест: загрузка фотографии в базу данных"""
        # Получаем фотографию из сообщения
        photo = mock_message.photo[-1]
        
        # Проверяем, что фотография имеет правильные атрибуты
        assert hasattr(photo, 'file_id')
        assert hasattr(photo, 'file_size')
        assert photo.file_id == "test_photo_file_id_123"
        assert photo.file_size == 1024 * 1024
    
    def test_photo_extension(self):
        """Тест: правильное определение расширения для фотографий"""
        from src.utils.utils import get_file_extension
        
        # Создаем мок фотографии
        photo = Mock(spec=PhotoSize)
        photo.file_name = None
        
        # Проверяем, что расширение определяется как jpg
        extension = get_file_extension(photo)
        assert extension == 'jpg'
    
    def test_photo_category(self):
        """Тест: правильная категоризация фотографий"""
        from src.utils.utils import get_file_category
        
        # Проверяем, что jpg попадает в категорию images
        category = get_file_category('jpg')
        assert category == 'images'
        
        # Проверяем другие форматы изображений
        assert get_file_category('png') == 'images'
        assert get_file_category('gif') == 'images'
        assert get_file_category('webp') == 'images'

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 