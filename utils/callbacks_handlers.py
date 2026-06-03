"""
Callback handlers for inline keyboard interactions:
  tog:<path>   — toggle folder
  refresh      — refresh tree
  dl:<path>    — download file
  rm:<path>    — delete file
  noop         — no-op (file name label)
"""

import os

from aiogram import Router, types, F
from aiogram.types import FSInputFile

from src.log import logger
from utils.helpers import make_user_files
from utils.keyboards import build_dir_keyboard
from utils.state import get_open_dirs, toggle_dir

router = Router()



#  Toggle folder


@router.callback_query(F.data.startswith("tog:"))
async def cb_toggle(callback: types.CallbackQuery):
    path = callback.data[4:]
    toggle_dir(callback.from_user.id, path)

    uf = make_user_files(callback.from_user)
    markup = build_dir_keyboard(uf, "", get_open_dirs(callback.from_user.id))
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass
    await callback.answer()



#  Refresh tree


@router.callback_query(F.data == "refresh")
async def cb_refresh(callback: types.CallbackQuery):
    uf = make_user_files(callback.from_user)
    markup = build_dir_keyboard(uf, "", get_open_dirs(callback.from_user.id))
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass
    await callback.answer("🔄 Обновлено ✅")



#  Download file


@router.callback_query(F.data.startswith("dl:"))
async def cb_download(callback: types.CallbackQuery):
    rel = callback.data[3:]
    uf = make_user_files(callback.from_user)

    if not uf.file_exists(rel):
        await callback.answer("❌ Файл не найден.", show_alert=True)
        return

    try:
        await callback.message.answer_document(
            FSInputFile(uf.get_file_path(rel), filename=os.path.basename(rel))
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Download error [{callback.from_user.id}]: {e}")
        await callback.answer("❌ Ошибка при отправке файла.", show_alert=True)



#  Delete file (from tree button)


@router.callback_query(F.data.startswith("rm:"))
async def cb_delete(callback: types.CallbackQuery):
    rel = callback.data[3:]
    uf = make_user_files(callback.from_user)

    if not uf.delete(rel):
        await callback.answer("❌ Файл не найден.", show_alert=True)
        return

    await callback.answer(f"🗑 Удалено: {os.path.basename(rel)}")
    markup = build_dir_keyboard(uf, "", get_open_dirs(callback.from_user.id))
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass



#  No-op (file name label buttons)


@router.callback_query(F.data == "noop")
async def cb_noop(callback: types.CallbackQuery):
    await callback.answer()