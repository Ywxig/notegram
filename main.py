import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile
from aiogram.types import BotCommand

from src import users
from src.log import logger
from config_loader import Config

try:
    CONFIG = Config("config.json").load()
    BOT_TOKEN = CONFIG["token"]

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
except Exception as e:
    logger.error(f"Error loading config: {e}")


#  Helpers
def _uf(user: types.User) -> users.UserFiles:
    return users.UserFiles(
        id=user.id,
        first_name=user.first_name,
        username=user.username,
    )


def build_dir_keyboard(
    uf: users.UserFiles,
    rel_path: str,
    open_dirs: set[str],
) -> types.InlineKeyboardMarkup:
    """
    Build an inline keyboard that represents the directory tree.

    - Folders show ▶ (closed) or ▼ (open); tapping toggles them.
    - Files show ⬇️ (download) and 🗑 (delete) buttons.
    - A "📁 New folder here" button is shown at every level.
    """
    buttons: list[list[types.InlineKeyboardButton]] = []

    def _render(path: str, depth: int):
        listing = uf.list_dir(path)
        indent = "  " * depth

        for d in listing["dirs"]:
            child_path = os.path.join(path, d) if path else d
            is_open = child_path in open_dirs
            icon = "▼" if is_open else "▶"
            buttons.append([
                types.InlineKeyboardButton(
                    text=f"{indent}{icon} 📁 {d}",
                    callback_data=f"tog:{child_path}",
                )
            ])
            if is_open:
                _render(child_path, depth + 1)

        for f in listing["files"]:
            file_rel = os.path.join(path, f) if path else f
            buttons.append([
                types.InlineKeyboardButton(
                    text=f"{indent}📄 {f}",
                    callback_data="noop",
                ),
                types.InlineKeyboardButton(
                    text="⬇️",
                    callback_data=f"dl:{file_rel}",
                ),
                types.InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"rm:{file_rel}",
                ),
            ])

    _render(rel_path, 0)

    if not buttons:
        buttons.append([
            types.InlineKeyboardButton(text="(пусто)", callback_data="noop")
        ])

    buttons.append([
        types.InlineKeyboardButton(
            text="🔄 Обновить",
            callback_data="refresh",
        )
    ])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)



#  Per-user UI state  {user_id: set_of_open_dirs}
_open_dirs: dict[int, set[str]] = {}


#  /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    author = message.from_user
    try:
        u = users.User(id=author.id, first_name=author.first_name, username=author.username)
        u.create()
        await message.answer(f"Привет, {author.first_name}! Аккаунт создан.")
    except Exception as e:
        logger.error(f"/start error: {e}")
        await message.answer("Что-то пошло не так…")



#  /help
HELP_TEXT = (
    "<b>Команды:</b>\n"
    "/start — Создать аккаунт\n"
    "/help — Эта справка\n"
    "/ls — Дерево файлов\n"
    "/mkdir &lt;папка&gt; — Создать папку\n"
    "/rmdir &lt;папка&gt; — Удалить папку\n"
    "/rm &lt;путь&gt; — Удалить файл\n"
    "/repo &lt;ссылка&gt; — Привязать GitHub репозиторий\n\n"
    "<b>Загрузка файла в папку:</b>\n"
    "Отправьте файл с подписью <code>/add папка</code>\n"
    "Если папка не существует — она создастся автоматически.\n"
    "Без подписи — файл сохранится в корень."
)

# menu with all commands
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="ls", description="Показать список файлов/команд"),
        BotCommand(command="help", description="Справка по использованию"),
        BotCommand(command="mkdir", description="Создать папку"),
        BotCommand(command="rmdir", description="Удалить папку"),
        BotCommand(command="rm", description="Удалить файл"),
        BotCommand(command="repo", description="Привязать GitHub репозиторий"),
    ]
    # Отправляем список команд в Telegram
    await bot.set_my_commands(commands=main_menu_commands)


#  Получение файла  (с опциональным /add <dir>)
@dp.message(F.document)
async def handle_file_upload(message: types.Message, bot: Bot):
    author = message.from_user
    file_name = message.document.file_name
    uf = _uf(author)

    # Определяем папку назначения из подписи (/add <dir>)
    rel_dir = ""
    caption = (message.caption or "").strip()
    if caption.lower().startswith("/add"):
        parts = caption.split(maxsplit=1)
        if len(parts) == 2:
            rel_dir = parts[1].strip()

    try:
        dest_path = uf.save_file(rel_dir, file_name)
        await bot.download(message.document, destination=dest_path)
        folder_note = f" в папку <code>{rel_dir}</code>" if rel_dir else ""
        logger.info(f"Saved '{file_name}'{folder_note} for user {author.id}")
        await message.answer(
            f"✅ Файл <b>{file_name}</b> сохранён{folder_note}.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Upload error for {author.id}: {e}")
        await message.answer("Ошибка при сохранении файла.")



#  /mkdir <dir>
@dp.message(Command("rmdir"))
async def cmd_mkdir(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /rmdir <имя папки>")
        return

    dir_name = args[1].strip()
    uf = _uf(message.from_user)

    try:
        removed = uf.rmdir(dir_name)
        if removed:
            await message.answer(f"📁 Папка <code>{dir_name}</code> удалена.", parse_mode="HTML")
        else:
            await message.answer(f"📁 Папка <code>{dir_name}</code> должна быть пустой для удаления.", parse_mode="HTML")
    except ValueError:
        await message.answer("⚠️ Недопустимое имя папки.")

#  /rmdir <dir>
@dp.message(Command("mkdir"))
async def cmd_mkdir(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /mkdir <имя папки>")
        return

    dir_name = args[1].strip()
    uf = _uf(message.from_user)

    try:
        created = uf.mkdir(dir_name)
        if created:
            await message.answer(f"📁 Папка <code>{dir_name}</code> создана.", parse_mode="HTML")
        else:
            await message.answer(f"📁 Папка <code>{dir_name}</code> уже существует.", parse_mode="HTML")
    except ValueError:
        await message.answer("⚠️ Недопустимое имя папки.")



#  /myfiles — дерево с inline-кнопками
@dp.message(Command("ls"))
async def cmd_myfiles(message: types.Message):
    author = message.from_user
    uf = _uf(author)
    open_set = _open_dirs.setdefault(author.id, set())
    markup = build_dir_keyboard(uf, "", open_set)
    await message.answer("📂 <b>Ваши конспекты:</b>", parse_mode="HTML", reply_markup=markup)



#  Callback: toggle папки
@dp.callback_query(F.data.startswith("tog:"))
async def callback_toggle(callback: types.CallbackQuery):
    dir_path = callback.data[4:]
    uid = callback.from_user.id
    open_set = _open_dirs.setdefault(uid, set())

    if dir_path in open_set:
        open_set.discard(dir_path)
    else:
        open_set.add(dir_path)

    uf = _uf(callback.from_user)
    markup = build_dir_keyboard(uf, "", open_set)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass
    await callback.answer()



#  Callback: обновить
@dp.callback_query(F.data == "refresh")
async def callback_refresh(callback: types.CallbackQuery):
    uid = callback.from_user.id
    open_set = _open_dirs.setdefault(uid, set())
    uf = _uf(callback.from_user)
    markup = build_dir_keyboard(uf, "", open_set)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass
    await callback.answer("Обновлено ✅")



#  Callback: скачать файл
@dp.callback_query(F.data.startswith("dl:"))
async def callback_download(callback: types.CallbackQuery):
    rel_path = callback.data[3:]
    uf = _uf(callback.from_user)

    if not uf.file_exists(rel_path):
        await callback.answer("Файл не найден.", show_alert=True)
        return

    try:
        abs_path = uf.get_file_path(rel_path)
        filename = os.path.basename(rel_path)
        await callback.message.answer_document(FSInputFile(abs_path, filename=filename))
        await callback.answer()
    except Exception as e:
        logger.error(f"Download error: {e}")
        await callback.answer("Ошибка при отправке файла.", show_alert=True)



#  Callback: удалить файл (из дерева)
@dp.callback_query(F.data.startswith("rm:"))
async def callback_delete(callback: types.CallbackQuery):
    rel_path = callback.data[3:]
    uf = _uf(callback.from_user)

    if uf.delete(rel_path):
        await callback.answer(f"🗑 Удалено: {os.path.basename(rel_path)}")
        # Перерисовать дерево
        uid = callback.from_user.id
        open_set = _open_dirs.setdefault(uid, set())
        markup = build_dir_keyboard(uf, "", open_set)
        try:
            await callback.message.edit_reply_markup(reply_markup=markup)
        except Exception:
            pass
    else:
        await callback.answer("Файл не найден.", show_alert=True)



#  /delete <rel_path>  — текстовая команда удаления
@dp.message(Command("rm"))
async def cmd_delete(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /rm <путь к файлу>")
        return

    rel_path = args[1].strip()
    uf = _uf(message.from_user)

    if uf.delete(rel_path):
        await message.answer(f"🗑 Файл <code>{rel_path}</code> удалён.", parse_mode="HTML")
    else:
        await message.answer(f"Файл <code>{rel_path}</code> не найден.", parse_mode="HTML")



#  /repo
@dp.callback_query(F.data == "noop")
async def callback_noop(callback: types.CallbackQuery):
    await callback.answer()


@dp.message(Command("repo"))
async def cmd_repo(message: types.Message):
    args = message.text.split(maxsplit=1)
    author = message.from_user
    u = users.User(id=author.id, first_name=author.first_name, username=author.username)

    if len(args) < 2:
        current = u.get_repository()
        if current:
            await message.answer(f"📦 Репозиторий:\n<code>{current}</code>", parse_mode="HTML")
        else:
            await message.answer("Репозиторий не привязан.\nИспользование: /repo <ссылка>")
        return

    repo_url = args[1].strip()
    if not repo_url.startswith("https://github.com/"):
        await message.answer(
            "⚠️ Ссылка должна начинаться с <code>https://github.com/</code>",
            parse_mode="HTML",
        )
        return

    try:
        u.set_repository(repo_url)
        await message.answer(
            f"✅ Репозиторий привязан:\n<code>{repo_url}</code>",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Repo save error for {author.id}: {e}")
        await message.answer("Ошибка при сохранении.")



#  Entry point


async def main():
    # Setup menu
    await set_main_menu(bot)
    # Setup logger and start bot
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    # check if /users folkder exist
    if not os.path.exists("users"):
        os.mkdir("users")
     
    # check if config.json exist
    if not os.path.exists("config.json"):
        with open("config.json", "w") as f:
            Config("config.json").create({"token" : "TOKEN"})

# entery point
if __name__ == "__main__":
    asyncio.run(main())