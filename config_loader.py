import json

class Config:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict:
        """this method for load config"""
        with open(self.path, 'r') as f:
            config = json.load(f)
        return config
    
    def create(self, config: dict) -> None:
        """this method for create config"""
        with open(self.path, 'w') as f:
            json.dump(config, f, indent=4)