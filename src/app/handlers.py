import logging
import os

from aiogram import F, Bot, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.helpers.file_operations import get_file_caching_data, get_file_data
from app.helpers.table_exporter import export_result_table
from app.helpers.utils import is_excel, extract_article, extract_barcode
from app.helpers.wrappers import group_files


router = Router()

UPLOAD_DIR = "data"
TEMP_DIR = f"{UPLOAD_DIR}/temp/input/"
EXPORT_DIR = f"{UPLOAD_DIR}/temp/export/"


# Welcome message handler
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = [
        "👋",
        "📄 Отправь мне один файл формата xlsx или xls",
        "ℹ️ Ты можешь отправить несколько файлов сразу",
        "❗️ <b>Файл обязательно должен содержать артикул в названии, например:</b> <code>A123 - специальный заказ.xlsx</code>"
    ]
    
    for text in welcome_text:
        await message.answer(text)

# Document handler
@router.message(F.document)
@group_files(waiting_time=3)
async def document_handler(files: list[Message]):
    results = []
    reference_data = get_file_caching_data("data/", "справочник.xlsx")

    for message in files:
        document = message.document
        filename = document.file_name
        temp_path = os.path.join(TEMP_DIR, filename)

        # Validate filename
        if not filename or not is_excel(filename):
            await message.reply(f"Файл <code>{filename}</code> не подходи\nФормат: xlsx/xls. Название: <code>A123 - заказ.xlsx</code>")
            continue

        # Save file
        await message.bot.download(document, temp_path)
        logging.info(f"Downloaded: {temp_path}")

        file_data = get_file_data(TEMP_DIR, filename)
        article = extract_article(filename)

        # Validate data
        if file_data.empty:
            await message.reply(f"❌ Файл {filename} пустой или повреждён.")
            continue

        barcode = extract_barcode(reference_data, article)
        if barcode is None:
            await message.reply(f"❌ Не найден штрихкод для артикула {article}")
            continue

        # Export result
        export_path = export_result_table(article, barcode, file_data, EXPORT_DIR)
        result_file = FSInputFile(export_path)

        results.append((result_file, message.chat.id))

    # Send exported files
    for file_ref, chat_id in results:
        await files[0].bot.send_document(chat_id, file_ref)

    # Cleanup input and export files
    for file in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, file)
        os.remove(file_path)

    for file in os.listdir(EXPORT_DIR):
        file_path = os.path.join(EXPORT_DIR, file)
        os.remove(file_path)
    
    # Summary
    if len(results) > 1:
        await files[0].answer(f"✅ Обработано файлов: {len(results)}")
