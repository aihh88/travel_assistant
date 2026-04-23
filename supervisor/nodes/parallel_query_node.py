"""
parallel_query_node - Parallel query weather and attractions
"""

from typing import Sequence
from langgraph.types import Command, Send

from state import State


def parallel_query_node(state: State) -> Command:
    """Dispatch parallel queries for weather and attractions"""
    preferences = state.get("preferences", {})

    destination = preferences.get("destinations", [None])[0]

    if not destination:
        return Command(goto="__end__")

    # Use Command with Send list to invoke both nodes in parallel
    return Command(
        goto=[
            Send("weather_query_node", state),
            Send("attractions_query_node", state),
        ]
    )