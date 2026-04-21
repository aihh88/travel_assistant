from typing import TypedDict


# 对助手的输出约束


class TransportationOption(TypedDict):
    """交通选项 - 航班/火车/租车"""
    type: str  # "flight", "train", "car_rental"
    route: str  # 路线
    departure_time: str | None  # 出发时间
    arrival_time: str | None  # 到达时间
    duration: str | None  # 行程时长
    price: float  # 价格
    currency: str  # 币种
    booking_url: str | None  # 预订链接


class AccommodationOption(TypedDict):
    """住宿选项 - 酒店/Airbnb/民宿"""
    name: str  # 名称
    type: str  # "hotel", "airbnb", "hostel", "resort"
    location: str  # 位置
    price_per_night: float  # 每晚价格
    currency: str  # 币种
    rating: float | None  # 评分
    amenities: list[str]  # 设施/服务
    booking_url: str | None  # 预订链接


class ActivityOption(TypedDict):
    """活动/景点选项"""
    name: str  # 名称
    location: str  # 位置
    category: str  # "sightseeing", "restaurant", "shopping", "entertainment"
    duration: str | None  # 时长
    price: float | None  # 价格
    currency: str | None  # 币种
    rating: float | None  # 评分
    booking_url: str | None  # 预订链接


class WeatherInfo(TypedDict):
    """天气预报信息"""
    city: str  # 城市
    date: str  # 日期
    temperature_high: float  # 最高温度
    temperature_low: float  # 最低温度
    condition: str  # "sunny", "cloudy", "rainy", etc.
    humidity: int | None  # 湿度
