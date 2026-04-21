"""
Main entry point for travel assistant
"""

from datetime import date

from assistants.preferences_assistant.graph import preferences_subgraph


def test_weather():
    """测试天气查询"""
    from assistants.weather_practical_info_assistant.utils import lookup_city, query_weather

    city = lookup_city("西安")
    print(f"城市: {city.name}, ID: {city.id}")

    weather = query_weather(city.id, days=3)
    print(f"更新时间: {weather.update_time}")
    print("-" * 60)

    for day in weather.daily:
        print(f"日期: {day.fx_date}")
        print(f"  白天: {day.text_day} ({day.temp_min}~{day.temp_max}°C)")
        print(f"  夜间: {day.text_night}")
        print(f"  风力: {day.wind_dir_day} {day.wind_scale_day}级")
        print(f"  紫外线: {day.uv_index}, 湿度: {day.humidity}%")
        print()


def test_get_current_date():
    """测试 get_current_date 工具 - '后天去旅行'"""
    print(f"当前日期: {date.today()}")
    print("-" * 60)

    # 初始化完整的 PreferencesState
    initial_state = {
        "messages": [{"role": "user", "content": "后天去旅行"}],
        "origin": None,
        "destinations": [],
        "departure_date": None,
        "days": None,
        "budget": None,
        "travelers": None,
        "children": None,
        "tags": [],
        "special_needs": [],
        "current_step": "",
        "complete_state": "not_started",
    }

    # 测试：用户说"后天去旅行"
    result = preferences_subgraph.invoke(
        initial_state,
        config={"thread_id": "test_1"}
    )

    print("提取的偏好信息:")
    print(f"  出发日期: {result.get('departure_date')}")
    print(f"  complete_state: {result.get('complete_state')}")


if __name__ == "__main__":
    test_get_current_date()
