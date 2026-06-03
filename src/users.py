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
        with open(f"users/{id}/config.json", "r") as f:
            return json.load(f)

    def save(self, data: dict):
        with open(f"users/{self.id}/config.json", "w") as f:
            json.dump(data, f, indent=2)

    def index(self) -> list[dict]:
        users = []
        for user in os.listdir("users"):
            users.append(self.load(user))
        return users

    def create(self):
        if os.path.exists(f"users/{self.id}"):
            print(f"User {self.id} already exists")
            return
        os.makedirs(f"users/{self.id}/_notes_", exist_ok=True)
        user_data = {
            "id": self.id,
            "first_name": self.first_name,
            "username": self.username,
            "repository": None,
        }
        self.save(user_data)
        logger.info(f"User {self.id} created successfully")

    def set_repository(self, repo_url: str):
        data = self.load(self.id)
        data["repository"] = repo_url
        self.save(data)
        logger.info(f"User {self.id} set repository to {repo_url}")

    def get_repository(self) -> str | None:
        data = self.load(self.id)
        return data.get("repository")


class UserFiles(User):
    """
    Working with files/dirs inside a user's _notes_ directory.

    All paths passed to public methods are RELATIVE to _notes_,
    e.g.  ""            → root of _notes_
          "math"        → _notes_/math/
          "math/week1"  → _notes_/math/week1/
    """

    NOTES_DIR_NAME = "_notes_"

    def __init__(self, id: int, first_name: str, username: str):
        super().__init__(id, first_name, username)
        self.notes_dir = f"users/{self.id}/{self.NOTES_DIR_NAME}"

    
    #  Internal helpers                                                    #
    

    def _abs(self, rel_path: str = "") -> str:
        """Convert a relative _notes_ path to an absolute filesystem path."""
        if rel_path:
            return os.path.join(self.notes_dir, rel_path)
        return self.notes_dir

    def _safe_rel(self, rel_path: str) -> str:
        """
        Normalise and validate a relative path so it cannot escape _notes_.
        Raises ValueError on path-traversal attempts.
        """
        norm = os.path.normpath(rel_path).lstrip("/")
        if norm.startswith(".."):
            raise ValueError(f"Path traversal attempt: {rel_path!r}")
        return norm

    
    #  Directory operations                                                #
    

    def mkdir(self, rel_path: str) -> bool:
        """
        Create a directory (and any parents) inside _notes_.
        Returns True if created, False if it already existed.
        """
        rel_path = self._safe_rel(rel_path)
        abs_path = self._abs(rel_path)
        if os.path.exists(abs_path):
            return False
        os.makedirs(abs_path, exist_ok=True)
        logger.info(f"User {self.id} created directory '{rel_path}'")
        return True

    def mkdir_if_missing(self, rel_path: str):
        """Create directory only if it does not exist yet."""
        abs_path = self._abs(self._safe_rel(rel_path))
        os.makedirs(abs_path, exist_ok=True)

    def rmdir(self, rel_path: str) -> bool:
        """
        Remove an EMPTY directory. Returns True on success.
        Will not remove _notes_ root itself.
        """
        rel_path = self._safe_rel(rel_path)
        if not rel_path or rel_path == ".":
            return False  # never remove root
        abs_path = self._abs(rel_path)
        if not os.path.isdir(abs_path):
            return False
        try:
            os.rmdir(abs_path)  # fails if not empty — intentional
            logger.info(f"User {self.id} removed directory '{rel_path}'")
            return True
        except OSError:
            return False

    
    #  Tree / listing                                                      #
    

    def list_dir(self, rel_path: str = "") -> dict:
        """
        List the immediate contents of a directory.

        Returns:
            {
              "dirs":  ["math", "physics"],   # sub-directory names
              "files": ["intro.pdf", ...],    # file names
            }
        """
        abs_path = self._abs(rel_path)
        if not os.path.isdir(abs_path):
            return {"dirs": [], "files": []}

        dirs, files = [], []
        for entry in sorted(os.scandir(abs_path), key=lambda e: e.name.lower()):
            if entry.is_dir():
                dirs.append(entry.name)
            elif entry.is_file():
                files.append(entry.name)

        return {"dirs": dirs, "files": files}

    def tree(self, rel_path: str = "") -> dict:
        """
        Recursively build a nested tree starting at rel_path.

        Structure:
            {
              "name": "root",
              "dirs": [
                  {"name": "math", "dirs": [...], "files": [...]},
                  ...
              ],
              "files": ["intro.pdf", ...]
            }
        """
        abs_path = self._abs(rel_path)
        name = os.path.basename(rel_path) if rel_path else self.NOTES_DIR_NAME

        node: dict = {"name": name, "dirs": [], "files": []}
        if not os.path.isdir(abs_path):
            return node

        for entry in sorted(os.scandir(abs_path), key=lambda e: e.name.lower()):
            child_rel = os.path.join(rel_path, entry.name) if rel_path else entry.name
            if entry.is_dir():
                node["dirs"].append(self.tree(child_rel))
            elif entry.is_file():
                node["files"].append(entry.name)

        return node

    
    #  File operations                                                     #
    

    def get_file_path(self, rel_path: str) -> str:
        """Absolute path for a file given its relative path inside _notes_."""
        return self._abs(self._safe_rel(rel_path))

    def file_exists(self, rel_path: str) -> bool:
        return os.path.isfile(self.get_file_path(rel_path))

    def save_file(self, rel_dir: str, filename: str) -> str:
        """
        Ensure rel_dir exists and return the full destination path for a file.
        Used by the upload handler before calling bot.download().
        """
        rel_dir = self._safe_rel(rel_dir) if rel_dir else ""
        self.mkdir_if_missing(rel_dir) if rel_dir else None
        dest_dir = self._abs(rel_dir)
        return os.path.join(dest_dir, filename)

    def delete(self, rel_path: str) -> bool:
        """
        Delete a file. rel_path is relative to _notes_.
        Returns True on success, False if not found.
        """
        path = self.get_file_path(rel_path)
        if not os.path.isfile(path):
            logger.warning(f"Delete failed — not found: {path}")
            return False
        os.remove(path)
        logger.info(f"User {self.id} deleted '{rel_path}'")
        return True