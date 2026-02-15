"""LLM service for provider management and configuration."""

from app.config import get_settings
from app.llm.provider import LLMProvider
from app.llm.litellm_provider import LiteLLMProvider, LLMProviderError


def get_llm_provider() -> LLMProvider:
    """
    Factory function to create and configure the LLM provider.

    Reads configuration from settings and returns the appropriate
    provider instance. Currently supports LiteLLM, but structured
    for easy addition of other providers.

    Returns:
        Configured LLM provider instance

    Raises:
        ValueError: If the configured provider is not supported
    """
    settings = get_settings()

    # Currently only LiteLLM is supported, but this structure
    # makes it easy to add other providers in the future
    if settings.LLM_PROVIDER in ["anthropic", "openai", "litellm"]:
        return LiteLLMProvider(
            model=settings.LLM_MODEL,
            api_key=settings.ANTHROPIC_API_KEY or None
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


__all__ = ["get_llm_provider", "LLMProviderError"]
