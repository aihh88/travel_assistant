"""
error_handler_node - Handle errors and generate user-friendly error messages
"""

from langgraph.types import Command

from state import State
from llm import get_llm


ERROR_PROMPT = """你是一个旅行助手，请根据下面的错误信息生成一段简短、友好、易于理解的回复。不要透露技术细节，不要说"抱歉"。

错误信息：{error_message}

请直接回复用户（不超过50字）："""


def error_handler_node(state: State) -> Command:
    """Handle error and generate user-friendly message"""
    error_info = state.get("error")

    if not error_info:
        error_msg = "发生了未知错误"
        recovery_hint = None
    else:
        error_msg = error_info.get("message", "发生了未知错误")
        recovery_hint = error_info.get("recovery_hint")

    # Generate friendly error message using LLM
    llm = get_llm()
    prompt = ERROR_PROMPT.format(error_message=error_msg)

    response = llm.invoke([{"role": "user", "content": prompt}])
    friendly_message = response.content if hasattr(response, "content") else str(response)

    # Build error reply
    error_reply = friendly_message
    if recovery_hint:
        error_reply += f"\n\n提示: {recovery_hint}"

    return Command(
        goto="__end__",
        update={
            "messages": [{"role": "assistant", "content": error_reply}],
        }
    )
