import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.knowledge import Document, DocumentChunk
from backend.app.rag.embeddings import embeddings_provider, cosine_similarity

def index_all_documents(db: Session) -> int:
    """Compute and persist embeddings for all unindexed document chunks."""
    chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding_json == None).all()
    count = 0
    for chunk in chunks:
        vec = embeddings_provider.get_embedding(chunk.content)
        chunk.embedding_json = json.dumps(vec)
        count += 1
    if count > 0:
        db.commit()
    return count

def search_knowledge(
    db: Session,
    query: str,
    category: Optional[str] = None,
    service_id: Optional[int] = None,
    limit: int = 4
) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant knowledge chunks using vector cosine similarity."""
    index_all_documents(db)
    query_vec = embeddings_provider.get_embedding(query)

    doc_query = db.query(DocumentChunk).join(Document)
    if category:
        doc_query = doc_query.filter(Document.category == category.upper())
    if service_id:
        doc_query = doc_query.filter(Document.service_id == service_id)

    chunks = doc_query.all()
    scored_results = []

    for chunk in chunks:
        if not chunk.embedding_json:
            continue
        try:
            chunk_vec = json.loads(chunk.embedding_json)
            sim = cosine_similarity(query_vec, chunk_vec)
            scored_results.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_title": chunk.document.title,
                "category": chunk.document.category.value,
                "service_id": chunk.document.service_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "similarity_score": round(float(sim), 4),
                "metadata": json.loads(chunk.document.metadata_json or "{}")
            })
        except Exception:
            continue

    # Sort descending by similarity score
    scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_results[:limit]
