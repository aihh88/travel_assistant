"""
Itinerary Assistant State Definition
"""

from typing import Annotated, Literal, TypedDict

from langgraph.graph import add_messages


class ItineraryState(TypedDict):
    """Itinerary assistant subgraph local state"""

    # Conversation history
    messages: Annotated[list, add_messages]

    # Input data from parent graph
    destination: str  # 目的地
    departure_date: str  # 出发日期
    days: int  # 旅行天数
    budget: float | None  # 预算金额
    travelers: int  # 成人人数
    children: int  # 儿童人数
    tags: list[str]  # 偏好标签
    special_needs: list[str] | None  # 特殊需求

    # Weather data
    weather_data: list[dict]  # 每日天气数据

    # Attractions data
    attractions_data: list[dict]  # 景点列表

    # Generated itinerary
    itinerary: list[dict]  # 生成的行程

    # Current step
    current_step: str

    # Completion state
    complete_state: Literal["completed", "not_started", "in_progress"]
