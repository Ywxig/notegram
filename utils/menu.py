"""Bot command menu registration."""

from aiogram import Bot
from aiogram.types import BotCommand


async def set_menu(bot: Bot):
    """Register bot commands visible in Telegram menu."""
    await bot.set_my_commands([
        BotCommand(command="start", description="Создать аккаунт"),
        BotCommand(command="ls",    description="Показать файлы и папки"),
        BotCommand(command="help",  description="Справка"),
        BotCommand(command="mkdir", description="Создать папку"),
        BotCommand(command="rmdir", description="Удалить папку"),
        BotCommand(command="rm",    description="Удалить файл"),
        BotCommand(command="repo",  description="Привязать GitHub репозиторий"),
    ])