import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# for config
from config_loader import Config

CONFIG = Config("config.json").load()

# Insert your token here, which you received from @BotFather
BOT_TOKEN = CONFIG["token"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Reaction to the /start command
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Hello, World! I'm your new bot. Write me something!")


# Main function for launching
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())