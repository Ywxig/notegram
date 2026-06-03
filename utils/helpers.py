"""Shared helper functions used across handlers and callbacks."""

from aiogram import types
from src.users import UserFiles


def make_user_files(user: types.User) -> UserFiles:
    """Create a UserFiles instance from a Telegram User object."""
    return UserFiles(
        id=user.id,
        first_name=user.first_name,
        username=user.username,
    )