import fitz  # PyMuPDF
import pymongo
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Conexão com o MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["pdf_database"]
collection = db["pdf_data"]

def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extrai texto de um PDF e retorna um dicionário com os dados estruturados.
    """
    if not os.path.exists(file_path):
        logging.error(f"Arquivo não encontrado: {file_path}")
        return None

    try:
        document = fitz.open(file_path)
        text_parts = []
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text_parts.append(page.get_text("text"))
        document.close()

        full_text = "".join(text_parts)
        if not full_text.strip():
            logging.warning(f"O arquivo '{file_path}' não contém texto extraível.")
            return None

        # Aqui você pode usar os extratores para identificar informações específicas
        extracted_data = {
            "file_name": os.path.basename(file_path),
            "full_text": full_text,
            # Adicione aqui os campos extraídos pelos seus extratores
            "titulo": "Título extraído",
            "autor": "Autor extraído",
            "ano_publicacao": "Ano extraído"
        }
        return extracted_data

    except Exception as e:
        logging.error(f"Erro ao processar o arquivo {file_path}: {e}")
        return None

def save_to_mongo(data: dict):
    """
    Salva os dados extraídos no MongoDB.
    """
    if data:
        collection.insert_one(data)
        logging.info(f"Dados salvos no MongoDB: {data['file_name']}")

# Exemplo de uso
if __name__ == "__main__":
    base_path = "/app/pdfs/"  # Diretório base para os PDFs
    pdf_files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith(".pdf")]

    for file_path in pdf_files:
        logging.info(f"Processando arquivo: {file_path}")
        extracted_data = extract_text_from_pdf(file_path)
        if extracted_data:
            save_to_mongo(extracted_data)
        else:
            logging.warning(f"Não foi possível processar o arquivo: {file_path}")
