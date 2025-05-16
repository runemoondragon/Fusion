from typing import List, Dict, Any
import logging
import os
import json
import time

# Attempt to import the google.generativeai library
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold, FunctionDeclaration, Tool
except ImportError:
    raise ImportError("The 'google-generativeai' library is required for GeminiProvider. Please install it using: pip install google-generativeai")

from .base_provider import BaseProvider
from config import Config

# Mapping from internal roles to Gemini roles
ROLE_MAPPING = {
    "user": "user",
    "assistant": "model" 
    # System prompts are handled differently in Gemini (as of latest versions)
}

class GeminiProvider(BaseProvider):
    """Provider implementation for Google's Gemini API."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        if not Config.GEMINI_API_KEY:
            self.logger.warning("GEMINI_API_KEY not found in environment variables. Gemini provider will not work.")
        else:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                # Choose a model - let's use a recent one capable of function calling
                model_name = getattr(Config, 'GEMINI_MODEL', 'gemini-1.5-flash-latest') 
                # TODO: Consider adding safety settings configuration
                self.model = genai.GenerativeModel(
                    model_name,
                    # Example Safety Settings (adjust as needed)
                    # safety_settings={
                    #     HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    #     HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    # }
                )
                self.logger.info(f"Gemini client configured for model: {model_name}")
            except Exception as e:
                self.logger.exception("Failed to configure Gemini client")
                # Keep self.model as None

    @property
    def name(self) -> str:
        return "GeminiProvider"

    def _sanitize_schema_for_gemini(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize schema fields for Gemini compatibility."""
        if not isinstance(schema, dict):
            return schema

        unsupported_fields = ["default", "additionalProperties", "oneOf", "minItems", "maxItems", "pattern", "format"]
        
        sanitized = {}
        # Temporarily store items schema if type is list containing 'array'
        items_schema = schema.get('items') 

        for key, value in schema.items():
            if key in unsupported_fields:
                self.logger.warning(f"Removing unsupported Gemini schema field: '{key}'")
                continue
            elif key == 'type':
                # Handle type field: 
                if isinstance(value, list):
                    # If list contains 'array', prioritize it
                    if "array" in value:
                        self.logger.warning(f"Prioritizing 'array' type from list {value} for Gemini.")
                        sanitized[key] = "array"
                        # Keep items_schema for potential later use
                    elif value: # Pick the first non-array type if 'array' is not present
                        primary_type = next((t for t in value if isinstance(t, str) and t != "array"), None)
                        if primary_type:
                             self.logger.warning(f"Converting list type {value} to single type '{primary_type}' for Gemini.")
                             sanitized[key] = primary_type
                             items_schema = None # Discard items if final type is not array
                        else:
                             self.logger.error(f"Skipping list type {value} as no valid primary string type found.")
                             continue
                    else: # Skip empty list type
                        self.logger.warning(f"Skipping empty list type for key '{key}'")
                        continue
                elif isinstance(value, str): # Keep valid string types
                     sanitized[key] = value
                     if value != "array": items_schema = None # Discard items if type is not array
                else: # Skip invalid types
                     self.logger.warning(f"Skipping invalid type value '{value}' for key '{key}'")
                     continue
            # Skip processing 'items' here, handle it after determining the final type
            elif key == 'items':
                 continue 
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_schema_for_gemini(value)
            elif isinstance(value, list):
                # Sanitize list elements recursively
                sanitized[key] = [self._sanitize_schema_for_gemini(item) for item in value if item is not None] # Skip None items
            else:
                sanitized[key] = value

        # After processing other keys, handle 'items' based on the final type
        final_type = sanitized.get('type')
        if final_type == "array":
            if items_schema:
                 # Ensure items_schema is a dict (schema object)
                 if isinstance(items_schema, list):
                     # If original items was a list, take the first element as schema
                     if items_schema:
                         items_schema = items_schema[0]
                     else:
                          items_schema = None # No valid schema found
                 
                 if isinstance(items_schema, dict):
                      sanitized_items = self._sanitize_schema_for_gemini(items_schema)
                      if sanitized_items and sanitized_items.get('type'): # Ensure sanitized items schema is valid
                          sanitized['items'] = sanitized_items
                      else:
                           self.logger.error(f"Invalid 'items' schema after sanitization for array type: {items_schema}. Removing.")
                 else:
                      self.logger.error(f"Invalid 'items' value for array type: {items_schema}. Removing.")
            else:
                 # If type is array but no items were defined, it's invalid for Gemini?
                 self.logger.warning(f"Schema type is 'array' but 'items' is missing or invalid. Removing type.")
                 del sanitized['type'] # Remove type to make schema potentially valid as simple type

        # Ensure 'type': 'object' exists if 'properties' exists
        if "properties" in sanitized and "type" not in sanitized:
            # Check if it was explicitly set to array previously
            if final_type != 'array': 
                self.logger.warning("Adding missing 'type': 'object' for schema with properties.")
                sanitized["type"] = "object"
            
        # Final validation removed as it might be too strict, let Gemini API handle final validation
        # if ("properties" in sanitized or "items" in sanitized):
        #     if "type" not in sanitized or not isinstance(sanitized.get("type"), str):
        #          self.logger.error(f"Schema invalid after sanitization (missing/invalid type): {sanitized}")
        #          return {}

        return sanitized

    def _format_tools_for_gemini(self, tools: List[Dict[str, Any]]) -> Tool | None:
        """Convert the internal tool format to Gemini's FunctionDeclaration list within a Tool object, sanitizing the schema."""
        if not tools:
            return None
        
        function_declarations = []
        for tool_spec in tools:
            try:
                if not all(k in tool_spec for k in ['name', 'description', 'input_schema']):
                     self.logger.warning(f"Skipping tool '{tool_spec.get('name')}' due to missing keys for Gemini format.")
                     continue

                original_schema = tool_spec['input_schema']
                sanitized_schema = self._sanitize_schema_for_gemini(original_schema)
                
                # Check if sanitization resulted in an empty/invalid schema
                if not sanitized_schema or not isinstance(sanitized_schema, dict) or not sanitized_schema.get('type'):
                     self.logger.error(f"Skipping tool '{tool_spec.get('name')}' after schema sanitization resulted in invalid format: {sanitized_schema}")
                     continue

                function_declaration = FunctionDeclaration(
                    name=tool_spec['name'],
                    description=tool_spec['description'],
                    parameters=sanitized_schema
                )
                function_declarations.append(function_declaration)
            except Exception as e:
                # Log the full traceback for unexpected errors during formatting
                self.logger.exception(f"Unexpected error formatting tool '{tool_spec.get('name')}' for Gemini: {e}")

        return Tool(function_declarations=function_declarations) if function_declarations else None

    def _format_messages_for_gemini(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
         """Convert message history to Gemini's format, handling roles and content types."""
         gemini_history = []
         system_prompt = None # System prompts handled separately
         # Potentially extract system prompt if it exists (though not standard in history)
         # if messages and messages[0]['role'] == 'system':
         #     system_prompt = messages[0]['content']
         #     messages = messages[1:]

         for msg in messages:
             role = ROLE_MAPPING.get(msg['role'])
             content = msg.get('content')

             if not role:
                 self.logger.warning(f"Skipping message with unmapped role: {msg['role']}")
                 continue

             # Gemini expects 'parts' which is a list.
             # Handle different content structures (string, list of blocks)
             parts = []
             if isinstance(content, str):
                 parts.append({"text": content})
             elif isinstance(content, list):
                 # Process potential multimodal or tool result content
                 for item in content:
                     if isinstance(item, dict):
                         if item.get('type') == 'text':
                             parts.append({"text": item.get('text', '')})
                         elif item.get('type') == 'image':
                             # Requires image bytes or specific format, handle base64
                             source = item.get('source', {})
                             if source.get('type') == 'base64':
                                 # TODO: Need image processing to convert base64 to bytes/PIL Image
                                 self.logger.warning("Image parts not yet fully supported for Gemini base64.")
                                 # parts.append({"inline_data": {"mime_type": source.get('media_type'), "data": base64.b64decode(source.get('data'))}})
                         elif item.get('type') == 'tool_result':
                              # Gemini expects FunctionResponse part for tool results
                              parts.append({
                                  "function_response": {
                                      "name": item.get('tool_name'), # Needs tool_name in result? Check ce3.py
                                      # Content might be complex, Gemini expects serializable response
                                      "response": {"content": json.dumps(item.get('content'))}
                                  }
                              })
                         elif item.get('type') == 'tool_use': # Assistant decided to use tool
                              # Map to FunctionCall for Gemini history
                             parts.append({
                                 "function_call": {
                                     "name": item.get('name'),
                                     "args": item.get('input') # Assumes input is dict
                                 }
                             })
                     elif isinstance(item, str): # Simple string in list?
                          parts.append({"text": item})
             
             if parts:
                 gemini_history.append({"role": role, "parts": parts})

         # TODO: Handle system prompt if needed (passed separately to generate_content)
         return gemini_history

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], config: Config) -> Dict[str, Any]:
        """Send chat request to Gemini API."""
        if not self.model:
            return {
                'content': [{'type': 'text', 'text': 'Gemini client not configured (check API key?). Cannot process request.'}],
                'usage': {'input_tokens': 0, 'output_tokens': 0, 'runtime': 0.0},
                'stop_reason': 'error'
            }
        
        self.logger.debug(f"Sending request to Gemini with {len(messages)} messages and {len(tools)} tools.")
        gemini_tools = self._format_tools_for_gemini(tools)
        gemini_history = self._format_messages_for_gemini(messages)
        
        # Extract latest user message as the current prompt for generate_content
        # The history should contain previous turns
        if not gemini_history:
             return {'content': [{'type': 'text', 'text': 'Cannot send empty message history to Gemini.'}], 'usage': {'input_tokens': 0, 'output_tokens': 0}, 'stop_reason': 'error'}
        
        # Note: Gemini API structure might prefer a conversational chat session
        # chat_session = self.model.start_chat(history=gemini_history[:-1]) # History excluding last message
        # response = chat_session.send_message(gemini_history[-1]['parts'], tools=gemini_tools)
        # Simpler approach for now: send full history directly if supported
        try:
            start_time = time.time()
            response = self.model.generate_content(
                gemini_history, 
                tools=gemini_tools,
                generation_config=genai.types.GenerationConfig(
                     # candidate_count=1, # Default
                     # stop_sequences=['...'],
                     # max_output_tokens=config.MAX_TOKENS, # Set max output tokens
                     temperature=config.DEFAULT_TEMPERATURE
                 )
            )
            end_time = time.time()
            runtime = end_time - start_time

            # Extract content and usage
            response_content = []
            finish_reason = "unknown"
            input_token_count = 0
            output_token_count = 0

            if response.candidates:
                 candidate = response.candidates[0]
                 finish_reason = candidate.finish_reason.name if candidate.finish_reason else "unknown"

                 # --- Calculate Token Usage --- >
                 try:
                     # Count input tokens (using the history sent)
                     input_token_result = self.model.count_tokens(gemini_history)
                     input_token_count = input_token_result.total_tokens
                     self.logger.debug(f"Gemini calculated input tokens: {input_token_count}")
                 except Exception as e:
                     self.logger.error(f"Failed to count Gemini input tokens: {e}")

                 try:
                     # Count output tokens (using the candidate content)
                     if candidate.content and candidate.content.parts:
                         output_token_result = self.model.count_tokens(candidate.content)
                         output_token_count = output_token_result.total_tokens
                         self.logger.debug(f"Gemini calculated output tokens: {output_token_count}")
                 except Exception as e:
                     self.logger.error(f"Failed to count Gemini output tokens: {e}")
                 # < --- End Token Usage Calculation ---

                 if candidate.content and candidate.content.parts:
                     for part in candidate.content.parts:
                         if hasattr(part, 'text') and part.text:
                             response_content.append({"type": "text", "text": part.text})
                         elif hasattr(part, 'function_call'):
                             # Map Gemini function call to Claude-like format
                             fc = part.function_call
                             response_content.append({
                                 "type": "tool_use",
                                 "id": fc.name, # Gemini doesn't seem to provide a unique ID per call like others
                                 "name": fc.name,
                                 "input": dict(fc.args) if hasattr(fc, 'args') else {} # Convert args MapComposite to dict
                             })
                             # Standardize finish reason
                             finish_reason = "tool_calls" 
            else:
                 # Handle blocked responses
                 self.logger.warning(f"Gemini response potentially blocked. Prompt feedback: {response.prompt_feedback}")
                 finish_reason = "blocked" # Or map from prompt_feedback
                 response_content = [{'type': 'text', 'text': '[Response blocked by safety settings or other reasons]'}]

            # Prepare final usage dictionary
            usage_dict = {
                'input_tokens': input_token_count,
                'output_tokens': output_token_count,
                'runtime': runtime
            }

            self.logger.debug(f"Gemini usage: input_tokens={input_token_count}, output_tokens={output_token_count}, runtime={runtime}")
            return {
                'content': response_content,
                'usage': usage_dict,
                'stop_reason': finish_reason.lower()
            }

        except Exception as e:
            self.logger.exception("An unexpected error occurred during Gemini API call")
            # You might want to inspect the specific error type from google.api_core.exceptions
            raise RuntimeError(f"An unexpected error occurred interacting with Gemini: {e}") from e 

    def _prepare_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # ... existing helper ...
        pass

    def _prepare_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # ... existing helper ...
        pass

    def _parse_response(self, response) -> Dict[str, Any]:
        # ... existing helper ...
        pass 