# 📊 Retriever Module - Visual Input/Output Map

## 🎯 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETRIEVER MODULE                             │
└─────────────────────────────────────────────────────────────────┘

                          INPUT: Query
                             ↓
        ┌────────────────────┴────────────────────┐
        ↓                                         ↓
  ┌─────────────────┐                   ┌─────────────────┐
  │ dense_retrieval │                   │sparse_retrieval │
  │  (Embeddings)   │                   │  (Keywords)     │
  └─────────────────┘                   └─────────────────┘
        ↓                                         ↓
    Dict Results                           Dict Results
        ├─ dense_score                       ├─ sparse_score
        ├─ text                              ├─ text
        └─ metadata                          └─ metadata

        └────────────────────┬────────────────────┘
                             ↓
                  ┌──────────────────────┐
                  │  hybrid_fusion()     │
                  │  (70% + 30% blend)   │
                  └──────────────────────┘
                             ↓
                      List Results
                   [sorted by hybrid_score]
                             ↓
                  ┌──────────────────────┐
                  │   rerank()           │
                  │ (Cross-encoder)      │
                  └──────────────────────┘
                             ↓
                      List Results
                    [sorted by rerank_score]
                             ↓
                      OUTPUT: Top-K Results
```

---

## 📥 INPUT STRUCTURES

### 1. ClauseIndexer.ingest_data()

```
INPUT EXAMPLE:
═════════════════════════════════════════════════════════════

    [
        {
            "id": "clause_001",
            ├─ "text": "The receiving party shall hold...",
            └─ "metadata": {
                 ├─ "agreement_type": "NDA",
                 ├─ "clause_type": "Confidentiality",
                 └─ "document_id": "doc_001"
               }
        },
        {
            "id": "clause_002",
            ├─ "text": "Employer shall provide severance...",
            └─ "metadata": {
                 ├─ "agreement_type": "Employment",
                 ├─ "clause_type": "Termination",
                 └─ "document_id": "doc_002"
               }
        }
    ]

REQUIRED FIELDS:
✅ id          (string: unique identifier)
✅ text        (string: full clause text)
✅ metadata    (object with agreement_type, clause_type, document_id)

INTERNAL STATE AFTER INGEST:
════════════════════════════════════════════════════════════
indexer.sparse_corpus:
    [clause_001, clause_002, ...]

indexer.tokenized_corpus:
    [["the", "receiving", "party", ...], ...]

indexer.bm25: BM25Okapi(tokenized_corpus)

ChromaDB collection:
    - Stored embeddings for each clause
    - Stored text and metadata
```

---

### 2. dense_retrieval()

```
INPUTS:
═════════════════════════════════════════════════════════════

    query: "How long is the NDA term?"
    filters: {"agreement_type": "NDA"}
    top_k: 10

BREAKDOWN:
┌─────────────────────┐
│ query (str)         │ → Required
│ "How long is the    │
│  NDA term?"         │
└─────────────────────┘

┌─────────────────────┐
│ filters (dict)      │ → Optional
│ {                   │
│   "agreement_type": │
│   "NDA"             │
│ }                   │
└─────────────────────┘
  or {} (empty dict)

┌─────────────────────┐
│ top_k (int)         │ → Default: 10
│ 15                  │   Range: 1-∞
└─────────────────────┘

PROCESSING:
    query
      ↓
    encode to vector (using SentenceTransformer)
      ↓
    search ChromaDB collection
      ↓
    apply filters (if provided)
      ↓
    return top_k results
```

---

### 3. sparse_retrieval()

```
INPUTS:
═════════════════════════════════════════════════════════════

    query: "termination severance"
    top_k: 10

BREAKDOWN:
┌─────────────────────┐
│ query (str)         │ → Required
│ "termination        │
│  severance"         │
└─────────────────────┘

┌─────────────────────┐
│ top_k (int)         │ → Default: 10
│ 15                  │   Range: 1-∞
└─────────────────────┘

PROCESSING:
    query
      ↓
    tokenize to ["termination", "severance"]
      ↓
    compute BM25 scores for each clause
      ↓
    select top_k indices
      ↓
    return results
```

---

### 4. hybrid_fusion()

```
INPUTS:
═════════════════════════════════════════════════════════════

    dense_res: {...}
    ├─ "clause_001": {
    │      "id": "clause_001",
    │      "text": "...",
    │      "metadata": {...},
    │      "dense_score": 0.92
    │  }
    └─ ...

    sparse_res: {...}
    ├─ "clause_001": {
    │      "id": "clause_001",
    │      "text": "...",
    │      "metadata": {...},
    │      "sparse_score": 0.78
    │  }
    ├─ "clause_004": {
    │      "id": "clause_004",
    │      "text": "...",
    │      "metadata": {...},
    │      "sparse_score": 0.65
    │  }
    └─ ...

PROCESSING:
    Find all unique document IDs
      ↓
    For each unique ID:
    ├─ Get dense_score (default 0.0)
    ├─ Get sparse_score (default 0.0)
    ├─ Calculate: hybrid = (0.7 × dense) + (0.3 × sparse)
    └─ Create combined entry
      ↓
    Sort by hybrid_score (descending)
      ↓
    Return as list
```

---

### 5. rerank()

```
INPUTS:
═════════════════════════════════════════════════════════════

    query: "How long is the NDA term?"

    candidates: [
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

    top_k: 5
    threshold: -10.0

BREAKDOWN:
┌──────────────────────┐
│ query (str)          │ → Required
│ "How long is the     │
│  NDA term?"          │
└──────────────────────┘

┌──────────────────────┐
│ candidates (list)    │ → Required
│ List of dicts with   │
│ 'text' field         │
└──────────────────────┘

┌──────────────────────┐
│ top_k (int)          │ → Default: 5
│ 5                    │   Return limit
└──────────────────────┘

┌──────────────────────┐
│ threshold (float)    │ → Default: -10.0
│ -10.0                │   Minimum score
└──────────────────────┘

PROCESSING:
    Create pairs: [query, text] for each candidate
      ↓
    Use cross-encoder to score each pair
      ↓
    Attach rerank_score to each candidate
      ↓
    Filter: keep only score > threshold
      ↓
    Sort by rerank_score (descending)
      ↓
    Return top_k results
```

---

## 📤 OUTPUT STRUCTURES

### 1. dense_retrieval() Output

```
RETURN TYPE: Dict[str, Any]

STRUCTURE:
{
    "clause_001": {                    ← Key: document ID
        "id": "clause_001",            ← Document identifier
        "text": "The receiving party shall hold and maintain...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "dense_score": 0.92            ← Similarity score (0-1)
    },
    "clause_003": {
        "id": "clause_003",
        "text": "Confidential information includes...",
        "metadata": {...},
        "dense_score": 0.85
    }
}

EMPTY CASE:
{}

KEY FIELDS:
✅ dense_score    (float: 0.0 to 1.0, higher = better)
✅ text           (str: full clause text)
✅ metadata       (dict: agreement/clause info)
```

---

### 2. sparse_retrieval() Output

```
RETURN TYPE: Dict[str, Any]

STRUCTURE:
{
    "clause_004": {
        "id": "clause_004",
        "text": "In the event of termination without cause...",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        },
        "sparse_score": 0.78           ← BM25 score (normalized)
    },
    "clause_005": {
        "id": "clause_005",
        "text": "Employee shall receive severance...",
        "metadata": {...},
        "sparse_score": 0.65
    }
}

EMPTY CASE:
{}

KEY FIELDS:
✅ sparse_score   (float: 0.0 to 1.0, higher = better)
```

---

### 3. hybrid_fusion() Output

```
RETURN TYPE: List[Dict[str, Any]]

STRUCTURE:
[
    {
        "id": "clause_001",
        "text": "The receiving party shall...",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        },
        "hybrid_score": 0.88           ← Combined score ((0.7×dense)+(0.3×sparse))
    },
    {
        "id": "clause_004",
        "text": "In the event of termination...",
        "metadata": {...},
        "hybrid_score": 0.65
    },
    {
        "id": "clause_003",
        "text": "Confidential information includes...",
        "metadata": {...},
        "hybrid_score": 0.52
    }
]

SORTED BY: hybrid_score (descending, highest first)

EMPTY CASE:
[]

KEY FIELDS:
✅ hybrid_score   (float: 0.0 to 1.0)
                  Calculation: (0.7 × dense_score) + (0.3 × sparse_score)
```

---

### 4. rerank() Output

```
RETURN TYPE: List[Dict[str, Any]]

STRUCTURE:
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
        "rerank_score": 9.2            ← Cross-encoder score
    },
    {
        "id": "clause_003",
        "text": "Confidential information includes...",
        "metadata": {...},
        "hybrid_score": 0.72,
        "rerank_score": 8.1
    }
]

SORTED BY: rerank_score (descending)

LIMITED TO: top_k results (default: 5)

FILTERED BY: threshold (default: -10.0)
  - Only included if rerank_score > threshold

EMPTY CASE:
[]  ← If no candidates pass threshold

KEY FIELDS:
✅ rerank_score   (float: can be negative)
                  Cross-encoder relevance score
                  Higher = more relevant
```

---

## 🔄 Complete Example Output Chain

```
STEP 1: ingest_data()
    Input:  2 clauses
    Output: (None, but state updated)

STEP 2: dense_retrieval()
    Input:  query="How long is NDA?"
    Output:
    {
        "clause_001": {"id": "...", "text": "...", "dense_score": 0.95}
    }

STEP 3: sparse_retrieval()
    Input:  query="How long is NDA?"
    Output:
    {
        "clause_001": {"id": "...", "text": "...", "sparse_score": 0.82},
        "clause_002": {"id": "...", "text": "...", "sparse_score": 0.50}
    }

STEP 4: hybrid_fusion()
    Input:  dense_res + sparse_res (above)
    Output:
    [
        {"id": "clause_001", "text": "...", "hybrid_score": 0.90},
        {"id": "clause_002", "text": "...", "hybrid_score": 0.15}
    ]

STEP 5: rerank()
    Input:  query + candidates (from hybrid_fusion)
    Output:
    [
        {"id": "clause_001", "text": "...", "hybrid_score": 0.90, "rerank_score": 9.2}
    ]

FINAL: Top-K refined results ready for LLM
```

---

## 💾 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ INGEST PHASE                                                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Raw Clauses                                                     │
│      │                                                           │
│      ├──→ ClauseIndexer.ingest_data()                           │
│          │                                                       │
│          ├──→ ChromaDB (Dense Embeddings)                       │
│          │    └─ Store embeddings + text + metadata             │
│          │                                                       │
│          └──→ BM25 Index (Sparse Keywords)                      │
│               └─ Store tokenized terms + scores                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ RETRIEVAL PHASE                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Query                                                           │
│      │                                                           │
│      ├──→ dense_retrieval()                                      │
│      │    └─ Output: Dict {id: {dense_score, ...}}              │
│      │                                                           │
│      └──→ sparse_retrieval()                                     │
│           └─ Output: Dict {id: {sparse_score, ...}}             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ FUSION PHASE                                                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  dense_results + sparse_results                                 │
│      │                                                           │
│      └──→ hybrid_fusion()                                        │
│           └─ Output: List [id: {hybrid_score, ...}]             │
│                    (sorted by hybrid_score)                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ RERANKING PHASE                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Query + Candidates                                              │
│      │                                                           │
│      └──→ rerank()                                               │
│           └─ Output: List [id: {rerank_score, ...}]             │
│                    (sorted by rerank_score, top_k)               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

                            ↓
                      FINAL RESULTS
                   (Ready for LLM input)
```

---

## 📊 Score Comparison

| Score Type       | Range     | Source                   | Meaning              |
| ---------------- | --------- | ------------------------ | -------------------- |
| **dense_score**  | 0.0 - 1.0 | Embeddings               | Semantic similarity  |
| **sparse_score** | 0.0 - 1.0 | BM25 algorithm           | Keyword relevance    |
| **hybrid_score** | 0.0 - 1.0 | (0.7×dense + 0.3×sparse) | Combined relevance   |
| **rerank_score** | - ∞ to +∞ | Cross-encoder            | Contextual relevance |

---

This visual guide clarifies all input/output relationships in the retriever module!
