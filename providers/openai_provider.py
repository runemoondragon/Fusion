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

    @property
    def name(self) -> str:
        return "OpenAIProvider"

    def _normalize_message_blocks(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recursively convert any Pydantic/Anthropic message blocks to dicts. Leaves dicts unchanged.
        Only used internally for OpenAIProvider to ensure compatibility.
        """
        def block_to_dict(block):
            # If it's a Pydantic object (Anthropic), convert to dict
            if hasattr(block, 'dict') and callable(getattr(block, 'dict', None)):
                return block.dict()
            # If it's a known Anthropic block (TextBlock, ToolUseBlock, etc.)
            if hasattr(block, '__dict__') and hasattr(block, 'type'):
                # Only include public attributes
                return {k: v for k, v in block.__dict__.items() if not k.startswith('_')}
            # If it's already a dict, return as is
            if isinstance(block, dict):
                return block
            return block  # fallback (should not happen)

        normalized = []
        for msg in messages:
            content = msg.get('content')
            if isinstance(content, list):
                norm_content = [block_to_dict(b) for b in content]
            else:
                norm_content = content
            norm_msg = dict(msg)
            norm_msg['content'] = norm_content
            normalized.append(norm_msg)
        return normalized

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

    def _format_messages_for_openai(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert internal message history to OpenAI's expected format."""
        formatted_messages = []
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content')

            # --- Handle Assistant Message with Tool Use ---
            if role == 'assistant' and isinstance(content, list) and content and content[0].get('type') == 'tool_use':
                tool_calls = []
                valid_conversion = True
                for item in content:
                    if item.get('type') == 'tool_use':
                        tool_calls.append({
                            "id": item.get('id'), # Pass the ID back
                            "type": "function",
                            "function": {
                                "name": item.get('name'),
                                "arguments": json.dumps(item.get('input', {})) # Arguments must be a JSON string
                            }
                        })
                    else:
                        self.logger.error(f"Assistant message contains mixed content with tool_use, cannot format as tool_calls: {content}")
                        valid_conversion = False
                        break

                if tool_calls and valid_conversion:
                    formatted_messages.append({"role": "assistant", "tool_calls": tool_calls})
                    self.logger.debug(f"Formatted assistant tool_use to tool_calls: {tool_calls}")
                elif valid_conversion:
                     formatted_messages.append({"role": "assistant", "content": ""})
                else:
                     formatted_messages.append({"role": "assistant", "content": "[Internal formatting error: unable to convert mixed tool_use message]"})

            # --- Handle User Message Containing Tool Result(s) ---
            # ce3.py sends tool results back as role:user, content: [{type:tool_result, ...}]
            elif role == 'user' and isinstance(content, list) and content and content[0].get('type') == 'tool_result':
                self.logger.debug(f"Detected user message containing tool results: {content}")
                # Convert each tool result into a separate OpenAI tool message
                for item in content:
                    if item.get('type') == 'tool_result':
                        tool_use_id = item.get('tool_use_id')
                        tool_output = item.get('content')
                        if not tool_use_id:
                            self.logger.error(f"Tool result item missing 'tool_use_id': {item}")
                            continue # Skip invalid tool result message

                        formatted_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_use_id,
                            "content": str(tool_output) # Content must be a string
                        })
                        self.logger.debug(f"Formatted tool result for tool_call_id: {tool_use_id}")
                    else:
                         self.logger.warning(f"Found unexpected item type within user tool result message: {item.get('type')}")

            # --- Handle Regular User/Assistant Messages (excluding tool use/result handling above) ---
            elif role in ['user', 'assistant']:
                 if isinstance(content, str):
                     formatted_messages.append({"role": role, "content": content})
                 elif isinstance(content, list):
                     # This branch should now mainly handle multimodal user messages
                     openai_parts = []
                     for item in content:
                         if item.get('type') == 'text':
                             openai_parts.append({'type': 'text', 'text': item.get('text', '')})
                         elif item.get('type') == 'image' and item.get('source', {}).get('type') == 'base64':
                             source = item['source']
                             media_type = source.get('media_type', 'image/jpeg')
                             base64_data = source.get('data', '')
                             if base64_data:
                                 openai_parts.append({
                                     'type': 'image_url',
                                     'image_url': {'url': f'data:{media_type};base64,{base64_data}'}
                                 })
                             else:
                                 self.logger.warning("Image message part missing base64 data.")
                         else:
                             # Avoid logging 'tool_result' here as it's handled above
                             if item.get('type') != 'tool_result': 
                                 self.logger.warning(f"Unsupported item type in {role} message content list: {item.get('type')}")
                     if openai_parts:
                          formatted_messages.append({"role": role, "content": openai_parts})
                     # Decide how to handle user messages that *only* contained unsupported types (or were empty lists)
                     # else: maybe append a placeholder or skip?
                     #     formatted_messages.append({"role": role, "content": "[Unsupported list content]"})
                 else:
                    self.logger.warning(f"Unexpected content type in {role} message: {type(content)}. Converting to string.")
                    formatted_messages.append({"role": role, "content": str(content)})
            
            # --- Skip System/Other roles ---
            elif role == 'system':
                 self.logger.debug("Skipping system message during history formatting.")
            else:
                 self.logger.warning(f"Skipping message with unhandled role: {role}")

        return formatted_messages

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """Send chat request to OpenAI API."""
        if not self.client:
            return {
                'content': [{'type': 'text', 'text': 'OpenAI API key not configured. Cannot process request.'}],
                'usage': {'input_tokens': 0, 'output_tokens': 0},
                'stop_reason': 'error'
            }

        # --- Normalize message blocks for OpenAI only ---
        messages = self._normalize_message_blocks(messages)
        # --- End normalization ---

        # Extract system prompt if present (OpenAI prefers it separate)
        system_prompt = None
        user_messages = []
        if messages and messages[0].get('role') == 'system':
             system_prompt = messages[0].get('content')
             # Check if content is complex (list) and extract text if possible
             if isinstance(system_prompt, list):
                 system_prompt_text = next((item.get('text') for item in system_prompt if item.get('type') == 'text'), None)
                 if system_prompt_text:
                     system_prompt = system_prompt_text
                 else:
                     self.logger.error("System prompt was a list but contained no text part. Ignoring.")
                     system_prompt = None # Ignore non-text system prompt for OpenAI
             user_messages = messages[1:]
             self.logger.debug(f"Using system prompt: {str(system_prompt)[:100]}...") # Log beginning
        else:
             user_messages = messages # No system prompt found

        self.logger.debug(f"Sending request to OpenAI with {len(user_messages)} history messages and {len(tools)} tools.")
        openai_tools = self._format_tools_for_openai(tools)
        formatted_history = self._format_messages_for_openai(user_messages)

        # Determine the model to use (can be made dynamic later)
        # Defaulting to gpt-4o-mini for cost/performance balance
        model_name = getattr(config, 'OPENAI_MODEL', 'gpt-4o-mini')
        self.logger.debug(f"Using OpenAI model: {model_name}")

        request_params = {
            "model": model_name,
            "messages": formatted_history,
            "tools": openai_tools if openai_tools else None,
            "tool_choice": "auto" if openai_tools else None,
            "temperature": config.DEFAULT_TEMPERATURE,
            "max_tokens": config.MAX_TOKENS
        }
        # Add system prompt if extracted
        if system_prompt:
            request_params["system"] = system_prompt

        try:
            # Make the API call
            response = self.client.chat.completions.create(**request_params)

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
                    try:
                        # Map OpenAI tool call format to Claude-like format for ce3.py handler
                        response_content.append({
                            "type": "tool_use",
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "input": json.loads(tool_call.function.arguments) # Arguments are JSON strings
                        })
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to parse JSON arguments for tool call {tool_call.function.name}: {tool_call.function.arguments}")
                        response_content.append({
                             "type": "text",
                             "text": f"[Error processing tool call {tool_call.function.name}: Invalid arguments format]"
                        })
                    except Exception as e:
                        self.logger.exception(f"Error processing tool call: {e}")
                        response_content.append({
                             "type": "text",
                             "text": f"[Error processing tool call {tool_call.function.name}]"
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
            raise ConnectionError(f"OpenAI API error (Status {e.status_code}): {e.response.json().get('error', {}).get('message', e.response.text)}") from e
        except Exception as e:
            self.logger.exception("An unexpected error occurred during OpenAI API call")
            raise RuntimeError(f"An unexpected error occurred interacting with OpenAI: {e}") from e 