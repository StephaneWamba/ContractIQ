"""
Embedding service for generating text embeddings using OpenAI.
Centralized service for consistent embedding generation across the application.
"""
from typing import List, Optional
from openai import OpenAI, APIError, RateLimitError as OpenAIRateLimitError
import hashlib

from src.core.config import settings
from src.core.cache import cache_service, hash_text
from src.core.retry import retry_with_backoff, RetryConfig
from src.core.logging_config import get_logger
from src.core.exceptions import ExternalServiceError, RateLimitError

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI"""
    
    def __init__(self):
        """Initialize embedding service"""
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not set. Embeddings will be disabled.")
    
    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
        """
        Generate embedding for text (with caching).
        
        Args:
            text: Text to embed
            model: Embedding model to use (default: text-embedding-3-small)
        
        Returns:
            Embedding vector or None if error
        """
        if not self.client or not text:
            return None
        
        # Build cache key
        text_hash = hash_text(text)
        cache_key = f"embedding:{model}:{text_hash}"
        
        # Try cache first
        cached = cache_service.get(cache_key)
        if cached is not None:
            return cached
        
        # Truncate if too long (OpenAI limit is 8192 tokens, ~32K chars)
        max_chars = 32000
        original_text = text
        if len(text) > max_chars:
            text = text[:max_chars]
        
        # Retry configuration for OpenAI API calls
        retry_config = RetryConfig(
            max_retries=3,
            initial_delay=1.0,
            max_delay=10.0,
            retryable_exceptions=[APIError, OpenAIRateLimitError, ConnectionError, TimeoutError]
        )
        
        def _call_openai():
            try:
                response = self.client.embeddings.create(
                    model=model,
                    input=text
                )
                return response.data[0].embedding
            except OpenAIRateLimitError as e:
                logger.warning(f"Rate limit hit for embeddings: {e}")
                raise RateLimitError(
                    message="OpenAI rate limit exceeded",
                    retry_after=60
                ) from e
            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise ExternalServiceError(
                    service="OpenAI Embeddings",
                    message=str(e),
                    retryable=True
                ) from e
        
        # Apply retry decorator
        _call_openai_with_retry = retry_with_backoff(
            _call_openai,
            config=retry_config,
            operation_name="get_embedding"
        )
        
        try:
            embedding = _call_openai_with_retry()
            
            # Cache embedding (7 days)
            cache_service.set(cache_key, embedding, ttl=settings.cache_embedding_ttl)
            
            logger.debug(f"Generated embedding for text (hash: {text_hash[:8]}...)")
            return embedding
        except (ExternalServiceError, RateLimitError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}", exc_info=True)
            raise ExternalServiceError(
                service="OpenAI Embeddings",
                message=f"Unexpected error: {str(e)}",
                retryable=False
            ) from e
    
    def get_embeddings_batch(self, texts: List[str], model: str = "text-embedding-3-small") -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
        
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        if not self.client:
            return [None] * len(texts)
        
        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                # Truncate if needed
                max_chars = 32000
                if len(text) > max_chars:
                    text = text[:max_chars]
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            return [None] * len(texts)
        
        # Retry configuration for batch embeddings
        retry_config = RetryConfig(
            max_retries=3,
            initial_delay=1.0,
            max_delay=10.0,
            retryable_exceptions=[APIError, OpenAIRateLimitError, ConnectionError, TimeoutError]
        )
        
        def _call_openai_batch():
            try:
                response = self.client.embeddings.create(
                    model=model,
                    input=valid_texts
                )
                return response.data
            except OpenAIRateLimitError as e:
                logger.warning(f"Rate limit hit for batch embeddings: {e}")
                raise RateLimitError(
                    message="OpenAI rate limit exceeded",
                    retry_after=60
                ) from e
            except APIError as e:
                logger.error(f"OpenAI API error in batch: {e}")
                raise ExternalServiceError(
                    service="OpenAI Embeddings",
                    message=str(e),
                    retryable=True
                ) from e
        
        # Apply retry wrapper
        _call_openai_batch_with_retry = retry_with_backoff(
            _call_openai_batch,
            config=retry_config,
            operation_name="get_embeddings_batch"
        )
        
        try:
            response_data = _call_openai_batch_with_retry()
            
            # Map results back to original indices
            embeddings = [None] * len(texts)
            for idx, embedding_data in zip(valid_indices, response_data):
                embeddings[idx] = embedding_data.embedding
            
            logger.debug(f"Generated {len(valid_texts)} embeddings in batch")
            return embeddings
        except (ExternalServiceError, RateLimitError):
            # Return None for all on error (caller should handle)
            logger.error("Failed to generate batch embeddings after retries")
            return [None] * len(texts)
        except Exception as e:
            logger.error(f"Unexpected error in batch embeddings: {e}", exc_info=True)
            return [None] * len(texts)

