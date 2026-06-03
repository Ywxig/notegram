import json
import os


class Config:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Config not found: {self.filepath}")
        with open(self.filepath, "r") as f:
            return json.load(f)

    def create(self, data: dict):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)