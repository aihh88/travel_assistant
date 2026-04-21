"""
Preferences Assistant Tools
"""

from datetime import date

from langchain_core.tools import tool


@tool
def get_current_date() -> str:
    """
    获取当前日期

    用于帮助LLM理解用户提到的相对日期，如"明天"、"后天"等。

    Returns:
        当前日期字符串，格式为 "YYYY-MM-DD"
    """
    return date.today().isoformat()
