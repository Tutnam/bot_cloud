import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, Document, PhotoSize, Video, Audio, Voice, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
import aiofiles
import os
from datetime import datetime
import io
import csv

from config.config import Config
from database.database import Database
from utils.utils import format_file_size, get_file_extension, get_file_category, get_category_icon, get_category_name

logger = logging.getLogger(__name__)
router = Router()
db = Database()

class FileUploadStates(StatesGroup):
    waiting_for_description = State()
    waiting_for_tags = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    
    logger.info(f"Получена команда start: {message.text}")
    logger.info(f"От пользователя: {message.from_user.id}")
    
    # Проверяем, есть ли параметры в команде start
    if message.text and len(message.text.split()) > 1:
        start_param = message.text.split()[1]
        logger.info(f"Получен параметр start: {start_param}")
        
        # Если параметр начинается с "file_", это ссылка на файл
        if start_param.startswith("file_"):
            share_id = start_param.replace("file_", "")
            logger.info(f"Обрабатываем ссылку на файл с share_id: {share_id}")
            await handle_shared_file_download(message, share_id)
            return
        else:
            logger.info(f"Параметр start не является ссылкой на файл: {start_param}")
    else:
        logger.info("Команда start без параметров")
    
    welcome_text = """
🤖 **Добро пожаловать в FileStorage Bot!**

Этот бот поможет вам хранить и управлять вашими файлами.

📁 **Основные команды:**
• /upload - Загрузить файл
• /files - Показать ваши файлы
• /search - Поиск файлов
• /delete - Удаление файлов
• /export - Экспорт файлов
• /stats - Статистика
• /help - Помощь

💡 **Просто отправьте файл, и я сохраню его для вас!**
🗑️ **Удаление:** Используйте кнопку "🗑️ Удалить" рядом с файлом
📊 **Экспорт:** Создайте CSV со списком файлов
🔗 **Поделиться:** Используйте кнопку "🔗 Поделиться" для создания ссылки
    """
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📁 Мои файлы", callback_data="show_files")
    keyboard.button(text="📤 Загрузить файл", callback_data="upload_file")
    keyboard.button(text="🔍 Поиск", callback_data="search_files")
    keyboard.button(text="📊 Статистика", callback_data="show_stats")
    keyboard.adjust(2)
    
    await message.answer(welcome_text, reply_markup=keyboard.as_markup())

@router.message()
async def handle_all_messages(message: Message):
    """Обработчик всех сообщений для отладки"""
    logger.info(f"Получено сообщение: {message.text}")
    logger.info(f"Тип сообщения: {type(message)}")
    logger.info(f"От пользователя: {message.from_user.id}")
    
    # Если это команда start с параметрами, обрабатываем её
    if message.text and message.text.startswith("/start "):
        start_param = message.text.split()[1]
        logger.info(f"Обрабатываем start с параметром: {start_param}")
        
        if start_param.startswith("file_"):
            share_id = start_param.replace("file_", "")
            logger.info(f"Обрабатываем ссылку на файл с share_id: {share_id}")
            await handle_shared_file_download(message, share_id)
            return

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
📚 **Справка по использованию бота:**

**Загрузка файлов:**
• Просто отправьте файл в чат
• Или используйте команду /upload

**Управление файлами:**
• /files - Показать все ваши файлы
• /search <запрос> - Поиск файлов
• /delete - Информация об удалении файлов
• /export - Экспорт файлов в CSV
• /stats - Статистика использования

**Удаление файлов:**
• Используйте кнопку "🗑️ Удалить" рядом с файлом
• Подтверждение удаления для безопасности
• Удаленные файлы нельзя восстановить

**Экспорт файлов:**
• /export - Создать CSV файл со списком файлов
• Включает название, размер, тип, дату загрузки
• Описания и теги файлов

**Ограничения:**
• Максимальный размер файла: {max_size}MB

**Дополнительные возможности:**
• Добавление описаний к файлам
• Теги для организации
• Поиск по названию и описанию
• Поддержка любых типов файлов
• Создание ссылок для скачивания файлов
    """.format(
        max_size=Config.MAX_FILE_SIZE // (1024 * 1024)
    )
    
    await message.answer(help_text)

@router.message(Command("files"))
async def cmd_files(message: Message):
    """Показать файлы пользователя"""
    await show_user_files(message, message.from_user.id)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Показать статистику пользователя"""
    stats = await db.get_file_stats(message.from_user.id)
    
    total_size_mb = stats['total_size'] / (1024 * 1024)
    
    stats_text = f"""
📊 **Ваша статистика:**

📁 Всего файлов: {stats['total_files']}
💾 Общий размер: {total_size_mb:.2f} MB
📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    await message.answer(stats_text)

@router.message(Command("search"))
async def cmd_search(message: Message):
    """Поиск файлов"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("🔍 **Использование:** /search <запрос>\n\nПример: /search документ")
        return
    
    query = " ".join(args[1:])
    files = await db.search_files(message.from_user.id, query)
    
    if not files:
        await message.answer(f"🔍 По запросу '{query}' ничего не найдено.")
        return
    
    await show_files_list(message, files, f"🔍 Результаты поиска: '{query}'")

@router.message(Command("delete"))
async def cmd_delete(message: Message):
    """Удаление файлов"""
    await message.answer("🗑️ **Удаление файлов**\n\nИспользуйте кнопку '🗑️ Удалить' рядом с файлом в списке ваших файлов.\n\nКоманда: /files")

@router.message(Command("export"))
async def cmd_export(message: Message):
    """Экспорт файлов"""
    user_id = message.from_user.id
    files = await db.get_user_files(user_id)
    
    if not files:
        await message.answer("📁 У вас нет файлов для экспорта.\n\nЗагрузите файлы, чтобы создать экспорт!")
        return
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📊 Создать экспорт", callback_data="export_files")
    keyboard.button(text="📁 Мои файлы", callback_data="show_files")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    await message.answer(
        f"📊 **Экспорт файлов**\n\n📁 Всего файлов: {len(files)}\n\nСоздастся CSV файл со списком всех ваших файлов.",
        reply_markup=keyboard.as_markup()
    )

@router.message(F.document)
async def handle_document(message: Message, state: FSMContext):
    """Обработчик загрузки документов"""
    await handle_file_upload(message, state, message.document)

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработчик загрузки фото"""
    # Берем фото максимального размера
    photo = message.photo[-1]
    await handle_file_upload(message, state, photo)

@router.message(F.video)
async def handle_video(message: Message, state: FSMContext):
    """Обработчик загрузки видео"""
    await handle_file_upload(message, state, message.video)

@router.message(F.audio)
async def handle_audio(message: Message, state: FSMContext):
    """Обработчик загрузки аудио"""
    await handle_file_upload(message, state, message.audio)

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Обработчик загрузки голосовых сообщений"""
    await handle_file_upload(message, state, message.voice)

async def handle_file_upload(message: Message, state: FSMContext, file_obj):
    """Общий обработчик загрузки файлов"""
    user_id = message.from_user.id
    
    # Получаем информацию о файле
    file_id = file_obj.file_id
    file_extension = get_file_extension(file_obj)
    
    # Формируем имя файла
    if hasattr(file_obj, 'file_name') and file_obj.file_name:
        file_name = file_obj.file_name
    else:
        # Если нет оригинального имени, создаем на основе типа
        if isinstance(file_obj, PhotoSize):
            file_name = f"photo_{file_id[:8]}.jpg"
        elif isinstance(file_obj, Video):
            file_name = f"video_{file_id[:8]}.mp4"
        elif isinstance(file_obj, Audio):
            file_name = f"audio_{file_id[:8]}.mp3"
        elif isinstance(file_obj, Voice):
            file_name = f"voice_{file_id[:8]}.ogg"
        else:
            file_name = f"file_{file_id[:8]}.{file_extension}" if file_extension else f"file_{file_id[:8]}"
    
    file_size = file_obj.file_size
    
    # Проверяем размер файла
    if file_size > Config.MAX_FILE_SIZE:
        max_size_mb = Config.MAX_FILE_SIZE // (1024 * 1024)
        await message.answer(f"❌ Файл слишком большой! Максимальный размер: {max_size_mb}MB")
        return
    
    # Получаем расширение файла
    file_ext = get_file_extension(file_obj)
    
    # Проверяем, существует ли файл у пользователя
    existing_file = await db.check_file_exists(file_id, user_id)
    if existing_file:
        existing_name, existing_size = existing_file
        existing_size_mb = existing_size / (1024 * 1024)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="📁 Мои файлы", callback_data="show_files")
        keyboard.button(text="📤 Загрузить другой файл", callback_data="upload_file")
        keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
        keyboard.adjust(2)
        
        error_text = f"""
⚠️ **Файл уже существует!**

📁 Название: {existing_name}
📏 Размер: {existing_size_mb:.2f} MB

Этот файл уже был сохранен ранее.
        """
        await message.answer(error_text, reply_markup=keyboard.as_markup())
        return
    
    # Определяем категорию файла
    category = get_file_category(file_ext)
    
    # Сохраняем информацию о файле в состоянии
    await state.update_data(
        file_id=file_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_ext,
        category=category,
        message_id=message.message_id,
        chat_id=message.chat.id
    )
    
    # Спрашиваем описание с кнопками
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⏭️ Пропустить", callback_data="skip_description")
    keyboard.button(text="❌ Отменить загрузку", callback_data="cancel_upload")
    
    await message.answer("📝 Добавьте описание к файлу (или отправьте пустое сообщение для пропуска):", reply_markup=keyboard.as_markup())
    await state.set_state(FileUploadStates.waiting_for_description)

@router.message(FileUploadStates.waiting_for_description)
async def handle_description(message: Message, state: FSMContext):
    """Обработчик описания файла"""
    # Проверяем, не пустое ли сообщение
    if not message.text or message.text.strip() == '':
        description = None
    else:
        description = message.text
    
    await state.update_data(description=description)
    
    # Спрашиваем теги с кнопками
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⏭️ Пропустить", callback_data="skip_tags")
    keyboard.button(text="❌ Отменить загрузку", callback_data="cancel_upload")
    
    await message.answer("🏷️ Добавьте теги через запятую (или отправьте пустое сообщение для пропуска):", reply_markup=keyboard.as_markup())
    await state.set_state(FileUploadStates.waiting_for_tags)

@router.message(FileUploadStates.waiting_for_tags)
async def handle_tags(message: Message, state: FSMContext):
    """Обработчик тегов файла"""
    # Проверяем, не пустое ли сообщение
    if not message.text or message.text.strip() == '':
        tags = None
    else:
        tags = message.text
    
    # Получаем данные из состояния
    data = await state.get_data()
    
    # Сохраняем файл в базу данных
    result = await db.add_file(
        file_id=data['file_id'],
        file_name=data['file_name'],
        file_size=data['file_size'],
        file_type=data['file_type'],
        category=data['category'],
        user_id=message.from_user.id,
        description=data['description'],
        tags=tags,
        message_id=data['message_id'],
        chat_id=data['chat_id']
    )
    
    # Создаем клавиатуру с кнопками навигации
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📁 Мои файлы", callback_data="show_files")
    keyboard.button(text="📤 Загрузить еще", callback_data="upload_file")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    if isinstance(result, int):  # Успешное сохранение
        file_size_mb = data['file_size'] / (1024 * 1024)
        success_text = f"""
✅ **Файл успешно сохранен!**

📁 Название: {data['file_name']}
📏 Размер: {file_size_mb:.2f} MB
📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        if data['description']:
            success_text += f"\n📝 Описание: {data['description']}"
        
        if tags:
            success_text += f"\n🏷️ Теги: {tags}"
        
        await message.answer(success_text, reply_markup=keyboard.as_markup())
        
    else:  # Общая ошибка
        error_text = f"""
❌ **Ошибка при сохранении файла!**

📁 Название: {data['file_name']}
📏 Размер: {data['file_size'] / (1024 * 1024):.2f} MB

Попробуйте загрузить файл еще раз или обратитесь к администратору.
        """
        await message.answer(error_text, reply_markup=keyboard.as_markup())
    
    await state.clear()

@router.callback_query(F.data == "show_files")
async def callback_show_files(callback: CallbackQuery):
    """Callback для показа файлов"""
    await show_categories(callback.message, callback.from_user.id)
    await callback.answer()

async def show_categories(message: Message, user_id: int):
    """Показать категории файлов пользователя"""
    categories = await db.get_user_categories(user_id)
    
    if not categories:
        await message.answer("📁 У вас пока нет сохраненных файлов.\n\nОтправьте файл, чтобы начать!")
        return
    
    categories_text = "📁 **Выберите категорию файлов:**\n\n"
    
    keyboard = InlineKeyboardBuilder()
    
    for category, count, total_size in categories:
        icon = get_category_icon(category)
        name = get_category_name(category)
        size_mb = total_size / (1024 * 1024) if total_size else 0
        
        categories_text += f"{icon} **{name}** - {count} файлов ({size_mb:.1f} MB)\n"
        keyboard.button(text=f"{icon} {name} ({count})", callback_data=f"category_{category}")
    
    # Добавляем кнопку "Все файлы"
    keyboard.button(text="📋 Все файлы", callback_data="all_files")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    await message.answer(categories_text, reply_markup=keyboard.as_markup())

@router.callback_query(F.data == "upload_file")
async def callback_upload_file(callback: CallbackQuery):
    """Callback для загрузки файла"""
    await callback.message.answer("📤 Отправьте файл, который хотите сохранить:")
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def callback_show_category(callback: CallbackQuery):
    """Callback для показа файлов определенной категории"""
    category = callback.data.replace("category_", "")
    await show_user_files_by_category(callback.message, callback.from_user.id, category)
    await callback.answer()

@router.callback_query(F.data == "all_files")
async def callback_show_all_files(callback: CallbackQuery):
    """Callback для показа всех файлов"""
    await show_user_files(callback.message, callback.from_user.id)
    await callback.answer()

async def show_user_files_by_category(message: Message, user_id: int, category: str):
    """Показать файлы пользователя по категории"""
    files = await db.get_user_files_by_category(user_id, category)
    
    if not files:
        category_name = get_category_name(category)
        await message.answer(f"📁 В категории '{category_name}' пока нет файлов.")
        return
    
    category_name = get_category_name(category)
    await show_files_list(message, files, f"📁 {category_name}:")

@router.callback_query(F.data == "search_files")
async def callback_search_files(callback: CallbackQuery):
    """Callback для поиска файлов"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    
    await callback.message.answer("🔍 Введите поисковый запрос:", reply_markup=keyboard.as_markup())
    await callback.answer()

@router.callback_query(F.data == "show_stats")
async def callback_show_stats(callback: CallbackQuery):
    """Callback для показа статистики"""
    stats = await db.get_file_stats(callback.from_user.id)
    
    total_size_mb = stats['total_size'] / (1024 * 1024)
    
    stats_text = f"""
📊 **Ваша статистика:**

📁 Всего файлов: {stats['total_files']}
💾 Общий размер: {total_size_mb:.2f} MB
📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    
    await callback.message.answer(stats_text, reply_markup=keyboard.as_markup())
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Callback для возврата в главное меню"""
    welcome_text = """
🤖 **Добро пожаловать в FileStorage Bot!**

Этот бот поможет вам хранить и управлять вашими файлами.

📁 **Основные команды:**
• /upload - Загрузить файл
• /files - Показать ваши файлы
• /search - Поиск файлов
• /delete - Удаление файлов
• /export - Экспорт файлов
• /stats - Статистика
• /help - Помощь

💡 **Просто отправьте файл, и я сохраню его для вас!**
🗑️ **Удаление:** Используйте кнопку "🗑️ Удалить" рядом с файлом
📊 **Экспорт:** Создайте CSV со списком файлов
🔗 **Поделиться:** Используйте кнопку "🔗 Поделиться" для создания ссылки
    """
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📁 Мои файлы", callback_data="show_files")
    keyboard.button(text="📤 Загрузить файл", callback_data="upload_file")
    keyboard.button(text="🔍 Поиск", callback_data="search_files")
    keyboard.button(text="📊 Статистика", callback_data="show_stats")
    keyboard.adjust(2)
    
    await callback.message.answer(welcome_text, reply_markup=keyboard.as_markup())
    await callback.answer()

@router.callback_query(F.data == "cancel_upload")
async def callback_cancel_upload(callback: CallbackQuery, state: FSMContext):
    """Callback для отмены загрузки файла"""
    await state.clear()
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📁 Мои файлы", callback_data="show_files")
    keyboard.button(text="📤 Загрузить файл", callback_data="upload_file")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    await callback.message.answer("❌ Загрузка файла отменена.", reply_markup=keyboard.as_markup())
    await callback.answer()

@router.callback_query(F.data == "skip_description")
async def callback_skip_description(callback: CallbackQuery, state: FSMContext):
    """Callback для пропуска описания"""
    await state.update_data(description=None)
    
    # Спрашиваем теги с кнопками
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⏭️ Пропустить", callback_data="skip_tags")
    keyboard.button(text="❌ Отменить загрузку", callback_data="cancel_upload")
    
    await callback.message.answer("🏷️ Добавьте теги через запятую (или отправьте пустое сообщение для пропуска):", reply_markup=keyboard.as_markup())
    await state.set_state(FileUploadStates.waiting_for_tags)
    await callback.answer()

@router.callback_query(F.data == "skip_tags")
async def callback_skip_tags(callback: CallbackQuery, state: FSMContext):
    """Callback для пропуска тегов"""
    await state.update_data(tags=None)
    
    # Получаем данные из состояния и сохраняем файл
    data = await state.get_data()
    
    # Сохраняем файл в базу данных
    result = await db.add_file(
        file_id=data['file_id'],
        file_name=data['file_name'],
        file_size=data['file_size'],
        file_type=data['file_type'],
        category=data['category'],
        user_id=callback.from_user.id,
        description=data['description'],
        tags=None,
        message_id=data['message_id'],
        chat_id=data['chat_id']
    )
    
    # Создаем клавиатуру с кнопками навигации
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📁 Мои файлы", callback_data="show_files")
    keyboard.button(text="📤 Загрузить еще", callback_data="upload_file")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)
    
    if isinstance(result, int):  # Успешное сохранение
        file_size_mb = data['file_size'] / (1024 * 1024)
        success_text = f"""
✅ **Файл успешно сохранен!**

📁 Название: {data['file_name']}
📏 Размер: {file_size_mb:.2f} MB
📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        if data['description']:
            success_text += f"\n📝 Описание: {data['description']}"
        
        await callback.message.answer(success_text, reply_markup=keyboard.as_markup())
        
    else:  # Общая ошибка
        error_text = f"""
❌ **Ошибка при сохранении файла!**

📁 Название: {data['file_name']}
📏 Размер: {data['file_size'] / (1024 * 1024):.2f} MB

Попробуйте загрузить файл еще раз или обратитесь к администратору.
        """
        await callback.message.answer(error_text, reply_markup=keyboard.as_markup())
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("download_"))
async def callback_download_file(callback: CallbackQuery):
    """Callback для скачивания файла"""
    record_id = callback.data.replace("download_", "")
    
    # Добавляем отладочную информацию
    logger.info(f"Попытка скачивания файла с record_id: {record_id}")
    
    # Получаем информацию о файле по ID записи
    file_data = await db.get_file_by_record_id(record_id)
    
    if not file_data:
        logger.error(f"Файл с record_id {record_id} не найден в базе данных")
        await callback.answer("❌ Файл не найден!")
        return
    
    logger.info(f"Найден файл: {file_data}")
    
    # Проверяем, что файл принадлежит пользователю
    _, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id = file_data
    
    if user_id != callback.from_user.id:
        await callback.answer("❌ У вас нет доступа к этому файлу!")
        return
    
    try:
        # Отправляем файл пользователю
        await callback.message.answer(f"📤 Отправляю файл: {file_name}")
        
        # Используем file_id для отправки файла
        if file_type in ['jpg', 'jpeg', 'png', 'gif']:
            await callback.message.answer_photo(file_id, caption=f"📄 {file_name}")
        elif file_type in ['mp4', 'avi', 'mov']:
            await callback.message.answer_video(file_id, caption=f"📄 {file_name}")
        elif file_type in ['mp3', 'wav', 'ogg']:
            await callback.message.answer_audio(file_id, caption=f"📄 {file_name}")
        else:
            await callback.message.answer_document(file_id, caption=f"📄 {file_name}")
        
        await callback.answer("✅ Файл отправлен!")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {e}")
        await callback.answer("❌ Ошибка при отправке файла!")

@router.callback_query(F.data.startswith("delete_"))
async def callback_delete_file(callback: CallbackQuery):
    """Callback для удаления файла"""
    record_id = callback.data.replace("delete_", "")
    
    # Получаем информацию о файле
    file_data = await db.get_file_by_record_id(record_id)
    
    if not file_data:
        await callback.answer("❌ Файл не найден!")
        return
    
    # Проверяем, что файл принадлежит пользователю
    _, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id = file_data
    
    if user_id != callback.from_user.id:
        await callback.answer("❌ У вас нет доступа к этому файлу!")
        return
    
    # Создаем клавиатуру подтверждения
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{record_id}")
    keyboard.button(text="❌ Отмена", callback_data="cancel_delete")
    keyboard.adjust(2)
    
    file_size_mb = file_size / (1024 * 1024)
    confirm_text = f"""
🗑️ **Подтверждение удаления**

📄 Файл: {file_name}
📏 Размер: {file_size_mb:.2f} MB
📅 Загружен: {datetime.fromisoformat(upload_date).strftime('%d.%m.%Y %H:%M')}

⚠️ **Внимание:** Это действие нельзя отменить!
    """
    
    await callback.message.answer(confirm_text, reply_markup=keyboard.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_"))
async def callback_confirm_delete(callback: CallbackQuery):
    """Callback для подтверждения удаления файла"""
    record_id = callback.data.replace("confirm_delete_", "")
    
    # Получаем информацию о файле
    file_data = await db.get_file_by_record_id(record_id)
    
    if not file_data:
        await callback.answer("❌ Файл не найден!")
        return
    
    # Проверяем, что файл принадлежит пользователю
    _, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id = file_data
    
    if user_id != callback.from_user.id:
        await callback.answer("❌ У вас нет доступа к этому файлу!")
        return
    
    # Удаляем файл из базы данных
    success = await db.delete_file_by_record_id(record_id, user_id)
    
    if success:
        file_size_mb = file_size / (1024 * 1024)
        success_text = f"""
✅ **Файл успешно удален!**

📄 Файл: {file_name}
📏 Размер: {file_size_mb:.2f} MB
🗑️ Удален: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="📁 Мои файлы", callback_data="show_files")
        keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
        keyboard.adjust(2)
        
        await callback.message.answer(success_text, reply_markup=keyboard.as_markup())
        await callback.answer("✅ Файл удален!")
        
        # Логируем удаление
        logger.info(f"Пользователь {user_id} удалил файл {file_name} (record_id: {record_id})")
    else:
        await callback.answer("❌ Ошибка при удалении файла!")

@router.callback_query(F.data.startswith("share_"))
async def callback_share_file(callback: CallbackQuery):
    """Callback для генерации ссылки на файл"""
    record_id = callback.data.replace("share_", "")
    
    # Получаем информацию о файле
    file_data = await db.get_file_by_record_id(record_id)
    
    if not file_data:
        await callback.answer("❌ Файл не найден!")
        return
    
    # Проверяем, что файл принадлежит пользователю
    _, file_id, file_name, file_size, file_type, category, user_id, upload_date, description, tags, message_id, chat_id = file_data
    
    if user_id != callback.from_user.id:
        await callback.answer("❌ У вас нет доступа к этому файлу!")
        return
    
    try:
        # Генерируем уникальную ссылку для файла
        import hashlib
        import time
        
        # Создаем уникальный хеш
        unique_string = f"{file_id}_{user_id}_{record_id}_{int(time.time())}"
        share_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        # Сохраняем информацию о ссылке в базе данных
        success = await db.add_share_link(share_id, file_id, user_id, record_id)
        
        if success:
            file_size_mb = file_size / (1024 * 1024)
            share_text = f"""
🔗 **Ссылка для скачивания файла**

📄 Файл: {file_name}
📏 Размер: {file_size_mb:.2f} MB
📅 Загружен: {datetime.fromisoformat(upload_date).strftime('%d.%m.%Y %H:%M')}

🔗 **Ссылка для скачивания:**
{get_bot_share_url(share_id)}

💡 **Как использовать:**
1. Скопируйте ссылку и отправьте другу
2. Или просто перешлите это сообщение другу
3. При переходе по ссылке файл будет отправлен автоматически

⚠️ **Внимание:** Ссылка действительна 24 часа
            """
            
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text="📁 Мои файлы", callback_data="show_files")
            keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
            keyboard.adjust(2)
            
            await callback.message.answer(share_text, reply_markup=keyboard.as_markup())
            await callback.answer("✅ Ссылка создана!")
            
            # Логируем создание ссылки
            logger.info(f"Пользователь {user_id} создал ссылку для файла {file_name} (share_id: {share_id})")
        else:
            await callback.answer("❌ Ошибка при создании ссылки!")
            
    except Exception as e:
        logger.error(f"Ошибка при создании ссылки: {e}")
        await callback.answer("❌ Ошибка при создании ссылки!")



async def generate_share_link(file_id: str, user_id: int, record_id: int) -> str:
    """Генерирует уникальную ссылку для файла"""
    try:
        # Создаем уникальный ID для ссылки
        import hashlib
        import time
        
        # Создаем уникальный хеш
        unique_string = f"{file_id}_{user_id}_{record_id}_{int(time.time())}"
        share_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        # Сохраняем информацию о ссылке в базе данных
        success = await db.add_share_link(share_id, file_id, user_id, record_id)
        
        if success:
            return share_id
        else:
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при генерации ссылки: {e}")
        return None

async def create_files_export(user_id: int, files: list) -> tuple[str, io.BytesIO]:
    """Создает экспорт списка файлов в формате CSV"""
    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Записываем заголовки
    writer.writerow([
        'Название файла',
        'Размер (MB)',
        'Тип файла',
        'Категория',
        'Дата загрузки',
        'Описание',
        'Теги'
    ])
    
    # Записываем данные файлов
    for file_data in files:
        record_id, file_id, file_name, file_size, file_type, category, _, upload_date, description, tags, message_id, chat_id = file_data
        
        file_size_mb = file_size / (1024 * 1024)
        upload_date_str = datetime.fromisoformat(upload_date).strftime('%d.%m.%Y %H:%M')
        
        writer.writerow([
            file_name,
            f"{file_size_mb:.2f}",
            file_type,
            get_category_name(category),
            upload_date_str,
            description or '',
            tags or ''
        ])
    
    # Получаем содержимое и создаем BytesIO объект
    csv_content = output.getvalue()
    output.close()
    
    # Создаем BytesIO объект для отправки
    csv_bytes = io.BytesIO(csv_content.encode('utf-8'))
    csv_bytes.seek(0)
    
    # Формируем имя файла
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"files_export_{current_date}.csv"
    
    return filename, csv_bytes

@router.callback_query(F.data == "export_files")
async def callback_export_files(callback: CallbackQuery):
    """Callback для экспорта файлов"""
    user_id = callback.from_user.id
    
    # Получаем все файлы пользователя
    files = await db.get_user_files(user_id)
    
    if not files:
        await callback.answer("📁 У вас нет файлов для экспорта!")
        return
    
    try:
        # Создаем экспорт
        filename, csv_bytes = await create_files_export(user_id, files)
        
        # Создаем временный файл
        temp_file_path = f"/tmp/{filename}"
        with open(temp_file_path, 'wb') as f:
            f.write(csv_bytes.getvalue())
        
        # Отправляем файл
        await callback.message.answer_document(
            document=FSInputFile(temp_file_path),
            caption=f"📊 **Экспорт файлов**\n\n📁 Всего файлов: {len(files)}\n📅 Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        # Удаляем временный файл
        os.remove(temp_file_path)
        
        await callback.answer("✅ Экспорт создан и отправлен!")
        
        # Логируем экспорт
        logger.info(f"Пользователь {user_id} экспортировал {len(files)} файлов")
        
    except Exception as e:
        logger.error(f"Ошибка при создании экспорта: {e}")
        await callback.answer("❌ Ошибка при создании экспорта!")

async def show_user_files(message: Message, user_id: int):
    """Показать файлы пользователя"""
    files = await db.get_user_files(user_id)
    
    if not files:
        await message.answer("📁 У вас пока нет сохраненных файлов.\n\nОтправьте файл, чтобы начать!")
        return
    
    await show_files_list(message, files, "📁 Ваши файлы:")

async def show_files_list(message: Message, files: list, title: str):
    """Показать список файлов"""
    files_text = title + "\n\n"
    
    keyboard = InlineKeyboardBuilder()
    
    for i, file_data in enumerate(files[:8], 1):  # Показываем первые 8 файлов (лимит кнопок)
        record_id, file_id, file_name, file_size, file_type, category, _, upload_date, description, tags, message_id, chat_id = file_data
        
        file_size_mb = file_size / (1024 * 1024)
        upload_date_str = datetime.fromisoformat(upload_date).strftime('%d.%m.%Y %H:%M')
        
        files_text += f"{i}. 📄 **{file_name}**\n"
        files_text += f"   📏 {file_size_mb:.2f} MB | 📅 {upload_date_str}\n"
        
        if description:
            files_text += f"   📝 {description}\n"
        
        if tags:
            files_text += f"   🏷️ {tags}\n"
        
        files_text += "\n"
        
        # Добавляем кнопки для скачивания, удаления и шаринга файла
        short_name = file_name[:12] if len(file_name) > 12 else file_name
        keyboard.button(text=f"📥 {short_name}", callback_data=f"download_{record_id}")
        keyboard.button(text=f"🔗 Поделиться", callback_data=f"share_{record_id}")
        keyboard.button(text=f"🗑️ Удалить", callback_data=f"delete_{record_id}")
    
    if len(files) > 8:
        files_text += f"... и еще {len(files) - 8} файлов"
    
    # Добавляем общие кнопки
    keyboard.button(text="📊 Экспорт", callback_data="export_files")
    keyboard.button(text="🔍 Поиск", callback_data="search_files")
    keyboard.button(text="📊 Статистика", callback_data="show_stats")
    keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
    keyboard.adjust(2)  # По две кнопки в строке
    
    await message.answer(files_text, reply_markup=keyboard.as_markup())

async def handle_shared_file_download(message: Message, share_id: str):
    """Обработчик скачивания файла по ссылке"""
    logger.info(f"Начинаем обработку ссылки: {share_id}")
    try:
        # Получаем информацию о ссылке
        share_data = await db.get_share_link(share_id)
        logger.info(f"Получены данные ссылки: {share_data}")
        
        if not share_data:
            logger.warning(f"Ссылка {share_id} не найдена или недействительна")
            await message.answer("❌ **Ссылка недействительна или истекла!**\n\nВозможные причины:\n• Ссылка была удалена\n• Истек срок действия (24 часа)\n• Файл был удален")
            return
        
        # Распаковываем данные из share_data
        share_id, file_id, user_id, record_id, created_date, expires_date, is_active, file_name, file_size, file_type, category, description, tags = share_data
        
        # Форматируем информацию о файле
        file_size_mb = file_size / (1024 * 1024)
        created_date_str = datetime.fromisoformat(created_date).strftime('%d.%m.%Y %H:%M')
        expires_date_str = datetime.fromisoformat(expires_date).strftime('%d.%m.%Y %H:%M')
        
        # Создаем сообщение с информацией о файле
        file_info = f"""
🔗 **Файл по ссылке**

📄 **Название:** {file_name}
📏 **Размер:** {file_size_mb:.2f} MB
📁 **Тип:** {file_type}
📅 **Загружен:** {created_date_str}
⏰ **Действует до:** {expires_date_str}
        """
        
        if description:
            file_info += f"\n📝 **Описание:** {description}"
        
        if tags:
            file_info += f"\n🏷️ **Теги:** {tags}"
        
        # Создаем клавиатуру для скачивания
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="📥 Скачать файл", callback_data=f"download_shared_{share_id}")
        keyboard.button(text="🏠 Главное меню", callback_data="main_menu")
        keyboard.adjust(1)
        
        await message.answer(file_info, reply_markup=keyboard.as_markup())
        
        # Сразу отправляем файл пользователю
        try:
            await message.answer_document(
                document=file_id,
                caption=f"📄 **{file_name}**\n📏 {file_size_mb:.2f} MB\n📁 {file_type}"
            )
            logger.info(f"Файл {file_name} отправлен пользователю {message.from_user.id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке файла: {e}")
            await message.answer("❌ Ошибка при отправке файла. Попробуйте скачать через кнопку выше.")
        
        # Логируем обращение к ссылке
        logger.info(f"Пользователь {message.from_user.id} перешел по ссылке {share_id} для файла {file_name}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ссылки {share_id}: {e}")
        await message.answer("❌ Произошла ошибка при обработке ссылки!")

def get_bot_share_url(share_id: str) -> str:
    """Получить ссылку через бота с реальным именем бота"""
    from config.config import Config
    bot_username = Config.BOT_USERNAME or "your_bot_username"
    return f"https://t.me/{bot_username}?start=file_{share_id}"

async def get_direct_file_url(file_id: str) -> str:
    """Получить прямую ссылку на файл через Telegram File API"""
    from src.config.config import Config
    import aiohttp
    
    bot_token = Config.BOT_TOKEN
    api_url = f"https://api.telegram.org/bot{bot_token}/getFile"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json={"file_id": file_id}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        file_path = data["result"]["file_path"]
                        return f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                    else:
                        logger.error(f"Telegram API вернул ошибку: {data}")
                else:
                    logger.error(f"HTTP ошибка {response.status}: {await response.text()}")
    except Exception as e:
        logger.error(f"Ошибка при получении прямой ссылки: {e}")
    
    return None

@router.callback_query(F.data.startswith("download_shared_"))
async def callback_download_shared_file(callback: CallbackQuery):
    """Callback для скачивания файла по ссылке"""
    share_id = callback.data.replace("download_shared_", "")
    
    try:
        # Получаем информацию о ссылке
        share_data = await db.get_share_link(share_id)
        
        if not share_data:
            await callback.answer("❌ Ссылка недействительна или истекла!")
            return
        
        # Распаковываем данные
        share_id, file_id, user_id, record_id, created_date, expires_date, is_active, file_name, file_size, file_type, category, description, tags = share_data
        
        # Отправляем файл
        await callback.message.answer_document(
            document=file_id,
            caption=f"📄 **{file_name}**\n📏 {file_size / (1024 * 1024):.2f} MB\n📁 {file_type}"
        )
        
        await callback.answer("✅ Файл отправлен!")
        
        # Логируем скачивание
        logger.info(f"Пользователь {callback.from_user.id} скачал файл {file_name} по ссылке {share_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при скачивании файла по ссылке: {e}")
        await callback.answer("❌ Ошибка при скачивании файла!") 