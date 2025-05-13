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
    """Recursively sanitize nested structures."""
    if isinstance(obj, list):
        return [_deep_sanitize(_to_dict_if_possible(item)) for item in obj]
    elif isinstance(obj, dict):
        return {k: _deep_sanitize(_to_dict_if_possible(v)) for k, v in obj.items()}
    else:
        return obj

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

    # Special handling for OpenAI: enforce tool/tool_result alternation
    if provider == 'openai':
        last_was_tool_call = False
        for message in history:
            if not isinstance(message, dict):
                continue
            role = message.get("role", "")
            content = message.get("content", "")
            # Recursively sanitize content
            try:
                content = _deep_sanitize(content)
            except Exception as e:
                print(f"Warning: Failed to sanitize content: {e}")
                continue
            # Assistant tool_use block
            if role == "assistant" and isinstance(content, list) and any(
                isinstance(part, dict) and part.get("type") == "tool_use" for part in content
            ):
                sanitized.append({"role": role, "content": content})
                last_was_tool_call = True
            # User tool_result block
            elif role == "user" and isinstance(content, list) and any(
                isinstance(part, dict) and part.get("type") == "tool_result" for part in content
            ):
                if last_was_tool_call:
                    # Only keep if immediately after tool_use
                    sanitized.append({"role": role, "content": _sanitize_for_openai(content)})
                else:
                    # Convert to plain text summary to preserve context
                    summary = []
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "tool_result":
                            tool_name = part.get("tool_name", "[unknown tool]")
                            tool_content = part.get("content", "[no result]")
                            summary.append(f"[Tool result for {tool_name} omitted: {tool_content}]")
                    if summary:
                        sanitized.append({"role": role, "content": [{"type": "text", "text": ' '.join(summary)}]})
                last_was_tool_call = False
            else:
                # Regular message or other content
                sanitized.append({"role": role, "content": _sanitize_for_openai(content)})
                last_was_tool_call = False
        return sanitized

    # Special handling for Claude: enforce tool/tool_result alternation
    if provider == 'claude':
        last_was_tool_call = False
        for message in history:
            if not isinstance(message, dict):
                continue
            role = message.get("role", "")
            content = message.get("content", "")
            try:
                content = _deep_sanitize(content)
            except Exception as e:
                print(f"Warning: Failed to sanitize content: {e}")
                continue
            # Assistant tool_use block
            if role == "assistant" and isinstance(content, list) and any(
                isinstance(part, dict) and part.get("type") == "tool_use" for part in content
            ):
                sanitized.append({"role": role, "content": _sanitize_for_claude(content)})
                last_was_tool_call = True
            # User tool_result block
            elif role == "user" and isinstance(content, list) and any(
                isinstance(part, dict) and part.get("type") == "tool_result" for part in content
            ):
                if last_was_tool_call:
                    sanitized.append({"role": role, "content": _sanitize_for_claude(content)})
                else:
                    # Convert to plain text summary to preserve context
                    summary = []
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "tool_result":
                            tool_name = part.get("tool_name", "[unknown tool]")
                            tool_content = part.get("content", "[no result]")
                            summary.append(f"[Tool result for {tool_name} omitted: {tool_content}]")
                    if summary:
                        sanitized.append({"role": role, "content": [{"type": "text", "text": ' '.join(summary)}]})
                last_was_tool_call = False
            else:
                sanitized.append({"role": role, "content": _sanitize_for_claude(content)})
                last_was_tool_call = False
        return sanitized

    # All other providers: sanitize message-by-message as before
    for message in history:
        if not isinstance(message, dict):
            continue
        role = message.get("role", "")
        content = message.get("content", "")
        if not role:
            continue
        try:
            content = _deep_sanitize(content)
        except Exception as e:
            print(f"Warning: Failed to sanitize content: {e}")
            continue
        try:
            if provider == "gemini":
                content = _sanitize_for_gemini(content)
            elif provider == "claude":
                content = _sanitize_for_claude(content)
        except Exception as e:
            print(f"Warning: Provider-specific sanitization failed: {e}")
            continue
        sanitized.append({"role": role, "content": content})
    return sanitized

def _sanitize_for_gemini(content: Any) -> Any:
    """Remove or reformat structures that Gemini can't parse."""
    if isinstance(content, str):
        return re.sub(r"\[.*?tool.*?\]", "[Tool call removed for compatibility]", content)

    elif isinstance(content, list):
        cleaned = []
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type", "")
                if part_type == "tool_use":
                    cleaned.append({"text": "[Tool call redacted for Gemini]"})
                elif part_type == "tool_result":
                    cleaned.append({"text": "[Tool response redacted for Gemini]"})
                elif part_type == "text":
                    cleaned.append({"text": part.get("text", "")})
                else:
                    # Handle unknown types as text if possible
                    text = part.get("text", str(part))
                    cleaned.append({"text": text})
            elif isinstance(part, str):
                cleaned.append({"text": part})
        return cleaned

    return content

def _sanitize_for_openai(content: Any) -> Any:
    """Remove exotic parts like Gemini-style function_call or tool markup."""
    if isinstance(content, list):
        cleaned = []
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type")
                if part_type in {"text", "image"}:
                    cleaned.append(part)
                elif "text" in part:  # Convert Gemini-style to OpenAI format
                    cleaned.append({"type": "text", "text": part["text"]})
            elif isinstance(part, str):
                cleaned.append({"type": "text", "text": part})
        return cleaned or content  # Return original if cleaned is empty
    return content

def _sanitize_for_claude(content: Any) -> Any:
    """Clean up malformed tool results and standardize format."""
    if isinstance(content, list):
        cleaned = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "tool_result" and "tool_name" in part:
                    # Remove tool_name but preserve other metadata
                    filtered = {k: v for k, v in part.items() if k != "tool_name"}
                    cleaned.append(filtered)
                else:
                    cleaned.append(part)
            elif isinstance(part, str):
                cleaned.append({"type": "text", "text": part})
            else:
                cleaned.append(part)
        return cleaned
    return content