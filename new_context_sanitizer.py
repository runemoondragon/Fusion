import re
import json
from typing import List, Dict, Any, Union

def _to_dict_if_possible(obj: Any) -> Union[Dict, Any]:
    if hasattr(obj, 'dict') and callable(getattr(obj, 'dict', None)):
        return obj.dict()
    if hasattr(obj, '__dict__') and hasattr(obj, 'type'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return obj

def _deep_sanitize(obj: Any) -> Any:
    if isinstance(obj, list):
        return [_deep_sanitize(_to_dict_if_possible(item)) for item in obj]
    elif isinstance(obj, dict):
        return {k: _deep_sanitize(_to_dict_if_possible(v)) for k, v in obj.items()}
    else:
        return obj

def _inflate_tool_result_from_text_block(part):
    if (
        isinstance(part, dict)
        and part.get("type") == "text"
        and part.get("text", "").startswith("[[OMITTED_TOOL_RESULT_JSON]]")
    ):
        try:
            marker = part["text"][len("[[OMITTED_TOOL_RESULT_JSON]]") :]
            data = json.loads(marker)
            if data.get("_omitted_tool_result"):
                return {
                    "type": "tool_result",
                    "tool_name": data.get("tool_name"),
                    "content": data.get("tool_content"),
                }
        except Exception:
            return None
    return None

def sanitize_history(history: List[Dict], provider: str) -> List[Dict]:
    if not isinstance(history, list):
        raise TypeError(f"Expected history to be a list, got {type(history)}")

    sanitized = []
    valid_providers = {'gemini', 'openai', 'claude'}
    if provider not in valid_providers:
        raise ValueError(f"Provider must be one of {valid_providers}, got {provider}")

    if provider == 'openai':
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
            if role == "tool_call":
                sanitized.append(message)
                last_was_tool_call = True
            elif role == "user":
                if isinstance(content, list) and any(
                    isinstance(part, dict) and part.get("type") == "tool_result"
                    for part in content
                ):
                    if last_was_tool_call:
                        sanitized.append({"role": role, "content": _sanitize_for_openai(content)})
                    else:
                        summary = []
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "tool_result":
                                tool_name = part.get("tool_name", "[unknown tool]")
                                tool_content = part.get("content", "[no result]")
                                summary.append("[[OMITTED_TOOL_RESULT_JSON]]" + json.dumps({
                                    "_omitted_tool_result": True,
                                    "tool_name": tool_name,
                                    "tool_content": tool_content,
                                    "original_content": part
                                }))
                        if summary:
                            sanitized.append({"role": role, "content": [{"type": "text", "text": ' '.join(summary)}]})
                    last_was_tool_call = False
            else:
                sanitized.append({"role": role, "content": _sanitize_for_openai(content)})
                last_was_tool_call = False
        return sanitized

    if provider == 'claude':
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
            if isinstance(content, list):
                new_parts = []
                for part in content:
                    inflated = _inflate_tool_result_from_text_block(part)
                    if inflated:
                        new_parts.append(inflated)
                    else:
                        new_parts.append(part)
                sanitized.append({"role": role, "content": new_parts})
            else:
                sanitized.append({"role": role, "content": _sanitize_for_claude(content)})
        return sanitized

    if provider == 'gemini':
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
            if isinstance(content, list):
                new_parts = []
                for part in content:
                    inflated = _inflate_tool_result_from_text_block(part)
                    if inflated:
                        new_parts.append(inflated)
                    else:
                        new_parts.append(part)
                sanitized.append({"role": role, "content": new_parts})
            else:
                sanitized.append({"role": role, "content": _sanitize_for_gemini(content)})
        return sanitized

    return sanitized

def _sanitize_for_gemini(content: Any) -> Any:
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
                    text = part.get("text", str(part))
                    cleaned.append({"text": text})
            elif isinstance(part, str):
                cleaned.append({"text": part})
        return cleaned
    return content

def _sanitize_for_openai(content: Any) -> Any:
    if isinstance(content, list):
        cleaned = []
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type")
                if part_type in {"text", "image"}:
                    cleaned.append(part)
                elif "text" in part:
                    cleaned.append({"type": "text", "text": part["text"]})
            elif isinstance(part, str):
                cleaned.append({"type": "text", "text": part})
        return cleaned or content
    return content

def _sanitize_for_claude(content: Any) -> Any:
    if isinstance(content, list):
        cleaned = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "tool_result" and "tool_name" in part:
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
