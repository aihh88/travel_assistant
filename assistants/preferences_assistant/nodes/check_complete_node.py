"""
check_complete node - Check if all required info has been collected
"""

from typing import Literal

from langgraph.types import Command

from ..state import PreferencesState


def check_complete_node(state: PreferencesState) -> Command[Literal["ask_followup_node", "__end__"]]:
    """Check if all required fields have been collected"""
    required_fields = {
        "origin": state["origin"],
        "destinations": state["destinations"],
        "departure_date": state["departure_date"],
        "days": state["days"],
        "budget": state["budget"],
        "travelers": state["travelers"],
    }

    missing = [k for k, v in required_fields.items() if v is None]

    if missing:
        return Command(
            goto="ask_followup_node",
            update={
                "complete_state": "incomplete",
            },
        )
    else:
        return Command(
            goto="__end__",
            update={
                "complete_state": "completed",
                "current_step": "complete",
            },
        )
