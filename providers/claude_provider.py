import anthropic
from typing import List, Dict, Any
import logging
import time
import json

from .base_provider import BaseProvider
from config import Config

class ClaudeProvider(BaseProvider):
    """Provider implementation for Anthropic's Claude API."""

    def __init__(self, api_key: str = None, client_model: str = None):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.client_model = client_model

        final_api_key_to_use = api_key # This is the key selected by app.py

        if final_api_key_to_use:
            # app.py has already logged the original source (header or .env)
            try:
                self.client = anthropic.Anthropic(api_key=final_api_key_to_use)
                self.logger.info(f"Claude client configured with the API key selected by application logic.")
            except Exception as e:
                self.logger.exception(f"Failed to initialize Claude client with the API key selected by application logic: {e}")
                self.client = None
                # Optionally re-raise, as Claude provider was stricter before
                # raise ValueError(f"Failed to initialize Claude client with selected key: {e}")
        else:
            self.logger.warning(f"No API key was determined by application logic for Claude. Claude provider will not work.")
            # self.client remains None
            # Optionally re-raise, as Claude provider was stricter before
            # raise ValueError(f"No API key determined for Claude by application logic.")

    @property
    def name(self) -> str:
        return "claude"

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """Send chat request to Claude API."""
        self.logger.debug(f"Sending request to Claude with {len(messages)} messages and {len(tools)} tools.")
        
        # TEMPORARY: Remove 'tool_name' from tool_result blocks in user messages
        # ALSO: Remove any system messages from the messages array as Claude expects system prompts as separate parameter
        processed_messages = []
        for msg in messages:
            # Skip any system messages - Claude handles system prompts separately
            if msg.get('role') == 'system':
                continue
                
            if msg.get('role') == 'user' and isinstance(msg.get('content'), list):
                new_content = []
                for item in msg['content']:
                    if isinstance(item, dict) and item.get('type') == 'tool_result' and 'tool_name' in item:
                        filtered_item = {k: v for k, v in item.items() if k != 'tool_name'}
                        new_content.append(filtered_item)
                    else:
                        new_content.append(item)
                processed_messages.append({'role': msg['role'], 'content': new_content})
            else:
                processed_messages.append(msg)

        self.logger.debug(f"ClaudeProvider: History after formatting (sent to API): {json.dumps(processed_messages, indent=2)}")

        # ITEM 2: Modified Model Selection Logic
        model_name_to_use = None
        if self.client_model:
            model_name_to_use = self.client_model
            self.logger.info(f"Using client-specified Claude model: {model_name_to_use}")
        else:
            model_name_to_use = Config.MODEL # Assumes Config.MODEL has a default
            self.logger.info(f"Using configured/default Claude model: {model_name_to_use}")
        # END ITEM 2

        try:
            start_time = time.time()
            
            # Prepare request parameters
            request_params = {
                "model": model_name_to_use,
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.DEFAULT_TEMPERATURE,
                "system": self._get_system_prompt(),
                "messages": processed_messages
            }
            
            # Only include tools and tool_choice if tools are provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = {"type": "auto"}
            
            response = self.client.messages.create(**request_params)
            end_time = time.time()
            runtime = end_time - start_time
            self.logger.debug(f"Received response from Claude. Stop reason: {response.stop_reason}")
            self.logger.debug(f"Claude usage: input_tokens={response.usage.input_tokens}, output_tokens={response.usage.output_tokens}, runtime={runtime}")
            
            # Extract text content from Claude's response content blocks
            content_text = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        content_text += block.text
                    elif isinstance(block, dict) and 'text' in block:
                        content_text += block['text']
            
            # Convert the response object to a dictionary for consistent return type
            response_dict = {
                'content': content_text,  # Use extracted text instead of raw content blocks
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'runtime': runtime
                },
                'stop_reason': response.stop_reason,
                'model_used': model_name_to_use,
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
            # Pass the detailed error message back if possible
            error_details = e.response.json().get('error', {})
            error_message = error_details.get('message', str(e))
            error_type = error_details.get('type', 'unknown_error')
            full_error = f"Anthropic API error (Status {e.status_code}, Type: {error_type}): {error_message}"
            raise ConnectionError(full_error) from e
        except Exception as e:
            self.logger.exception("An unexpected error occurred during Claude API call")
            raise RuntimeError(f"An unexpected error occurred interacting with Claude: {e}") from e

    def _get_system_prompt(self) -> str:
        """Helper to load the system prompt using SystemPrompts class."""
        try:
            from prompts.system_prompts import SystemPrompts
            system_prompts = SystemPrompts()
            return system_prompts.get_system_prompt("normal")
        except ImportError:
            self.logger.warning("SystemPrompts class not found. Using a basic default prompt.")
            return "You are a helpful assistant." # Default basic prompt 
        except Exception as e:
            self.logger.warning(f"Error loading system prompt: {e}. Using a basic default prompt.")
            return "You are a helpful assistant." 