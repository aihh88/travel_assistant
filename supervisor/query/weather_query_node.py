"""
weather_query_node - Query weather data
"""

from typing import Literal

from langgraph.types import Command

from state import State
from utils.weather_utils import get_travel_weather


def weather_query_node(state: State) -> Command[Literal["error_handler_node", "call_itinerary_subgraph_node"]]:
    """Query weather for the travel destination"""
    preferences = state.get("preferences", {})
    destination = preferences.get("destinations", [None])[0]
    departure_date = preferences.get("departure_date")
    days = preferences.get("days", 0)

    if not destination or not departure_date or not days:
        return Command(goto="call_itinerary_subgraph_node")

    try:
        weather_data = get_travel_weather(destination, departure_date, days)
        travel_weather = {
            "destination": destination,
            "start_date": departure_date,
            "days": days,
            "daily": weather_data,
        }
    except Exception as e:
        # Jump to error handler with error info
        return Command(
            goto="error_handler_node",
            update={
                "error": {
                    "source": "weather_query_node",
                    "message": f"查询天气失败：{str(e)}",
                    "recovery_hint": "请稍后重试，或检查目的地名称是否正确",
                }
            },
        )

    return Command(goto="call_itinerary_subgraph_node", update={"travel_weather": travel_weather})
