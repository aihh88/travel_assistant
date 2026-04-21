"""
Preferences Assistant State Definition
"""

from typing import Annotated, Literal, TypedDict

from langgraph.graph import add_messages


class PreferencesState(TypedDict):
    """Preferences subgraph local state"""

    # Conversation history
    messages: Annotated[list, add_messages]

    # Collected fields
    origin: str | None
    destinations: list[str]
    departure_date: str | None
    days: int | None
    budget: float | None
    travelers: int | None
    children: int | None
    tags: list[str]
    special_needs: list[str]


    # Current step
    current_step: str

    # Completion state: completed, not_started, incomplete
    complete_state: Literal["completed", "not_started", "incomplete"]
