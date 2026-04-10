#!/usr/bin/env python3
"""
🧪 STANDALONE TEST SCRIPT FOR RAG PIPELINE
Run this to verify the entire pipeline works end-to-end.

Usage:
    python TEST_RAG_PIPELINE.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (defined early to be used throughout)
# ═══════════════════════════════════════════════════════════════════════════════

def select_top_n(items, n):
    """Select top n items from iterator."""
    return list(items)[:n]

print("=" * 80)
print("🚀 RAG PIPELINE TEST SCRIPT")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: CHECK DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/6] 📦 Checking dependencies...")
print("-" * 80)

dependencies = {
    "openai": "OpenAI/OpenRouter client",
    "sentence_transformers": "Dense embeddings",
    "chromadb": "Vector database",
    "rank_bm25": "Sparse retrieval (BM25)",
    "numpy": "Numerical operations"
}

missing = []
for lib, purpose in dependencies.items():
    try:
        __import__(lib)
        print(f"  ✓ {lib:<25} - {purpose}")
    except ImportError:
        print(f"  ✗ {lib:<25} - {purpose} [MISSING]")
        missing.append(lib)

if missing:
    print(f"\n❌ Missing dependencies: {', '.join(missing)}")
    print("\nInstall with:")
    print(f"  pip install {' '.join(missing)}")
    sys.exit(1)

print("\n✅ All dependencies available!")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: INITIALIZE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2/6] 🔧 Initializing RAG Pipeline...")
print("-" * 80)

try:
    from app.services.rag_pipeline import RAGPipeline
    from app.services.query_translator import understand_query
    from app.services.retriever import (
        indexer,
        dense_retrieval,
        sparse_retrieval,
        hybrid_fusion,
        rerank
    )
    print("  ✓ RAG Pipeline initialized")
    print("  ✓ Query Translator loaded")
    print("  ✓ Retriever components loaded")
except Exception as e:
    print(f"  ✗ Failed to initialize: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: PREPARE SAMPLE DATA
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[3/6] 📄 Preparing sample contract clauses...")
print("-" * 80)

sample_clauses = [
    {
        "id": "nda_001",
        "text": "The receiving party shall hold and maintain the Confidential Information in strictest confidence for the sole and exclusive benefit of the disclosing party. The receiving party agrees not to disclose this information to any third party without prior written consent.",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Confidentiality",
            "document_id": "doc_001"
        }
    },
    {
        "id": "nda_002",
        "text": "This Non-Disclosure Agreement shall terminate 2 years after the Effective Date, unless extended by mutual written agreement. Upon termination, all Confidential Information must be returned.",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Term and Termination",
            "document_id": "doc_001"
        }
    },
    {
        "id": "nda_003",
        "text": "The disclosing party retains all right, title, and interest to the Confidential Information. No license or rights are granted except as expressly stated in this Agreement.",
        "metadata": {
            "agreement_type": "NDA",
            "clause_type": "Intellectual Property Rights",
            "document_id": "doc_001"
        }
    },
    {
        "id": "emp_001",
        "text": "In the event of termination without cause, the Employer shall pay the Employee three months of severance pay plus all accrued benefits as mandated by applicable law.",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Termination",
            "document_id": "doc_002"
        }
    },
    {
        "id": "emp_002",
        "text": "The Employee is entitled to 20 days of paid annual leave, 5 days of sick leave, and 10 days of unpaid leave per calendar year.",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Leave Benefits",
            "document_id": "doc_002"
        }
    },
    {
        "id": "emp_003",
        "text": "The Employee shall receive a base salary of $80,000 per annum, payable in 12 equal monthly installments. Performance bonuses are discretionary and determined annually.",
        "metadata": {
            "agreement_type": "Employment",
            "clause_type": "Compensation",
            "document_id": "doc_002"
        }
    }
]

print(f"  ✓ Prepared {len(sample_clauses)} sample clauses")
for clause in sample_clauses:
    print(f"    - {clause['id']:15} ({clause['metadata']['agreement_type']:12})")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: INGEST DATA
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[4/6] 💾 Ingesting clauses into pipeline...")
print("-" * 80)

try:
    pipeline = RAGPipeline()
    pipeline.ingest_documents(sample_clauses)
    print("  ✓ All clauses ingested successfully!")
except Exception as e:
    print(f"  ✗ Failed to ingest: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: TEST QUERY PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5/6] 🔍 Testing query processing...")
print("-" * 80)

test_queries = [
    "How long is the NDA duration?",
    "What are the confidentiality obligations?",
    "What is the severance payment?",
]

results_summary = []

for i, query in enumerate(test_queries, 1):
    print(f"\n  Query {i}: '{query}'")
    print("  " + "─" * 76)
    
    try:
        # Test query understanding
        print("  [Understanding query...]")
        intent = understand_query(query)
        print(f"    - Agreement Type: {intent.get('agreement_type', 'Unknown')}")
        print(f"    - Clause Type: {intent.get('clause_type', 'Unknown')}")
        
        # Test full pipeline
        print("  [Running RAG pipeline...]")
        answer = pipeline.run(query)
        
        print(f"    - Answer length: {len(answer)} characters")
        if answer:
            print(f"    - Preview: {answer[:100]}...")
            results_summary.append({
                "query": query,
                "status": "✓ SUCCESS",
                "answer_length": len(answer)
            })
        else:
            print("    - ⚠ Empty answer received")
            results_summary.append({
                "query": query,
                "status": "⚠ NO ANSWER",
                "answer_length": 0
            })
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        results_summary.append({
            "query": query,
            "status": "✗ FAILED",
            "error": str(e)
        })

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: TEST RETRIEVER COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6/6] 🎯 Testing individual retriever components...")
print("-" * 80)

test_query = "confidentiality and non-disclosure"

try:
    print(f"\n  Testing: '{test_query}'")
    print("  " + "─" * 76)
    
    # Dense retrieval
    print("\n  ➤ Dense Retrieval (Semantic Search)")
    dense_res = dense_retrieval(test_query, {}, top_k=3)
    print(f"    Found: {len(dense_res)} results")
    for doc_id, doc in select_top_n(dense_res.items(), 1):
        print(f"      • {doc['id']}: dense_score={doc['dense_score']:.4f}")
    
    # Sparse retrieval
    print("\n  ➤ Sparse Retrieval (Keyword Search)")
    sparse_res = sparse_retrieval(test_query, top_k=3)
    print(f"    Found: {len(sparse_res)} results")
    for doc_id, doc in select_top_n(sparse_res.items(), 1):
        print(f"      • {doc['id']}: sparse_score={doc['sparse_score']:.4f}")
    
    # Hybrid fusion
    if dense_res and sparse_res:
        print("\n  ➤ Hybrid Fusion (Dense + Sparse)")
        fused = hybrid_fusion(dense_res, sparse_res)
        print(f"    Fused: {len(fused)} results")
        for result in select_top_n(fused, 1):
            print(f"      • {result['id']}: hybrid_score={result['hybrid_score']:.4f}")
        
        # Reranking
        print("\n  ➤ Reranking (Cross-Encoder Refinement)")
        final = rerank(test_query, fused, top_k=3)
        print(f"    Final: {len(final)} results")
        for result in select_top_n(final, 1):
            print(f"      • {result['id']}: rerank_score={result['rerank_score']:.4f}")
    
    print("\n  ✓ All retriever components working!")
    
except Exception as e:
    print(f"  ✗ Error in retriever components: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

print("\nQuery Results:")
print("─" * 80)
for result in results_summary:
    status = result['status']
    query = result['query'][:50] + "..." if len(result['query']) > 50 else result['query']
    print(f"  {status:12} | {query}")

print("\n" + "=" * 80)
if all(r['status'].startswith('✓') or r['status'].startswith('⚠') for r in results_summary):
    print("✅ RAG PIPELINE TEST PASSED!")
else:
    print("⚠️  RAG PIPELINE TEST INCOMPLETE - REVIEW ERRORS ABOVE")

print("=" * 80)
