import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
MONGO_USER = os.getenv("mongo_user")
MONGO_PASS = os.getenv("mongo_pass")

URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@fraldas.1gjvb.mongodb.net/?retryWrites=true&w=majority&appName=fraldas"
CLIENT = MongoClient(URI, server_api=ServerApi('1'))
DATABASE = CLIENT['essentiel']

# Usage example:
# from .mongo import DATABASE
# collection = DATABASE['filter_usage']
