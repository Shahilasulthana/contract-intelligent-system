# 🏗️ RAG Pipeline Refactoring - Complete Architecture

## 📋 Overview

The monolithic `rag_pipeline.py` has been successfully refactored into a clean, modular architecture with clear separation of concerns:

```
backend/app/
├── core/
│   └── config.py              ← CENTRAL CONFIGURATION
├── services/
│   ├── query_translator.py    ← QUERY TRANSFORMATION
│   ├── retriever.py           ← RETRIEVAL & RANKING
│   └── rag_pipeline.py        ← ORCHESTRATION
├── main.py                    ← API ENTRY POINT
└── ...
```

---

## 🔧 Module Responsibilities

### 1. `core/config.py` - CENTRALIZED CONFIGURATION

**Purpose:** Single source of truth for all configurations, API keys, and ML models.

**Exports:**

- `OPENAI_API_KEY` - API key (from environment or default)
- `MODEL_NAME` - LLM model name (default: "openai/gpt-4o-mini")
- `MODEL_NAME_GENERATION` - LLM for answer generation (default: "openai/gpt-4o")
- `DENSE_MODEL_NAME` - Embedding model ("BAAI/bge-small-en")
- `RERANKER_MODEL_NAME` - Cross-encoder model ("cross-encoder/ms-marco-MiniLM-L-6-v2")
- `client` - Initialized OpenAI/OpenRouter client
- `dense_model` - Loaded embedding model
- `cross_encoder` - Loaded reranker model
- `chroma_client` - ChromaDB client
- `dense_collection` - Vector collection for semantic search

**Key Features:**
✅ No hardcoded API keys (uses environment variables)
✅ Central model initialization (reduces memory footprint)
✅ Single import point for all dependencies

---

### 2. `services/query_translator.py` - QUERY TRANSFORMATION

**Purpose:** Extract query intent and transform queries for optimal retrieval.

**Exports:**

1. **`understand_query(query: str) -> Dict[str, Any]`**
   - Extracts legal intent from user queries
   - Returns: `{"agreement_type": "...", "clause_type": "..."}`
   - Used to filter and contextualize retrieval

2. **`QueryTranslator` Class**
   - Multi-faceted query transformation
   - Methods:
     - `translate(query: str) -> Dict[str, Any]`
       ```python
       {
         "original": "original query",
         "expanded": ["variant1", "variant2", "variant3"],
         "rewritten": "formal rewritten question",
         "decomposed": ["sub_query1", "sub_query2"]
       }
       ```

**Key Features:**
✅ Query expansion for improved recall
✅ Query decomposition for complex queries
✅ Intent extraction using LLM
✅ Synonym and paraphrase generation

---

### 3. `services/retriever.py` - RETRIEVAL & RANKING

**Purpose:** Handle all retrieval operations across dense and sparse systems.

**Exports:**

1. **`ClauseIndexer` Class**
   - Manages dual indexing (dense vectors + BM25)
   - Methods:
     - `__init__()` - Initialize empty indexes
     - `ingest_data(clauses: List[Dict])` - Ingest clauses into ChromaDB and BM25

2. **`indexer`** - Global singleton instance of ClauseIndexer

3. **`dense_retrieval(query, filters, top_k) -> Dict`**
   - Semantic search using ChromaDB and embeddings
   - Supports metadata filtering by agreement_type
   - Returns document IDs mapped to results with `dense_score`

4. **`sparse_retrieval(query, top_k) -> Dict`**
   - Keyword-based search using BM25
   - Returns document IDs mapped to results with `sparse_score`

5. **`hybrid_fusion(dense_res, sparse_res) -> List`**
   - Combines dense and sparse results
   - Weighted scoring: 70% dense + 30% sparse
   - Handles deduplication
   - Returns sorted list by `hybrid_score`

6. **`rerank(query, candidates, top_k, threshold) -> List`**
   - Cross-encoder re-ranking for precision
   - Filters by relevance threshold (default: -10.0)
   - Returns top_k highest-scoring results

**Key Features:**
✅ Dual retrieval for recall and precision
✅ Hybrid fusion with intelligent weighting
✅ Cross-encoder refinement
✅ Confidence threshold filtering
✅ Clean indexer interface

---

### 4. `services/rag_pipeline.py` - ORCHESTRATION

**Purpose:** Orchestrate the complete RAG workflow by coordinating other modules.

**Exports:**

1. **`build_context(clauses) -> str`**
   - Formats retrieved clauses into LLM-ready context
   - Preserves document metadata for citations

2. **`generate_grounded_answer(query, context, intent) -> str`**
   - Generates LLM response grounded in retrieved context
   - Strictly enforces grounding rules to prevent hallucination
   - Includes system prompt with 8 explicit rules

3. **`RAGPipeline` Class**
   - Master orchestrator
   - Methods:
     - `__init__()` - Initialize with indexer reference
     - `ingest_documents(clauses)` - Ingest clauses
     - `run(query, k_initial=15, top_k_final=5) -> str`

       Pipeline stages:
       1. Query Understanding → Extract intent
       2. Parallel Retrieval → Dense + Sparse search
       3. Hybrid Fusion → Combine scores
       4. Reranking → Cross-encoder refinement
       5. Context Building → Format for LLM
       6. Answer Generation → Grounded response

4. **`hybrid_rag_pipeline(query) -> str`**
   - Convenience function for simple usage
   - Creates pipeline and runs with default settings

**Key Features:**
✅ Clear pipeline stages with documentation
✅ Configurable k_initial and top_k_final parameters
✅ Guardrails against hallucination
✅ Citation-aware answer generation
✅ Clean orchestration pattern

---

### 5. `main.py` - API ENTRY POINT

**Purpose:** FastAPI application providing REST interface to RAG pipeline.

**Endpoints:**

1. **`GET /`** - Health check

   ```json
   { "status": "ok", "service": "Legal RAG Pipeline API" }
   ```

2. **`POST /api/ingest`** - Ingest clauses

   ```python
   Request: [{"text": "...", "agreement_type": "...", "clause_type": "...", "document_id": "..."}]
   Response: {"status": "success", "count": 3}
   ```

3. **`POST /api/query`** - Execute RAG pipeline

   ```python
   Request: {"query": "How long...?"}
   Response: {"query": "...", "answer": "...", "status": "success"}
   ```

4. **`POST /api/query/understand`** - Extract intent

   ```python
   Request: {"query": "..."}
   Response: {"query": "...", "intent": {"agreement_type": "...", "clause_type": "..."}}
   ```

5. **`POST /api/query/translate`** - Transform query

   ```python
   Request: {"query": "..."}
   Response: {"original": "...", "expanded": [...], "rewritten": "...", "decomposed": [...]}
   ```

6. **`POST /api/demo`** - Run demo with sample data
   ```json
   {"status": "success", "ingested_clauses": 3, "results": [...]}
   ```

**Key Features:**
✅ CORS enabled for frontend
✅ Pydantic schema validation
✅ Clean REST interface
✅ Demo endpoint for testing
✅ Comprehensive documentation

---

## 🔄 Data Flow Example

### Query: "How long does the NDA last?"

```
1. Query Understanding (query_translator.py)
   Input:  "How long does the NDA last?"
   Output: {"agreement_type": "NDA", "clause_type": "Term"}

2. Parallel Retrieval (retriever.py)
   Dense Search:  → semantic similarity → 10 candidates
   Sparse Search: → keyword matching   → 10 candidates

3. Hybrid Fusion (retriever.py)
   Input:  Dense results + Sparse results
   Output: 15 unique candidates with hybrid_score

4. Reranking (retriever.py)
   Input:  15 candidates + query
   Output: 5 top-ranked results with rerank_score

5. Context Building (rag_pipeline.py)
   Input:  5 reranked clauses
   Output: Formatted context string

6. Answer Generation (rag_pipeline.py)
   Input:  Query + Context + Intent
   Output: Grounded answer with citations

7. API Response (main.py)
   Output: {"query": "...", "answer": "...", "status": "success"}
```

---

## 📦 Import Structure

**No Circular Dependencies:**

```
main.py
  ├── rag_pipeline.RAGPipeline
  ├── query_translator.{understand_query, QueryTranslator}
  ├── retriever.{dense_retrieval, sparse_retrieval, hybrid_fusion, rerank}
  └── config.{client, models, ...}

rag_pipeline.py
  ├── query_translator.understand_query
  ├── retriever.{dense_retrieval, sparse_retrieval, hybrid_fusion, rerank, indexer}
  └── config.{client, MODEL_NAME_GENERATION}

retriever.py
  └── config.{dense_model, cross_encoder, dense_collection}

query_translator.py
  └── config.{client, MODEL_NAME}

config.py
  (No internal imports, just external dependencies)
```

---

## ✅ Refactoring Completeness

### All Original Logic Preserved:

✅ Query Understanding (legal intent extraction)
✅ Dense Retrieval (semantic search with ChromaDB)
✅ Sparse Retrieval (BM25 keyword search)
✅ Hybrid Fusion (weighted combination)
✅ Reranking (cross-encoder refinement)
✅ Context Building (clause formatting)
✅ Guardrails (hallucination prevention)
✅ Answer Generation (grounded LLM response)
✅ Data Indexing (dual indexing strategy)
✅ Test Harness (demo with sample data)

### Code Quality Improvements:

✅ Clear module responsibilities
✅ Comprehensive docstrings
✅ Type hints throughout
✅ No hardcoded API keys
✅ Single configuration source
✅ Configurable parameters
✅ Error handling
✅ Clean separation of concerns

---

## 🚀 Usage Examples

### 1. Direct Python Usage

```python
from app.services.rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline()

# Ingest documents
pipeline.ingest_documents([
    {
        "id": "1",
        "text": "NDA term is 2 years...",
        "metadata": {"agreement_type": "NDA", "clause_type": "Term", "document_id": "doc_001"}
    }
])

# Query
answer = pipeline.run("How long is the NDA?")
print(answer)
```

### 2. DI FastAPI (main.py)

```bash
# Start server
uvicorn app.main:app --reload

# Query via curl
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How long is the NDA?"}'
```

### 3. Test via Demo

```bash
curl -X POST "http://localhost:8000/api/demo"
```

---

## 🎯 Architecture Advantages

1. **Modularity** - Each module has single responsibility
2. **Testability** - Components can be tested independently
3. **Maintainability** - Clear boundaries and interfaces
4. **Extensibility** - Easy to add new retrievers or ranking methods
5. **Configurability** - Centralized settings management
6. **Reusability** - Components used by both API and CLI
7. **No Duplication** - Logic exists in exactly one place
8. **Security** - API keys managed via environment variables

---

## 📝 Migration Checklist

- [x] Extract query understanding logic
- [x] Extract retrieval logic (dense + sparse)
- [x] Extract fusion and reranking logic
- [x] Extract context building logic
- [x] Extract answer generation logic
- [x] Create centralized config module
- [x] Create query_translator module
- [x] Create retriever module
- [x] Refactor rag_pipeline as orchestrator
- [x] Update main.py with API endpoints
- [x] Preserve all functionality
- [x] Add comprehensive docstrings
- [x] Add type hints
- [x] Test imports and structure
- [x] Create documentation

---

## 📚 File References

- **Configuration:** `backend/app/core/config.py`
- **Query Transform:** `backend/app/services/query_translator.py`
- **Retrieval:** `backend/app/services/retriever.py`
- **Orchestration:** `backend/app/services/rag_pipeline.py`
- **API:** `backend/app/main.py`

All functionality from the original monolithic `rag_pipeline.py` has been preserved and distributed across these modules with clear separation of concerns.
