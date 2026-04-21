"""
Preferences Assistant - 需求收集与偏好助手

负责与用户多轮对话，提取/澄清关键信息，输出结构化用户画像。
"""

from .graph import preferences_subgraph
from .state import PreferencesState

__all__ = ["preferences_subgraph", "PreferencesState"]
