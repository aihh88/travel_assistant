"""
call_preferences_node - Call the preferences subgraph
"""

from langgraph.types import Command

from assistants.preferences_assistant import preferences_subgraph, PreferencesState
from state import State, UserPreferences


def transform_state2subgraph(state: State) -> PreferencesState:
    """Convert parent graph state to subgraph state"""
    user_preferences: UserPreferences = state.get("preferences")
    preferences_state = {
        "messages": state["messages"],
        "origin": user_preferences["origin"],
        "destinations": user_preferences["destinations"],
        "departure_date": user_preferences["departure_date"],
        "days": user_preferences["days"],
        "budget": user_preferences["budget"],
        "travelers": user_preferences["travelers"],
        "children": user_preferences["children"],
        "tags": user_preferences["tags"],
        "special_needs": user_preferences["special_needs"],
        "current_step": state.get("current_step", "start"),
        "complete_state": user_preferences.get("complete_state", "not_started"),
    }
    return preferences_state


def transform_subgraph2state(subgraph_result: PreferencesState) -> State:
    """Convert subgraph state to parent graph state"""
    state = {
        "messages": subgraph_result["messages"],
        "preferences": {
            "origin": subgraph_result["origin"],
            "destinations": subgraph_result["destinations"],
            "departure_date": subgraph_result["departure_date"],
            "days": subgraph_result["days"],
            "budget": subgraph_result["budget"],
            "travelers": subgraph_result["travelers"],
            "children": subgraph_result["children"],
            "tags": subgraph_result["tags"],
            "special_needs": subgraph_result["special_needs"],
            "complete_state": subgraph_result.get("complete_state", "not_started"),
        },
    }
    return state


def call_preferences_subgraph_node(
        state: State, config=None
):
    subgraph_config = {"configurable": {"thread_id": config["configurable"]["thread_id"]}} if config else None
    subgraph_result = preferences_subgraph.invoke(
        transform_state2subgraph(state), subgraph_config
    )
    return Command(
        goto="__end__",
        update=transform_subgraph2state(subgraph_result)
    )
