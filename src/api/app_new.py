import sys
import pathlib
import logging
import os

from fastapi import FastAPI, Query, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from src.utils.dependencies import get_db
from src.api.routers import documents

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

log_dirs = [
    os.path.join(os.getcwd(), "logs"),
    "/app/logs",
    "logs",
    "/tmp",
    "."
]
log_success = False
for log_dir in log_dirs:
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "oxossi_api.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )
        log_success = True
        break
    except Exception:
        continue
if not log_success:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("oxossi_api")

app = FastAPI(
    title="Oxossi PDF Search API",
    description="API para busca em PDFs armazenados no MongoDB",
    version="1.0.0",
    docs_url="/back-end-oxossi-py/docs",
    openapi_url="/back-end-oxossi-py/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pdf_dir = pathlib.Path(os.getenv("PDF_FILE_PATH", "/app/src/pdfs"))
app.mount("/back-end-oxossi-py/pdfs", StaticFiles(directory=str(pdf_dir)), name="pdfs")
logger.info(f"PDF directory mounted at /back-end-oxossi-py/pdfs: {pdf_dir}")

app.include_router(documents.router, prefix="/back-end-oxossi-py")

def get_mongo_client():
    client = get_db()
    try:
        yield client
    finally:
        client.close()

def get_mongo_db(client: MongoClient = Depends(get_mongo_client)):
    return client["pdf_documents"]

@app.get("/back-end-oxossi-py")
async def root():
    return {
        "name": "Oxossi PDF Search API",
        "version": "1.0.0",
        "description": "API para busca em PDFs armazenados no MongoDB"
    }

@app.get("/")
async def redirect_root():
    return {
        "message": "Please use the /back-end-oxossi-py basepath for all requests",
    }

@app.get("/itens/")
async def read_items(skip: int = 0, limit: int = 10, db=Depends(get_mongo_db)):
    items = db["pdf_documents"].find().skip(skip).limit(limit)
    return list(items)

@app.get("/back-end-oxossi-py/search")
async def search_items(
    query: str = Query(..., description="Search query string"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of items to return"),
    db=Depends(get_mongo_db)
):
    """Search for items in the database based on a query string."""
    try:
        results = db["pdf_documents"].find({"full_text": {"$regex": query, "$options": "i"}}).skip(skip).limit(limit)
        return {"results": list(results)}
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return {"error": "An error occurred during the search."}

@app.post("/back-end-oxossi-py/search")
async def detailed_search(
    search_params: dict = Body(..., description="Search parameters from the front-end"),
    db=Depends(get_mongo_db)
):
    """Perform a detailed search in the database based on provided parameters."""
    try:
        query = []
        for key, value in search_params.items():
            if value:
                words = value.split()
                word_queries = [{key: {"$regex": word, "$options": "i"}} for word in words]
                query.append({"$or": word_queries})

        combined_query = {"$and": query} if query else {}
        results = db["pdf_documents"].find(combined_query)
        return {"results": list(results)}
    except Exception as e:
        logger.error(f"Error during detailed search: {str(e)}")
        return {"error": "An error occurred during the search."}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
