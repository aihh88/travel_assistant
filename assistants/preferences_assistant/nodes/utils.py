"""
Preferences Assistant Shared Utilities
"""

import json
import re
from typing import Any

SYSTEM_PROMPT = """你是一个旅行助手的需求收集专家。

收集以下信息：
1. origin - 出发地，例如"北京"、"上海"
2. destinations - 目的地列表，例如["东京", "大阪"]
3. departure_date - 出发日期，例如"2024-05-01"
4. days - 旅行天数（数字）
5. budget - 预算金额（人民币元）
6. travelers - 成人人数
7. children - 儿童人数
8. tags - 偏好标签，例如["美食", "文化", "家庭", "购物"]
9. special_needs - 特殊需求，例如["带小孩", "素食", "无障碍"]

注意：
- "你只负责从消息中提取上面的信息，绝对不要实现其他的任何功能"
- "从X出发"中的X是出发地(origin)
- "去X"或"目的地是X"中的X是目的地(destinations)
- 用户可能分多次提供信息，不要修改用户没有提到的信息
"""


def _get_message_text(msg) -> str:
    """Extract text content from message object or dict"""
    if hasattr(msg, "content"):
        return msg.content
    if isinstance(msg, dict):
        return msg.get("content", "")
    return str(msg)


def _format_current_state(state) -> str:
    return f"""当前已收集：
- 出发地: {state.get('origin')}
- 目的地: {state.get('destinations')}
- 出发日期: {state.get('departure_date')}
- 天数: {state.get('days')}
- 预算: {state.get('budget')}
- 成人: {state.get('travelers')}
- 儿童: {state.get('children')}
- 偏好标签: {state.get('tags')}
- 特殊需求: {state.get('special_needs')}"""


def parse_llm_json_response(response: Any) -> dict:
    """Parse JSON from LLM response, handling both list and str formats"""
    content = response.content if hasattr(response, 'content') else str(response)

    result = {}
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                try:
                    result = json.loads(text)
                    break
                except json.JSONDecodeError:
                    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            break
                        except json.JSONDecodeError:
                            pass
    elif isinstance(content, str):
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

    return result


def extract_and_build_updates(result: dict) -> dict:
    """Parse JSON result and build updates dict with only non-null/non-empty values"""
    origin = result.get("origin")
    destinations = result.get("destinations", [])
    departure_date = result.get("departure_date")
    days = result.get("days")
    budget = result.get("budget")
    travelers = result.get("travelers")
    children = result.get("children")
    tags = result.get("tags", [])
    special_needs = result.get("special_needs", [])
    reply = result.get("reply_message", "收到您的信息了")

    updates: dict = {}

    if origin is not None:
        updates["origin"] = origin
    if destinations:
        updates["destinations"] = destinations
    if departure_date is not None:
        updates["departure_date"] = departure_date
    if days is not None:
        updates["days"] = days
    if budget is not None:
        updates["budget"] = budget
    if travelers is not None:
        updates["travelers"] = travelers
    if children is not None:
        updates["children"] = children
    if tags:
        updates["tags"] = tags
    if special_needs:
        updates["special_needs"] = special_needs

    return updates
