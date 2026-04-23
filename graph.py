from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph

from state import State
from supervisor.nodes.call_preferences_node import call_preferences_subgraph_node
from supervisor.nodes.call_itinerary_node import call_itinerary_subgraph_node
from supervisor.nodes.parallel_query_node import parallel_query_node
from supervisor.nodes.supervisor_node import supervisor_node
from supervisor.query import weather_query_node, attractions_query_node
from supervisor.error import error_handler_node


def build_supervisor_graph() -> StateGraph:
    memory = InMemorySaver()
    graph = StateGraph(State)
    graph.add_node("supervisor_node", supervisor_node)
    graph.add_node("call_preferences_subgraph_node", call_preferences_subgraph_node)
    graph.add_node("parallel_query_node", parallel_query_node)
    graph.add_node("weather_query_node", weather_query_node)
    graph.add_node("attractions_query_node", attractions_query_node)
    graph.add_node("call_itinerary_subgraph_node", call_itinerary_subgraph_node)
    graph.add_node("error_handler_node", error_handler_node)
    graph.add_edge(START, "supervisor_node")
    return graph.compile(checkpointer=memory)


main_graph = build_supervisor_graph()
