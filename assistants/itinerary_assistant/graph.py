"""
Itinerary Assistant Subgraph Builder
"""
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph

from .state import ItineraryState
from .nodes import generate_itinerary_node


def build_itinerary_graph() -> StateGraph:
    """Build itinerary assistant subgraph"""
    memory = InMemorySaver()
    builder = StateGraph(ItineraryState)

    builder.add_node("generate_itinerary_node", generate_itinerary_node)

    builder.add_edge(START, "generate_itinerary_node")

    return builder.compile(checkpointer=memory)


itinerary_subgraph = build_itinerary_graph()
