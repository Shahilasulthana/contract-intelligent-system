"""
Centralized Configuration Module
Manages all API keys, model names, and global client/model instances.
"""

import os
from openai import OpenAI
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from chromadb.config import Settings

# =====================================================
# API & MODEL CONFIGURATION
# =====================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
MODEL_NAME_GENERATION = os.getenv("MODEL_NAME_GENERATION", "openai/gpt-4o")

DENSE_MODEL_NAME = "BAAI/bge-small-en"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# =====================================================
# API CLIENT INITIALIZATION
# =====================================================

# Initialize OpenAI/OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY
)

# =====================================================
# ML MODEL INITIALIZATION
# =====================================================

print("Loading Dense Embedding Model...")
dense_model = SentenceTransformer(DENSE_MODEL_NAME)

print("Loading Cross-Encoder Reranker...")
cross_encoder = CrossEncoder(RERANKER_MODEL_NAME)

# =====================================================
# VECTOR DATABASE INITIALIZATION
# =====================================================

print("Initializing ChromaDB...")
chroma_client = chromadb.Client(Settings(is_persistent=False))
dense_collection = chroma_client.create_collection(name="legal_clauses")
