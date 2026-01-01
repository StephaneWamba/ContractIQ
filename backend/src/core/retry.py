"""
Retry logic for external API calls and operations.

Provides exponential backoff and configurable retry strategies.
"""
import time
import random
from typing import Callable, TypeVar, Optional, List, Type
from functools import wraps
import logging

from src.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to delays
            retryable_exceptions: List of exception types that should be retried
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [Exception]


def retry_with_backoff(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None
) -> Callable[..., T]:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        func: Function to retry
        config: Retry configuration (uses default if None)
        operation_name: Name of operation for logging
    
    Returns:
        Wrapped function with retry logic
    """
    if config is None:
        config = RetryConfig()
    
    op_name = operation_name or func.__name__
    
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                    logger.warning(f"{op_name}: Non-retryable exception: {type(e).__name__}: {e}")
                    raise
                
                # Don't retry on last attempt
                if attempt >= config.max_retries:
                    logger.error(
                        f"{op_name}: Failed after {config.max_retries + 1} attempts. "
                        f"Last error: {type(e).__name__}: {e}"
                    )
                    raise ExternalServiceError(
                        service=op_name,
                        message=str(e),
                        retryable=False
                    ) from e
                
                # Calculate delay with exponential backoff
                delay = min(
                    config.initial_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                
                # Add jitter if enabled
                if config.jitter:
                    jitter_amount = delay * 0.1  # 10% jitter
                    delay += random.uniform(-jitter_amount, jitter_amount)
                    delay = max(0, delay)  # Ensure non-negative
                
                logger.warning(
                    f"{op_name}: Attempt {attempt + 1}/{config.max_retries + 1} failed. "
                    f"Retrying in {delay:.2f}s. Error: {type(e).__name__}: {e}"
                )
                
                time.sleep(delay)
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
    
    return wrapper


def retry_async_with_backoff(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    operation_name: Optional[str] = None
) -> Callable[..., T]:
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        func: Async function to retry
        config: Retry configuration (uses default if None)
        operation_name: Name of operation for logging
    
    Returns:
        Wrapped async function with retry logic
    """
    import asyncio
    
    if config is None:
        config = RetryConfig()
    
    op_name = operation_name or func.__name__
    
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                    logger.warning(f"{op_name}: Non-retryable exception: {type(e).__name__}: {e}")
                    raise
                
                # Don't retry on last attempt
                if attempt >= config.max_retries:
                    logger.error(
                        f"{op_name}: Failed after {config.max_retries + 1} attempts. "
                        f"Last error: {type(e).__name__}: {e}"
                    )
                    raise ExternalServiceError(
                        service=op_name,
                        message=str(e),
                        retryable=False
                    ) from e
                
                # Calculate delay with exponential backoff
                delay = min(
                    config.initial_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                
                # Add jitter if enabled
                if config.jitter:
                    jitter_amount = delay * 0.1  # 10% jitter
                    delay += random.uniform(-jitter_amount, jitter_amount)
                    delay = max(0, delay)
                
                logger.warning(
                    f"{op_name}: Attempt {attempt + 1}/{config.max_retries + 1} failed. "
                    f"Retrying in {delay:.2f}s. Error: {type(e).__name__}: {e}"
                )
                
                await asyncio.sleep(delay)
        
        # Should never reach here
        if last_exception:
            raise last_exception
    
    return wrapper

