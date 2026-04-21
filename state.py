from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph import add_messages


class UserPreferences(TypedDict):
    """用户偏好"""
    origin: str | None  # 出发地
    destinations: list[str]  # 目的地列表
    departure_date: str | None  # 出发日期
    days: int  # 旅行天数
    budget: float | None  # 预算金额
    travelers: int  # 成人人数
    children: int  # 儿童人数
    tags: list[str]  # 偏好标签
    special_needs: list[str] | None  # 特殊需求
    complete_state: Literal["completed", "not_started", "incomplete"]  # Completion status


class DayPlan(TypedDict):
    """单日行程计划"""
    day_number: int  # 第几天
    city: str  # 城市
    date: str | None  # 日期
    morning: str | None  # 上午活动
    afternoon: str | None  # 下午活动
    evening: str | None  # 晚间活动
    accommodation: str | None  # 住宿
    transportation_to_next: str | None  # 前往下一站的交通


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
    uv_index: int # 紫外线强度


class TravelWeather(TypedDict):
    """旅行天气汇总"""
    destination: str  # 目的地
    start_date: str  # 开始日期
    days: int  # 天数
    daily: list[DayWeather]  # 每日天气列表


class BudgetBreakdown(TypedDict):
    """预算细分"""
    total_budget: float  # 总预算
    currency: str  # 币种
    transportation_cost: float  # 交通费用
    accommodation_cost: float  # 住宿费用
    activities_cost: float  # 活动费用
    food_cost: float | None  # 餐饮费用
    contingency: float  # 应急储备


class State(TypedDict):
    """主状态 - 旅行助手监督图的主要状态"""

    # 对话历史
    messages: Annotated[list, add_messages]

    # 用户偏好（统一存储）
    preferences: UserPreferences

    # 当前行程
    itinerary: list[DayPlan]

    # 旅行天气
    travel_weather: TravelWeather | None


    # 预算细分
    budget_breakdown: BudgetBreakdown | None

    # Workflow state
    current_step: str


