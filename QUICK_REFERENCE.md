"""
QUICK REFERENCE - RAG Pipeline Modules
=======================================
"""

# ═══════════════════════════════════════════════════════════════════════════════

# 1. IMPORT PATTERNS

# ═══════════════════════════════════════════════════════════════════════════════

# Use the pipeline directly

from app.services.rag_pipeline import RAGPipeline, hybrid_rag_pipeline

# Use components individually

from app.services.query_translator import understand_query, QueryTranslator
from app.services.retriever import dense_retrieval, sparse_retrieval, indexer

# Use config

from app.core.config import client, dense_model, cross_encoder

# ═══════════════════════════════════════════════════════════════════════════════

# 2. COMPLETE WORKFLOW

# ═══════════════════════════════════════════════════════════════════════════════

from app.services.rag_pipeline import RAGPipeline

# 1. Initialize

pipeline = RAGPipeline()

# 2. Ingest documents

clauses = [
{
"id": "clause_1",
"text": "NDA text here...",
"metadata": {
"agreement_type": "NDA",
"clause_type": "Confidentiality",
"document_id": "doc_001"
}
}
]
pipeline.ingest_documents(clauses)

# 3. Query

answer = pipeline.run("How long does the NDA last?")
print(answer)

# ═══════════════════════════════════════════════════════════════════════════════

# 3. INDIVIDUAL COMPONENTS

# ═══════════════════════════════════════════════════════════════════════════════

# Query Understanding

from app.services.query_translator import understand_query
intent = understand_query("What about confidentiality?")

# Returns: {"agreement_type": "NDA", "clause_type": "Confidentiality"}

# Query Transformation

from app.services.query_translator import QueryTranslator
translator = QueryTranslator()
transformed = translator.translate("What about confidentiality?")

# Returns: {

# "original": "...",

# "expanded": ["variant1", "variant2"],

# "rewritten": "...",

# "decomposed": ["sub1", "sub2"]

# }

# Dense Retrieval (Semantic Search)

from app.services.retriever import dense_retrieval
dense_results = dense_retrieval(
query="How long is the NDA?",
filters={"agreement_type": "NDA"},
top_k=10
)

# Returns: {doc_id: {"id": "...", "text": "...", "dense_score": 0.9}, ...}

# Sparse Retrieval (Keyword Search)

from app.services.retriever import sparse_retrieval
sparse_results = sparse_retrieval(query="How long is the NDA?", top_k=10)

# Returns: {doc_id: {"id": "...", "text": "...", "sparse_score": 0.8}, ...}

# Hybrid Fusion

from app.services.retriever import hybrid_fusion
fused = hybrid_fusion(dense_results, sparse_results)

# Returns: [{"id": "...", "text": "...", "hybrid_score": 0.85}, ...]

# Reranking

from app.services.retriever import rerank
reranked = rerank(query="How long?", candidates=fused, top_k=5)

# Returns: [{"id": "...", "text": "...", "rerank_score": 8.5}, ...]

# Context Building

from app.services.rag_pipeline import build_context
context = build_context(reranked)

# Returns: "Clause 1 [Document ID: doc_001]:\nNDA text...\n\nClause 2..."

# Answer Generation

from app.services.rag_pipeline import generate_grounded_answer
answer = generate_grounded_answer(
query="How long is the NDA?",
context=context,
intent={"agreement_type": "NDA", "clause_type": "Term"}
)

# Returns: "Based on the retrieved clauses: ..."

# ═══════════════════════════════════════════════════════════════════════════════

# 4. CONFIGURATION

# ═══════════════════════════════════════════════════════════════════════════════

# All configuration in core/config.py

from app.core.config import (
OPENAI_API_KEY, # From env or default
MODEL_NAME, # gpt-4o-mini
MODEL_NAME_GENERATION, # gpt-4o
DENSE_MODEL_NAME, # BAAI/bge-small-en
RERANKER_MODEL_NAME, # cross-encoder/ms-marco-MiniLM-L-6-v2
client, # OpenAI client
dense_model, # Embedding model
cross_encoder, # Reranker model
chroma_client, # ChromaDB client
dense_collection # Vector collection
)

# Access models

from app.core.config import dense_model, cross_encoder
embeddings = dense_model.encode(["text 1", "text 2"])
scores = cross_encoder.predict([["query", "doc1"], ["query", "doc2"]])

# ═══════════════════════════════════════════════════════════════════════════════

# 5. API USAGE (FastAPI)

# ═══════════════════════════════════════════════════════════════════════════════

# Start server

# $ uvicorn app.main:app --reload

# Health Check

# GET /

# Response: {"status": "ok", "service": "Legal RAG Pipeline API"}

# Ingest Documents

# POST /api/ingest

# Body: [{"text": "...", "agreement_type": "NDA", "clause_type": "Term", "document_id": "doc_001"}]

# Response: {"status": "success", "count": 1}

# Execute RAG Pipeline

# POST /api/query

# Body: {"query": "How long is the NDA?"}

# Response: {"query": "...", "answer": "...", "status": "success"}

# Extract Intent

# POST /api/query/understand

# Body: {"query": "How long is the NDA?"}

# Response: {"query": "...", "intent": {"agreement_type": "NDA", "clause_type": "Term"}, "status": "success"}

# Transform Query

# POST /api/query/translate

# Body: {"query": "How long is the NDA?"}

# Response: {"original": "...", "expanded": [...], "rewritten": "...", "decomposed": [...], "status": "success"}

# Demo

# POST /api/demo

# Response: {"status": "success", "ingested_clauses": 3, "results": [...]}

# ═══════════════════════════════════════════════════════════════════════════════

# 6. ENVIRONMENT VARIABLES

# ═══════════════════════════════════════════════════════════════════════════════

# Set before running

# export OPENAI_API_KEY="your-api-key-here"

# export MODEL_NAME="openai/gpt-4o-mini" # Optional

# export MODEL_NAME_GENERATION="openai/gpt-4o" # Optional

# Access in code

import os
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")

# ═══════════════════════════════════════════════════════════════════════════════

# 7. PIPELINE STAGES

# ═══════════════════════════════════════════════════════════════════════════════

# pipeline.run() executes these stages in order:

"""
Stage 1: Query Understanding
understand_query() → {agreement_type, clause_type}

Stage 2: Parallel Retrieval
dense_retrieval() → semantic results
sparse_retrieval() → keyword results

Stage 3: Hybrid Fusion
hybrid_fusion() → combined results (70% dense + 30% sparse)

Stage 4: Reranking
rerank() → top-k refined results

Stage 5: Context Building
build_context() → formatted string

Stage 6: Answer Generation
generate_grounded_answer() → final answer
"""

# ═══════════════════════════════════════════════════════════════════════════════

# 8. ERROR HANDLING

# ═══════════════════════════════════════════════════════════════════════════════

try:
pipeline = RAGPipeline()
pipeline.ingest_documents(clauses)
answer = pipeline.run(query)
except Exception as e:
print(f"Error: {e}") # Fallback to default message
answer = "The information is not available in the retrieved clauses."

# ═══════════════════════════════════════════════════════════════════════════════

# 9. TESTING

# ═══════════════════════════════════════════════════════════════════════════════

# Test individual components

def test_query_understanding():
intent = understand_query("Help")
assert "agreement_type" in intent
assert "clause_type" in intent
print("✓ Query understanding works")

def test_retrieval():
results = dense_retrieval("test", {}, top_k=5)
assert isinstance(results, dict)
print("✓ Retrieval works")

def test_pipeline():
pipeline = RAGPipeline()
answer = pipeline.run("test query")
assert isinstance(answer, str)
print("✓ Pipeline works")

# Run demo

if **name** == "**main**":
from app.services.rag_pipeline import RAGPipeline
import uuid

    sample_clauses = [
        {
            "id": str(uuid.uuid4()),
            "text": "NDA term is 2 years",
            "metadata": {"agreement_type": "NDA", "clause_type": "Term", "document_id": "doc_001"}
        }
    ]

    pipeline = RAGPipeline()
    pipeline.ingest_documents(sample_clauses)
    answer = pipeline.run("How long is the NDA?")
    print(answer)

# ═══════════════════════════════════════════════════════════════════════════════

# 10. MODULE DEPENDENCIES

# ═══════════════════════════════════════════════════════════════════════════════

# Clean dependency hierarchy (no cycles):

#

# main.py

# ├── rag_pipeline.py

# │ ├── query_translator.py

# │ │ └── config.py

# │ └── retriever.py

# │ └── config.py

# ├── query_translator.py

# │ └── config.py

# ├── retriever.py

# │ └── config.py

# └── config.py (no dependencies)

# ═══════════════════════════════════════════════════════════════════════════════
