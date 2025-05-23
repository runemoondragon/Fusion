from typing import List, Dict, Any
import logging
import os
import json
import time

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

    def __init__(self, api_key: str = None):
        self.logger = logging.getLogger(__name__)
        self.client = None 

        final_api_key_to_use = api_key # This is the key selected by app.py

        if final_api_key_to_use:
            # app.py has already logged the original source (header or .env)
            try:
                self.client = openai.OpenAI(api_key=final_api_key_to_use)
                # Simplified log: app.py now logs the source more accurately.
                self.logger.info(f"OpenAI client configured with the API key selected by application logic.")
            except Exception as e:
                self.logger.exception(f"Failed to initialize OpenAI client with the API key selected by application logic: {e}")
                self.client = None # Ensure client is None if initialization fails
        else:
            # This case means app.py found NO key (neither header nor .env for OpenAI)
            self.logger.warning(f"No API key was determined by application logic for OpenAI. OpenAI provider will not work.")
            # self.client remains None

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
            content = msg.get('content') # This content is already processed by context_sanitizer

            if role == 'assistant':
                assistant_text_accumulated = []
                assistant_tool_calls = []
                has_any_tool_use_defined = False # To track if a tool_use was seen, even if it failed to format

                if isinstance(content, list):
                    for item in content:
                        if not isinstance(item, dict):
                            self.logger.warning(f"Assistant message content part is not a dict: {item}. Skipping.")
                            continue
                        
                        item_type = item.get('type')
                        if item_type == 'text':
                            assistant_text_accumulated.append(item.get('text', ''))
                        elif item_type == 'tool_use':
                            has_any_tool_use_defined = True
                            tool_id = item.get('id')
                            tool_name = item.get('name')
                            tool_input_args = item.get('input', {})
                            
                            if not tool_id or not tool_name:
                                self.logger.error(f"Assistant tool_use item missing id or name: {item}. Skipping this tool_call.")
                                continue

                            tool_arguments_str = ""
                            if isinstance(tool_input_args, str):
                                tool_arguments_str = tool_input_args
                            elif isinstance(tool_input_args, dict):
                                try:
                                    tool_arguments_str = json.dumps(tool_input_args)
                                except TypeError as e:
                                    self.logger.error(f"Could not serialize tool arguments to JSON for tool '{tool_name}': {tool_input_args}. Error: {e}")
                                    tool_arguments_str = "{}"
                            else:
                                self.logger.warning(f"Tool arguments for tool '{tool_name}' are not a dict or string: {tool_input_args}. Using empty JSON object string.")
                                tool_arguments_str = "{}"

                            assistant_tool_calls.append({
                                "id": tool_id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_arguments_str
                                }
                            })
                        else:
                            self.logger.warning(f"Unsupported part type '{item_type}' in assistant message content: {item}. It will be ignored.")

                elif isinstance(content, str):
                    assistant_text_accumulated.append(content)
                elif content is None and role == 'assistant':
                    pass
                else:
                    self.logger.warning(f"Assistant message content is of unexpected type or None: {type(content)}. Content: {content}")

                openai_assistant_msg = {"role": "assistant"}
                final_assistant_text_content = " ".join(filter(None, assistant_text_accumulated)).strip()

                if assistant_tool_calls:
                    openai_assistant_msg["tool_calls"] = assistant_tool_calls
                    if final_assistant_text_content:
                        openai_assistant_msg["content"] = final_assistant_text_content
                    else:
                        openai_assistant_msg["content"] = None
                elif final_assistant_text_content:
                    openai_assistant_msg["content"] = final_assistant_text_content
                else:
                    if has_any_tool_use_defined and not assistant_tool_calls:
                        self.logger.error(f"Assistant message contained tool_use parts that could not be formatted: {content}")
                        openai_assistant_msg["content"] = "[Internal error: Failed to process tool calls for assistant message.]"
                        # Append this error message only if it's constructed
                        formatted_messages.append(openai_assistant_msg) 
                    elif content is not None and not isinstance(content, list) and not isinstance(content, str):
                         openai_assistant_msg["content"] = f"[Unparseable assistant content: {str(content)[:100]}]"
                         formatted_messages.append(openai_assistant_msg)
                    # elif not (final_assistant_text_content or assistant_tool_calls or (has_any_tool_use_defined and not assistant_tool_calls)):
                    #     self.logger.debug(f"Skipping empty or fully unhandled assistant message. Original content: {content}")
                    # The above elif is commented out to ensure that if an error message was set, it gets appended by the next check

                if "tool_calls" in openai_assistant_msg or ("content" in openai_assistant_msg and openai_assistant_msg["content"] is not None):
                    # Avoid appending if it was already appended due to an error message construction above
                    if not (has_any_tool_use_defined and not assistant_tool_calls and "content" in openai_assistant_msg and openai_assistant_msg["content"].startswith("[Internal error")) and \
                       not (content is not None and not isinstance(content, list) and not isinstance(content, str) and "content" in openai_assistant_msg and openai_assistant_msg["content"].startswith("[Unparseable assistant content")):
                        if openai_assistant_msg not in formatted_messages: # Ensure it wasn't added if an error message was already set and appended
                            formatted_messages.append(openai_assistant_msg)
                    
                    if assistant_tool_calls:
                         self.logger.debug(f"Formatted assistant message with tool_calls: {json.dumps(openai_assistant_msg, indent=2)}")
                    elif final_assistant_text_content:
                         self.logger.debug(f"Formatted assistant message with text content: {json.dumps(openai_assistant_msg, indent=2)}")

            elif role == 'user' and isinstance(content, list) and content and \
                 isinstance(content[0], dict) and content[0].get('type') == 'tool_result':
                self.logger.debug(f"Detected user message containing tool results: {content}")
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_result':
                        tool_use_id = item.get('tool_use_id')
                        tool_output = item.get('content')

                        if not tool_use_id:
                            self.logger.error(f"Tool result item missing 'tool_use_id': {item}. Skipping this result.")
                            continue
                        
                        tool_output_str = str(tool_output) if tool_output is not None else ""

                        formatted_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_use_id,
                            "content": tool_output_str
                        })
                        self.logger.debug(f"Formatted tool result for tool_call_id: {tool_use_id}")
                    else:
                         self.logger.warning(f"Found unexpected item within user-role tool result message list: {item}")

            elif role == 'user':
                 if isinstance(content, str):
                     formatted_messages.append({"role": "user", "content": content})
                 elif isinstance(content, list):
                     openai_parts = []
                     for item in content:
                         if not isinstance(item, dict):
                             self.logger.warning(f"User message content part is not a dict: {item}. Converting to text.")
                             openai_parts.append({'type': 'text', 'text': str(item)})
                             continue

                         item_type = item.get('type')
                         if item_type == 'text':
                             openai_parts.append({'type': 'text', 'text': item.get('text', '')})
                         elif item_type == 'image_url':
                             if isinstance(item.get("image_url"), dict) and "url" in item["image_url"]:
                                 openai_parts.append(item)
                             else:
                                 self.logger.warning(f"Malformed image_url part in user message: {item}. Skipping.")
                         else:
                             self.logger.warning(f"Unsupported item type '{item_type}' in user message content list: {item}. Converting to text representation.")
                             openai_parts.append({'type': 'text', 'text': f"[Unsupported content part: {str(item)[:100]}]"})
                     
                     if openai_parts:
                          formatted_messages.append({"role": "user", "content": openai_parts})
                     else:
                          self.logger.warning(f"User message content was a list but resulted in no processable OpenAI parts: {content}")
            
            elif role == 'system':
                 self.logger.debug(f"System message encountered in _format_messages_for_openai; should be handled by caller. Content: {str(content)[:100]}")
                 pass

            elif role == 'tool':
                tool_call_id = msg.get("tool_call_id")
                if not tool_call_id:
                    self.logger.error(f"Message with role 'tool' is missing 'tool_call_id': {msg}. Skipping.")
                    continue
                
                tool_content_str = str(msg.get("content", ""))

                formatted_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_content_str
                })
                self.logger.debug(f"Passed through existing 'tool' role message for tool_call_id: {tool_call_id}")
            else:
                 self.logger.warning(f"Skipping message with unhandled role '{role}' in _format_messages_for_openai")
        
        return formatted_messages

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """Send chat request to OpenAI API."""
        if not self.client:
            return {
                'content': [{'type': 'text', 'text': 'OpenAI API key not configured. Cannot process request.'}],
                'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0.0},
                'stop_reason': 'error'
            }

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

        self.logger.debug(f"OpenAIProvider: Messages to be formatted by _format_messages_for_openai: {json.dumps(user_messages, indent=2)}")
        openai_tools = self._format_tools_for_openai(tools)
        formatted_history = self._format_messages_for_openai(user_messages)
        self.logger.debug(f"OpenAIProvider: Messages after formatting by _format_messages_for_openai (sent to API): {json.dumps(formatted_history, indent=2)}")

        # Directly use Config.OPENAI_MODEL as it now has a guaranteed default
        model_name = Config.OPENAI_MODEL
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
            start_time = time.time()
            # Make the API call
            response = self.client.chat.completions.create(**request_params)
            end_time = time.time()
            runtime = end_time - start_time
            response_message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Extract usage data
            usage_data = response.usage
            usage_dict = {
                'input_tokens': getattr(usage_data, 'prompt_tokens', 0),
                'output_tokens': getattr(usage_data, 'completion_tokens', 0),
                'runtime': runtime
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

            self.logger.debug(f"OpenAI usage: input_tokens={usage_dict['input_tokens']}, output_tokens={usage_dict['output_tokens']}, runtime={runtime}")
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