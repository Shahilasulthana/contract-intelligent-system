"""
Main FastAPI Application Entry Point
Provides REST API endpoints for the Legal RAG Query Translation System.
"""

import uuid
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.routes import router as api_router
from app.services.rag_pipeline import RAGPipeline
from app.services.query_translator import QueryTranslator, understand_query

# =====================================================
# PYDANTIC SCHEMAS
# =====================================================

class ClauseInput(BaseModel):
    """Schema for ingesting legal clauses."""
    text: str
    agreement_type: str
    clause_type: str
    document_id: str


class QueryRequest(BaseModel):
    """Schema for RAG query requests."""
    query: str


# =====================================================
# APP INITIALIZATION
# =====================================================

app = FastAPI(
    title="Legal Contract Intelligence RAG API",
    description="Retrieval-Augmented Generation system for legal contract analysis",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Initialize services
rag_pipeline = RAGPipeline()
query_translator = QueryTranslator()


# =====================================================
# HEALTH CHECK ENDPOINT
# =====================================================

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Legal RAG Pipeline API"}


# =====================================================
# DOCUMENT INGESTION ENDPOINTS
# =====================================================

@app.post("/api/ingest")
def ingest_clauses(clauses: List[ClauseInput]) -> Dict[str, Any]:
    """
    Ingests legal clauses into the RAG system.
    
    Args:
        clauses: List of clause objects with text, agreement_type, clause_type, document_id
        
    Returns:
        Status confirmation with count of ingested clauses
    """
    formatted_clauses = [
        {
            "id": str(uuid.uuid4()),
            "text": clause.text,
            "metadata": {
                "agreement_type": clause.agreement_type,
                "clause_type": clause.clause_type,
                "document_id": clause.document_id
            }
        }
        for clause in clauses
    ]
    
    rag_pipeline.ingest_documents(formatted_clauses)
    
    return {
        "status": "success",
        "message": f"Ingested {len(clauses)} clauses",
        "count": len(clauses)
    }


# =====================================================
# RAG QUERY ENDPOINTS
# =====================================================

@app.post("/api/query")
def rag_query(request: QueryRequest) -> Dict[str, Any]:
    """
    Executes end-to-end RAG pipeline for a user query.
    
    Args:
        request: QueryRequest with user query string
        
    Returns:
        Grounded answer based on retrieved legal clauses
    """
    answer = rag_pipeline.run(request.query)
    
    return {
        "query": request.query,
        "answer": answer,
        "status": "success"
    }


@app.post("/api/query/understand")
def understand_legal_intent(request: QueryRequest) -> Dict[str, Any]:
    """
    Extracts legal intent from a query (agreement type, clause type).
    
    Args:
        request: QueryRequest with user query string
        
    Returns:
        Extracted intent components
    """
    intent = understand_query(request.query)
    
    return {
        "query": request.query,
        "intent": intent,
        "status": "success"
    }


@app.post("/api/query/translate")
def translate_query(request: QueryRequest) -> Dict[str, Any]:
    """
    Transforms a query into multiple retrieval-optimized forms.
    
    Args:
        request: QueryRequest with user query string
        
    Returns:
        Expanded, rewritten, and decomposed query variations
    """
    translation = query_translator.translate(request.query)
    
    return {
        **translation,
        "status": "success"
    }


# =====================================================
# DEMO ENDPOINT
# =====================================================

@app.post("/api/demo")
def run_demo() -> Dict[str, Any]:
    """
    Runs a demo with sample legal clauses and test queries.
    
    Returns:
        Demo results showing the pipeline in action
    """
    # Sample clauses
    sample_clauses = [
        {
            "id": str(uuid.uuid4()),
            "text": "The receiving party shall hold and maintain the Confidential Information in strictest confidence for the sole and exclusive benefit of the disclosing party.",
            "metadata": {"agreement_type": "NDA", "clause_type": "Confidentiality", "document_id": "doc_001"}
        },
        {
            "id": str(uuid.uuid4()),
            "text": "This Non-Disclosure Agreement shall terminate 2 years after the Effective Date, unless extended by mutual written agreement.",
            "metadata": {"agreement_type": "NDA", "clause_type": "Term and Termination", "document_id": "doc_001"}
        },
        {
            "id": str(uuid.uuid4()),
            "text": "In the event of termination without cause, the Employer shall pay the Employee 3 months of severance pay.",
            "metadata": {"agreement_type": "Employment", "clause_type": "Termination", "document_id": "doc_002"}
        }
    ]
    
    # Create fresh pipeline for demo
    demo_pipeline = RAGPipeline()
    demo_pipeline.ingest_documents(sample_clauses)
    
    # Test queries
    test_queries = [
        "How long does the NDA term last?",
        "What happens if an employee is fired without cause?"
    ]
    
    results = []
    for query in test_queries:
        answer = demo_pipeline.run(query)
        results.append({
            "query": query,
            "answer": answer
        })
    
    return {
        "status": "success",
        "message": "Demo completed successfully",
        "ingested_clauses": len(sample_clauses),
        "test_queries": len(test_queries),
        "results": results
    }

