import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# import os for creating dir
import os

# import src
from src import users

#import log for logging
from src.log import logger

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
    try:
        new_user = users.User(id=author.id, first_name=author.first_name, username=author.username)
        new_user.create()
        await message.answer(f"your account created successfully, welcome {author.first_name}")

    except Exception as e:
        logger.error(f"Fatal error {e}")
        await message.answer(f"sooting wrong...")

@dp.message(F.document)
async def handle_file_upload(message: types.Message, bot: Bot):
    # 1. Get user ID and file name
    user_id = message.from_user.id
    file_name = message.document.file_name

    user_dir = f"users/{user_id}/_notes_"
    
    file_path = os.path.join(user_dir, file_name)
    
    try:
        # 5. Command the bot to download the file from Telegram servers to your computer/server
        await bot.download(message.document, destination=file_path)
        
        # Log event to info.log
        logger.info(f"File '{file_name}' saved to directory {user_dir}")
        await message.answer(f"File successfully saved to your personal folder!")
        
    except Exception as e:
        # If Telegram fails to provide the file or disk space runs out, log to error.log
        logger.error(f"Failed to save file '{file_name}' for {user_id}. Reason: {e}")
        await message.answer("Oops! An error occurred while saving the file.")

# Main function for launching
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())