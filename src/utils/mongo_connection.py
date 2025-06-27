import os
from pymongo import MongoClient
import logging
import time

MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "oxossi_db")

client = None
db = None

logger = logging.getLogger("MongoConnection")

def get_db_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados MongoDB.
    Reutiliza a conexão existente se já estiver estabelecida.
    Levanta uma exceção se a conexão não puder ser estabelecida.
    """
    global client, db
    retries = 5
    while retries > 0:
        if client is None:
            try:
                logger.info(f"Tentando conectar ao MongoDB no URI: {MONGO_URI}")
                client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000, socketTimeoutMS=20000)
                # Testa a conexão
                client.admin.command('ping')
                db = client[DB_NAME]
                logger.info("Conexão com o MongoDB estabelecida com sucesso.")
                break
            except Exception as e:
                logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
                client = None
                db = None
                retries -= 1
                if retries > 0:
                    logger.info(f"Tentando novamente em 5 segundos... ({retries} tentativas restantes)")
                    time.sleep(5)
                else:
                    raise e
        if db is None:
            logger.critical("Falha ao inicializar o banco de dados MongoDB.")
            raise RuntimeError("Falha ao inicializar o banco de dados MongoDB.")
    return db

def close_db_connection():
    """
    Fecha a conexão com o banco de dados MongoDB, se estiver aberta.
    """
    global client
    if client:
        client.close()
        client = None
