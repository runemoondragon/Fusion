import re
import json
from typing import List, Dict, Any, Union

def _to_dict_if_possible(obj: Any) -> Union[Dict, Any]:
    """Convert object to dictionary if possible, otherwise return as-is."""
    if hasattr(obj, 'dict') and callable(getattr(obj, 'dict', None)):
        return obj.dict()
    if hasattr(obj, '__dict__') and hasattr(obj, 'type'):
        # For Anthropic blocks like TextBlock, ToolUseBlock, etc.
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return obj

def _deep_sanitize(obj: Any) -> Any:
    """Recursively sanitize nested structures by converting to dicts where possible."""
    if isinstance(obj, list):
        return [_deep_sanitize(_to_dict_if_possible(item)) for item in obj]
    elif isinstance(obj, dict):
        return {k: _deep_sanitize(_to_dict_if_possible(v)) for k, v in obj.items()}
    else:
        return _to_dict_if_possible(obj) # Ensure top-level non-list/dict are also processed by _to_dict_if_possible

def sanitize_history(history: List[Dict], provider: str) -> List[Dict]:
    """
    Clean and reformat conversation history depending on the destination provider.
    This prevents cross-model formatting issues.
    
    Args:
        history: List of message dictionaries with 'role' and 'content' keys
        provider: Target AI provider ('gemini', 'openai', or 'claude')
    
    Returns:
        List of sanitized message dictionaries
    """
    if not isinstance(history, list):
        raise TypeError(f"Expected history to be a list, got {type(history)}")    

    sanitized = []
    valid_providers = {'gemini', 'openai', 'claude'}
    
    if provider not in valid_providers:
        raise ValueError(f"Provider must be one of {valid_providers}, got {provider}")

    # First pass: deep sanitize all messages to ensure they are dicts with basic structure
    # and content is also recursively sanitized to basic Python types (dicts, lists, strings).
    pre_sanitized_history = []
    for message in history:
        if not isinstance(message, dict): continue # Skip non-dict messages
        role = message.get("role")
        content = message.get("content") # Raw content
        if not role or content is None: continue

        try:
            # Convert Pydantic objects, Anthropic blocks etc., to dicts recursively
            # This ensures content is a serializable structure (dict, list, or primitive)
            processed_content = _deep_sanitize(content)
            pre_sanitized_history.append({"role": role, "content": processed_content})
        except Exception as e:
            print(f"Warning: Deep sanitization failed for message role {role}: {e}. Skipping message.")
            continue
            
    # Second pass: provider-specific formatting and alternation logic
    final_sanitized_history = []

    if provider == 'openai':
        last_was_assistant_tool_request = False
        for i, message in enumerate(pre_sanitized_history):
            role = message["role"]
            current_content = message["content"] # This is now a dict/list/str from _deep_sanitize

            if role == "assistant":
                # Check if content contains what looks like a tool_use request
                # openai_provider.py will convert this to "tool_calls"
                if isinstance(current_content, list) and any(isinstance(part, dict) and part.get("type") == "tool_use" for part in current_content):
                    final_sanitized_history.append(message) 
                    last_was_assistant_tool_request = True
                else:
                    final_sanitized_history.append({"role": role, "content": _sanitize_for_openai(current_content)})
                    last_was_assistant_tool_request = False
            
            elif role == "user":
                is_tool_result_message = False
                if isinstance(current_content, list) and current_content and isinstance(current_content[0], dict) and current_content[0].get("type") == "tool_result":
                    is_tool_result_message = True

                if is_tool_result_message:
                    if last_was_assistant_tool_request:
                        # Valid: assistant tool_use -> user tool_result.
                        # Pass as is; openai_provider will convert role to "tool" & add tool_call_id.
                        # Content of each tool_result part should be string. ce3.py ensures this.
                        final_sanitized_history.append(message) 
                    else:
                        # Invalid: user tool_result without preceding assistant tool_use. Convert to text.
                        summary_parts = []
                        for part in current_content: 
                            if isinstance(part, dict) and part.get("type") == "tool_result":
                                tool_name = part.get("name", part.get("tool_name", "[unknown_tool]"))
                                tool_output_summary = str(part.get("content", "[no_result]"))[:100] 
                                summary_parts.append(f"[User-provided tool result for '{tool_name}' (output: {tool_output_summary}...) was removed due to invalid sequence for OpenAI.]")
                        if summary_parts:
                             final_sanitized_history.append({"role": "user", "content": _sanitize_for_openai(" ".join(summary_parts))})
                    last_was_assistant_tool_request = False 
                else:
                    final_sanitized_history.append({"role": role, "content": _sanitize_for_openai(current_content)})
                    last_was_assistant_tool_request = False
            
            elif role == "tool": # This message already has role "tool" (likely from a previous OpenAI turn)
                                 # openai_provider expects content to be a string and tool_call_id to be present.
                                 # The _sanitize_for_openai should just ensure content is string.
                                 # The original message should have tool_call_id if it was valid.
                if i > 0 and final_sanitized_history and final_sanitized_history[-1].get("role") == "assistant": 
                     # And ideally check if that assistant message had tool_calls.
                     # For now, if it follows an assistant, assume it's part of a valid sequence.
                     message["content"] = str(message.get("content", "")) # Ensure content is string
                     final_sanitized_history.append(message)
                else:
                      summary = f"[Standalone 'role:tool' message (tool_call_id: {message.get('tool_call_id')}, content: {str(message.get('content'))[:100]}) converted to user text due to missing preceding assistant tool_call.]"
                      final_sanitized_history.append({"role": "user", "content": _sanitize_for_openai(summary)})
                last_was_assistant_tool_request = False
            
            else: # system, other valid roles
                # For system messages, content should be string for OpenAI.
                if role == "system":
                    message["content"] = str(message.get("content", "")) # Ensure string
                final_sanitized_history.append(message)
                last_was_assistant_tool_request = False
        return final_sanitized_history

    # Simplified general loop for Claude and Gemini (they are more flexible with role:user for tool results)
    # The main job here is to use the provider-specific content sanitizer.
    # Alternation logic for tool_use/tool_result is less strict or handled differently by their APIs / ce3.py sending role:user for results.
    for message in pre_sanitized_history:
        role = message["role"]
        current_content = message["content"]
        
        try:
            if provider == "claude":
                sanitized_content = _sanitize_for_claude(current_content)
            elif provider == "gemini":
                sanitized_content = _sanitize_for_gemini(current_content)
            else: # Should not happen due to guard clause, but as a fallback
                sanitized_content = str(current_content) 

            final_sanitized_history.append({"role": role, "content": sanitized_content})
        except Exception as e:
            print(f"Warning: Provider-specific sanitization for {provider} failed for role {role}: {e}. Skipping message.")
            continue
            
    return final_sanitized_history

def _sanitize_for_gemini(content: Any) -> Any:
    """Convert content to a list of Gemini 'parts', translating tool_use/tool_result appropriately."""
    
    gemini_parts = []

    if not isinstance(content, list): # If content is not a list (e.g. str or single dict), wrap it in a list to process uniformly
        content_list = [content]
    else:
        content_list = content

    for item in content_list:
        if isinstance(item, dict):
            part_type = item.get("type")
            if part_type == "text":
                gemini_parts.append({"text": item.get("text", "")})
            elif part_type == "image" and item.get("source", {}).get("type") == "base64":
                source = item["source"]
                # For sanitization, represent as text. Actual image upload to Gemini is by provider.
                gemini_parts.append({"text": f"[Image content: {source.get('media_type', 'image/jpeg')}, data omitted for history sanitization]"})
            
            elif part_type == "tool_use":
                tool_name = item.get("name")
                tool_input_args = item.get("input", {})
                if tool_name:
                    # Convert input args to a simple dict if it's not already (Gemini expects a plain dict for args)
                    # The _deep_sanitize earlier should have handled Pydantic objects, but ensure it's basic.
                    processed_args = {k: v for k, v in tool_input_args.items()} if isinstance(tool_input_args, dict) else {}
                    gemini_parts.append({
                        "function_call": {
                            "name": tool_name,
                            "args": processed_args
                        }
                    })
                else:
                    gemini_parts.append({"text": "[Invalid 'tool_use' part encountered: missing name]"})
            
            elif part_type == "tool_result":
                # For Gemini, tool_result needs to be a "function_response".
                # The 'name' in function_response should match the 'name' from the corresponding 'function_call'.
                # The 'tool_use_id' from the shared history format often serves as the 'name' for matching.
                # Some LLMs use the tool_name directly as this identifier in their request/response.
                # We need to get the 'name' of the tool this result is for.
                # Assuming 'tool_use_id' from input part IS the function name for Gemini's matching.
                # Or, if 'name' or 'tool_name' field is present in the tool_result part, use that.
                
                # Heuristic: The 'id' of a tool_use block often becomes the 'tool_use_id' of a tool_result.
                # Gemini's FunctionResponse expects 'name' to be the function name.
                # Let's assume 'tool_use_id' in the incoming 'tool_result' part is the function's name.
                # If 'name' or 'tool_name' is explicitly in the part, prioritize that.
                function_name = item.get("name", item.get("tool_name", item.get("tool_use_id")))
                
                result_content = item.get("content", "") # This should be the string output from the tool (e.g. error message)

                if function_name:
                    gemini_parts.append({
                        "function_response": {
                            "name": function_name,
                            "response": {
                                # Gemini expects the 'response' to contain the actual content from the tool.
                                # This content should be serializable (e.g., string, dict).
                                # If 'result_content' is a simple string (like an error message), it's fine.
                                # If it's JSON string, it might need to be parsed if Gemini expects a dict,
                                # or kept as string if Gemini expects a stringified JSON.
                                # For now, let's assume 'content' from tool result is the direct data.
                                # The `_execute_tool` in `ce3.py` returns a string.
                                "content": result_content
                            }
                        }
                    })
                else:
                    gemini_parts.append({"text": "[Invalid 'tool_result' part encountered: missing function name/id]"})
            
            else: # Unknown dict part, or dict without a recognized 'type'
                # Convert to text to avoid Gemini API errors with unexpected structures
                gemini_parts.append({"text": f"[Unsupported structured part converted to text: {str(item)[:100]}]"})
        
        elif isinstance(item, str): # If item in content_list is just a string
            gemini_parts.append({"text": item})
        
        else: # Other non-dict, non-string items in content_list
             gemini_parts.append({"text": f"[Unsupported content type '{type(item)}' converted to text: {str(item)[:100]}]"})

    # Ensure we always return some parts, even if it's just a placeholder for empty/fully unsupported content
    return gemini_parts if gemini_parts else [{"text": "[Content was empty or fully unsupported after sanitization for Gemini]"}]

def _sanitize_for_openai(content: Any) -> Any:
    """
    Prepares content for OpenAI.
    - If content is from a 'tool_result' (already a string by the time it gets here), keep as string.
    - If content is a list (e.g. from Claude/Gemini text/image blocks):
        - Convert to OpenAI's expected list of content parts (text, image_url).
        - If it contains unsupported types for a simple user/assistant message 
          (like 'tool_use' or 'tool_result' types that shouldn't be here directly),
          convert them to a text placeholder.
    - If content is a simple string, return as is.
    """
    if isinstance(content, str): # Could be a simple text message or already stringified tool result from previous step
        return content

    if isinstance(content, list):
        openai_parts = []
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type")
                if part_type == "text":
                    openai_parts.append({"type": "text", "text": part.get("text", "")})
                elif part_type == "image_url": 
                    openai_parts.append(part)
                elif part_type == "image" and part.get("source", {}).get("type") == "base64":
                    source = part["source"]
                    openai_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{source.get('media_type', 'image/jpeg')};base64,{source.get('data', '')}"
                        }
                    })
                elif part_type in {"tool_result", "tool_use"}: # These should not be directly inside a message content list for OpenAI user/assistant text messages
                    openai_parts.append({"type": "text", "text": f"[Unsupported content part type '{part_type}' in message was converted to text.]"})
                else: 
                    text_val = part.get("text", str(part)) # Fallback for other dicts
                    openai_parts.append({"type": "text", "text": text_val})
            elif isinstance(part, str):
                openai_parts.append({"type": "text", "text": part})
        return openai_parts if openai_parts else [{"type": "text", "text": "[Empty or unsupported list content]"}] # Ensure not empty list
        
    if isinstance(content, dict): # Fallback for a single dict as content not in a list
        # If it's a 'tool_use' or 'tool_result' dict here, it means it wasn't in a list.
        # This shouldn't happen for standard message content parts but as a safeguard:
        if content.get("type") in {"tool_use", "tool_result"}:
             return f"[Unsupported content type '{content.get('type')}' at top level of message content converted to text.]"
        return str(content) 

    return content

def _sanitize_for_claude(content: Any) -> Any:
    """Clean up and standardize format for Claude."""
    if isinstance(content, str): # If already a simple string, pass through
        return content
    
    if isinstance(content, list):
        cleaned_parts = []
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type")
                # Claude expects text, image, tool_use, tool_result
                if part_type in {"text", "image", "tool_use", "tool_result"}:
                    # For tool_result, Claude doesn't want 'tool_name' (it uses tool_use_id)
                    if part_type == "tool_result" and "tool_name" in part:
                        # ce3.py adds tool_use_id, this is more about incoming history from other models
                        clean_part = {k:v for k,v in part.items() if k != "tool_name"}
                        cleaned_parts.append(clean_part)
                    else:
                        cleaned_parts.append(part)
                else: # Convert unknown dict parts to text
                    cleaned_parts.append({"type": "text", "text": str(part)})
            elif isinstance(part, str): # Convert string parts in list to Claude text block
                cleaned_parts.append({"type": "text", "text": part})
            else: # Pass through other types if any (should be rare)
                cleaned_parts.append(part)
        return cleaned_parts if cleaned_parts else [{"type": "text", "text": "[Empty or unsupported list content]"}]

    if isinstance(content, dict): # Single dict as content
        # Similar to list, ensure type is one Claude expects or convert
        part_type = content.get("type")
        if part_type in {"text", "image", "tool_use", "tool_result"}:
            if part_type == "tool_result" and "tool_name" in content:
                 return {k:v for k,v in content.items() if k != "tool_name"}
            return content
        else:
            return {"type": "text", "text": str(content)}
            
    return content # Fallback