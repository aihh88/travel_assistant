"""
attractions_query_node - Query attractions via Amap API
"""

from typing import Literal

from langgraph.types import Command

from state import State
from utils.amap_utils import get_attractions_by_destination


def attractions_query_node(state: State) -> Command[Literal["error_handler_node", "call_itinerary_subgraph_node"]]:
    """Query attractions for the travel destination"""
    preferences = state.get("preferences", {})
    destination = preferences.get("destinations", [None])[0]

    if not destination:
        return Command(goto="call_itinerary_subgraph_node")

    try:
        attractions_data = get_attractions_by_destination(destination)
        # Convert to AttractionInfo format
        attractions_list = [
            {
                "name": attr.get("name", ""),
                "location": attr.get("location", ""),
                "address": attr.get("address", ""),
                "rating": attr.get("rating"),
                "type": attr.get("type", ""),
            }
            for attr in attractions_data
        ]
        attractions_result = {
            "destination": destination,
            "attractions": attractions_list,
        }
    except Exception as e:
        # Jump to error handler with error info
        return Command(
            goto="error_handler_node",
            update={
                "error": {
                    "source": "attractions_query_node",
                    "message": f"查询景点失败：{str(e)}",
                    "recovery_hint": "请稍后重试，或尝试更换目的地",
                }
            },
        )

    return Command(goto="call_itinerary_subgraph_node", update={"attractions": [attractions_result]})
