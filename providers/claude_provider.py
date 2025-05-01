import anthropic
from typing import List, Dict, Any
import logging

from .base_provider import BaseProvider
from config import Config

class ClaudeProvider(BaseProvider):
    """Provider implementation for Anthropic's Claude API."""

    def __init__(self):
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.logger = logging.getLogger(__name__)

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """Send chat request to Claude API."""
        self.logger.debug(f"Sending request to Claude with {len(messages)} messages and {len(tools)} tools.")
        try:
            response = self.client.messages.create(
                model=config.MODEL,
                max_tokens=config.MAX_TOKENS,
                temperature=config.DEFAULT_TEMPERATURE,
                system=self._get_system_prompt(), # Assuming system prompt is needed
                messages=messages,
                tools=tools,
                tool_choice={"type": "auto"} # Let Claude decide when to use tools
            )
            self.logger.debug(f"Received response from Claude. Stop reason: {response.stop_reason}")
            # Convert the response object to a dictionary for consistent return type
            # The exact structure needed depends on how Assistant processes it later.
            # For now, return the raw object's __dict__ or relevant parts.
            # Need to ensure 'content' and 'usage' keys are present or mapped.
            response_dict = {
                'content': response.content,
                'usage': {'input_tokens': response.usage.input_tokens, 'output_tokens': response.usage.output_tokens},
                'stop_reason': response.stop_reason,
                # Add other relevant fields if needed
                'id': response.id,
                'model': response.model,
                'role': response.role,
                'stop_sequence': response.stop_sequence,
                'type': response.type,
            }
            return response_dict

        except anthropic.APIConnectionError as e:
            self.logger.error(f"Claude APIConnectionError: {e}")
            raise ConnectionError(f"Failed to connect to Anthropic API: {e}") from e
        except anthropic.RateLimitError as e:
            self.logger.error(f"Claude RateLimitError: {e}")
            raise ConnectionError(f"Anthropic API rate limit exceeded: {e}") from e # Or a more specific exception
        except anthropic.APIStatusError as e:
            self.logger.error(f"Claude APIStatusError: status={e.status_code}, response={e.response}")
            raise ConnectionError(f"Anthropic API error (Status {e.status_code}): {e}") from e
        except Exception as e:
            self.logger.exception("An unexpected error occurred during Claude API call")
            raise RuntimeError(f"An unexpected error occurred interacting with Claude: {e}") from e

    def _get_system_prompt(self) -> str:
        """Helper to potentially load a system prompt. TODO: Adapt based on original Assistant logic."""
        # This needs to replicate how the system prompt was handled in the Assistant class
        # For now, returning a placeholder or checking if SystemPrompts was used.
        # Let's assume SystemPrompts might be used later or was part of Assistant.
        try:
            from prompts.system_prompts import SystemPrompts
            # Combine the default prompt and tool usage guidelines
            return f"{SystemPrompts.DEFAULT}\n\n{SystemPrompts.TOOL_USAGE}"
        except ImportError:
            self.logger.warning("SystemPrompts class not found. Using a basic default prompt.")
            return "You are a helpful assistant." # Default basic prompt 