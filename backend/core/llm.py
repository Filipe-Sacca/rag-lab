"""
Google Gemini LLM Configuration with API Key Rotation

Handles initialization and configuration of Google Gemini models
with automatic API key rotation to distribute rate limits across
multiple projects.
"""

import logging
from typing import Optional

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from core.api_keys import get_api_key_rotator, initialize_rotator

logger = logging.getLogger(__name__)

# Initialize rotator on module load
_rotator_initialized = False


def _ensure_rotator_initialized() -> None:
    """Ensure the API key rotator is initialized."""
    global _rotator_initialized
    if not _rotator_initialized:
        initialize_rotator(
            primary_key=settings.GOOGLE_API_KEY,
            additional_keys=settings.GOOGLE_API_KEYS,
        )
        _rotator_initialized = True


def configure_gemini(api_key: Optional[str] = None) -> None:
    """
    Configure Google Generative AI with API key.

    Args:
        api_key: Specific API key to use. If None, uses rotator.
    """
    _ensure_rotator_initialized()

    if api_key is None:
        rotator = get_api_key_rotator()
        api_key = rotator.get_next_key()

    if api_key:
        genai.configure(api_key=api_key)


def get_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
    **kwargs,
) -> ChatGoogleGenerativeAI:
    """
    Get configured Google Gemini LLM instance with key rotation.

    Args:
        model_name: Model name (defaults to settings.GEMINI_MODEL)
        temperature: Generation temperature (defaults to settings.TEMPERATURE)
        api_key: Specific API key to use. If None, uses next key from rotator.
        **kwargs: Additional parameters for ChatGoogleGenerativeAI

    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance

    Example:
        >>> llm = get_llm()
        >>> response = llm.invoke("What is RAG?")
    """
    _ensure_rotator_initialized()

    # Get API key from rotator if not provided
    if api_key is None:
        rotator = get_api_key_rotator()
        api_key = rotator.get_next_key()

        if api_key is None:
            raise RuntimeError("No API keys available. All keys may be exhausted.")

    # Configure genai with the selected key
    configure_gemini(api_key)

    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL,
        google_api_key=api_key,
        temperature=temperature or settings.TEMPERATURE,
        **kwargs,
    )


def get_llm_with_retry(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: int = 3,
    cooldown_seconds: float = 60.0,
    **kwargs,
) -> ChatGoogleGenerativeAI:
    """
    Get LLM with automatic retry on rate limit errors.

    Will try different API keys from the rotation pool on 429 errors.

    Args:
        model_name: Model name
        temperature: Generation temperature
        max_retries: Maximum number of keys to try
        cooldown_seconds: How long to mark exhausted keys as unavailable
        **kwargs: Additional parameters

    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance

    Raises:
        RuntimeError: If all keys are exhausted
    """
    _ensure_rotator_initialized()
    rotator = get_api_key_rotator()

    for attempt in range(max_retries):
        api_key = rotator.get_next_key()

        if api_key is None:
            raise RuntimeError(
                f"All API keys exhausted after {attempt} attempts. "
                f"Stats: {rotator.get_stats()}"
            )

        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name or settings.GEMINI_MODEL,
                google_api_key=api_key,
                temperature=temperature or settings.TEMPERATURE,
                **kwargs,
            )
            # Record success
            rotator.record_success(api_key)
            return llm

        except ResourceExhausted as e:
            logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
            rotator.mark_key_exhausted(api_key, cooldown_seconds)
            continue

    raise RuntimeError(f"Failed after {max_retries} attempts")


def mark_current_key_exhausted(cooldown_seconds: float = 60.0) -> None:
    """
    Mark the most recently used API key as exhausted.

    Call this when you catch a 429 error from an LLM call.

    Args:
        cooldown_seconds: How long to wait before retrying this key
    """
    _ensure_rotator_initialized()
    rotator = get_api_key_rotator()
    rotator.mark_current_exhausted(cooldown_seconds)


def get_api_key_stats() -> dict:
    """Get statistics about API key usage."""
    _ensure_rotator_initialized()
    return get_api_key_rotator().get_stats()


def invoke_with_rotation(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: int = 4,
    cooldown_seconds: float = 60.0,
    **kwargs,
) -> str:
    """
    Invoke LLM with automatic API key rotation on 429 errors.

    This function tries each available API key when a rate limit error occurs,
    providing true rotation across different Google Cloud projects.

    Args:
        prompt: The prompt to send to the LLM
        model_name: Model name (defaults to settings.GEMINI_MODEL)
        temperature: Generation temperature
        max_retries: Maximum number of different keys to try
        cooldown_seconds: How long to mark exhausted keys as unavailable
        **kwargs: Additional parameters for ChatGoogleGenerativeAI

    Returns:
        str: The LLM response content

    Raises:
        RuntimeError: If all keys are exhausted

    Example:
        >>> response = invoke_with_rotation("What is RAG?")
        >>> print(response)
    """
    _ensure_rotator_initialized()
    rotator = get_api_key_rotator()

    last_error = None

    for attempt in range(max_retries):
        api_key = rotator.get_next_key()

        if api_key is None:
            raise RuntimeError(
                f"All API keys exhausted after {attempt} attempts. "
                f"Stats: {rotator.get_stats()}"
            )

        try:
            # Create fresh LLM instance with this specific key
            llm = ChatGoogleGenerativeAI(
                model=model_name or settings.GEMINI_MODEL,
                google_api_key=api_key,
                temperature=temperature or settings.TEMPERATURE,
                # Disable internal retries to let our rotation handle it
                max_retries=1,
                **kwargs,
            )

            response = llm.invoke(prompt)

            # Record success
            rotator.record_success(api_key)
            logger.info(f"LLM call succeeded with key attempt {attempt + 1}")

            return response.content

        except ResourceExhausted as e:
            logger.warning(
                f"Rate limit hit on attempt {attempt + 1}/{max_retries}: {e}"
            )
            rotator.mark_key_exhausted(api_key, cooldown_seconds)
            last_error = e
            continue

        except Exception as e:
            # For other errors, don't rotate - just raise
            logger.error(f"LLM call failed with non-rate-limit error: {e}")
            raise

    raise RuntimeError(
        f"All {max_retries} API key attempts failed. Last error: {last_error}"
    )


async def ainvoke_with_rotation(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: int = 4,
    cooldown_seconds: float = 60.0,
    **kwargs,
) -> str:
    """
    Async version of invoke_with_rotation.

    Same as invoke_with_rotation but for async contexts.
    """
    _ensure_rotator_initialized()
    rotator = get_api_key_rotator()

    last_error = None

    for attempt in range(max_retries):
        api_key = rotator.get_next_key()

        if api_key is None:
            raise RuntimeError(
                f"All API keys exhausted after {attempt} attempts. "
                f"Stats: {rotator.get_stats()}"
            )

        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name or settings.GEMINI_MODEL,
                google_api_key=api_key,
                temperature=temperature or settings.TEMPERATURE,
                max_retries=1,
                **kwargs,
            )

            response = await llm.ainvoke(prompt)
            rotator.record_success(api_key)
            logger.info(f"Async LLM call succeeded with key attempt {attempt + 1}")

            return response.content

        except ResourceExhausted as e:
            logger.warning(
                f"Rate limit hit on async attempt {attempt + 1}/{max_retries}: {e}"
            )
            rotator.mark_key_exhausted(api_key, cooldown_seconds)
            last_error = e
            continue

        except Exception as e:
            logger.error(f"Async LLM call failed with non-rate-limit error: {e}")
            raise

    raise RuntimeError(
        f"All {max_retries} API key attempts failed. Last error: {last_error}"
    )


def get_generation_config(
    temperature: Optional[float] = None,
    top_p: float = 0.95,
    top_k: int = 40,
    max_output_tokens: int = 8192,
) -> dict:
    """
    Get generation configuration for Gemini.

    Args:
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
        max_output_tokens: Maximum tokens to generate

    Returns:
        dict: Generation configuration
    """
    return {
        "temperature": temperature or settings.TEMPERATURE,
        "top_p": top_p,
        "top_k": top_k,
        "max_output_tokens": max_output_tokens,
    }


async def smart_invoke(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    force_live: bool = False,
    force_standard: bool = False,
    **kwargs,
) -> tuple[str, str]:
    """
    Smart LLM invocation that automatically chooses between Live API and Standard API.

    Priority:
    1. If USE_LIVE_API=True (default): Use Live API (unlimited RPM/RPD)
    2. If Live API fails and LIVE_API_FALLBACK=True: Fallback to Standard API
    3. If USE_LIVE_API=False: Use Standard API with key rotation

    Args:
        prompt: The prompt to send
        model_name: Model name
        temperature: Generation temperature
        max_output_tokens: Maximum tokens to generate
        force_live: Force use of Live API regardless of settings
        force_standard: Force use of Standard API regardless of settings
        **kwargs: Additional parameters

    Returns:
        tuple: (response_text, api_type) where api_type is "live" or "standard"

    Example:
        >>> response, api = await smart_invoke("What is RAG?")
        >>> print(f"Response from {api} API: {response}")
    """
    # Determine which API to use
    use_live = settings.USE_LIVE_API

    if force_standard:
        use_live = False
    elif force_live:
        use_live = True

    if use_live:
        try:
            # Try Live API first (unlimited RPM/RPD)
            from core.llm_live import live_invoke

            response = await live_invoke(
                prompt=prompt,
                model_name=model_name,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            logger.info("smart_invoke: Used Live API successfully")
            return response, "live"

        except Exception as e:
            logger.warning(f"smart_invoke: Live API failed: {e}")

            if settings.LIVE_API_FALLBACK and not force_live:
                logger.info("smart_invoke: Falling back to Standard API")
                # Fall through to standard API
            else:
                raise

    # Use Standard API with key rotation
    response = await ainvoke_with_rotation(
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        **kwargs,
    )
    logger.info("smart_invoke: Used Standard API")
    return response, "standard"


async def ainvoke_smart(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    **kwargs,
) -> str:
    """
    Simplified smart invoke that returns only the response (for drop-in replacement).

    Uses Live API if enabled, with automatic fallback to Standard API.

    Args:
        prompt: The prompt to send
        model_name: Model name
        temperature: Generation temperature
        max_output_tokens: Maximum tokens to generate
        **kwargs: Additional parameters

    Returns:
        str: Model response

    Example:
        >>> response = await ainvoke_smart("What is RAG?")
        >>> print(response)
    """
    response, _ = await smart_invoke(
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        **kwargs,
    )
    return response
