# POST /rag/query
#        │
#        ├── authenticate user
#        │
#        ├── get organization context
#        │
#        ▼
#     RAGService
#        │
#        ├── RetrievalService
#        ├── ContextBuilder
#        └── LLM
#        │
#        ▼
#    RAGResponse
#        │
#        ▼
#       JSON

# POST /api/v1/rag/query
#         ↓
# authenticate user
#         ↓
# verify organization membership
#         ↓
# RAGService.answer(...)
#         ↓
# return RAGResponse

from fastapi import APIRouter, Depends

from app.api.dependencies import require_member
from app.db.models.membership import Membership
from app.rag.dependancies import get_rag_service
from app.rag.model import RAGQueryRequest, RAGResponse
from app.rag.service import RAGService


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


@router.post("/query", response_model=RAGResponse)
def query_rag(
    request: RAGQueryRequest,
    membership: Membership = Depends(require_member),
    rag_service: RAGService = Depends(get_rag_service),
):
    return rag_service.answer(
        question=request.question,
        organization_id=membership.organization_id,
    )