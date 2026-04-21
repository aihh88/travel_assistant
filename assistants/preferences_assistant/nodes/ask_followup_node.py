"""
ask_followup node - Ask user for missing information
"""

from typing import Literal

from langgraph.types import Command

from llm import get_llm
from ..state import PreferencesState
from .utils import _format_current_state, parse_llm_json_response

llm = get_llm()

FIELD_MAP = {
    "origin": "出发地",
    "destinations": "目的地",
    "days": "旅行天数",
    "budget": "预算",
    "travelers": "成人人数",
    "children": "儿童人数",
    "tags": "偏好标签",
    "special_needs": "特殊需求",
}


def ask_followup_node(state: PreferencesState) -> Command[Literal["__end__"]]:
    """向用户追问缺失的信息"""
    current = state["current_step"].replace("ask_", "")
    msg = state["messages"][-1].content
    prompt = f"""你是一个旅行助手，正在收集用户偏好信息。

当前已收集的状态：
{_format_current_state(state)}

请生成一条友好的追问消息，询问用户关于「**缺失**字段」（缺失字段指值为None的字段）的信息。
语气要友好，鼓励用户提供信息。

严格按以下JSON格式返回，不要其他内容：
{{"message": "追问消息"}}"""

    response = llm.invoke([
        {"role": "system", "content": "你是一个友好的旅行助手。"},
        {"role": "user", "content": prompt}
    ])

    result = parse_llm_json_response(response)
    message = result.get("message")

    return Command(
        goto="__end__",
        update={
            "messages": [{"role": "assistant", "content": message}],
            "complete_state": "incomplete",
        },
    )
