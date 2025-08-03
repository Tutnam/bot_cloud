#!/usr/bin/env python3
"""
Интеграционный тест для проверки загрузки фотографий
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from aiogram.types import Message, PhotoSize, User, Chat
from src.handlers.handlers import handle_photo, handle_file_upload
from src.database.database import Database
from src.config.config import Config

class TestIntegrationPhotoUpload:
    """Интеграционные тесты для загрузки фотографий"""
    
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
    async def test_photo_upload_flow(self, mock_message, mock_state):
        """Тест: полный процесс загрузки фотографии"""
        # Мокаем базу данных
        with patch('src.handlers.handlers.db') as mock_db:
            # Настраиваем мок базы данных
            mock_db.check_file_exists = AsyncMock(return_value=None)  # Файл не существует
            mock_db.add_file = AsyncMock(return_value=1)  # Успешное добавление
            
            # Запускаем обработчик фотографии
            await handle_photo(mock_message, mock_state)
            
            # Проверяем, что были вызваны правильные методы
            mock_state.update_data.assert_called()
            mock_state.set_state.assert_called()
            mock_message.answer.assert_called()
            
            # Проверяем, что был запрос к базе данных
            mock_db.check_file_exists.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_photo_already_exists(self, mock_message, mock_state):
        """Тест: попытка загрузить уже существующую фотографию"""
        # Мокаем базу данных
        with patch('src.handlers.handlers.db') as mock_db:
            # Настраиваем мок базы данных - файл уже существует
            mock_db.check_file_exists = AsyncMock(return_value=("existing_photo.jpg", 1024 * 1024))
            
            # Запускаем обработчик фотографии
            await handle_photo(mock_message, mock_state)
            
            # Проверяем, что было отправлено сообщение об ошибке
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args[0][0]
            assert "уже существует" in call_args
            
            # Проверяем, что не было попытки добавить файл
            mock_db.add_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_photo_too_large(self, mock_message, mock_state):
        """Тест: попытка загрузить слишком большую фотографию"""
        # Устанавливаем размер файла больше максимального
        photo = mock_message.photo[-1]
        photo.file_size = Config.MAX_FILE_SIZE + 1024 * 1024  # На 1MB больше лимита
        
        # Запускаем обработчик фотографии
        await handle_photo(mock_message, mock_state)
        
        # Проверяем, что было отправлено сообщение об ошибке
        mock_message.answer.assert_called()
        call_args = mock_message.answer.call_args[0][0]
        assert "слишком большой" in call_args
    
    @pytest.mark.asyncio
    async def test_photo_file_processing(self, mock_message, mock_state):
        """Тест: обработка информации о фотографии"""
        # Получаем фотографию из сообщения
        photo = mock_message.photo[-1]
        
        # Проверяем, что фотография имеет правильные атрибуты
        assert photo.file_id == "test_photo_file_id_123"
        assert photo.file_size == 1024 * 1024
        
        # Проверяем, что фотография имеет правильный тип
        from aiogram.types import PhotoSize
        assert isinstance(photo, PhotoSize)
    
    @pytest.mark.asyncio
    async def test_photo_description_flow(self, mock_message, mock_state):
        """Тест: процесс добавления описания к фотографии"""
        # Мокаем базу данных
        with patch('src.handlers.handlers.db') as mock_db:
            mock_db.check_file_exists = AsyncMock(return_value=None)
            
            # Запускаем обработчик фотографии
            await handle_photo(mock_message, mock_state)
            
            # Проверяем, что было запрошено описание
            mock_message.answer.assert_called()
            call_args = mock_message.answer.call_args[0][0]
            assert "описание" in call_args.lower()
            
            # Проверяем, что состояние было установлено
            mock_state.set_state.assert_called()

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 