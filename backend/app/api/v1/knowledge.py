import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.knowledge import Document
from backend.app.schemas.ml import DocumentResponse, RAGSearchRequest, RAGSearchResponse
from backend.app.rag.retriever import search_knowledge
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    category: Optional[str] = None,
    service_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if category:
        query = query.filter(Document.category == category.upper())
    if service_id:
        query = query.filter(Document.service_id == service_id)

    docs = query.order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        results.append(DocumentResponse(
            id=d.id,
            title=d.title,
            category=d.category.value,
            service_id=d.service_id,
            content=d.content,
            metadata=json.loads(d.metadata_json or "{}"),
            created_at=d.created_at
        ))
    return results

@router.post("/search", response_model=RAGSearchResponse)
def search_rag_knowledge(
    payload: RAGSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chunks = search_knowledge(
        db,
        query=payload.query,
        category=payload.category,
        service_id=payload.service_id,
        limit=payload.limit
    )
    return RAGSearchResponse(
        query=payload.query,
        chunks=chunks,
        retrieval_count=len(chunks)
    )
