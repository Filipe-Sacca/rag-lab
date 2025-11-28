"""
Gemini Live API Client for Unlimited RPM/RPD

Uses WebSocket-based Live API which has no published RPM/RPD limits
in the free tier, only TPM (1M tokens/min) limit.

Key Benefits:
- No RPM limit (vs 15 RPM on standard API)
- No RPD limit (vs 200 RPD on standard API)
- Same model family: gemini-2.0-flash-live

Trade-offs:
- Uses WebSocket instead of REST
- Session-based (opens connection per request)
- Slightly more complex error handling
"""

import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from google import genai

from config import settings

# Thread pool for running async code in sync context
_executor = ThreadPoolExecutor(max_workers=4)

logger = logging.getLogger(__name__)

# Live API model mapping
LIVE_MODEL_MAPPING = {
    "gemini-2.0-flash": "gemini-2.0-flash-live-001",
    "gemini-2.5-flash": "gemini-2.5-flash-live-001",
}

# Default Live API model
DEFAULT_LIVE_MODEL = "gemini-2.0-flash-live-001"


def _get_live_model(standard_model: Optional[str] = None) -> str:
    """
    Map standard model name to Live API model name.

    Args:
        standard_model: Standard model name (e.g., "gemini-2.0-flash")

    Returns:
        Live API model name
    """
    if standard_model is None:
        standard_model = settings.GEMINI_MODEL

    # Remove any version suffix for matching
    base_model = standard_model.split("-exp")[0]

    return LIVE_MODEL_MAPPING.get(base_model, DEFAULT_LIVE_MODEL)


async def live_invoke(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Invoke Gemini via Live API (WebSocket) for unlimited RPM/RPD.

    This function opens a Live API session, sends the prompt,
    collects the streamed response, and closes the session.

    Args:
        prompt: The prompt to send to the model
        model_name: Model name (will be mapped to Live API equivalent)
        temperature: Generation temperature (0.0-1.0)
        max_output_tokens: Maximum tokens to generate
        api_key: API key to use (defaults to settings.GOOGLE_API_KEY)

    Returns:
        str: The complete model response

    Raises:
        RuntimeError: If Live API connection fails

    Example:
        >>> response = await live_invoke("What is RAG?")
        >>> print(response)
    """
    # Get API key
    key = api_key or settings.GOOGLE_API_KEY
    if not key:
        raise RuntimeError("No API key available for Live API")

    # Map to Live API model
    live_model = _get_live_model(model_name)

    # Build configuration
    config = {
        "response_modalities": ["TEXT"],
    }

    # Add generation config if specified
    generation_config = {}
    if temperature is not None:
        generation_config["temperature"] = temperature
    if max_output_tokens is not None:
        generation_config["max_output_tokens"] = max_output_tokens

    if generation_config:
        config["generation_config"] = generation_config

    logger.info(f"Live API call: model={live_model}")

    try:
        # Create client with API key
        client = genai.Client(api_key=key)

        # Collect response parts
        response_parts = []

        # Connect and send prompt
        async with client.aio.live.connect(model=live_model, config=config) as session:
            # Send the prompt
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": prompt}]},
                turn_complete=True
            )

            # Collect streamed response
            async for response in session.receive():
                if hasattr(response, 'text') and response.text:
                    response_parts.append(response.text)

                # Check for turn completion
                if hasattr(response, 'server_content'):
                    if getattr(response.server_content, 'turn_complete', False):
                        break

        # Combine all response parts
        full_response = "".join(response_parts)

        if not full_response:
            logger.warning("Live API returned empty response")
            raise RuntimeError("Live API returned empty response")

        logger.info(f"Live API success: {len(full_response)} chars")
        return full_response

    except Exception as e:
        logger.error(f"Live API error: {type(e).__name__}: {e}")
        raise RuntimeError(f"Live API failed: {e}") from e


async def live_invoke_with_fallback(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    fallback_to_standard: bool = True,
) -> tuple[str, str]:
    """
    Try Live API first, fallback to standard API if it fails.

    Args:
        prompt: The prompt to send
        model_name: Model name
        temperature: Generation temperature
        max_output_tokens: Max tokens
        fallback_to_standard: If True, falls back to ainvoke_with_rotation

    Returns:
        tuple: (response, api_type) where api_type is "live" or "standard"

    Example:
        >>> response, api_type = await live_invoke_with_fallback("What is RAG?")
        >>> print(f"Response from {api_type} API: {response}")
    """
    try:
        response = await live_invoke(
            prompt=prompt,
            model_name=model_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        return response, "live"

    except Exception as e:
        logger.warning(f"Live API failed, falling back to standard: {e}")

        if not fallback_to_standard:
            raise

        # Import here to avoid circular imports
        from core.llm import ainvoke_with_rotation

        response = await ainvoke_with_rotation(
            prompt=prompt,
            model_name=model_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        return response, "standard"


# Convenience function matching ainvoke_with_rotation signature
async def ainvoke_live(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    **kwargs,
) -> str:
    """
    Drop-in replacement for ainvoke_with_rotation using Live API.

    This function has the same signature as ainvoke_with_rotation,
    making it easy to swap between the two.

    Args:
        prompt: The prompt to send
        model_name: Model name
        temperature: Generation temperature
        max_output_tokens: Maximum tokens
        **kwargs: Ignored (for compatibility)

    Returns:
        str: Model response
    """
    return await live_invoke(
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


def live_invoke_sync(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Synchronous wrapper for live_invoke.

    Uses asyncio to run the async function in a sync context.
    Ideal for RAGAS evaluation and other sync code.

    Args:
        prompt: The prompt to send
        model_name: Model name
        temperature: Generation temperature
        max_output_tokens: Maximum tokens

    Returns:
        str: Model response

    Example:
        >>> response = live_invoke_sync("What is RAG?")
        >>> print(response)
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, use thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    live_invoke(
                        prompt=prompt,
                        model_name=model_name,
                        temperature=temperature,
                        max_output_tokens=max_output_tokens,
                    )
                )
                return future.result(timeout=60)
        else:
            # No loop running, run directly
            return loop.run_until_complete(
                live_invoke(
                    prompt=prompt,
                    model_name=model_name,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
            )
    except RuntimeError:
        # No event loop exists, create new one
        return asyncio.run(
            live_invoke(
                prompt=prompt,
                model_name=model_name,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
        )
