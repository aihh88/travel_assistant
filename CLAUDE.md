# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LangChain-based multi-agent travel assistant** using a hierarchical supervisor pattern. The project is in early stages and uses Python 3.12+.

## Architecture

**Hierarchical Supervisor Pattern:**
- **Top level**: A Supervisor (coordinator) that understands user needs, decomposes tasks, calls specialized assistants, collects results, and synthesizes final travel plans.
- **Middle level**: Specialized Assistant Subgraphs - each is an independent subgraph that handles a specific domain.
- **Bottom level**: Tools and external services (flight search, weather API, etc.).

**Workflow:**
1. User input → `supervisor_node` (路由判断)
2. `supervisor_node` checks `preferences.complete_state`:
   - `"not_started"` or `"incomplete"` → `Command(goto="call_preferences_subgraph_node")`
   - `"completed"` → `Command(goto="call_weather_subgraph_node")` → 天气查询 → `__end__`
3. `call_preferences_subgraph_node`:
   - `transform_state2subgraph()` → 转换状态
   - `preferences_subgraph.invoke()` → 调用子图
   - 子图返回后 `transform_subgraph2state()` → 转换状态
   - `Command(goto="__end__", update={...})` → 直接结束（不回 supervisor）
4. Human-in-the-loop at key confirmation points
5. Output complete travel plan with export options

**State 转换流程:**
```
父图 State
  → supervisor_node (complete_state 判断)
  → transform_state2subgraph() → PreferencesState
  → preferences_subgraph.invoke()
  → transform_subgraph2state() → 父图 State 字典
  → Command(goto="__end__", update={...}) 返回
```

## File Structure

```
/Users/yuanhl/langchainStudy/travel_assistant/
├── main.py                           # Entry point (currently empty)
├── llm.py                            # LLM initialization (ChatAnthropic/MiniMax)
├── state.py                          # Main state: State, UserPreferences, DayPlan, BudgetBreakdown
├── graph.py                          # Main graph: build_supervisor_graph(), exports main_graph
├── schemas.py                        # Assistant output schemas
├── pyproject.toml                    # Project config
├── .python-version                   # Python version
├── README.md                         # Architecture documentation
├── CLAUDE.md                         # This file
├── supervisor/                       # Supervisor graph nodes
│   └── nodes/
│       ├── __init__.py
│       ├── supervisor_node.py        # Supervisor node, routes based on complete_state
│       ├── call_preferences_node.py  # Call subgraph + parent-child state transform
│       └── call_weather_node.py      # Weather query node (serial, TODO: parallel)
├── assistants/                       # Assistant subgraphs
│   └── preferences_assistant/         # Preferences collection subgraph
│       ├── __init__.py
│       ├── graph.py                 # Subgraph builder
│       ├── state.py                 # PreferencesState
│       ├── tools.py                 # Tools (get_current_date)
│       └── nodes/
│           ├── __init__.py
│           ├── utils.py             # Shared utilities (SYSTEM_PROMPT, parse_llm_json_response, etc.)
│           ├── extract_intent_node.py # Extract user intent from message
│           ├── check_complete_node.py # Check if all required fields collected
│           └── ask_followup_node.py   # Ask user for missing fields
├── utils/                           # Utility functions
│   ├── __init__.py
│   └── weather_utils/                # Weather API utilities
│       ├── __init__.py
│       ├── city_utils.py            # lookup_city, lookup_city_by_coordinates
│       ├── jwt_utils.py            # JWT token generation
│       ├── weather_utils.py        # query_weather, get_travel_weather
│       └── state.py                # Weather-related state definitions
├── tests/                           # Test files
└── problem.md                       # 问题总结文档
```

## Tech Stack

- Python 3.12+
- LangChain/LangGraph for multi-agent orchestration
- `langchain-anthropic` for LLM API
- Pydantic for structured output

## Commands

```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e . --python .venv/bin/python

# Run the application
python main.py

# Run tests
.venv/bin/python tests/test_complete_info.py
```

## Assistant Subgraph Specification

**Node naming**: All node functions must end with `_node`; registration name matches function name (with `_node` suffix)
**File organization**: One node per file in `assistant_name/nodes/` directory
**State definition**: State defined in `assistant_name/state.py`
**Graph building**: Graph built in `assistant_name/graph.py`
**Node registration**: Use full name with `_node` suffix, e.g., `"check_complete_node"`
**Node routing**: Use `Command` instead of conditional edges, `goto` target must match registration name
**LLM calls**: Use JSON parsing instead of `with_structured_output` (model compatibility issue)

**Node file template:**
```python
"""
Node name
"""

from typing import Literal
from langgraph.types import Command

from llm import get_llm
from ..state import PreferencesState
from .utils import SYSTEM_PROMPT, parse_llm_json_response, extract_and_build_updates

llm = get_llm()


def my_node(state: PreferencesState) -> Command[Literal["next_node"]]:
    """Node description"""
    # ...
    response = llm.invoke([...])
    result = parse_llm_json_response(response)
    updates = extract_and_build_updates(result)
    return Command(goto="next_node", update=updates)
```

## State Structure

### Main Graph State (state.py)

```python
class DayWeather(TypedDict):
    """单日天气"""
    date: str                   # 日期 YYYY-MM-DD
    temp_max: int               # 最高温度
    temp_min: int               # 最低温度
    text_day: str               # 白天天气描述
    text_night: str             # 夜间天气描述
    wind_dir_day: str           # 白天风向
    wind_scale_day: str         # 白天风力
    precip: float               # 降水量
    uv_index: int               # 紫外线强度


class TravelWeather(TypedDict):
    """旅行天气汇总"""
    destination: str            # 目的地
    start_date: str             # 开始日期
    days: int                   # 天数
    daily: list[DayWeather]     # 每日天气列表


class UserPreferences(TypedDict):
    """User preferences stored in parent graph State.preferences"""
    origin: str | None                       # Origin/starting location
    destinations: list[str]                   # Destination(s)
    departure_date: str | None                # Departure date
    days: int                                 # Number of travel days
    budget: float | None                      # Budget in CNY
    travelers: int                           # Number of adult travelers
    children: int                            # Number of children
    tags: list[str]                           # Preference tags
    special_needs: list[str] | None          # Special needs
    complete_state: Literal["completed", "not_started", "incomplete"]


class State(TypedDict):
    """Main graph state"""
    messages: Annotated[list, add_messages]   # Conversation history
    preferences: UserPreferences             # User preferences
    itinerary: list[DayPlan]                 # Daily itinerary
    travel_weather: TravelWeather | None     # Travel weather
    budget_breakdown: BudgetBreakdown | None # Budget breakdown
    current_step: str                        # Current step
```

### Subgraph State (PreferencesState)

```python
class PreferencesState(TypedDict):
    """Preferences subgraph local state"""
    messages: Annotated[list, add_messages]  # Conversation history
    origin: str | None                        # Origin
    destinations: list[str]                    # Destination(s)
    departure_date: str | None                # Departure date
    days: int | None                          # Days
    budget: float | None                      # Budget
    travelers: int | None                    # Adult travelers
    children: int | None                    # Children
    tags: list[str]                          # Tags
    special_needs: list[str]                  # Special needs
    current_step: str                        # Current step
    complete_state: Literal["completed", "not_started", "incomplete"]
```

## Weather Query Node

**Current: Serial execution (串行)**
```
supervisor_node (complete_state="completed")
    ↓ goto call_weather_subgraph_node
call_weather_subgraph_node
    ↓ 直接调用 get_travel_weather()
weather API
    ↓ update={travel_weather: ...}
__end__
```

**Planned: Parallel execution (并行) - TODO**
```
supervisor_node (complete_state="completed")
    ↓ goto parallel_query_node
parallel_query_node
    ├─→ weather_query_node (Send)
    └─→ transportation_query_node (Send)
         ↓ (两者并行完成)
plan_generation_node
    ↓
__end__
```

## Weather Utilities

Weather utilities are plain functions (not LangGraph nodes) in `utils/weather_utils/`:

```python
from utils.weather_utils import get_travel_weather

# 获取游玩期间的天气预报
weather = get_travel_weather("成都", "2026-04-24", 3)
# 返回: [{"date": "2026-04-24", "temp_max": 26, "temp_min": 15, ...}, ...]
```

**Functions:**
- `lookup_city(location)` - 根据城市名查找城市信息，返回 `CityInfo`
- `query_weather(city_id, days)` - 查询天气预报，返回 `WeatherResult`
- `get_travel_weather(destination, departure_date, days)` - 获取游玩期间的天气预报

## Parent-Child State Transform

`supervisor/nodes/call_preferences_node.py` handles parent-child state transform:

- `transform_state2subgraph(state)`: Parent `State` → Child `PreferencesState`
  - Maps `state.messages` → `messages`
  - Maps `state.preferences.*` → corresponding fields
  - Maps `state.current_step` → `current_step`
  - Sets `complete_state` from `preferences.complete_state` or `"not_started"`

- `transform_subgraph2state(subgraph_result)`: Child `PreferencesState` → Parent `State`
  - Maps `subgraph_result.messages` → `messages`
  - Maps all fields to `preferences.*`
  - Preserves `complete_state` from subgraph

- `call_preferences_subgraph_node(state, config)`: Returns `Command(goto="__end__", update={transformed_state})`

## complete_state Values

| Value | Meaning | Supervisor Action |
|-------|---------|------------------|
| `"not_started"` | No preference collection started | Continue to subgraph |
| `"incomplete"` | Some fields missing, awaiting user response | Pause (goto `__end__`), wait for user |
| `"completed"` | All required fields collected | End (goto `call_weather_subgraph_node`) |

## Workflow for Single Turn (Complete Info)

```
User provides all info
    ↓
supervisor_node (complete_state="not_started")
    ↓ goto call_preferences_subgraph_node
call_preferences_subgraph_node
    ↓ transform_state2subgraph()
preferences_subgraph
    ↓ START
extract_intent_node (extracts all fields)
    ↓ goto check_complete_node
check_complete_node (all required fields present)
    ↓ goto __end__, complete_state="completed"
preferences_subgraph returns
    ↓ transform_subgraph2state()
call_preferences_subgraph_node returns
    ↓ Command(goto="__end__", update={...})
END
```

## Workflow for Multi Turn (Incomplete Info)

```
User provides partial info
    ↓
supervisor_node (complete_state="not_started")
    ↓ goto call_preferences_subgraph_node
preferences_subgraph
    ↓ START
extract_intent_node (extracts some fields, origin=None)
    ↓ goto check_complete_node
check_complete_node (origin is None)
    ↓ goto ask_followup_node
ask_followup_node (generates follow-up question)
    ↓ goto __end__, complete_state="incomplete"
preferences_subgraph returns
    ↓ transform_subgraph2state()
call_preferences_subgraph_node returns
    ↓ Command(goto="__end__", update={...})
END (checkpoint saved, pause for user input)

User provides missing info
    ↓
supervisor_node (complete_state="incomplete")
    ↓ goto call_preferences_subgraph_node
preferences_subgraph (resumes from checkpoint)
    ↓
extract_intent_node (extracts origin)
    ↓ goto check_complete_node
check_complete_node (all fields present)
    ↓ goto __end__, complete_state="completed"
preferences_subgraph returns
    ↓ transform_subgraph2state()
call_preferences_subgraph_node returns
    ↓ Command(goto="__end__", update={...})
END
```

## Notes

- README.md contains detailed architecture documentation in Chinese
- Use `Command` for node routing, not conditional edges
- LLM JSON parsing: Use `parse_llm_json_response()` and `extract_and_build_updates()` from utils
- All prompts are in Chinese (SYSTEM_PROMPT, extract_intent_node, ask_followup_node)
- Current LLM uses Anthropic/MiniMax via langchain-anthropic
- `call_preferences_subgraph_node` requires `config` parameter with `thread_id`
- Parent graph calls subgraph via `transform_state2subgraph` / `transform_subgraph2state`
- Supervisor routes based on `complete_state`: `"completed"` → `__end__`, otherwise continue

## Important: config Parameter Type Annotation

**DO NOT use type annotation on `config` parameter in node functions.**

LangGraph passes a `RunnableConfig` object to node functions. If you add a type annotation like `config: dict[str, Any] | None`, the config will NOT be passed correctly (it will be `None`).

**Correct:**
```python
def supervisor_node(state: State, config=None) -> Command[...]:
```

**Incorrect:**
```python
def supervisor_node(state: State, config: dict[str, Any] | None = None) -> Command[...]:
```

This applies to ALL node functions that receive `config`.