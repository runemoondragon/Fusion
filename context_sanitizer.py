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
    """Remove or reformat structures that Gemini can't parse well in history from other models."""
    # Gemini expects content to be a list of "parts" (each part a dict, typically with 'text' or 'inline_data').
    # It's less tolerant of 'type' fields like 'tool_use' or 'tool_result' directly in history messages
    # that are not responses from Gemini itself (FunctionCall/FunctionResponse).
    
    if isinstance(content, str):
        return [{"text": content}] # Gemini wants parts to be a list of dicts

    gemini_parts = []
    if isinstance(content, list): # Content is already a list of parts (hopefully dicts)
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type")
                if part_type == "text":
                    gemini_parts.append({"text": part.get("text", "")})
                elif part_type == "image" and part.get("source", {}).get("type") == "base64":
                    source = part["source"]
                    # Gemini needs actual image bytes for inline_data, not just base64 string directly in "data" field
                    # This requires conversion. For sanitization, we might just represent it as text or omit.
                    # For now, let's represent as text. Actual image upload to Gemini is handled by provider.
                    gemini_parts.append({"text": f"[Image content: {source.get('media_type', 'image/jpeg')}, data omitted]"})
                elif part_type == "tool_use": # From Claude/OpenAI history
                    gemini_parts.append({"text": f"[Assistant tool call to '{part.get('name')}' with input '{part.get('input')}' omitted for Gemini history compatibility.]"})
                elif part_type == "tool_result": # From Claude/OpenAI history
                    gemini_parts.append({"text": f"[Tool result for '{part.get('tool_use_id')}' (content: '{str(part.get('content'))[:50]}...') omitted for Gemini history compatibility.]"})
                else: # Unknown dict part
                    gemini_parts.append({"text": str(part)}) # Convert to text
            elif isinstance(part, str):
                gemini_parts.append({"text": part})
    elif isinstance(content, dict): # Content is a single dict
        # Similar logic as above, try to convert based on 'type' or just stringify
        part_type = content.get("type")
        if part_type == "text":
            gemini_parts.append({"text": content.get("text", "")})
        elif part_type == "image": # ... (similar image handling as above) ...
            # This block was incomplete in the prompt, assuming placeholder for now or simple pass
            # For a real implementation, image handling logic for Gemini history would go here.
            # If just redacting, it could be: 
            # gemini_parts.append({"text": f"[Image content omitted for Gemini history.]"})
            pass # Placeholder, as the original logic was also 'pass'
        elif part_type == "tool_use":
             gemini_parts.append({"text": f"[Assistant tool call '{content.get('name')}' omitted.]"})
        elif part_type == "tool_result":
             gemini_parts.append({"text": f"[Tool result '{str(content.get('content'))[:50]}' omitted.]"})
        else:
            gemini_parts.append({"text": str(content)})
            
    return gemini_parts if gemini_parts else [{"text": "[Unsupported or empty content]"}]

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