from typing import List, Dict, Any
import logging
import os
import json

# Attempt to import the openai library
try:
    import openai
except ImportError:
    # Provide a clear error message if the library is missing
    raise ImportError("The 'openai' library is required for OpenAIProvider. Please install it using: pip install openai")

from .base_provider import BaseProvider
from config import Config

class OpenAIProvider(BaseProvider):
    """Provider implementation for OpenAI's ChatGPT API."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not Config.OPENAI_API_KEY:
            self.logger.warning("OPENAI_API_KEY not found in environment variables. OpenAI provider will not work.")
            # Optionally raise an error to prevent usage without a key
            # raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = None # Indicate client is not initialized
        else:
            # Initialize the OpenAI client
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.logger.info("OpenAI client initialized.")

    def _format_tools_for_openai(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert the internal tool format to OpenAI's expected format."""
        openai_tools = []
        for tool in tools:
            try:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool['name'],
                        "description": tool['description'],
                        "parameters": tool['input_schema'] # Assumes input_schema is directly compatible
                    }
                })
            except KeyError as e:
                self.logger.error(f"Tool '{tool.get('name', '<unknown>')}' is missing required key for OpenAI formatting: {e}")
            except Exception as e:
                 self.logger.error(f"Error formatting tool '{tool.get('name', '<unknown>')}' for OpenAI: {e}")
        return openai_tools

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """Send chat request to OpenAI API."""
        if not self.client:
            return {
                'content': [{'type': 'text', 'text': 'OpenAI API key not configured. Cannot process request.'}],
                'usage': {'input_tokens': 0, 'output_tokens': 0},
                'stop_reason': 'error'
            }

        self.logger.debug(f"Sending request to OpenAI with {len(messages)} messages and {len(tools)} tools.")
        openai_tools = self._format_tools_for_openai(tools)

        # Determine the model to use (can be made dynamic later)
        # Defaulting to gpt-4o-mini for cost/performance balance
        model_name = getattr(config, 'OPENAI_MODEL', 'gpt-4o-mini') 

        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages, # Assumes messages are already in OpenAI format
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None, # Let OpenAI decide when to use tools
                temperature=config.DEFAULT_TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )

            response_message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Extract usage data
            usage_data = response.usage
            usage_dict = {
                'input_tokens': getattr(usage_data, 'prompt_tokens', 0),
                'output_tokens': getattr(usage_data, 'completion_tokens', 0)
            }
            self.logger.debug(f"Received response from OpenAI. Finish reason: {finish_reason}")

            # Process the response message
            response_content = []
            if response_message.content:
                 response_content.append({"type": "text", "text": response_message.content})
            
            # Check for tool calls
            tool_calls = getattr(response_message, 'tool_calls', None)
            if tool_calls:
                finish_reason = "tool_calls" # Standardize stop reason for tool use
                for tool_call in tool_calls:
                    # Map OpenAI tool call format to Claude-like format for ce3.py handler
                    response_content.append({
                        "type": "tool_use",
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "input": json.loads(tool_call.function.arguments) # Arguments are JSON strings
                    })

            return {
                'content': response_content, # Return list similar to Claude
                'usage': usage_dict,
                'stop_reason': finish_reason
            }

        except openai.APIConnectionError as e:
            self.logger.error(f"OpenAI APIConnectionError: {e}")
            raise ConnectionError(f"Failed to connect to OpenAI API: {e}") from e
        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI RateLimitError: {e}")
            raise ConnectionError(f"OpenAI API rate limit exceeded: {e}") from e
        except openai.APIStatusError as e:
            self.logger.error(f"OpenAI APIStatusError: status={e.status_code}, response={e.response}")
            raise ConnectionError(f"OpenAI API error (Status {e.status_code}): {e}") from e
        except Exception as e:
            self.logger.exception("An unexpected error occurred during OpenAI API call")
            raise RuntimeError(f"An unexpected error occurred interacting with OpenAI: {e}") from e 