from src.utils.mongo_connection import get_db_connection
import os
import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId

logger = logging.getLogger("DBSearch")

class DatabaseSearchEngine:
    """Engine otimizado para busca no MongoDB"""
    
    def __init__(self):
        """Initialize database search engine"""
        self.db = None
        self.collection = None
        self.cache_enabled = True
        self.cache = {}
        
    def connect(self) -> bool:
        """Connect to MongoDB using centralized connection logic"""
        try:
            logger.info("Connecting to MongoDB using centralized connection logic")
            self.db = get_db_connection()
            self.collection = self.db[os.getenv('MONGODB_COLLECTION', 'pdf_documents')]
            self._ensure_search_indexes()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False

    def _ensure_search_indexes(self) -> None:
        """Ensure we have the necessary indexes for searching"""
        try:
            if self.collection is None:
                raise RuntimeError("A conexão com o banco de dados não foi inicializada. Certifique-se de chamar o método `connect` antes de usar `_ensure_search_indexes`.")

            indexes = list(self.collection.list_indexes())
            has_text_index = any("text_search_index" in idx.get('name', '') for idx in indexes)
            
            if not has_text_index:
                logger.info("Creating text search index on full_text field")
                self.collection.create_index([("full_text", TEXT)], 
                                          name="text_search_index", 
                                          default_language="portuguese")
            
            self.collection.create_index([("is_scraped_item", ASCENDING)],
                                      name="scraped_item_index")
            
        except Exception as e:
            logger.error(f"Error ensuring indexes: {str(e)}")
