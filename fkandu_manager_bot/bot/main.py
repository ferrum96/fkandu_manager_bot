"""Entry point for the FKandu bot."""

import logging
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Config
from bot.database import Database
from bot.handlers import lead_form_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def handle_file(request: web.Request) -> web.Response:
    db: Database = request.app["db"]
    file_id = int(request.match_info["file_id"])
    row = db.get_file(file_id)
    if not row:
        return web.Response(status=404, text="Not found")
    filename, mime_type, data = row
    return web.Response(
        body=data,
        content_type=mime_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


async def main():
    config = Config.from_env()
    db = Database(config.db_path)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(lead_form_router)

    dp["config"] = config
    dp["db"] = db
    dp["bot"] = bot

    app = web.Application()
    app["db"] = db
    app.router.add_get("/files/{file_id}", handle_file)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.file_server_port)
    await site.start()
    logger.info(f"✅ Файловый сервер запущен на порту {config.file_server_port}")

    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
