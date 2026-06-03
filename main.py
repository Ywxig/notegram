import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# import src
from src import users

# for config
from config_loader import Config

CONFIG = Config("config.json").load()

# Insert your token here, which you received from @BotFather
BOT_TOKEN = CONFIG["token"]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Reaction to the /start command
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Hello, World! I'm your new bot. Write me something!")
    author = message.from_user
    print(f"id:{author.id}\n first_name:{author.first_name}\nusername:{author.username}")
    new_user = users.User(id=author.id, first_name=author.first_name, username=author.username)
    new_user.create()


# Main function for launching
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())