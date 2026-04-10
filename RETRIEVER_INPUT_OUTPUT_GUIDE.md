# 📊 Retriever Module - Input/Output Structure Guide

## Overview

The retriever module has **4 main components** with specific input/output structures:

1. **ClauseIndexer** - Data ingestion & indexing
2. **dense_retrieval()** - Semantic search
3. **sparse_retrieval()** - Keyword search
4. **hybrid_fusion()** - Combine results
5. **rerank()** - Refine results

---

## 1️⃣ ClauseIndexer Class

### Purpose
Manages dual indexing: dense vectors (ChromaDB) + sparse keywords (BM25)

### Input: `ingest_data(clauses)`

**Type:** `List[Dict[str, Any]]`

**Structure:**
```python
[
    {
        "id": "clause_001",                    # ← Unique identifier
        "text": "The receiving party shall...", # ← Full clause text
        "metadata": {                          # ← Optional metadata
            "agreement_type": "NDA",           # ← Agreement type (e.g., NDA, Employment)
            "clause_type": "Confidentiality",  # ← Clause type
            "document_id": "doc_001"           # ← Document reference
        }
    },
    {
        "id": "clause_002",
        "text": "In case of termination...",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        }
    }
]
```

### Output: `None`

**What it does:**
- Stores clauses in `self.sparse_corpus` (list)
- Creates dense embeddings via SentenceTransformer
- Stores dense embeddings in ChromaDB
- Builds BM25 index from tokenized text
- Prints: `"Successfully ingested X clauses."`

### Internal State After Ingestion:
```python
self.sparse_corpus = [
    {"id": "...", "text": "...", "metadata": {...}},
    {"id": "...", "text": "...", "metadata": {...}},
    ...
]

self.tokenized_corpus = [
    ["the", "receiving", "party", "shall", ...],
    ["in", "case", "of", "termination", ...],
    ...
]

self.bm25 = BM25Okapi(self.tokenized_corpus)  # ← Ready for search
```

---

## 2️⃣ dense_retrieval() Function

### Purpose
Semantic search using embedding vectors

### Inputs

**Parameter 1: `query`**
- Type: `str`
- Example: `"How long is the NDA term?"`

**Parameter 2: `filters`**
- Type: `Dict[str, Any]`
- Example: `{"agreement_type": "NDA"}`
- Optional: Can be empty `{}`
- Supports filtering by: `agreement_type`, `clause_type`, etc.

**Parameter 3: `top_k`** (optional)
- Type: `int`
- Default: `10`
- Example: `top_k=15`

### Complete Input Example:
```python
dense_retrieval(
    query="What is the confidentiality term?",
    filters={"agreement_type": "NDA"},
    top_k=10
)
```

### Output: `Dict[str, Any]`

**Structure:**
```python
{
    "clause_001": {
        "id": "clause_001",
        "text": "The receiving party shall hold and maintain...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "dense_score": 0.92  # ← Similarity score (0-1), higher is better
    },
    "clause_003": {
        "id": "clause_003",
        "text": "Confidential information includes...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "dense_score": 0.85
    },
    ...
}
```

### Output (Empty Case):
```python
{}  # ← If no results found or error occurs
```

---

## 3️⃣ sparse_retrieval() Function

### Purpose
Keyword-based search using BM25 ranking

### Inputs

**Parameter 1: `query`**
- Type: `str`
- Example: `"termination severance"`

**Parameter 2: `top_k`** (optional)
- Type: `int`
- Default: `10`

### Complete Input Example:
```python
sparse_retrieval(
    query="What happens on termination?",
    top_k=10
)
```

### Output: `Dict[str, Any]`

**Structure:**
```python
{
    "clause_004": {
        "id": "clause_004",
        "text": "In the event of termination without cause...",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        },
        "sparse_score": 0.78  # ← BM25 score (normalized to 0-1)
    },
    "clause_005": {
        "id": "clause_005",
        "text": "Employee shall receive severance...",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        },
        "sparse_score": 0.65
    }
}
```

### Output (Empty Case):
```python
{}  # ← If no indexer data or error occurs
```

---

## 4️⃣ hybrid_fusion() Function

### Purpose
Combine dense and sparse results with weighted scoring

### Inputs

**Parameter 1: `dense_res`**
- Type: `Dict[str, Any]`
- Same format as `dense_retrieval()` output
- Contains: `dense_score` field

**Parameter 2: `sparse_res`**
- Type: `Dict[str, Any]`
- Same format as `sparse_retrieval()` output
- Contains: `sparse_score` field

### Complete Input Example:
```python
# From dense_retrieval()
dense_res = {
    "clause_001": {
        "id": "clause_001",
        "text": "...",
        "metadata": {...},
        "dense_score": 0.92
    }
}

# From sparse_retrieval()
sparse_res = {
    "clause_001": {
        "id": "clause_001",
        "text": "...",
        "metadata": {...},
        "sparse_score": 0.78
    },
    "clause_004": {
        "id": "clause_004",
        "text": "...",
        "metadata": {...},
        "sparse_score": 0.65
    }
}

# Call fusion
hybrid_fusion(dense_res, sparse_res)
```

### Output: `List[Dict[str, Any]]`

**Structure:**
```python
[
    {
        "id": "clause_001",
        "text": "The receiving party shall...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "hybrid_score": 0.88  # ← Weighted score (70% dense + 30% sparse)
    },
    {
        "id": "clause_004",
        "text": "In the event of termination...",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        },
        "hybrid_score": 0.65  # ← Only sparse, no dense match
    }
]
```

**Calculation Example:**
```
For clause_001:
  dense_score = 0.92
  sparse_score = 0.78
  hybrid_score = (0.7 × 0.92) + (0.3 × 0.78)
               = 0.644 + 0.234
               = 0.878 ≈ 0.88

For clause_004 (only in sparse):
  dense_score = 0.0 (not present)
  sparse_score = 0.65
  hybrid_score = (0.7 × 0.0) + (0.3 × 0.65)
               = 0.0 + 0.195
               = 0.195
```

### Important Notes:
- ✅ **Deduplication:** Uses document IDs to merge results
- ✅ **Sorted:** Returns list sorted by `hybrid_score` (descending, highest first)
- ✅ **Union:** Includes docs from both dense AND sparse results

---

## 5️⃣ rerank() Function

### Purpose
Refine results using cross-encoder model for higher precision

### Inputs

**Parameter 1: `query`**
- Type: `str`
- Example: `"How long is the NDA term?"`

**Parameter 2: `candidates`**
- Type: `List[Dict[str, Any]]`
- From `hybrid_fusion()` output
- Must have: `text` field for each candidate

**Parameter 3: `top_k`** (optional)
- Type: `int`
- Default: `5`
- Number of results to return after reranking

**Parameter 4: `threshold`** (optional)
- Type: `float`
- Default: `-10.0`
- Minimum relevance score (below = filtered out)

### Complete Input Example:
```python
# Results from hybrid_fusion()
candidates = [
    {
        "id": "clause_001",
        "text": "The receiving party shall...",
        "metadata": {...},
        "hybrid_score": 0.88
    },
    {
        "id": "clause_004",
        "text": "In the event of termination...",
        "metadata": {...},
        "hybrid_score": 0.65
    }
]

# Call rerank
rerank(
    query="How long is the NDA term?",
    candidates=candidates,
    top_k=5,
    threshold=-10.0
)
```

### Output: `List[Dict[str, Any]]`

**Structure:**
```python
[
    {
        "id": "clause_001",
        "text": "The receiving party shall...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "hybrid_score": 0.88,
        "rerank_score": 8.5  # ← Cross-encoder score (higher = better)
    },
    {
        "id": "clause_003",
        "text": "Confidential information includes...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "hybrid_score": 0.72,
        "rerank_score": 7.2
    }
]
```

### Output (Empty Case):
```python
[]  # ← If no candidates or all filtered by threshold
```

---

## 📈 Complete Data Flow

```
INPUT: Raw Clauses
    ↓
[1] ClauseIndexer.ingest_data(clauses)
    ├─ Store in ChromaDB (dense vectors)
    └─ Build BM25 index (sparse keywords)
    ↓
[2] Query Input: "How long is the NDA?"
    ↓
    ├─ dense_retrieval()  →  {clause_id: {text, dense_score}, ...}
    │
    └─ sparse_retrieval() →  {clause_id: {text, sparse_score}, ...}
    ↓
[3] hybrid_fusion()
    Input: dense_res + sparse_res
    Output: [{id, text, metadata, hybrid_score}, ...]
    ↓
[4] rerank()
    Input: [candidates from hybrid_fusion]
    Output: [{id, text, metadata, hybrid_score, rerank_score}, ...]
    ↓
FINAL OUTPUT: Top-K refined results
```

---

## 🎯 Example Workflow

### Step 1: Ingest Documents
```python
from app.services.retriever import indexer

clauses = [
    {
        "id": "1",
        "text": "NDA term is 2 years from effective date",
        "metadata": {"agreement_type": "NDA", "clause_type": "Term", "document_id": "doc_001"}
    },
    {
        "id": "2",
        "text": "Confidential info must be held in strictest confidence",
        "metadata": {"agreement_type": "NDA", "clause_type": "Confidentiality", "document_id": "doc_001"}
    }
]

indexer.ingest_data(clauses)
# Output: "Successfully ingested 2 clauses."
```

### Step 2: Dense Retrieval
```python
from app.services.retriever import dense_retrieval

dense_results = dense_retrieval(
    query="How long is the NDA?",
    filters={"agreement_type": "NDA"},
    top_k=10
)

# Output:
# {
#     "1": {
#         "id": "1",
#         "text": "NDA term is 2 years from effective date",
#         "metadata": {...},
#         "dense_score": 0.95
#     }
# }
```

### Step 3: Sparse Retrieval
```python
from app.services.retriever import sparse_retrieval

sparse_results = sparse_retrieval(
    query="How long is the NDA?",
    top_k=10
)

# Output:
# {
#     "1": {
#         "id": "1",
#         "text": "NDA term is 2 years from effective date",
#         "metadata": {...},
#         "sparse_score": 0.82
#     },
#     "2": {
#         "id": "2",
#         "text": "Confidential info must be held in strictest confidence",
#         "metadata": {...},
#         "sparse_score": 0.50
#     }
# }
```

### Step 4: Hybrid Fusion
```python
from app.services.retriever import hybrid_fusion

fused_results = hybrid_fusion(dense_results, sparse_results)

# Output (sorted by hybrid_score):
# [
#     {
#         "id": "1",
#         "text": "NDA term is 2 years from effective date",
#         "metadata": {...},
#         "hybrid_score": 0.90  # (0.7 × 0.95) + (0.3 × 0.82)
#     },
#     {
#         "id": "2",
#         "text": "Confidential info...",
#         "metadata": {...},
#         "hybrid_score": 0.15  # (0.7 × 0.0) + (0.3 × 0.50)
#     }
# ]
```

### Step 5: Reranking
```python
from app.services.retriever import rerank

reranked_results = rerank(
    query="How long is the NDA?",
    candidates=fused_results,
    top_k=5,
    threshold=-10.0
)

# Output (sorted by rerank_score):
# [
#     {
#         "id": "1",
#         "text": "NDA term is 2 years from effective date",
#         "metadata": {...},
#         "hybrid_score": 0.90,
#         "rerank_score": 9.2  # ← Cross-encoder confirms relevance
#     }
# ]
```

---

## 📋 Quick Reference Table

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `ingest_data()` | List of clauses | None | Index clauses |
| `dense_retrieval()` | Query + filters + top_k | Dict of results | Semantic search |
| `sparse_retrieval()` | Query + top_k | Dict of results | Keyword search |
| `hybrid_fusion()` | Dense dict + sparse dict | Sorted list | Combine results |
| `rerank()` | Query + candidates list + top_k | Top-k sorted list | Refine results |

---

## 🔑 Key Concepts

**Dense Score (0-1):**
- Measures semantic similarity
- Higher = more semantically similar
- Calculated from embedding distance

**Sparse Score (0-1):**
- Measures keyword relevance
- Higher = more keyword matches
- BM25 algorithm result

**Hybrid Score (0-1):**
- Weighted combination
- 70% dense + 30% sparse
- Balances semantic and keyword relevance

**Rerank Score:**
- Cross-encoder relevance score
- Can be negative
- Threshold filter: -10.0 default

---

## ⚠️ Important Notes

1. **Metadata Filtering:** Only `agreement_type` filtering is implemented in dense search
2. **Empty Results:** Functions return empty dict/list on error or no data
3. **Score Normalization:** Sparse scores are normalized (0-1), dense scores are similarity
4. **Sorting:** Results sorted by score (highest first)
5. **Deduplication:** Handled automatically in hybrid_fusion by using doc IDs

---

This document provides complete clarity on how data flows through the retriever module!
