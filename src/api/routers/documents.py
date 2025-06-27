import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Body, Request, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from src.utils.dependencies import get_mongo_conn
from src.models.models import MongoJSONEncoder
import json

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.get("/")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    mongo_conn=Depends(get_mongo_conn)
):
    """List all PDF documents in the database"""
    logger.info(f"Listando documentos com skip={skip}, limit={limit}")
    docs = mongo_conn.get_all_documents(limit=limit, skip=skip)
    return JSONResponse(
        content={"documents": json.loads(json.dumps(docs, cls=MongoJSONEncoder))}, 
        status_code=200
    )

@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    full_text: bool = Query(False),
    mongo_conn=Depends(get_mongo_conn)
):
    """Get a specific document by ID"""
    try:
        logger.info(f"Buscando documento com ID: {doc_id}")
        doc = mongo_conn.get_document_by_id(doc_id)
        
        if not doc:
            logger.warning(f"Documento não encontrado: {doc_id}")
            raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
        
        if not full_text and "full_text" in doc:
            del doc["full_text"]
        
        return JSONResponse(content=doc, status_code=200)
    except Exception as e:
        logger.error(f"Erro ao buscar documento: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search/simple")
async def search_simple(
    payload: dict = Body(...),
    mongo_conn=Depends(get_mongo_conn)
):
    """Perform a simple search based on a query string"""
    query = payload.get("input", "")
    limit = payload.get("limit", 1000)
    skip = payload.get("skip", 0)
    try:
        logger.info(f"Realizando busca simples com query: {query}")
        results = mongo_conn.document_collection.find(
            {"$text": {"$search": query}},
        )
        results = list(results)
        return JSONResponse(
            content={"results": json.loads(json.dumps(results, cls=MongoJSONEncoder))},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Erro ao realizar busca simples: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search/advanced")
async def search_advanced(
    payload: dict = Body(...),
    mongo_conn=Depends(get_mongo_conn)
):
    """Perform an advanced search with multiple filters"""
    filters = []
    limit = payload.get("limit", 1000)
    skip = payload.get("skip", 0)
    campos = ["termo", "autor", "titulo", "tema", "capitania", "data", "localizacao", "nome"]
    for campo in campos:
        if campo in payload and payload[campo]:
            filters.append({campo: {"$regex": payload[campo], "$options": "i"}})
    try:
        logger.info(f"Realizando busca avançada com filtros: {filters}")
        query = {"$and": filters} if filters else {}
        results = mongo_conn.document_collection.find(query).skip(skip).limit(limit)
        results = list(results)
        return JSONResponse(
            content={"results": json.loads(json.dumps(results, cls=MongoJSONEncoder))},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Erro ao realizar busca avançada: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

__all__ = ["router"]
