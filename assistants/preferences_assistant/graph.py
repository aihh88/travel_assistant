"""
Preferences Assistant 子图构建
"""
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph

from .state import PreferencesState
from .nodes import extract_intent_node, check_complete_node, ask_followup_node


def build_preferences_graph() -> StateGraph:
    """构建偏好收集子图"""
    memory = InMemorySaver()
    builder = StateGraph(PreferencesState)

    builder.add_node("extract_intent_node", extract_intent_node)
    builder.add_node("check_complete_node", check_complete_node)
    builder.add_node("ask_followup_node", ask_followup_node)

    builder.add_edge(START, "extract_intent_node")

    return builder.compile(checkpointer=memory)


preferences_subgraph = build_preferences_graph()
