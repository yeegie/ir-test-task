import html
import logging
import os

from aiogram import F, Bot, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.helpers.file_operations import get_file_caching_data, get_file_data
from app.helpers.table_exporter import export_result_table
from app.helpers.utils import is_excel, extract_article
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
        
        current_file_path = os.path.join(TEMP_DIR, filename)
        current_export_file_path = None

        if not filename or not is_excel(filename):
            await message.reply(f"Файл <code>{filename}</code> не подходит, отправь файлы в формате xlsx или xls и в следующем формате: <code>A123 - специальный заказ.xlsx</code>")
            continue

        # Save file to temp directory
        await message.bot.download(document, current_file_path)
        logging.info(f"Downloaded file {current_file_path}")

        file_data = get_file_data(path=TEMP_DIR, filename=filename)
        article_code = extract_article(filename)

        # Check nullable file data
        if len(file_data) == 0:
            await message.reply(f"❌ Файл {filename} пустой или не удалось прочитать данные.")
            continue

        # Find barcode from article code
        matches = reference_data.loc[
            reference_data["Артикул"].astype(str) == str(article_code),
            "Штрихкод"
        ]

        if matches.empty:
            await message.reply(f"❌ Не нашёл штрихкод для {article_code}")
            continue

        barcode = str(matches.iloc[0])

        # Get exported file
        current_export_file_path = export_result_table(article_code, barcode, file_data, EXPORT_DIR)
        result_file = FSInputFile(os.path.join(
            EXPORT_DIR, f"code_{article_code}.xlsx"))

        results.append((article_code, result_file, message.chat.id))

    # Send results
    for article_code, file_ref, chat_id in results:
        await files[0].bot.send_document(chat_id, file_ref)
        
        # Delete temp file
        if os.path.exists(current_file_path):
            os.remove(current_file_path)
        if os.path.exists(current_export_file_path):
            os.remove(current_export_file_path)

    # Final log
    if len(results) > 1:
        await files[0].answer(f"✅ Обработано файлов: {len(results) + 1}")
