import asyncio
import logging
import shutil
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from app.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, dispatcher: Dispatcher):
    dispatcher.include_router(router)
    logger.info(f'[!] Bot stated -- @{(await bot.get_me()).username}')

    # Create temp directories
    for dirname in ["input", "export"]:
        os.makedirs(f"data/temp/{dirname}", exist_ok=True)


async def on_shutdown(bot: Bot, dispatcher: Dispatcher):
    logger.info('[!] Bot stopped')

    # Clear temp files
    for dirname in ["input", "export"]:
        shutil.rmtree(f"data/temp/{dirname}", ignore_errors=True)

    await bot.session.close()


def main():
    # Parse bot token from file
    with open("token.txt", "r") as f:
        token = f.read().strip()
    
    properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(
        token=token,
        default=properties
    )

    dispatcher = Dispatcher()

    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    asyncio.run(dispatcher.start_polling(bot))
