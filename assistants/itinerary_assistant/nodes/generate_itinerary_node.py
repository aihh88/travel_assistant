"""
Itinerary generation node
"""

from typing import Literal

from langgraph.types import Command

from llm import get_llm
from ..state import ItineraryState
from .utils import SYSTEM_PROMPT, _get_message_text, parse_llm_json_response


llm = get_llm()

DAILY_PLAN_TEMPLATE = """根据以下信息为第{day}天规划行程：

目的地：{destination}
日期：{date}
天气：{weather}
景点列表：{attractions}

请规划这一天的行程，包括上午、下午、晚上的活动安排。
考虑以下因素：
1. 天气情况（避免在恶劣天气安排户外活动）
2. 景点之间的距离和游览时间
3. 适合{travelers}位成人{total_children}位儿童

请按以下JSON格式返回（不要其他内容）：
{{"morning": "上午活动", "afternoon": "下午活动", "evening": "晚间活动"}}"""


def generate_day_plan(state: ItineraryState, day: int) -> dict:
    """Generate plan for a single day"""
    weather_data = state.get("weather_data", [])
    attractions_data = state.get("attractions_data", [])

    # Find weather for this day
    day_weather = None
    for w in weather_data:
        if w.get("date") == day:  # This is simplified, should match by date
            day_weather = w
            break

    if not day_weather and weather_data:
        day_weather = weather_data[min(day - 1, len(weather_data) - 1)]

    weather_desc = ""
    if day_weather:
        weather_desc = f"{day_weather.get('text_day', '未知')}, 温度{day_weather.get('temp_min', 0)}-{day_weather.get('temp_max', 0)}°C"

    attractions_desc = "\n".join([
        f"- {a.get('name', '未知')} (地址: {a.get('address', '未知')})"
        for a in attractions_data[:10]  # Limit to first 10 attractions
    ])

    travelers = state.get("travelers", 2)
    children = state.get("children", 0)
    total_children = travelers + children

    prompt = DAILY_PLAN_TEMPLATE.format(
        day=day,
        destination=state.get("destination", ""),
        date=day_weather.get("date", f"第{day}天") if day_weather else f"第{day}天",
        weather=weather_desc or "暂无天气信息",
        attractions=attractions_desc or "暂无景点信息",
        travelers=travelers,
        total_children=total_children,
    )

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ])

    result = parse_llm_json_response(response)
    return result


def generate_itinerary_node(state: ItineraryState) -> Command[Literal["__end__"]]:
    """Generate complete itinerary based on weather and attractions"""
    destination = state.get("destination", "")
    days = state.get("days", 1)
    weather_data = state.get("weather_data", [])
    attractions_data = state.get("attractions_data", [])

    if not destination:
        return Command(
            goto="__end__",
            update={
                "itinerary": [],
                "complete_state": "completed",
            }
        )

    # Generate plan for each day
    daily_plans = []
    for day in range(1, days + 1):
        day_plan = generate_day_plan(state, day)
        day_plan["day_number"] = day

        # Set date if available from weather
        if weather_data and day - 1 < len(weather_data):
            day_plan["date"] = weather_data[day - 1].get("date")

        daily_plans.append(day_plan)

    return Command(
        goto="__end__",
        update={
            "itinerary": daily_plans,
            "complete_state": "completed",
        }
    )
