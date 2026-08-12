"""
Model Client
Handles LLM inference via Groq API and local embeddings via SentenceTransformers.
"""

import os
import requests
from typing import Optional, Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HFModelClient:
    """Client for LLM generation (Groq API) and embeddings (local SentenceTransformer)"""

    def __init__(self):
        """Initialize the client"""
        # Groq API config
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm_model_id = os.getenv("LLM_MODEL_ID", "llama-3.3-70b-versatile")
        self.groq_base_url = "https://api.groq.com/openai/v1/chat/completions"

        # Embeddings config (stays local — lightweight ~90MB model)
        self.embeddings_model_id = os.getenv(
            "EMBEDDINGS_MODEL_ID", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._embeddings_model = None
        self._device = "cpu"

        if not self.groq_api_key:
            print("WARNING: GROQ_API_KEY not set. LLM generation will fail.")

    @property
    def embeddings_model(self):
        """Lazy load embeddings model (deferred import to avoid loading torch at startup)"""
        if self._embeddings_model is None:
            from sentence_transformers import SentenceTransformer
            print(f"Loading embeddings model: {self.embeddings_model_id}...")
            self._embeddings_model = SentenceTransformer(
                self.embeddings_model_id, device=self._device
            )
            print(f"Embeddings model loaded successfully on {self._device}")
        return self._embeddings_model

    def generate_text(
        self,
        prompt: str,
        max_new_tokens: int = 150,
        temperature: float = 0.7,
        top_p: float = 0.95,
        system_prompt: str = None,
    ) -> str:
        """
        Generate text using Groq API (non-streaming).

        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            system_prompt: Optional custom system prompt (defaults to config)

        Returns:
            Generated text
        """
        if system_prompt is None:
            from app.config import RAG_SYSTEM_PROMPT
            system_prompt = RAG_SYSTEM_PROMPT

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.llm_model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
        }

        response = requests.post(
            self.groq_base_url, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def generate_text_stream(
        self,
        prompt: str,
        max_new_tokens: int = 150,
        temperature: float = 0.7,
        top_p: float = 0.95,
        system_prompt: str = None,
    ) -> Generator[str, None, None]:
        """
        Stream generated text chunk by chunk using Groq streaming API.

        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            system_prompt: Optional custom system prompt (defaults to config)

        Yields:
            Text chunks as they are generated
        """
        if system_prompt is None:
            from app.config import RAG_SYSTEM_PROMPT
            system_prompt = RAG_SYSTEM_PROMPT

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.llm_model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
        }

        response = requests.post(
            self.groq_base_url,
            headers=headers,
            json=payload,
            timeout=60,
            stream=True,
        )
        response.raise_for_status()

        # Parse SSE stream from Groq
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            data_str = line[6:]  # Remove "data: " prefix
            if data_str == "[DONE]":
                break

            try:
                import json
                chunk_data = json.loads(data_str)
                delta = chunk_data["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                continue

    def embed_text(self, text: str) -> list:
        """
        Generate embeddings for text (local SentenceTransformer).

        Args:
            text: Input text

        Returns:
            Embedding vector as list
        """
        embedding = self.embeddings_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_documents(self, documents: list) -> list:
        """
        Generate embeddings for multiple documents (local SentenceTransformer).

        Args:
            documents: List of text documents

        Returns:
            List of embedding vectors
        """
        embeddings = self.embeddings_model.encode(documents, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    def get_device(self) -> str:
        """Get the device being used for embeddings (cuda or cpu)"""
        return self._device


# Global client instance
_client: Optional[HFModelClient] = None


def get_hf_client() -> HFModelClient:
    """Get or create the global HF client instance"""
    global _client
    if _client is None:
        _client = HFModelClient()
    return _client
