"""
Main FastAPI Application
Serves the RAG API endpoints
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.router import router, get_rag

# Load environment variables
load_dotenv()

# Track whether knowledge base is loaded
_kb_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: auto-load all data into the knowledge base."""
    global _kb_loaded
    try:
        from app.data_loader import auto_load_knowledge_base
        rag = get_rag()
        auto_load_knowledge_base(rag)
        _kb_loaded = True
        print("Knowledge base auto-loaded successfully!")
    except Exception as e:
        print(f"WARNING: Failed to auto-load knowledge base: {e}")
        import traceback
        traceback.print_exc()
    yield


# Create FastAPI app
app = FastAPI(
    title="ShopAssist AI - RAG Application",
    description="Retrieval-Augmented Generation system for retail Q&A",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: restrict to known origins only
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://shopassistai-web.azurewebsites.net",
    "https://shopassist-api.azurewebsites.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ShopAssist AI",
        "version": "1.0.0",
        "description": "RAG-based Q&A system for retail data",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "RAG API is running",
        "knowledge_base_loaded": _kb_loaded,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
