"""
extract_intent node - Extract intent/preferences from user message
"""

from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from llm import get_llm
from ..state import PreferencesState
from .utils import SYSTEM_PROMPT, _get_message_text, _format_current_state, parse_llm_json_response, \
    extract_and_build_updates
from ..tools import get_current_date


def extract_intent_node(state: PreferencesState) -> Command[Literal["check_complete_node"]]:
    """从用户最新消息中提取意图/偏好信息"""
    llm = get_llm().bind_tools([get_current_date])
    messages = state["messages"]
    last_msg = messages[-1] if messages else None
    last_user_msg = _get_message_text(last_msg) if last_msg else ""

    prompt = SYSTEM_PROMPT + "\n\n" + """

从用户消息中提取旅行偏好信息。
只提取你确定的信息，不要猜测。

**严格按以下JSON格式返回**，不要其他内容：
{"origin": "出发地", "destinations": ["目的地"], "departure_date":"出发日期", "days": 数字, "budget": 数字, "travelers": 数字, "children": 数字, "tags": ["标签"], "special_needs": []}"""

    response = llm.invoke([
        {"role": "system", "content": prompt},
        {"role": "user", "content": last_user_msg}
    ])

    # 处理工具调用
    if hasattr(response, "tool_calls") and response.tool_calls:
        # LLM 调用了工具，执行工具获取当前日期
        for tc in response.tool_calls:
            if tc["name"] == "get_current_date":
                tool_result = get_current_date.invoke(tc)
                # 再次调用 LLM，让它基于工具结果继续
                response = llm.invoke([
                    {"role": "system", "content": prompt},
                    HumanMessage(content=last_user_msg),
                    response,
                    tool_result
                ])

    result = parse_llm_json_response(response)
    updates = extract_and_build_updates(result)

    return Command(goto="check_complete_node", update=updates)
