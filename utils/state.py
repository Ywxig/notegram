"""Per-user UI state: tracks which folders are expanded in /ls tree."""

_open_dirs: dict[int, set[str]] = {}


def get_open_dirs(user_id: int) -> set[str]:
    return _open_dirs.setdefault(user_id, set())


def toggle_dir(user_id: int, path: str):
    open_set = get_open_dirs(user_id)
    if path in open_set:
        open_set.discard(path)
    else:
        open_set.add(path)


def clear_state(user_id: int):
    _open_dirs.pop(user_id, None)