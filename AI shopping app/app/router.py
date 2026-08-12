"""
FastAPI Router
Defines API endpoints for the RAG application
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

# Initialize router (lightweight — no heavy imports here)
router = APIRouter(prefix="/api", tags=["rag"])

# Lazy-initialized globals (defer torch/presidio loading until first request)
_rag_pipeline = None
_pii_masker = None


def get_rag():
    """Lazy-load RAG pipeline (triggers torch + sentence-transformers on first call)"""
    global _rag_pipeline
    if _rag_pipeline is None:
        from app.rag import RAGPipeline
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


def get_pii():
    """Lazy-load PII masker (triggers presidio on first call)"""
    global _pii_masker
    if _pii_masker is None:
        from app.dbx_sql import get_pii_masker
        _pii_masker = get_pii_masker()
    return _pii_masker


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for RAG queries"""

    query: str
    n_results: int = 3
    max_length: int = 512
    temperature: float = 0.7
    conversation_context: Optional[dict] = None  # Carries state for order verification flow


class RetrieveRequest(BaseModel):
    """Request model for document retrieval"""

    query: str
    n_results: int = 3


class QueryResponse(BaseModel):
    """Response model for RAG queries"""

    response: str
    context: List[dict]
    prompt: str


# Routes
@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    """Query the RAG pipeline"""
    try:
        result = get_rag().generate_response(
            query=request.query,
            max_new_tokens=request.max_length,
            temperature=request.temperature,
        )

        return QueryResponse(
            response=result["response"],
            context=result["context"],
            prompt=result["prompt"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_rag_stream(request: QueryRequest):
    """
    Stream RAG response using Server-Sent Events (SSE).

    Handles 3 cases:
      1. Order verification: user was asked for Order ID and is providing it
      2. New order intent: user asks about their order, we ask for Order ID
      3. Normal RAG: query against policies + products knowledge base

    Event types:
      - metadata: JSON with context docs (sent first)
      - token: individual text chunks
      - done: signals end of stream (may include conversation_context)
      - error: error information
    """

    async def event_generator():
        try:
            from app.data_loader import (
                detect_order_intent,
                extract_order_id,
                lookup_order,
                format_order_for_context,
            )
            from app.config import ORDER_SYSTEM_PROMPT

            rag = get_rag()
            query = request.query
            ctx = request.conversation_context or {}

            # -----------------------------------------------------------
            # CASE 1: We were awaiting an Order ID — user should be providing it
            # -----------------------------------------------------------
            if ctx.get("awaiting_order_id"):
                order_id = extract_order_id(query)

                if not order_id:
                    # User didn't provide a valid Order ID
                    msg = (
                        "I couldn't find a valid Order ID in your message. "
                        "Please provide your Order ID — it looks like this: "
                        "`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`\n\n"
                        "You can find it in your order confirmation email."
                    )
                    yield f"event: token\ndata: {json.dumps({'text': msg})}\n\n"
                    yield f"event: done\ndata: {json.dumps({'status': 'complete', 'conversation_context': {'awaiting_order_id': True, 'original_question': ctx.get('original_question', query)}})}\n\n"
                    return

                order = lookup_order(order_id)
                if not order:
                    msg = f"I couldn't find an order with ID `{order_id}`. Please double-check your Order ID and try again."
                    yield f"event: token\ndata: {json.dumps({'text': msg})}\n\n"
                    yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"
                    return

                # Found the order — stream LLM response with order data as context
                original_question = ctx.get("original_question", query)
                order_context = format_order_for_context(order)

                metadata = {"context": [{"content": order_context, "metadata": {"source": "orders"}, "distance": 0}]}
                yield f"event: metadata\ndata: {json.dumps(metadata)}\n\n"

                for chunk in rag.generate_response_stream(
                    query=original_question,
                    max_new_tokens=max(request.max_length, 250),
                    temperature=request.temperature,
                    context_override=order_context,
                    system_prompt=ORDER_SYSTEM_PROMPT,
                ):
                    yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
                    await asyncio.sleep(0)

                yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"
                return

            # -----------------------------------------------------------
            # CASE 2: New query — check if it's about a personal order
            # -----------------------------------------------------------
            if detect_order_intent(query):
                # Check if the query already contains an Order ID
                order_id = extract_order_id(query)

                if order_id:
                    # Direct lookup — user provided the Order ID in the question
                    order = lookup_order(order_id)
                    if order:
                        order_context = format_order_for_context(order)
                        metadata = {"context": [{"content": order_context, "metadata": {"source": "orders"}, "distance": 0}]}
                        yield f"event: metadata\ndata: {json.dumps(metadata)}\n\n"

                        for chunk in rag.generate_response_stream(
                            query=query,
                            max_new_tokens=max(request.max_length, 250),
                            temperature=request.temperature,
                            context_override=order_context,
                            system_prompt=ORDER_SYSTEM_PROMPT,
                        ):
                            yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
                            await asyncio.sleep(0)

                        yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"
                        return
                    else:
                        msg = f"I couldn't find an order with ID `{order_id}`. Please double-check and try again."
                        yield f"event: token\ndata: {json.dumps({'text': msg})}\n\n"
                        yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"
                        return

                # No Order ID provided — ask for it
                msg = (
                    "I'd be happy to help you with your order! "
                    "For verification, could you please provide your **Order ID**?\n\n"
                    "It looks like this: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`\n\n"
                    "You can find it in your order confirmation email."
                )
                yield f"event: token\ndata: {json.dumps({'text': msg})}\n\n"
                yield f"event: done\ndata: {json.dumps({'status': 'complete', 'conversation_context': {'awaiting_order_id': True, 'original_question': query}})}\n\n"
                return

            # -----------------------------------------------------------
            # CASE 3: Normal RAG query (policies + products)
            # -----------------------------------------------------------
            # Retrieve enriched context and send as metadata event
            context_docs = rag.retrieve_with_enrichment(
                query=request.query, n_results=request.n_results
            )
            metadata = {"context": context_docs}
            yield f"event: metadata\ndata: {json.dumps(metadata)}\n\n"

            # Build context string for the LLM
            context = "\n\n".join([doc["content"][:500] for doc in context_docs])

            # Stream tokens from the RAG pipeline
            for chunk in rag.generate_response_stream(
                query=request.query,
                n_results=request.n_results,
                max_new_tokens=request.max_length,
                temperature=request.temperature,
                context_override=context,
            ):
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0)

            # Signal completion
            yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/retrieve")
async def retrieve_documents(request: RetrieveRequest) -> dict:
    """Retrieve documents without generation"""
    try:
        documents = get_rag().retrieve(
            query=request.query, n_results=request.n_results
        )

        return {
            "status": "success",
            "documents": documents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pii/mask")
async def mask_pii(text: str) -> dict:
    """Mask PII in text"""
    try:
        masker = get_pii()
        masked_text = masker.mask_text(text)
        detected_entities = masker.analyze_pii(text)

        return {
            "original_text": text,
            "masked_text": masked_text,
            "detected_entities": detected_entities,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pii/analyze")
async def analyze_pii(text: str) -> dict:
    """Analyze text for PII without masking"""
    try:
        detected_entities = get_pii().analyze_pii(text)

        return {
            "text": text,
            "detected_entities": detected_entities,
            "entity_count": len(detected_entities),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats() -> dict:
    """Get RAG pipeline statistics"""
    try:
        stats = get_rag().get_collection_stats()

        return {
            "status": "success",
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
