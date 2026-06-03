"""
Command handlers:
  /start, /help, /ls, /mkdir, /rmdir, /rm, /repo
  + file upload (F.document)
"""

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from src.users import User
from src.log import logger
from utils.helpers import make_user_files
from utils.keyboards import build_dir_keyboard
from utils.state import get_open_dirs

router = Router()


#  /start


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    author = message.from_user
    try:
        User(id=author.id, first_name=author.first_name, username=author.username).create()
        await message.answer(f"👋 Привет, {author.first_name}! Аккаунт создан.")
    except Exception as e:
        logger.error(f"/start error [{author.id}]: {e}")
        await message.answer("❌ Что-то пошло не так…")



#  /help


_HELP = (
    "<b>📋 Команды:</b>\n"
    "/start — Создать аккаунт\n"
    "/help  — Эта справка\n"
    "/ls    — Дерево файлов\n"
    "/mkdir <code>&lt;папка&gt;</code> — Создать папку\n"
    "/rmdir <code>&lt;папка&gt;</code> — Удалить папку\n"
    "/rm    <code>&lt;путь&gt;</code>  — Удалить файл\n"
    "/repo  <code>&lt;ссылка&gt;</code> — Привязать GitHub репозиторий\n\n"
    "<b>📤 Загрузка в папку:</b>\n"
    "Отправьте файл с подписью <code>/add &lt;папка&gt;</code>\n"
    "Папка создастся автоматически, если не существует."
)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(_HELP, parse_mode="HTML")



#  File upload  (with optional caption /add <dir>)


@router.message(F.document)
async def handle_upload(message: types.Message):
    author = message.from_user
    filename = message.document.file_name
    uf = make_user_files(author)

    # Parse /add <dir> from caption
    rel_dir = ""
    caption = (message.caption or "").strip()
    if caption.lower().startswith("/add"):
        parts = caption.split(maxsplit=1)
        if len(parts) == 2:
            rel_dir = parts[1].strip()

    try:
        dest = uf.save_file(rel_dir, filename)
        await message.bot.download(message.document, destination=dest)
        folder = f" в <code>{rel_dir}</code>" if rel_dir else ""
        logger.info(f"Saved '{filename}'{folder} for {author.id}")
        await message.answer(f"✅ <b>{filename}</b> сохранён{folder}.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Upload error [{author.id}]: {e}")
        await message.answer("❌ Ошибка при сохранении файла.")



#  /ls


@router.message(Command("ls"))
async def cmd_ls(message: types.Message):
    author = message.from_user
    uf = make_user_files(author)
    markup = build_dir_keyboard(uf, "", get_open_dirs(author.id))
    await message.answer("📂 <b>Ваши конспекты:</b>", parse_mode="HTML", reply_markup=markup)



#  /mkdir


@router.message(Command("mkdir"))
async def cmd_mkdir(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /mkdir <code>&lt;папка&gt;</code>", parse_mode="HTML")
        return

    name = args[1].strip()
    uf = make_user_files(message.from_user)

    try:
        if uf.mkdir(name):
            await message.answer(f"📁 Папка <code>{name}</code> создана.", parse_mode="HTML")
        else:
            await message.answer(f"⚠️ Папка <code>{name}</code> уже существует.", parse_mode="HTML")
    except ValueError:
        await message.answer("⚠️ Недопустимое имя папки.")



#  /rmdir


@router.message(Command("rmdir"))
async def cmd_rmdir(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /rmdir <code>&lt;папка&gt;</code>", parse_mode="HTML")
        return

    name = args[1].strip()
    uf = make_user_files(message.from_user)

    try:
        if uf.rmdir(name):
            await message.answer(f"🗑 Папка <code>{name}</code> удалена.", parse_mode="HTML")
        else:
            await message.answer(f"⚠️ Папка не найдена или не пуста.", parse_mode="HTML")
    except ValueError:
        await message.answer("⚠️ Недопустимое имя папки.")



#  /rm


@router.message(Command("rm"))
async def cmd_rm(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /rm <code>&lt;путь&gt;</code>", parse_mode="HTML")
        return

    path = args[1].strip()
    uf = make_user_files(message.from_user)

    if uf.delete(path):
        await message.answer(f"🗑 <code>{path}</code> удалён.", parse_mode="HTML")
    else:
        await message.answer(f"❌ Файл <code>{path}</code> не найден.", parse_mode="HTML")



#  /repo


@router.message(Command("repo"))
async def cmd_repo(message: types.Message):
    args = message.text.split(maxsplit=1)
    author = message.from_user
    u = User(id=author.id, first_name=author.first_name, username=author.username)

    if len(args) < 2:
        repo = u.get_repository()
        if repo:
            await message.answer(f"📦 <b>Репозиторий:</b>\n<code>{repo}</code>", parse_mode="HTML")
        else:
            await message.answer("📦 Репозиторий не привязан.\nИспользование: /repo <code>&lt;ссылка&gt;</code>")
        return

    url = args[1].strip()
    if not url.startswith("https://github.com/"):
        await message.answer(
            "⚠️ Ссылка должна начинаться с <code>https://github.com/</code>",
            parse_mode="HTML",
        )
        return

    try:
        u.set_repository(url)
        await message.answer(f"✅ <b>Репозиторий привязан:</b>\n<code>{url}</code>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Repo save error [{author.id}]: {e}")
        await message.answer("❌ Ошибка при сохранении.")