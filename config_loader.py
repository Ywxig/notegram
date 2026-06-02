import json

class Config:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict:
        """this method for load config"""
        with open(self.path, 'r') as f:
            config = json.load(f)
        return config