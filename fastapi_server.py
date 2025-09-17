#!/usr/bin/env python3
"""
FastAPI Server for Semantic Search and Chatbot
Replaces the process spawning approach with a proper web server
"""

import sys
import json
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import Config
from vector_store import VectorStore
from chatbot import Chatbot

# FastAPI app instance
app = FastAPI(title="Semantic Search API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vector_store = None
chatbot = None

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    userId: Optional[str] = None
    accessLevel: Optional[str] = None

class ChatbotRequest(BaseModel):
    query: str
    userId: Optional[str] = None
    accessLevel: Optional[str] = None

class ProcessRequest(BaseModel):
    files: List[str] = []

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]

class ChatbotResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]

class ProcessResponse(BaseModel):
    success: bool
    message: str
    chunks_count: Optional[int] = None

def initialize_backend():
    """Initialize the vector store and chatbot"""
    global vector_store, chatbot
    try:
        vector_store = VectorStore()
        chatbot = Chatbot(vector_store)
        logger.info("Backend initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        return False

def get_accessible_documents(userId: Optional[str], accessLevel: Optional[str] = None):
    """Get list of accessible documents for user"""
    try:
        # This would typically query your database
        # For now, we'll return all documents if no access level specified
        if not accessLevel or accessLevel == 'all':
            return None  # Return None to search all documents
        
        logger.info(f"Getting accessible documents for user {userId} with access level {accessLevel}")
        
        # For now, return all documents since we don't have proper access control implemented
        # This should be replaced with actual database query
        from pathlib import Path
        data_dir = Path(__file__).parent / "data"
        accessible_docs = [f.name for f in data_dir.glob('*.pdf')]
        
        logger.info(f"Returning {len(accessible_docs)} accessible documents")
        
        return accessible_docs
        
    except Exception as e:
        logger.error(f"Error getting accessible documents: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    """Initialize backend on startup"""
    logger.info("Starting FastAPI server...")
    initialize_backend()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Semantic Search API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "vector_store_available": vector_store is not None,
        "chatbot_available": chatbot is not None,
        "timestamp": time.time()
    }

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Handle search requests with performance monitoring"""
    start_time = time.time()
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="No query provided")
        
        if not vector_store:
            raise HTTPException(status_code=503, detail="Search service not available")
        
        # Get accessible documents for user
        accessible_docs = get_accessible_documents(request.userId, request.accessLevel)
        
        # Perform search
        results = vector_store.hybrid_search(request.query, accessible_docs)
        
        response_time = time.time() - start_time
        logger.info(f"Search completed in {response_time:.2f}s for query: '{request.query}'")
        
        return SearchResponse(results=results)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_query(request: ChatbotRequest):
    """Handle chatbot requests with performance monitoring"""
    start_time = time.time()
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="No query provided")
        
        if not chatbot:
            raise HTTPException(status_code=503, detail="Chatbot service not available")
        
        # Get accessible documents for user
        accessible_docs = get_accessible_documents(request.userId, request.accessLevel)
        
        # Generate response
        response, sources = chatbot.generate_response(request.query, accessible_docs)
        
        response_time = time.time() - start_time
        logger.info(f"Chatbot response generated in {response_time:.2f}s for query: '{request.query}'")
        
        return ChatbotResponse(response=response, sources=sources)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process", response_model=ProcessResponse)
async def process_documents(request: ProcessRequest):
    """Handle document processing requests"""
    try:
        files = request.files
        logger.info(f"Processing request received for files: {files}")
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Check if files exist in data directory
        from pathlib import Path
        data_dir = Path(__file__).parent / "data"
        logger.info(f"Data directory: {data_dir}")
        logger.info(f"Files in data directory: {list(data_dir.glob('*.pdf'))}")
        
        from pdf_processor import PDFProcessor
        processor = PDFProcessor()
        chunks = processor.process_pdfs()
        
        logger.info(f"Processed {len(chunks)} chunks")
        
        if chunks and vector_store:
            vector_store.create_index(chunks)
            return ProcessResponse(
                success=True,
                message=f"Successfully processed {len(chunks)} document chunks",
                chunks_count=len(chunks)
            )
        elif chunks:
            return ProcessResponse(
                success=True,
                message=f"Successfully processed {len(chunks)} document chunks (vector store not available)",
                chunks_count=len(chunks)
            )
        else:
            return ProcessResponse(
                success=False,
                message="No documents found to process"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

