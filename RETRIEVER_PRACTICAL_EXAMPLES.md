# 🎯 Retriever Module - Practical Code Examples

## Introduction

This document shows **real, runnable code examples** for each function in the retriever module, demonstrating input/output structures.

---

## Example 1: Complete Workflow with All Functions

```python
from app.services.retriever import (
    indexer,
    dense_retrieval,
    sparse_retrieval,
    hybrid_fusion,
    rerank
)

# ═══════════════════════════════════════════════════════════════════
# STEP 1: PREPARE AND INGEST DATA
# ═══════════════════════════════════════════════════════════════════

print("=" * 60)
print("STEP 1: INGESTING CLAUSES")
print("=" * 60)

# Create sample legal clauses
sample_clauses = [
    {
        "id": "nda_001",
        "text": "The receiving party shall hold and maintain the Confidential Information in strictest confidence for the sole and exclusive benefit of the disclosing party.",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        }
    },
    {
        "id": "nda_002",
        "text": "This Non-Disclosure Agreement shall terminate 2 years after the Effective Date, unless extended by mutual written agreement.",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Term and Termination",
            "document_id": "doc_001"
        }
    },
    {
        "id": "emp_001",
        "text": "In the event of termination without cause, the Employer shall pay the Employee 3 months of severance pay.",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        }
    }
]

# Ingest data
print(f"\nIngesting {len(sample_clauses)} clauses...")
indexer.ingest_data(sample_clauses)

# Output: "Successfully ingested 3 clauses."


# ═══════════════════════════════════════════════════════════════════
# STEP 2: DENSE RETRIEVAL (SEMANTIC SEARCH)
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 2: DENSE RETRIEVAL (SEMANTIC SEARCH)")
print("=" * 60)

query = "How long does the NDA last?"
print(f"\nQuery: '{query}'")

dense_results = dense_retrieval(
    query=query,
    filters={"agreement_type": "NDA"},  # Filter by agreement type
    top_k=10
)

print(f"\nDense Results (Semantic Search):")
print(f"─" * 40)
for doc_id, result in dense_results.items():
    print(f"Doc ID: {result['id']}")
    print(f"  Text: {result['text'][:60]}...")
    print(f"  Dense Score: {result['dense_score']:.4f}")
    print(f"  Agreement Type: {result['metadata']['agreement_type']}")
    print()

# Output Example:
# Dense Results (Semantic Search):
# ────────────────────────────────────────
# Doc ID: nda_002
#   Text: This Non-Disclosure Agreement shall termin...
#   Dense Score: 0.9487
#   Agreement Type: NDA
#
# Doc ID: nda_001
#   Text: The receiving party shall hold and maintain...
#   Dense Score: 0.8123
#   Agreement Type: NDA


# ═══════════════════════════════════════════════════════════════════
# STEP 3: SPARSE RETRIEVAL (KEYWORD SEARCH)
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 3: SPARSE RETRIEVAL (KEYWORD SEARCH)")
print("=" * 60)

sparse_results = sparse_retrieval(
    query=query,
    top_k=10
)

print(f"\nSparse Results (Keyword Search):")
print(f"─" * 40)
for doc_id, result in sparse_results.items():
    print(f"Doc ID: {result['id']}")
    print(f"  Text: {result['text'][:60]}...")
    print(f"  Sparse Score: {result['sparse_score']:.4f}")
    print()

# Output Example:
# Sparse Results (Keyword Search):
# ────────────────────────────────────────
# Doc ID: nda_002
#   Text: This Non-Disclosure Agreement shall termin...
#   Sparse Score: 0.8200
#
# Doc ID: nda_001
#   Text: The receiving party shall hold and maintain...
#   Sparse Score: 0.4100


# ═══════════════════════════════════════════════════════════════════
# STEP 4: HYBRID FUSION (COMBINE RESULTS)
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 4: HYBRID FUSION (COMBINE RESULTS)")
print("=" * 60)

fused_results = hybrid_fusion(dense_results, sparse_results)

print(f"\nFused Results (Hybrid Scoring):")
print(f"─" * 40)
print(f"Formula: hybrid_score = (0.7 × dense_score) + (0.3 × sparse_score)\n")

for i, result in enumerate(fused_results, 1):
    dense_score = 0.0
    sparse_score = 0.0

    # Look up original scores (illustration)
    if result['id'] in dense_results:
        dense_score = dense_results[result['id']]['dense_score']
    if result['id'] in sparse_results:
        sparse_score = sparse_results[result['id']]['sparse_score']

    print(f"{i}. Doc ID: {result['id']}")
    print(f"   Text: {result['text'][:60]}...")
    print(f"   Dense Score: {dense_score:.4f}")
    print(f"   Sparse Score: {sparse_score:.4f}")
    print(f"   Hybrid Score: {result['hybrid_score']:.4f}")
    print(f"   Calculation: (0.7 × {dense_score:.4f}) + (0.3 × {sparse_score:.4f}) = {result['hybrid_score']:.4f}")
    print()

# Output Example:
# Fused Results (Hybrid Scoring):
# ────────────────────────────────────────
# Formula: hybrid_score = (0.7 × dense_score) + (0.3 × sparse_score)
#
# 1. Doc ID: nda_002
#    Text: This Non-Disclosure Agreement shall termin...
#    Dense Score: 0.9487
#    Sparse Score: 0.8200
#    Hybrid Score: 0.8996
#    Calculation: (0.7 × 0.9487) + (0.3 × 0.8200) = 0.8996
#
# 2. Doc ID: nda_001
#    Text: The receiving party shall hold and maintain...
#    Dense Score: 0.8123
#    Sparse Score: 0.4100
#    Hybrid Score: 0.6972
#    Calculation: (0.7 × 0.8123) + (0.3 × 0.4100) = 0.6972


# ═══════════════════════════════════════════════════════════════════
# STEP 5: RERANKING (CROSS-ENCODER REFINEMENT)
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("STEP 5: RERANKING (CROSS-ENCODER REFINEMENT)")
print("=" * 60)

reranked_results = rerank(
    query=query,
    candidates=fused_results,
    top_k=5,
    threshold=-10.0
)

print(f"\nReranked Results (Cross-Encoder Scores):")
print(f"─" * 40)
for i, result in enumerate(reranked_results, 1):
    print(f"{i}. Doc ID: {result['id']}")
    print(f"   Text: {result['text'][:60]}...")
    print(f"   Hybrid Score: {result['hybrid_score']:.4f}")
    print(f"   Rerank Score: {result['rerank_score']:.4f}")
    print(f"   Status: {'✓ KEPT' if result['rerank_score'] > -10.0 else '✗ FILTERED'}")
    print()

# Output Example:
# Reranked Results (Cross-Encoder Scores):
# ────────────────────────────────────────
# 1. Doc ID: nda_002
#    Text: This Non-Disclosure Agreement shall termin...
#    Hybrid Score: 0.8996
#    Rerank Score: 8.5324
#    Status: ✓ KEPT
#
# 2. Doc ID: nda_001
#    Text: The receiving party shall hold and maintain...
#    Hybrid Score: 0.6972
#    Rerank Score: 7.1245
#    Status: ✓ KEPT
```

---

## Example 2: Dense Retrieval Only

```python
from app.services.retriever import dense_retrieval, indexer

# Must have ingested data first
# indexer.ingest_data(clauses)

# Query with filters
print("Dense Retrieval with Filters:")
print("─" * 40)

results = dense_retrieval(
    query="confidentiality obligations",
    filters={"agreement_type": "NDA"},
    top_k=5
)

print(f"Found {len(results)} results:\n")

for doc_id, doc in results.items():
    print(f"🔍 {doc['id']}")
    print(f"   Score: {doc['dense_score']:.3f}")
    print(f"   Text: {doc['text'][:80]}...")
    print()

# Output:
# Found 2 results:
#
# 🔍 nda_001
#    Score: 0.923
#    Text: The receiving party shall hold and maintain the Confidential...
#
# 🔍 nda_002
#    Score: 0.812
#    Text: This Non-Disclosure Agreement shall terminate 2 years after...
```

---

## Example 3: Sparse Retrieval Only

```python
from app.services.retriever import sparse_retrieval, indexer

# Query keywords
print("Sparse Retrieval (Keyword Search):")
print("─" * 40)

results = sparse_retrieval(
    query="termination severance payment",
    top_k=3
)

print(f"Found {len(results)} results:\n")

for doc_id, doc in results.items():
    print(f"🔑 {doc['id']}")
    print(f"   Score: {doc['sparse_score']:.3f}")
    print(f"   Type: {doc['metadata']['clause_type']}")
    print(f"   Text: {doc['text'][:80]}...")
    print()

# Output:
# Found 2 results:
#
# 🔑 emp_001
#    Score: 0.820
#    Type: Termination
#    Text: In the event of termination without cause, the Employer...
#
# 🔑 nda_002
#    Score: 0.410
#    Type: Term and Termination
#    Text: This Non-Disclosure Agreement shall terminate 2 years...
```

---

## Example 4: Quick Fusion Example

```python
from app.services.retriever import (
    dense_retrieval,
    sparse_retrieval,
    hybrid_fusion
)

query = "payment obligations"

# Get both results
dense_res = dense_retrieval(query, {}, top_k=10)
sparse_res = sparse_retrieval(query, top_k=10)

# Fuse them
fused = hybrid_fusion(dense_res, sparse_res)

print("Hybrid Fusion Results:")
print("─" * 40)
for i, item in enumerate(fused[:3], 1):
    print(f"{i}. {item['id']} - Score: {item['hybrid_score']:.3f}")

# Output:
# Hybrid Fusion Results:
# ────────────────────────────────────────
# 1. emp_001 - Score: 0.756
# 2. nda_002 - Score: 0.614
# 3. nda_001 - Score: 0.445
```

---

## Example 5: Error Handling

```python
from app.services.retriever import dense_retrieval, sparse_retrieval

# Empty results case
print("Handling Empty Results:")
print("─" * 40)

results = dense_retrieval(
    query="nonexistent legal term xyz",
    filters={},
    top_k=10
)

if not results:
    print("No dense results found.")
    print(f"Result type: {type(results)}")
    print(f"Result value: {results}")
else:
    print(f"Found {len(results)} results")

# Output:
# No dense results found.
# Result type: <class 'dict'>
# Result value: {}
```

---

## Example 6: Filtering by Agreement Type

```python
from app.services.retriever import dense_retrieval

filters = {"agreement_type": "Employment"}

print(f"Searching only in: {filters['agreement_type']} agreements")
print("─" * 40)

results = dense_retrieval(
    query="benefits compensation",
    filters=filters,
    top_k=10
)

for doc_id, doc in results.items():
    agreement_type = doc['metadata']['agreement_type']
    print(f"✓ {doc['id']} ({agreement_type})")

# Output:
# Searching only in: Employment agreements
# ────────────────────────────────────────
# ✓ emp_001 (Employment)
```

---

## Example 7: JSON-Safe Output (for API)

```python
import json
from app.services.retriever import (
    dense_retrieval,
    sparse_retrieval,
    hybrid_fusion,
    rerank
)

query = "payment terms"

dense_res = dense_retrieval(query, {}, top_k=5)
sparse_res = sparse_retrieval(query, top_k=5)
fused = hybrid_fusion(dense_res, sparse_res)
final = rerank(query, fused, top_k=3)

# Convert to JSON (for API response)
api_response = {
    "query": query,
    "results": final,
    "count": len(final)
}

# Make JSON-serializable (remove numpy types if any)
json_output = json.dumps(api_response, indent=2, default=str)
print(json_output)

# Output:
# {
#   "query": "payment terms",
#   "results": [
#     {
#       "id": "nda_001",
#       "text": "The receiving party...",
#       "metadata": {...},
#       "hybrid_score": 0.756,
#       "rerank_score": 8.234
#     }
#   ],
#   "count": 1
# }
```

---

## Example 8: Comparison of All Scores

```python
from app.services.retriever import (
    dense_retrieval,
    sparse_retrieval,
    hybrid_fusion,
    rerank,
    indexer
)

# Assume data ingested
query = "NDA duration"

# Get all scores
dense_res = dense_retrieval(query, {}, top_k=10)
sparse_res = sparse_retrieval(query, top_k=10)
fused = hybrid_fusion(dense_res, sparse_res)
final = rerank(query, fused, top_k=5)

print("SCORE COMPARISON TABLE")
print("=" * 100)
print(f"{'Doc ID':<15} {'Dense':<10} {'Sparse':<10} {'Hybrid':<10} {'Rerank':<10}")
print("─" * 100)

for result in final:
    doc_id = result['id']
    dense_score = dense_res.get(doc_id, {}).get('dense_score', 0.0) if doc_id in dense_res else 0.0
    sparse_score = sparse_res.get(doc_id, {}).get('sparse_score', 0.0) if doc_id in sparse_res else 0.0
    hybrid = result.get('hybrid_score', 0.0)
    rerank_score = result.get('rerank_score', 0.0)

    print(f"{doc_id:<15} {dense_score:<10.4f} {sparse_score:<10.4f} {hybrid:<10.4f} {rerank_score:<10.4f}")

# Output:
# SCORE COMPARISON TABLE
# ════════════════════════════════════════════════════════════════════════════════════════════════════
# Doc ID          Dense      Sparse     Hybrid     Rerank
# ────────────────────────────────────────────────────────────────────────────────────────────────────
# nda_002         0.9487     0.8200     0.8996     8.5324
# nda_001         0.8123     0.4100     0.6972     7.1245
```

---

## Example 9: Batch Processing

```python
from app.services.retriever import rerank, dense_retrieval, sparse_retrieval, hybrid_fusion

queries = [
    "How long is the NDA?",
    "What are termination conditions?",
    "What are confidentiality obligations?"
]

print("BATCH QUERY PROCESSING")
print("=" * 60)

results_by_query = {}

for query in queries:
    print(f"\nQuery: {query}")
    print("─" * 60)

    # Run retrieval pipeline
    dense_res = dense_retrieval(query, {}, top_k=10)
    sparse_res = sparse_retrieval(query, top_k=10)
    fused = hybrid_fusion(dense_res, sparse_res)
    final = rerank(query, fused, top_k=3)

    results_by_query[query] = final

    for i, result in enumerate(final, 1):
        print(f"{i}. {result['id']} (score: {result['rerank_score']:.2f})")

print("\n" + "=" * 60)
print(f"Processed {len(queries)} queries")
```

---

## Example 10: Custom Thresholds

```python
from app.services.retriever import rerank, hybrid_fusion, dense_retrieval, sparse_retrieval

query = "payment terms"

dense_res = dense_retrieval(query, {}, top_k=10)
sparse_res = sparse_retrieval(query, top_k=10)
fused = hybrid_fusion(dense_res, sparse_res)

# Strict threshold (filter low-confidence results)
strict_results = rerank(query, fused, top_k=5, threshold=5.0)

# Lenient threshold (keep more results)
lenient_results = rerank(query, fused, top_k=5, threshold=-20.0)

print(f"Strict threshold (> 5.0): {len(strict_results)} results")
print(f"Lenient threshold (> -20.0): {len(lenient_results)} results")

# Output:
# Strict threshold (> 5.0): 2 results
# Lenient threshold (> -20.0): 5 results
```

---

## Quick Reference for Common Patterns

### Pattern 1: Simple Query

```python
from app.services.retriever import dense_retrieval

results = dense_retrieval("your query", {}, top_k=10)
```

### Pattern 2: Filtered Query

```python
from app.services.retriever import dense_retrieval

results = dense_retrieval(
    "your query",
    {"agreement_type": "NDA"},
    top_k=10
)
```

### Pattern 3: Full Pipeline

```python
from app.services.retriever import *

dense = dense_retrieval(q, {}, 10)
sparse = sparse_retrieval(q, 10)
hybrid = hybrid_fusion(dense, sparse)
final = rerank(q, hybrid, 5)
```

### Pattern 4: Check Results

```python
results = dense_retrieval("query", {}, 10)

if results:
    for doc_id, doc in results.items():
        print(f"{doc['id']}: {doc['dense_score']:.3f}")
else:
    print("No results found")
```

---

These examples show all the different ways to use the retriever module!
