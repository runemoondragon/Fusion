from .base_provider import BaseProvider
from .claude_provider import ClaudeProvider
# Import placeholder providers once created
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider

class ProviderFactory:
    """Factory class to create provider instances based on name."""

    _providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider, # Uncomment when implemented
        "gemini": GeminiProvider, # Uncomment when implemented
    }

    @staticmethod
    def create_provider(provider_name: str, api_key: str = None) -> BaseProvider:
        """
        Create and return an instance of the specified provider.

        Args:
            provider_name: The name of the provider (e.g., 'claude').
            api_key: Optional API key to use for this provider instance.

        Returns:
            An instance of the corresponding BaseProvider subclass.

        Raises:
            ValueError: If the provider_name is unknown.
        """
        provider_class = ProviderFactory._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(ProviderFactory._providers.keys())}")
        
        # Instantiate and return the provider, passing the api_key
        return provider_class(api_key=api_key) 