# Repositório para interações com o MongoDB
from pymongo.database import Database

class MongoRepository:
    def __init__(self, db: Database):
        self.db = db

    def insert_document(self, collection_name: str, document: dict):
        collection = self.db[collection_name]
        return collection.insert_one(document)

    def find_document(self, collection_name: str, query: dict):
        collection = self.db[collection_name]
        return collection.find(query)

    def update_document(self, collection_name: str, query: dict, update: dict):
        collection = self.db[collection_name]
        return collection.update_one(query, {'$set': update})
