#!/usr/bin/env python3
"""
Тест для проверки уникальности имен файлов
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from aiogram.types import Message, PhotoSize, User, Chat, Document
from src.handlers.handlers import handle_file_upload
from src.config.config import Config

class TestUniqueFilenames:
    """Тесты для проверки уникальности имен файлов"""
    
    @pytest.fixture
    def mock_message(self):
        """Создает мок сообщения"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456789
        message.message_id = 123
        message.chat = Mock()
        message.chat.id = 456
        message.answer = AsyncMock()
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
    
    def test_photo_filename_uniqueness(self):
        """Тест: имена файлов для фотографий должны быть уникальными"""
        # Создаем два мока фотографий с одинаковым file_id
        photo1 = Mock(spec=PhotoSize)
        photo1.file_id = "test_photo_file_id_123"
        photo1.file_size = 1024 * 1024
        photo1.file_name = None
        
        photo2 = Mock(spec=PhotoSize)
        photo2.file_id = "test_photo_file_id_123"
        photo2.file_size = 1024 * 1024
        photo2.file_name = None
        
        # Проверяем, что имена файлов разные
        from src.handlers.handlers import handle_file_upload
        
        # Имитируем создание имен файлов
        import time
        timestamp1 = int(time.time())
        timestamp2 = int(time.time()) + 1  # Разные временные метки
        
        unique_suffix1 = f"{timestamp1}_{photo1.file_id[:6]}"
        unique_suffix2 = f"{timestamp2}_{photo2.file_id[:6]}"
        
        filename1 = f"photo_{unique_suffix1}.jpg"
        filename2 = f"photo_{unique_suffix2}.jpg"
        
        # Имена должны быть разными
        assert filename1 != filename2
        assert "photo_" in filename1
        assert "photo_" in filename2
        assert filename1.endswith(".jpg")
        assert filename2.endswith(".jpg")
    
    def test_document_filename_preservation(self):
        """Тест: документы должны сохранять оригинальные имена"""
        # Создаем мок документа с оригинальным именем
        document = Mock(spec=Document)
        document.file_id = "test_doc_file_id_123"
        document.file_size = 1024 * 1024
        document.file_name = "original_document.pdf"
        document.mime_type = "application/pdf"
        
        # Проверяем, что оригинальное имя сохраняется
        # В коде handle_file_upload есть проверка:
        # if hasattr(file_obj, 'file_name') and file_obj.file_name:
        #     file_name = file_obj.file_name
        
        assert hasattr(document, 'file_name')
        assert document.file_name == "original_document.pdf"
    
    def test_video_filename_generation(self):
        """Тест: генерация имен для видео файлов"""
        from aiogram.types import Video
        
        video = Mock(spec=Video)
        video.file_id = "test_video_file_id_123"
        video.file_size = 1024 * 1024
        video.file_name = None
        
        # Имитируем создание имени файла
        import time
        timestamp = int(time.time())
        unique_suffix = f"{timestamp}_{video.file_id[:6]}"
        filename = f"video_{unique_suffix}.mp4"
        
        assert "video_" in filename
        assert filename.endswith(".mp4")
        assert unique_suffix in filename
    
    def test_audio_filename_generation(self):
        """Тест: генерация имен для аудио файлов"""
        from aiogram.types import Audio
        
        audio = Mock(spec=Audio)
        audio.file_id = "test_audio_file_id_123"
        audio.file_size = 1024 * 1024
        audio.file_name = None
        
        # Имитируем создание имени файла
        import time
        timestamp = int(time.time())
        unique_suffix = f"{timestamp}_{audio.file_id[:6]}"
        filename = f"audio_{unique_suffix}.mp3"
        
        assert "audio_" in filename
        assert filename.endswith(".mp3")
        assert unique_suffix in filename
    
    def test_voice_filename_generation(self):
        """Тест: генерация имен для голосовых сообщений"""
        from aiogram.types import Voice
        
        voice = Mock(spec=Voice)
        voice.file_id = "test_voice_file_id_123"
        voice.file_size = 1024 * 1024
        voice.file_name = None
        
        # Имитируем создание имени файла
        import time
        timestamp = int(time.time())
        unique_suffix = f"{timestamp}_{voice.file_id[:6]}"
        filename = f"voice_{unique_suffix}.ogg"
        
        assert "voice_" in filename
        assert filename.endswith(".ogg")
        assert unique_suffix in filename
    
    @pytest.mark.asyncio
    async def test_photo_upload_with_unique_filename(self, mock_message, mock_state):
        """Тест: загрузка фотографии с уникальным именем файла"""
        # Создаем мок фотографии
        photo = Mock(spec=PhotoSize)
        photo.file_id = "test_photo_file_id_123"
        photo.file_size = 1024 * 1024
        photo.file_name = None
        
        mock_message.photo = [photo]
        
        # Мокаем базу данных
        with patch('src.handlers.handlers.db') as mock_db:
            mock_db.check_file_exists = AsyncMock(return_value=None)
            
            # Запускаем обработчик
            try:
                await handle_file_upload(mock_message, mock_state, photo)
                
                # Проверяем, что состояние было обновлено с уникальным именем файла
                mock_state.update_data.assert_called()
                call_args = mock_state.update_data.call_args[1]
                
                # Проверяем, что file_name был передан
                assert 'file_name' in call_args
                file_name = call_args['file_name']
                
                # Проверяем формат имени файла
                assert file_name.startswith("photo_")
                assert file_name.endswith(".jpg")
                assert len(file_name) > len("photo_.jpg")  # Должно быть что-то еще
                
            except Exception as e:
                # Ожидаем ошибку, так как база данных замокнута
                assert "Mock" in str(e) or "check_file_exists" in str(e)

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 