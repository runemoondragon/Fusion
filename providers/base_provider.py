from abc import ABC, abstractmethod
from typing import List, Dict, Any
from config import Config

class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """
        Send a request to the AI provider and get a response.

        Args:
            messages: A list of message objects representing the conversation history.
            tools: A list of tool definitions available for the provider to use.
            config: The application configuration object.

        Returns:
            A dictionary representing the provider's response, including content and usage data.
            Expected structure might vary slightly but should contain 'content' and 'usage'.
        """
        pass 