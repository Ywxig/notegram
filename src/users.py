import os
import json

# import logger
from src.log import logger

class User:

    def __init__(self, id: int, first_name: str, username: str):
        self.id = id
        self.first_name = first_name
        self.username = username

    @staticmethod
    def load(id) -> dict:
        """
            Load user data from json file
        """
        with open(f"users/{id}/config.json", "r") as f:
            return json.load(f)
    
    def index(self) -> list[dict]:
        """This method for indexing all users"""
        users = []
        for user in os.listdir("users"):
            users.append( self.load(user) )
        return users

    def create(self):
        """
        This function creates a new user in user directory
        1. make a directory for user using his id like: /users/1904245123
        2. make a _notes_ directory inside user directory
        3. make a config.json file inside user directory
        
        """

        # if user exist now
        if os.path.exists(f"users/{self.id}"):
            print(f"User {self.id} already exist")
            return

        else:
            os.mkdir(f"users/{self.id}")
            os.mkdir(f"users/{self.id}/_notes_")
            with open(f"users/{self.id}/config.json", "w") as f:
                user_data = {
                    "id": self.id,
                    "first_name": self.first_name,
                    "username": self.username,
                    "repositories" : None
                }

                json.dump(user_data, f)
            
            logger.info(f"User {self.id} created successfully")