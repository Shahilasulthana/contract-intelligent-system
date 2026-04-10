# 🚀 How to Run and Test the RAG Pipeline

## Quick Start (Choose One)

### Option 1: Run Standalone Test (Recommended for Verification)

```bash
# From project root directory
python TEST_RAG_PIPELINE.py
```

### Option 2: Run API Server

```bash
# From backend directory
cd backend
python app/run.py
```

---

## Detailed Step-by-Step Guide

### Step 1: Install Dependencies

```bash
# Navigate to backend
cd backend

# Install all required packages
pip install -r requirements.txt
```

**What gets installed:**

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - LLM client
- `sentence-transformers` - Embedding models
- `chromadb` - Vector database
- `rank-bm25` - Keyword search
- `pydantic` - Data validation

**Time:** ~5-10 minutes (first time downloads models)

---

### Step 2: Set Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
OPENAI_API_KEY=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
MODEL_NAME=openai/gpt-4o-mini
MODEL_NAME_GENERATION=openai/gpt-4o
```

Or set in terminal:

**Windows (PowerShell):**

```powershell
$env:OPENAI_API_KEY="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"
```

**Windows (CMD):**

```cmd
set OPENAI_API_KEY=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
```

**Linux/Mac:**

```bash
export OPENAI_API_KEY="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"
```

---

## Running the Tests

### Method A: STANDALONE TEST SCRIPT (Recommended)

**Best for: Verifying pipeline works without server**

```bash
# From project root
python TEST_RAG_PIPELINE.py
```

**What it does:**

1. ✅ Checks all dependencies
2. ✅ Loads all models
3. ✅ Ingests 6 sample clauses
4. ✅ Tests 3 queries end-to-end
5. ✅ Tests each retriever component
6. ✅ Shows results summary

**Expected Output:**

```
================================================================================
🚀 RAG PIPELINE TEST SCRIPT
================================================================================

[1/6] 📦 Checking dependencies...
────────────────────────────────────────────────────────────────────────────────
  ✓ openai                       - OpenAI/OpenRouter client
  ✓ sentence_transformers        - Dense embeddings
  ✓ chromadb                     - Vector database
  ✓ rank_bm25                    - Sparse retrieval (BM25)
  ✓ numpy                        - Numerical operations

✅ All dependencies available!

[2/6] 🔧 Initializing RAG Pipeline...
────────────────────────────────────────────────────────────────────────────────
  ✓ RAG Pipeline initialized
  ✓ Query Translator loaded
  ✓ Retriever components loaded

[3/6] 📄 Preparing sample contract clauses...
────────────────────────────────────────────────────────────────────────────────
  ✓ Prepared 6 sample clauses
    - nda_001       (NDA         )
    - nda_002       (NDA         )
    - nda_003       (NDA         )
    - emp_001       (Employment  )
    - emp_002       (Employment  )
    - emp_003       (Employment  )

[4/6] 💾 Ingesting clauses into pipeline...
────────────────────────────────────────────────────────────────────────────────
  ✓ All clauses ingested successfully!

[5/6] 🔍 Testing query processing...
────────────────────────────────────────────────────────────────────────────────

  Query 1: 'How long is the NDA duration?'
  ────────────────────────────────────────────────────────────────────────────
  [Understanding query...]
    - Agreement Type: NDA
    - Clause Type: Term and Termination
  [Running RAG pipeline...]
    - Answer length: 245 characters
    - Preview: The NDA lasts for 2 years after the Effective Date...

✅ RAG PIPELINE TEST PASSED!
================================================================================
```

---

### Method B: RUN API SERVER

**Best for: Testing via HTTP requests or frontend integration**

```bash
# From backend directory
cd backend
python app/run.py
```

**Server starts on:** `http://localhost:8000`

**Access:**

- Docs: `http://localhost:8000/docs` ← Interactive API explorer
- Swagger: `http://localhost:8000/swagger` ← Alternative docs

---

## Testing via API

### Test 1: Health Check

```bash
curl http://localhost:8000/
```

Response:

```json
{ "status": "ok", "service": "Legal RAG Pipeline API" }
```

---

### Test 2: Ingest Clauses

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '[
    {
      "text": "The NDA lasts for 2 years",
      "agreement_type": "NDA",
      "clause_type": "Term",
      "document_id": "doc001"
    }
  ]'
```

Response:

```json
{
  "status": "success",
  "message": "Ingested 1 clauses",
  "count": 1
}
```

---

### Test 3: Run RAG Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How long is the NDA?"}'
```

Response:

```json
{
  "query": "How long is the NDA?",
  "answer": "The NDA lasts for 2 years after the Effective Date...",
  "status": "success"
}
```

---

### Test 4: Understand Query Intent

```bash
curl -X POST http://localhost:8000/api/query/understand \
  -H "Content-Type: application/json" \
  -d '{"query": "What are confidentiality obligations?"}'
```

Response:

```json
{
  "query": "What are confidentiality obligations?",
  "intent": {
    "agreement_type": "NDA",
    "clause_type": "Confidentiality"
  },
  "status": "success"
}
```

---

### Test 5: Translate Query

```bash
curl -X POST http://localhost:8000/api/query/translate \
  -H "Content-Type: application/json" \
  -d '{"query": "How long does the agreement last?"}'
```

Response:

```json
{
  "query": "How long does the agreement last?",
  "translations": {
    "expanded": ["duration", "term", "validity period"],
    "rewritten": "What is the duration of the contract?",
    "decomposed": ["time period", "agreement"]
  },
  "status": "success"
}
```

---

## Testing with Python

### Test All Components

```python
import sys
sys.path.insert(0, 'backend')

from app.services.rag_pipeline import RAGPipeline
from app.services.query_translator import understand_query

# Initialize
pipeline = RAGPipeline()

# Prepare data
sample_clauses = [
    {
        "id": "nda_001",
        "text": "This NDA lasts for 2 years",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Term",
            "document_id": "doc_001"
        }
    }
]

# Ingest
pipeline.ingest_documents(sample_clauses)

# Query
query = "How long is the NDA?"
answer = pipeline.run(query)

print(f"Q: {query}")
print(f"A: {answer}")
```

---

## Troubleshooting

### Issue 1: "ImportError: No module named 'openai'"

**Solution:**

```bash
pip install openai
```

### Issue 2: "ImportError: No module named 'sentence_transformers'"

**Solution:**

```bash
pip install sentence-transformers
```

### Issue 3: "OPENAI_API_KEY not found"

**Solution:**

```bash
# Set environment variable
export OPENAI_API_KEY=your_api_key_here
```

### Issue 4: "Connection refused" on localhost:8000

**Solution:**

```bash
# Make sure server is running in another terminal
cd backend
python app/run.py
```

### Issue 5: Models downloading slowly

**Solution:** First run takes 5-10 minutes to download:

- `BAAI/bge-small-en` (embeddings model)
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (reranker)

Be patient! They only download once per machine.

---

## Verifying Success

✅ **Pipeline works correctly if you see:**

1. All dependencies installed without errors
2. Models loaded successfully
3. Clauses ingested without errors
4. Queries return answers with content
5. All retriever components produce results
6. No exceptions or stack traces

---

## Next Steps

After verification:

1. Test with your own contract data
2. Fine-tune query parameters (top_k, threshold)
3. Deploy to production
4. Connect frontend application
5. Monitor performance and latency

---

## Performance Metrics

**Expected timings (first run, with model downloads):**

- Dependencies install: ~5-10 minutes
- Model download: ~2-3 minutes (one-time)
- Pipeline initialization: ~2-3 seconds
- Single query: ~1-2 seconds
- Batch queries (3): ~3-5 seconds

**Expected timings (subsequent runs):**

- Pipeline initialization: ~1-2 seconds
- Single query: ~1 second
- Batch queries (3): ~2-3 seconds
