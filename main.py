"""
Notegram — Telegram bot for note management.
Entry point: initialises everything and starts polling.
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from config_loader import Config
from src.log import logger
from utils.menu import set_menu
from utils.commands_handlers import router as cmd_router
from utils.callbacks_handlers import router as cb_router

# ─────────────────────────────────────────────────────────
#  Config & bot setup
# ─────────────────────────────────────────────────────────

def _init_config() -> dict:
    if not os.path.exists("config.json"):
        logger.warning("config.json not found — creating default")
        Config("config.json").create({"token": "YOUR_BOT_TOKEN_HERE"})
    return Config("config.json").load()


CONFIG = _init_config()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=CONFIG["token"])
dp  = Dispatcher()

dp.include_router(cmd_router)
dp.include_router(cb_router)


# ─────────────────────────────────────────────────────────
#  Startup
# ─────────────────────────────────────────────────────────

def _init_dirs():
    os.makedirs("users", exist_ok=True)
    os.makedirs("logs",  exist_ok=True)


async def main():
    _init_dirs()
    await set_menu(bot)
    logger.info("Bot starting…")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# ─────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")