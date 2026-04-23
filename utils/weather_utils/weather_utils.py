"""
天气查询工具，根据城市ID查询天气预报
"""

import gzip
import json
import os
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from dotenv import load_dotenv

from .jwt_utils import get_cached_weather_jwt

load_dotenv()

API_HOST = os.getenv("WEATHER_API_HOST")


@dataclass
class DailyWeather:
    """单日天气预报"""
    fx_date: str  # 预报日期
    sunrise: str  # 日出时间
    sunset: str  # 日落时间
    moonrise: str  # 月升时间
    moonset: str  # 月落时间
    moon_phase: str  # 月相名称
    moon_phase_icon: str  # 月相图标代码
    temp_max: int  # 最高温度
    temp_min: int  # 最低温度
    icon_day: str  # 白天天气图标代码
    text_day: str  # 白天天气文字描述
    icon_night: str  # 夜间天气图标代码
    text_night: str  # 夜间天气文字描述
    wind_360_day: int  # 白天风向360角度
    wind_dir_day: str  # 白天风向
    wind_scale_day: str  # 白天风力等级
    wind_speed_day: int  # 白天风速（公里/小时）
    wind_360_night: int  # 夜间风向360角度
    wind_dir_night: str  # 夜间风向
    wind_scale_night: str  # 夜间风力等级
    wind_speed_night: int  # 夜间风速（公里/小时）
    precip: float  # 降水量（毫米）
    uv_index: int  # 紫外线强度指数
    humidity: int  # 相对湿度（百分比）
    pressure: int  # 气气压（百帕）
    vis: int  # 能见度（公里）
    cloud: int  # 云量（百分比）


@dataclass
class WeatherResult:
    """天气查询结果"""
    code: str  # 状态码
    update_time: str  # 最近更新时间
    fx_link: str  # 响应式页面链接
    daily: list[DailyWeather] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    license: list[str] = field(default_factory=list)


def _parse_daily_weather(daily_data: dict) -> DailyWeather:
    """解析单日天气数据"""
    return DailyWeather(
        fx_date=daily_data.get("fxDate", ""),
        sunrise=daily_data.get("sunrise", ""),
        sunset=daily_data.get("sunset", ""),
        moonrise=daily_data.get("moonrise", ""),
        moonset=daily_data.get("moonset", ""),
        moon_phase=daily_data.get("moonPhase", ""),
        moon_phase_icon=daily_data.get("moonPhaseIcon", ""),
        temp_max=int(daily_data.get("tempMax", 0)),
        temp_min=int(daily_data.get("tempMin", 0)),
        icon_day=daily_data.get("iconDay", ""),
        text_day=daily_data.get("textDay", ""),
        icon_night=daily_data.get("iconNight", ""),
        text_night=daily_data.get("textNight", ""),
        wind_360_day=int(daily_data.get("wind360Day", 0)),
        wind_dir_day=daily_data.get("windDirDay", ""),
        wind_scale_day=daily_data.get("windScaleDay", ""),
        wind_speed_day=int(daily_data.get("windSpeedDay", 0)),
        wind_360_night=int(daily_data.get("wind360Night", 0)),
        wind_dir_night=daily_data.get("windDirNight", ""),
        wind_scale_night=daily_data.get("windScaleNight", ""),
        wind_speed_night=int(daily_data.get("windSpeedNight", 0)),
        precip=float(daily_data.get("precip", 0)),
        uv_index=int(daily_data.get("uvIndex", 0)),
        humidity=int(daily_data.get("humidity", 0)),
        pressure=int(daily_data.get("pressure", 0)),
        vis=int(daily_data.get("vis", 0)),
        cloud=int(daily_data.get("cloud", 0)) if daily_data.get("cloud") else 0,
    )


def query_weather(
    city_id: str,
    days: Literal[3, 7, 10, 15, 30] = 3,
) -> WeatherResult:
    """
    根据城市ID查询天气预报

    Args:
        city_id: 城市/地区ID（通过 lookup_city 或 lookup_city_by_coordinates 获取）
        days: 预报天数，支持 3/7/10/15/30 天，默认 3 天

    Returns:
        WeatherResult 对象，包含天气预报数据

    Raises:
        ValueError: 参数无效
        RuntimeError: API 请求失败
    """
    if not city_id or not city_id.strip():
        raise ValueError("city_id 参数不能为空")

    valid_days = {3, 7, 10, 15, 30}
    if days not in valid_days:
        raise ValueError(f"days 参数必须是 {valid_days} 之一")

    token = get_cached_weather_jwt()
    days_param = f"{days}d"
    url = f"https://{API_HOST}/v7/weather/{days_param}?location={urllib.parse.quote(city_id)}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept-Encoding": "gzip",
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = gzip.decompress(response.read()).decode("utf-8")
            result = json.loads(data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"天气查询失败: HTTP {e.code} - {error_body}")
    except Exception as e:
        raise RuntimeError(f"天气查询失败: {str(e)}")

    if result.get("code") != "200":
        raise RuntimeError(f"API 返回错误: {result.get('code')}")

    daily_list = result.get("daily", [])
    weather_daily = [_parse_daily_weather(d) for d in daily_list]

    return WeatherResult(
        code=result.get("code", ""),
        update_time=result.get("updateTime", ""),
        fx_link=result.get("fxLink", ""),
        daily=weather_daily,
        sources=result.get("refer", {}).get("sources", []),
        license=result.get("refer", {}).get("license", []),
    )


def get_travel_weather(
    destination: str,
    departure_date: str,
    days: int
) -> list[dict]:
    """
    获取游玩期间的天气预报

    Args:
        destination: 目的地城市名
        departure_date: 出发日期 YYYY-MM-DD
        days: 游玩天数

    Returns:
        游玩期间的天气预报列表

    Raises:
        ValueError: 参数无效
        RuntimeError: 查询失败
    """
    if not destination or not departure_date or not days:
        raise ValueError("destination, departure_date, days 不能为空")

    if days <= 0:
        raise ValueError("days 必须大于 0")

    # 计算需要查询的天数
    departure_date_obj = date.fromisoformat(departure_date)
    today = date.today()
    days_from_today = (departure_date_obj - today).days
    needed_days = days_from_today + days

    # 向上取整到 API 支持的天数
    valid_days = {3, 7, 10, 15, 30}
    query_days = min(filter(lambda d: d >= needed_days, valid_days), default=30)

    # 查询城市ID
    from .city_utils import lookup_city
    city_info = lookup_city(destination)
    if not city_info:
        raise RuntimeError(f"无法找到城市: {destination}")

    # 查询天气
    weather_result = query_weather(city_info.id, query_days)

    # 过滤并转换结果，只保留游玩期间的数据
    travel_weather = []
    for dw in weather_result.daily:
        if date.fromisoformat(dw.fx_date) >= departure_date_obj:
            travel_weather.append({
                "date": dw.fx_date,
                "temp_max": dw.temp_max,
                "temp_min": dw.temp_min,
                "text_day": dw.text_day,
                "text_night": dw.text_night,
                "wind_dir_day": dw.wind_dir_day,
                "wind_scale_day": dw.wind_scale_day,
                "precip": dw.precip,
                "uv_index": dw.uv_index,
            })
            if len(travel_weather) >= days:
                break

    return travel_weather
