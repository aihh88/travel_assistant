"""
高德地图POI搜索工具

官方文档: https://lbs.amap.com/api/webservice/guide/api-advanced/search
"""

import json
import os
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

MAP_API_KEY = os.getenv("MAP_API_KEY", "")
AMAP_PLACE_API_URL = "https://restapi.amap.com/v3/place/text"


@dataclass
class POIInfo:
    """POI点信息"""
    name: str  # 名称
    location: str  # 经纬度 "经度,纬度"
    address: str  # 地址
    tel: str  # 电话
    type: str  # 类型代码
    type_des: str  # 类型描述
    biz_type: str  # 业务类型
    biz_ext: str  # 业务扩展信息
    rating: str  # 评分
    price: str  # 价格


@dataclass
class POISearchResult:
    """POI搜索结果"""
    count: str  # 数量
    page_count: str  # 总页数
    page_index: str  # 当前页码
    pois: list[POIInfo] = field(default_factory=list)  # POI列表


def _parse_poi(poi_data: dict) -> POIInfo:
    """解析POI数据"""
    return POIInfo(
        name=poi_data.get("name", ""),
        location=poi_data.get("location", ""),
        address=poi_data.get("address", ""),
        tel=poi_data.get("tel", ""),
        type=poi_data.get("type", ""),
        type_des=poi_data.get("type_des", ""),
        biz_type=poi_data.get("biz_type", ""),
        biz_ext=poi_data.get("biz_ext", ""),
        rating=poi_data.get("rating", ""),
        price=poi_data.get("price", ""),
    )


def search_pois(
    keywords: str | list[str] | None = None,
    city: str | None = None,
    types: str | None = None,
    page: int = 1,
    offset: int = 20,
) -> POISearchResult:
    """
    搜索POI点

    Args:
        keywords: 搜索关键词（字符串或列表），可选
        city: 城市名称或编码（可选）
        types: POI类型编码（可选）
        page: 页码，默认1
        offset: 每页数量，默认20

    Returns:
        POISearchResult 对象，包含搜索结果

    Raises:
        ValueError: 参数无效
        RuntimeError: API 请求失败
    """
    if not MAP_API_KEY:
        raise ValueError("MAP_API_KEY 未设置，请检查 .env 文件")

    if not keywords and not types:
        raise ValueError("keywords 和 types 至少需要一个不能为空")

    # 处理关键词列表
    if keywords:
        if isinstance(keywords, list):
            keywords = "|".join(keywords)
    else:
        keywords = None

    params = {
        "key": MAP_API_KEY,
        "page": page,
        "offset": offset,
    }

    if keywords:
        params["keywords"] = keywords
    if city:
        params["city"] = city
    if types:
        params["types"] = types

    url = f"{AMAP_PLACE_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"POI搜索失败: HTTP {e.code}")
    except Exception as e:
        raise RuntimeError(f"POI搜索失败: {str(e)}")

    if data.get("status") != "1":
        info = data.get("info", "")
        raise RuntimeError(f"POI搜索失败: {info}")

    pois_data = data.get("pois", [])
    pois = [_parse_poi(p) for p in pois_data]

    return POISearchResult(
        count=data.get("count", "0"),
        pois=pois,
        page_count=data.get("page_count", "0"),
        page_index=data.get("page_index", "0"),
    )


def search_attractions(
    city: str,
    keywords: str | list[str] | None = None,
    page: int = 1,
    offset: int = 20,
) -> POISearchResult:
    """
    搜索景点POI

    默认搜索"旅游景点"类型，可通过keywords扩展

    Args:
        city: 城市名称
        keywords: 额外关键词（可选）
        page: 页码，默认1
        offset: 每页数量，默认20

    Returns:
        POISearchResult 对象

    Raises:
        ValueError: 参数无效
        RuntimeError: API 请求失败
    """
    type_str = "风景名胜"  # 旅游景点类型

    # 处理关键词
    keywords_arg = None
    if keywords:
        if isinstance(keywords, str):
            keywords_arg = keywords
        else:
            keywords_arg = "|".join(keywords)

    return search_pois(
        keywords=keywords_arg,
        city=city,
        types=type_str,
        page=page,
        offset=offset,
    )


def get_attractions_by_destination(
    destination: str,
) -> list[dict]:
    """
    根据目的地获取景点列表

    Args:
        destination: 目的地城市名

    Returns:
        景点列表，每个元素包含 name, location, address, rating
    """
    if not destination:
        raise ValueError("destination 不能为空")

    # 搜索景点
    result = search_attractions(city=destination)

    if not result.pois:
        return []

    return [
        {
            "name": poi.name,
            "location": poi.location,
            "address": poi.address,
            "rating": float(poi.rating) if poi.rating and poi.rating != "" else None,
            "type": poi.type_des,
        }
        for poi in result.pois
    ]