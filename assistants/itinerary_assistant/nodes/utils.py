"""
Shared utilities for itinerary assistant nodes
"""

SYSTEM_PROMPT = """你是一个专业的旅行规划助手，擅长根据天气、景点等信息为用户规划合理的每日行程。
你的规划会考虑：
1. 天气条件对活动的影响
2. 景点的开放时间和游览时长
3. 适合不同年龄段的的活动
4. 交通便利性
5. 当地特色体验

请直接返回JSON格式的规划结果，不要有多余的解释。"""


def _get_message_text(message) -> str:
    """Extract text content from a message"""
    if isinstance(message, str):
        return message
    if hasattr(message, "content"):
        return message.content
    if isinstance(message, dict):
        return message.get("content", "")
    return str(message)


def parse_llm_json_response(response) -> dict:
    """Parse JSON from LLM response"""
    content = _get_message_text(response)

    # Try to extract JSON from content
    import json
    import re

    # Look for JSON in the content
    json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Try parsing the whole content as JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}
