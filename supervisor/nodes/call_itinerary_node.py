"""
call_itinerary_node - Call the itinerary generation subgraph
"""

from langgraph.types import Command

from assistants.itinerary_assistant import itinerary_subgraph, ItineraryState
from state import State, UserPreferences, TravelWeather, AttractionsResult


def transform_state2subgraph(state: State) -> ItineraryState:
    """Convert parent graph state to subgraph state"""
    preferences: UserPreferences = state.get("preferences", {})
    travel_weather: TravelWeather | None = state.get("travel_weather")
    attractions = state.get("attractions") or []

    # Convert weather data
    weather_data = []
    if travel_weather and travel_weather.get("daily"):
        weather_data = [
            {
                "date": d.get("date", ""),
                "temp_max": d.get("temp_max", 0),
                "temp_min": d.get("temp_min", 0),
                "text_day": d.get("text_day", ""),
                "text_night": d.get("text_night", ""),
            }
            for d in travel_weather["daily"]
        ]

    # Convert attractions data
    attractions_data = []
    for attr_result in attractions:
        if isinstance(attr_result, dict) and attr_result.get("attractions"):
            for a in attr_result["attractions"]:
                attractions_data.append(a)

    itinerary_state = {
        "messages": state["messages"],
        "destination": preferences.get("destinations", [None])[0] or "",
        "departure_date": preferences.get("departure_date") or "",
        "days": preferences.get("days", 1),
        "budget": preferences.get("budget"),
        "travelers": preferences.get("travelers", 1),
        "children": preferences.get("children", 0),
        "tags": preferences.get("tags", []),
        "special_needs": preferences.get("special_needs"),
        "weather_data": weather_data,
        "attractions_data": attractions_data,
        "itinerary": [],
        "current_step": "generate_itinerary",
        "complete_state": "not_started",
    }
    return itinerary_state


def transform_subgraph2state(subgraph_result: ItineraryState) -> State:
    """Convert subgraph state to parent graph state"""
    state = {
        "messages": subgraph_result["messages"],
        "itinerary": subgraph_result.get("itinerary", []),
    }
    return state


def call_itinerary_subgraph_node(state: State, config=None):
    """Call itinerary subgraph to generate travel plan"""
    subgraph_config = {"configurable": {"thread_id": config["configurable"]["thread_id"]}} if config else None

    subgraph_result = itinerary_subgraph.invoke(
        transform_state2subgraph(state), subgraph_config
    )

    return Command(
        goto="__end__",
        update=transform_subgraph2state(subgraph_result)
    )
