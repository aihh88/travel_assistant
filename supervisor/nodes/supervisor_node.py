"""
supervisor node - Supervisor coordinator

Routing based on preferences.complete_state:
- "completed": goto parallel_query_node (parallel query weather and attractions)
- "not_started" or "incomplete": goto call_preferences_subgraph_node (continue collecting)
"""

from typing import Literal

from langgraph.types import Command

from state import State


def supervisor_node(state: State, config=None) -> Command[
    Literal["call_preferences_subgraph_node", "parallel_query_node", "__end__"]]:
    """Supervisor node: route based on complete_state"""
    complete_state = state.get("preferences", {}).get("complete_state", "not_started")

    if complete_state == "not_started":
        # "not_started" - start collecting
        return Command(goto="call_preferences_subgraph_node")
    elif complete_state == "incomplete":
        # "incomplete" - continue collecting
        return Command(goto="__end__")
    else:
        # "completed" - all info collected, parallel query weather and attractions
        return Command(goto="parallel_query_node")
