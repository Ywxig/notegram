import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# for config
from config_loader import Config

CONFIG = Config("config.json").load()

# Insert your token here, which you received from @BotFather
BOT_TOKEN = CONFIG["token"]

# Enable logging to see what the bot is doing in the console
logging.basicConfig(level=logging.INFO)

# Initialize the bot and dispatcher (event handler)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Reaction to the /start command
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Hello, World! I'm your new bot. Write me something!")

# 2. Echo effect: the bot simply returns any text message back to you
@dp.message(F.text)
async def echo_message(message: types.Message):
    await message.answer(f"You said: {message.text}")

# Main function for launching
async def main():
    # Clear the message queue that arrived while the bot was offline
    await bot.delete_webhook(drop_pending_updates=True)
    # Start continuous polling of Telegram servers (Polling)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Start the asynchronous loop
    asyncio.run(main())