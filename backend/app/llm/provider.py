"""Abstract LLM provider interface."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Defines the interface that all LLM providers must implement,
    enabling easy switching between different providers (Anthropic,
    OpenAI, local models, etc.).
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text completion

        Raises:
            LLMProviderError: If the completion fails
        """
        pass

    @abstractmethod
    async def stream_complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Yields:
            Text chunks as they are generated

        Raises:
            LLMProviderError: If the completion fails
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model identifier for this provider.

        Returns:
            Model name/identifier string
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is accessible and working.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass
