"""
call_weather_subgraph_node - Call weather query
"""

from typing import Literal

from langgraph.types import Command

from state import State
from utils.weather_utils import get_travel_weather


def call_weather_subgraph_node(state: State) -> Command[Literal["__end__"]]:
    """Fetch weather for the travel destination"""
    preferences = state.get("preferences", {})

    destination = preferences.get("destinations", [None])[0]
    departure_date = preferences.get("departure_date")
    days = preferences.get("days", 0)

    if not destination or not departure_date or not days:
        # Missing required info, cannot fetch weather
        return Command(goto="__end__", update={"travel_weather": None})

    try:
        weather_data = get_travel_weather(destination, departure_date, days)
        travel_weather = {
            "destination": destination,
            "start_date": departure_date,
            "days": days,
            "daily": weather_data,
        }
    except Exception as e:
        # Weather query failed, continue without weather
        travel_weather = None

    return Command(goto="__end__", update={"travel_weather": travel_weather})