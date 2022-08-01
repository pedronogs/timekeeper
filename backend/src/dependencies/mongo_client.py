from pymongo import MongoClient


class AppMongoClient:

    def __init__(self, host: str = "localhost", port: int = 27017):
        self.mongo_client = MongoClient(f"mongodb://{host}:{port}/")

    def __call__(self) -> MongoClient:
        return self.mongo_client