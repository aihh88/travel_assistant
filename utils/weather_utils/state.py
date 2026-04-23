"""
Weather Assistant State Definition
"""

from typing import Annotated, Literal, TypedDict

from langgraph.graph import add_messages


class DayWeather(TypedDict):
    """单日天气"""
    date: str  # 日期 YYYY-MM-DD
    temp_max: int  # 最高温度
    temp_min: int  # 最低温度
    text_day: str  # 白天天气描述
    text_night: str  # 夜间天气描述
    wind_dir_day: str  # 白天风向
    wind_scale_day: str  # 白天风力
    precip: float  # 降水量
    uv_index: int  # 紫外线强度
    suggestion: str  # 建议


class WeatherState(TypedDict):
    """Weather subgraph local state"""
    # Conversation history
    messages: Annotated[list, add_messages]

    # Location info for weather query
    destination: str | None  # 目的地
    departure_date: str | None  # 出发日期
    days: int | None  # 天数

    # Weather result Daily Weather List
    travel_weather: list[DayWeather] | None  # 旅行天气汇总

    # Completion state: completed, not_started, incomplete, error
    complete_state: Literal["completed", "not_started", "incomplete", "error"]
