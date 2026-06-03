import os
import json

from src.log import logger


class User:

    def __init__(self, id: int, first_name: str, username: str):
        self.id = id
        self.first_name = first_name
        self.username = username

    @staticmethod
    def load(id) -> dict:
        """Load user data from config.json."""
        with open(f"users/{id}/config.json", "r") as f:
            return json.load(f)

    def save(self, data: dict):
        """Overwrite user config.json."""
        with open(f"users/{self.id}/config.json", "w") as f:
            json.dump(data, f, indent=2)

    def index(self) -> list[dict]:
        """List all registered users."""
        return [self.load(uid) for uid in os.listdir("users")]

    def create(self):
        """
        Create user directory structure:
          users/<id>/
          users/<id>/_notes_/
          users/<id>/config.json
        """
        if os.path.exists(f"users/{self.id}"):
            logger.info(f"User {self.id} already exists")
            return

        os.makedirs(f"users/{self.id}/_notes_", exist_ok=True)
        self.save({
            "id": self.id,
            "first_name": self.first_name,
            "username": self.username,
            "repository": None,
        })
        logger.info(f"User {self.id} created")

    def set_repository(self, repo_url: str):
        """Save GitHub repository URL."""
        data = self.load(self.id)
        data["repository"] = repo_url
        self.save(data)
        logger.info(f"User {self.id} set repo: {repo_url}")

    def get_repository(self) -> str | None:
        """Return saved repository URL, or None."""
        return self.load(self.id).get("repository")


class UserFiles(User):
    """File and directory operations inside a user's _notes_/ directory."""

    NOTES_DIR = "_notes_"

    def __init__(self, id: int, first_name: str, username: str):
        super().__init__(id, first_name, username)
        self.notes_dir = f"users/{self.id}/{self.NOTES_DIR}"

    # ── Internal ──────────────────────────────────────────

    def _abs(self, rel: str = "") -> str:
        return os.path.join(self.notes_dir, rel) if rel else self.notes_dir

    def _safe(self, rel: str) -> str:
        """Normalise path and block directory traversal."""
        norm = os.path.normpath(rel).lstrip("/")
        if norm.startswith(".."):
            raise ValueError(f"Path traversal blocked: {rel!r}")
        return norm

    # ── Directories ───────────────────────────────────────

    def mkdir(self, rel: str) -> bool:
        """Create directory. Returns False if already exists."""
        rel = self._safe(rel)
        if os.path.exists(self._abs(rel)):
            return False
        os.makedirs(self._abs(rel), exist_ok=True)
        logger.info(f"User {self.id} mkdir '{rel}'")
        return True

    def mkdir_if_missing(self, rel: str):
        os.makedirs(self._abs(self._safe(rel)), exist_ok=True)

    def rmdir(self, rel: str) -> bool:
        """Remove empty directory. Returns False if not empty or missing."""
        rel = self._safe(rel)
        if not rel or rel == ".":
            return False
        try:
            os.rmdir(self._abs(rel))
            logger.info(f"User {self.id} rmdir '{rel}'")
            return True
        except OSError:
            return False

    # ── Listing ───────────────────────────────────────────

    def list_dir(self, rel: str = "") -> dict:
        """Return immediate contents: {"dirs": [...], "files": [...]}."""
        abs_path = self._abs(rel)
        if not os.path.isdir(abs_path):
            return {"dirs": [], "files": []}

        dirs, files = [], []
        for e in sorted(os.scandir(abs_path), key=lambda e: e.name.lower()):
            (dirs if e.is_dir() else files).append(e.name)

        return {"dirs": dirs, "files": files}

    def tree(self, rel: str = "") -> dict:
        """Recursively build directory tree."""
        name = os.path.basename(rel) if rel else self.NOTES_DIR
        node: dict = {"name": name, "dirs": [], "files": []}
        abs_path = self._abs(rel)

        if not os.path.isdir(abs_path):
            return node

        for e in sorted(os.scandir(abs_path), key=lambda e: e.name.lower()):
            child = os.path.join(rel, e.name) if rel else e.name
            if e.is_dir():
                node["dirs"].append(self.tree(child))
            else:
                node["files"].append(e.name)

        return node

    # ── Files ─────────────────────────────────────────────

    def get_file_path(self, rel: str) -> str:
        return self._abs(self._safe(rel))

    def file_exists(self, rel: str) -> bool:
        return os.path.isfile(self.get_file_path(rel))

    def save_file(self, rel_dir: str, filename: str) -> str:
        """Ensure directory exists and return destination path for upload."""
        if rel_dir:
            self.mkdir_if_missing(rel_dir)
        return os.path.join(self._abs(rel_dir), filename)

    def delete(self, rel: str) -> bool:
        """Delete a file. Returns True on success."""
        path = self.get_file_path(rel)
        if not os.path.isfile(path):
            return False
        os.remove(path)
        logger.info(f"User {self.id} deleted '{rel}'")
        return True