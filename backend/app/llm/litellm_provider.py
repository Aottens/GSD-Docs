"""LiteLLM implementation of the LLM provider interface."""

from typing import AsyncGenerator, Optional
import litellm

from app.llm.provider import LLMProvider


class LLMProviderError(Exception):
    """Exception raised when LLM provider operations fail."""

    def __init__(self, provider: str, error_type: str, message: str):
        self.provider = provider
        self.error_type = error_type
        self.message = message
        super().__init__(f"[{provider}] {error_type}: {message}")


class LiteLLMProvider(LLMProvider):
    """
    LiteLLM-based provider implementation.

    Supports multiple LLM providers (Anthropic, OpenAI, etc.) through
    the LiteLLM library's unified interface.
    """

    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize the LiteLLM provider.

        Args:
            model: Model identifier in LiteLLM format (e.g., "anthropic/claude-sonnet-4-20250514")
            api_key: Optional API key (can also be set via environment variables)
        """
        self.model = model
        if api_key:
            # LiteLLM uses environment variables, but we can pass it in messages
            self.api_key = api_key
        else:
            self.api_key = None

    async def complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate a completion using LiteLLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional LiteLLM parameters

        Returns:
            Generated text completion

        Raises:
            LLMProviderError: If the completion fails
        """
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except litellm.exceptions.AuthenticationError as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Authentication Failed",
                message=f"Invalid or missing API key: {str(e)}"
            )
        except litellm.exceptions.RateLimitError as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Rate Limit Exceeded",
                message=f"Rate limit reached: {str(e)}"
            )
        except litellm.exceptions.NotFoundError as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Model Not Found",
                message=f"Model {self.model} not found: {str(e)}"
            )
        except Exception as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Completion Failed",
                message=f"Unexpected error: {str(e)}"
            )

    async def stream_complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming completion using LiteLLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional LiteLLM parameters

        Yields:
            Text chunks as they are generated

        Raises:
            LLMProviderError: If the completion fails
        """
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except litellm.exceptions.AuthenticationError as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Authentication Failed",
                message=f"Invalid or missing API key: {str(e)}"
            )
        except litellm.exceptions.RateLimitError as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Rate Limit Exceeded",
                message=f"Rate limit reached: {str(e)}"
            )
        except litellm.exceptions.NotFoundError as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Model Not Found",
                message=f"Model {self.model} not found: {str(e)}"
            )
        except Exception as e:
            raise LLMProviderError(
                provider=self.model,
                error_type="Streaming Failed",
                message=f"Unexpected error: {str(e)}"
            )

    def get_model_name(self) -> str:
        """
        Get the model identifier.

        Returns:
            Model name string
        """
        return self.model

    async def health_check(self) -> bool:
        """
        Check if the LiteLLM provider is accessible.

        Attempts a minimal completion to verify the provider is working.

        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            await litellm.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                temperature=0.0,
            )
            return True
        except Exception:
            # Any error means the provider is not healthy
            return False
