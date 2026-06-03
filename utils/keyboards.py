"""Inline keyboard builders for the file tree UI."""

import os
from aiogram import types
from src.users import UserFiles


def build_dir_keyboard(
    uf: UserFiles,
    rel_path: str,
    open_dirs: set[str],
) -> types.InlineKeyboardMarkup:
    """
    Build an inline keyboard representing the _notes_/ directory tree.

    - 📁 ▶/▼  — folder toggle (closed/open)
    - 📄       — file name (non-interactive)
    - ⬇️       — download file
    - 🗑       — delete file
    - 🔄       — refresh tree
    """
    buttons: list[list[types.InlineKeyboardButton]] = []

    def _render(path: str, depth: int):
        listing = uf.list_dir(path)
        indent = "  " * depth

        for d in listing["dirs"]:
            child = os.path.join(path, d) if path else d
            icon = "▼" if child in open_dirs else "▶"
            buttons.append([
                types.InlineKeyboardButton(
                    text=f"{indent}{icon} 📁 {d}",
                    callback_data=f"tog:{child}",
                )
            ])
            if child in open_dirs:
                _render(child, depth + 1)

        for f in listing["files"]:
            file_rel = os.path.join(path, f) if path else f
            buttons.append([
                types.InlineKeyboardButton(text=f"{indent}📄 {f}", callback_data="noop"),
                types.InlineKeyboardButton(text="⬇️", callback_data=f"dl:{file_rel}"),
                types.InlineKeyboardButton(text="🗑",  callback_data=f"rm:{file_rel}"),
            ])

    _render(rel_path, 0)

    if not buttons:
        buttons.append([types.InlineKeyboardButton(text="(пусто)", callback_data="noop")])

    buttons.append([types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)