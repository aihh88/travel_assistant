"""
supervisor node - Supervisor coordinator

Routing based on preferences.complete_state:
- "completed": goto __end__ (finish preference collection)
- "not_started" or "incomplete": goto call_preferences_subgraph_node (continue collecting)
"""

from typing import Literal

from langgraph.types import Command

from state import State


def supervisor_node(state: State, config=None) -> Command[Literal["call_preferences_subgraph_node", "call_weather_subgraph_node", "__end__"]]:
    """Supervisor node: route based on complete_state"""
    complete_state = state.get("preferences", {}).get("complete_state", "not_started")

    if complete_state == "not_started":
        # "not_started" - start collecting
        return Command(goto="call_preferences_subgraph_node")
    elif complete_state == "incomplete":

        return Command(goto="call_preferences_subgraph_node")
    else:

        return Command(goto="call_weather_subgraph_node")
