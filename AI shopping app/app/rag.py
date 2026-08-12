"""
RAG (Retrieval-Augmented Generation) Pipeline
Handles document ingestion, retrieval, and generation
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from app.hf_client import get_hf_client

# Load environment variables
load_dotenv()


class RAGPipeline:
    """RAG Pipeline for retrieval and generation"""

    def __init__(self, collection_name: str = "retail_knowledge_base"):
        """
        Initialize RAG pipeline

        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.hf_client = get_hf_client()
        self.collection_name = collection_name

        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        self.collection = None
        self._init_collection()

    def _init_collection(self):
        """Initialize or get ChromaDB collection"""
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.collection_name
            )
            print(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            print(f"Created new collection: {self.collection_name}")

    def ingest_documents(
        self, documents: List[str], metadata: Optional[List[Dict]] = None,
        id_prefix: str = "doc"
    ) -> None:
        """
        Ingest documents into the knowledge base

        Args:
            documents: List of document texts
            metadata: Optional list of metadata dictionaries
            id_prefix: Prefix for document IDs (avoids collisions between sources)
        """
        print(f"Ingesting {len(documents)} documents...")

        # Generate embeddings
        embeddings = self.hf_client.embed_documents(documents)

        # Prepare data for ChromaDB (use prefix to avoid ID collisions)
        ids = [f"{id_prefix}_{i}" for i in range(len(documents))]
        if metadata is None:
            metadata = [{} for _ in documents]

        # Add to collection
        self.collection.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadata
        )

        print(f"Successfully ingested {len(documents)} documents")

    def ingest_documents_batched(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: int = 500,
        id_prefix: str = "doc",
    ) -> None:
        """
        Ingest documents in batches to limit peak memory usage.
        Essential for 8GB RAM machines.

        Args:
            documents: List of document texts
            metadata: Optional list of metadata dictionaries
            batch_size: Number of documents per batch
            id_prefix: Prefix for document IDs
        """
        total = len(documents)
        if metadata is None:
            metadata = [{} for _ in documents]

        for i in range(0, total, batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadata[i:i + batch_size]
            batch_embeddings = self.hf_client.embed_documents(batch_docs)
            batch_ids = [f"{id_prefix}_{i + j}" for j in range(len(batch_docs))]

            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_docs,
                metadatas=batch_meta,
            )
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            print(f"    Batch {batch_num}/{total_batches}: {len(batch_docs)} docs ingested")

    def retrieve(
        self, query: str, n_results: int = 3
    ) -> List[Dict[str, str]]:
        """
        Retrieve relevant documents for a query

        Args:
            query: Query text
            n_results: Number of documents to retrieve

        Returns:
            List of retrieved documents with metadata
        """
        results = self.collection.query(
            query_texts=[query], n_results=n_results
        )

        retrieved_docs = []
        if results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                retrieved_docs.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"]
                        else {},
                        "distance": results["distances"][0][i]
                        if results["distances"]
                        else None,
                    }
                )

        return retrieved_docs

    def generate_response(
        self,
        query: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
    ) -> Dict[str, str]:
        """
        Generate response using RAG

        Args:
            query: User query
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature

        Returns:
            Dictionary with response and context
        """
        # Retrieve relevant documents
        context_docs = self.retrieve(query, n_results=3)

        # Build context string - limit context length
        context = "\n\n".join([doc["content"][:500] for doc in context_docs])

        # Create optimized prompt for faster response
        prompt = f"""Context: {context}

Question: {query}

Provide a brief, direct answer:"""

        # Generate response with limited tokens for speed
        response = self.hf_client.generate_text(
            prompt, max_new_tokens=max_new_tokens, temperature=temperature
        )

        return {
            "response": response,
            "context": context_docs,
            "prompt": prompt,
        }

    def retrieve_with_enrichment(
        self, query: str, n_results: int = 3
    ) -> List[Dict]:
        """
        Retrieve docs and enrich product results with full DataFrame data.
        For product matches, looks up the full row to provide richer context.
        """
        results = self.retrieve(query, n_results=n_results)
        enriched = []

        for doc in results:
            meta = doc.get("metadata", {})
            if meta.get("source") == "products" and meta.get("uniq_id"):
                # Try to enrich with full product data
                try:
                    from app.data_loader import lookup_product
                    full_product = lookup_product(meta["uniq_id"])
                    if full_product:
                        # Build richer context from full product data
                        name = str(full_product.get("product_name", ""))
                        price = str(full_product.get("price", ""))
                        category = str(full_product.get("amazon_category_and_sub_category", ""))
                        rating = str(full_product.get("average_review_rating", ""))
                        stock = str(full_product.get("number_available_in_stock", ""))
                        desc = str(full_product.get("description", ""))[:300]
                        doc["content"] = (
                            f"Product: {name}\nPrice: {price}\nCategory: {category}\n"
                            f"Rating: {rating}\nStock: {stock}\nDescription: {desc}"
                        )
                except Exception:
                    pass  # Fall back to original content
            enriched.append(doc)

        return enriched

    def generate_response_stream(
        self,
        query: str,
        n_results: int = 3,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        context_override: str = None,
        system_prompt: str = None,
    ):
        """
        Stream RAG response token by token.

        Args:
            query: User query
            n_results: Number of documents to retrieve
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
            context_override: Pre-built context string (skips retrieval if provided)
            system_prompt: Optional custom system prompt

        Yields:
            Text chunks as they are generated
        """
        if context_override:
            context = context_override
        else:
            # Retrieve and enrich relevant documents
            context_docs = self.retrieve_with_enrichment(query, n_results=n_results)
            context = "\n\n".join([doc["content"][:500] for doc in context_docs])

        # Create optimized prompt for faster response
        prompt = f"""Context: {context}

Question: {query}

Provide a helpful, accurate answer based on the context above:"""

        # Stream response token by token
        for chunk in self.hf_client.generate_text_stream(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
        ):
            yield chunk

    def clear_collection(self) -> None:
        """Clear all documents from the collection"""
        self.chroma_client.delete_collection(name=self.collection_name)
        self._init_collection()
        print(f"Collection {self.collection_name} cleared")

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
        }
