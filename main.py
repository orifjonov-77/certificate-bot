import asyncio
import logging
import sys
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.database import init_db
from app.handlers import router
from app.admin_handlers import admin_router
from app.scheduler import start_result_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Render bepul Web Service portini ochish uchun oddiy health-check handler
async def handle_ping(request):
    return web.Response(text="MDev Certificate Bot is running healthy!")

async def start_web_server():
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Render Web Service porti {port} da muvaffaqiyatli ochildi!")

async def main():
    token = os.getenv("BOT_TOKEN", "").strip() or BOT_TOKEN.strip()
    if not token or token == "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ":
        logger.error("XATOLIK: BOT_TOKEN ko'rsatilmagan!")
        sys.exit(1)

    logger.info(f"O'qilgan token uzunligi: {len(token)}, boshi: {token[:6]}..., oxiri: ...{token[-4:]}")

    await init_db()

    # Render bepul serveri uchun veb-portni fonda ochamiz
    await start_web_server()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(router)

    asyncio.create_task(start_result_scheduler(bot))

    logger.info("MDev Sertifikat Boti muvaffaqiyatli ishga tushdi! /start")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
