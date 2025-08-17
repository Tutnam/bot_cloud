import os
import hashlib
from pathlib import Path
from typing import Union
from aiogram.types import Document, PhotoSize, Video, Audio, Voice

def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def get_file_extension(file_obj: Union[Document, PhotoSize, Video, Audio, Voice]) -> str:
    """Получает расширение файла из объекта Telegram"""
    # Если есть оригинальное имя файла, используем его
    if hasattr(file_obj, 'file_name') and file_obj.file_name:
        return Path(file_obj.file_name).suffix.lower().lstrip('.')
    
    # Для фото используем jpg
    if isinstance(file_obj, PhotoSize):
        return 'jpg'
    
    # Для видео используем mp4
    if hasattr(file_obj, 'mime_type') and file_obj.mime_type and 'video' in file_obj.mime_type:
        return 'mp4'
    
    # Для аудио используем mp3
    if hasattr(file_obj, 'mime_type') and file_obj.mime_type and 'audio' in file_obj.mime_type:
        return 'mp3'
    
    # Для голосовых сообщений используем ogg
    if hasattr(file_obj, 'duration'):  # Voice имеет duration
        return 'ogg'
    
    # Для документов пытаемся определить по MIME типу
    mime_type = getattr(file_obj, 'mime_type', '')
    mime_to_ext = {
        'application/pdf': 'pdf',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/plain': 'txt',
        'application/zip': 'zip',
        'application/x-rar-compressed': 'rar',
        'application/vnd.android.package-archive': 'apk',
        'application/x-aab': 'aab',
        'application/x-xapk': 'xapk',
        'application/octet-stream': 'obb',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'video/mp4': 'mp4',
        'video/avi': 'avi',
        'video/mov': 'mov',
        'audio/mpeg': 'mp3',
        'audio/wav': 'wav',
        'audio/ogg': 'ogg'
    }
    
    if mime_type in mime_to_ext:
        return mime_to_ext[mime_type]
    
    # Если не удалось определить, используем оригинальное имя или тип объекта
    if hasattr(file_obj, 'file_name') and file_obj.file_name:
        return Path(file_obj.file_name).suffix.lower().lstrip('.')
    
    # Для документов без расширения используем 'doc'
    if hasattr(file_obj, 'file_name'):
        return 'doc'
    
    # Последний вариант - определяем по типу объекта
    if isinstance(file_obj, Document):
        return 'doc'
    elif isinstance(file_obj, PhotoSize):
        return 'jpg'
    elif isinstance(file_obj, Video):
        return 'mp4'
    elif isinstance(file_obj, Audio):
        return 'mp3'
    elif isinstance(file_obj, Voice):
        return 'ogg'
    
    # Если ничего не подошло, возвращаем пустую строку
    return ''

def generate_file_hash(file_path: str) -> str:
    """Генерирует MD5 хеш файла"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_valid_filename(filename: str) -> bool:
    """Проверяет, является ли имя файла допустимым"""
    # Запрещенные символы в именах файлов
    invalid_chars = '<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)

def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов"""
    # Заменяем недопустимые символы на подчеркивание
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Убираем множественные подчеркивания
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    # Убираем подчеркивания в начале и конце
    filename = filename.strip('_')
    
    return filename

def get_file_category(file_type: str) -> str:
    """Возвращает категорию файла"""
    file_type = file_type.lower()
    
    # Документы
    if file_type in ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']:
        return "documents"
    
    # Изображения
    elif file_type in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']:
        return "images"
    
    # Видео
    elif file_type in ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm']:
        return "videos"
    
    # Аудио
    elif file_type in ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']:
        return "audio"
    
    # Архивы
    elif file_type in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
        return "archives"
    
    # Android приложения
    elif file_type in ['apk', 'aab', 'xapk', 'apks', 'apkm', 'obb']:
        return "apk"
    
    # Другое
    else:
        return "other"

def get_category_icon(category: str) -> str:
    """Возвращает эмодзи для категории"""
    icons = {
        'documents': '📄',
        'images': '🖼️',
        'videos': '🎬',
        'audio': '🎵',
        'archives': '📦',
        'apk': '📱',
        'other': '📁'
    }
    return icons.get(category, '📱')

def get_category_name(category: str) -> str:
    """Возвращает название категории на русском"""
    names = {
        'documents': 'Документы',
        'images': 'Изображения',
        'videos': 'Видео',
        'audio': 'Аудио',
        'archives': 'Архивы',
        'apk': 'Android приложения',
        'other': 'Другое'
    }
    return names.get(category, 'Другое')

def get_file_type_icon(file_type: str) -> str:
    """Возвращает эмодзи для типа файла"""
    icons = {
        'pdf': '📄',
        'doc': '📝',
        'docx': '📝',
        'txt': '📄',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'gif': '🖼️',
        'mp3': '🎵',
        'mp4': '🎬',
        'zip': '📦',
        'rar': '📦',
        'apk': '📱',
        'aab': '📱',
        'xapk': '📱',
        'apks': '📱',
        'apkm': '📱',
        'obb': '📱',
        'bin': '📄'
    }
    return icons.get(file_type.lower(), '📄')

def format_date(date_str: str) -> str:
    """Форматирует дату в читаемый вид"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return date_str

def get_link_category_icon(category: str) -> str:
    """Возвращает эмодзи для категории ссылок"""
    icons = {
        'general': '🔗',
        'web': '🌐',
        'education': '📚',
        'work': '💼',
        'entertainment': '🎵',
        'shopping': '🛒',
        'social': '👥',
        'news': '📰',
        'tools': '🛠️',
        'games': '🎮'
    }
    return icons.get(category, '🔗')

def get_link_category_name(category: str) -> str:
    """Возвращает название категории ссылок на русском"""
    names = {
        'general': 'Общие',
        'web': 'Веб-сайты',
        'education': 'Образование',
        'work': 'Работа',
        'entertainment': 'Развлечения',
        'shopping': 'Покупки',
        'social': 'Социальные сети',
        'news': 'Новости',
        'tools': 'Инструменты',
        'games': 'Игры'
    }
    return names.get(category, 'Общие') 