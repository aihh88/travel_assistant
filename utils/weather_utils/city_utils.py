"""
城市查询工具，用于根据地址查找城市代码
"""

import gzip
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

from .jwt_utils import get_cached_weather_jwt

load_dotenv()

API_HOST = os.getenv("WEATHER_API_HOST")


@dataclass
class CityInfo:
    """城市信息"""
    name: str
    id: str  # 城市/地区ID
    lat: float # 纬度
    lon: float # 经度
    adm2: str  # 上级行政区划
    adm1: str  # 一级行政区域
    country: str # 国家
    tz: str  # 时区
    utc_offset: str  # UTC偏移
    is_dst: Literal[0, 1] # 是否夏令时
    city_type: str  # type 字段
    rank: int # 地区评分
    fx_link: str # 响应式页面链接
    sources: list[str] # 数据来源
    license: list[str] # 许可证信息


def lookup_city(location: str) -> CityInfo | None:
    """
    根据地址查找城市信息

    Args:
        location: 地址/城市名（如 "北京"、"上海"、"Beijing"）

    Returns:
        CityInfo 对象，查询失败返回 None

    Raises:
        ValueError: 参数为空
        RuntimeError: API 请求失败
    """
    if not location or not location.strip():
        raise ValueError("location 参数不能为空")

    token = get_cached_weather_jwt()
    url = f"https://{API_HOST}/geo/v2/city/lookup?location={urllib.parse.quote(location)}"

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
        raise RuntimeError(f"城市查询失败: HTTP {e.code} - {error_body}")
    except Exception as e:
        raise RuntimeError(f"城市查询失败: {str(e)}")

    if result.get("code") != "200":
        raise RuntimeError(f"API 返回错误: {result.get('code')}")

    locations = result.get("location", [])
    if not locations:
        return None

    # 返回第一个匹配结果
    loc = locations[0]
    return CityInfo(
        name=loc.get("name", ""),
        id=loc.get("id", ""),
        lat=float(loc.get("lat", 0)),
        lon=float(loc.get("lon", 0)),
        adm2=loc.get("adm2", ""),
        adm1=loc.get("adm1", ""),
        country=loc.get("country", ""),
        tz=loc.get("tz", ""),
        utc_offset=loc.get("utcOffset", ""),
        is_dst=loc.get("isDst", 0),
        city_type=loc.get("type", ""),
        rank=loc.get("rank", 0),
        fx_link=loc.get("fxLink", ""),
        sources=result.get("refer", {}).get("sources", []),
        license=result.get("refer", {}).get("license", []),
    )


def lookup_city_by_coordinates(lat: float, lon: float) -> CityInfo | None:
    """
    根据经纬度查找最近的城市信息

    Args:
        lat: 纬度
        lon: 经度

    Returns:
        CityInfo 对象，查询失败返回 None
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("无效的经纬度范围")

    token = get_cached_weather_jwt()
    url = f"https://{API_HOST}/geo/v2/city/lookup?location={lat},{lon}"

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
    except Exception as e:
        raise RuntimeError(f"城市查询失败: {str(e)}")

    if result.get("code") != "200":
        raise RuntimeError(f"API 返回错误: {result.get('code')}")

    locations = result.get("location", [])
    if not locations:
        return None

    loc = locations[0]
    return CityInfo(
        name=loc.get("name", ""),
        id=loc.get("id", ""),
        lat=float(loc.get("lat", 0)),
        lon=float(loc.get("lon", 0)),
        adm2=loc.get("adm2", ""),
        adm1=loc.get("adm1", ""),
        country=loc.get("country", ""),
        tz=loc.get("tz", ""),
        utc_offset=loc.get("utcOffset", ""),
        is_dst=loc.get("isDst", 0),
        city_type=loc.get("type", ""),
        rank=loc.get("rank", 0),
        fx_link=loc.get("fxLink", ""),
        sources=result.get("refer", {}).get("sources", []),
        license=result.get("refer", {}).get("license", []),
    )
