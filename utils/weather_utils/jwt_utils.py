"""
JWT 生成工具，用于请求天气数据 API

使用 Ed25519 算法签名
"""

import base64
import json
import time
import os
from functools import lru_cache

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dotenv import load_dotenv

load_dotenv()


# 从环境变量获取配置
JWT_SECRET = os.getenv("WEATHER_JWT_SECRET")  # Ed25519 私钥（base64 编码）
JWT_KID = os.getenv("WEATHER_JWT_KID")  # 凭据 ID
JWT_PROJECT_ID = os.getenv("WEATHER_PROJECT_ID")  # 项目 ID（作为 sub）
# 过期时间（秒），默认 30 天（2592000 秒）
JWT_EXPIRES_IN = int(os.getenv("WEATHER_JWT_EXPIRES_IN", "86400"))

def _base64url_encode(data: bytes) -> str:
    """Base64URL 编码（不带 padding）"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _get_private_key():
    """解析私钥，支持多种格式"""
    private_key_bytes = base64.b64decode(JWT_SECRET)

    # 纯私钥格式（32字节）
    if len(private_key_bytes) == 32:
        return Ed25519PrivateKey.from_private_bytes(private_key_bytes)

    # PKCS#8 格式（48字节）：302e020100300506032b657004220420<32字节私钥>
    # 或 64 字节格式（含公钥）：<32字节私钥><32字节公钥>
    hex_str = private_key_bytes.hex()

    # 查找 OCTET STRING 04 20 模式（PKCS#8 标准格式）
    pos = hex_str.find("0420")
    if pos >= 0 and len(private_key_bytes) == 48:
        key_hex = hex_str[pos + 4 : pos + 4 + 64]
        return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex))

    # 64字节格式：后32字节是私钥
    if len(private_key_bytes) == 64:
        return Ed25519PrivateKey.from_private_bytes(private_key_bytes[-32:])

    raise ValueError(f"无法解析私钥格式，长度: {len(private_key_bytes)}")


def generate_weather_jwt(expires_in: int | None = None) -> str:
    """
    生成天气 API 请求用的 JWT（Ed25519 签名）

    Args:
        expires_in: 过期时间（秒），默认从环境变量 WEATHER_JWT_EXPIRES_IN 读取（默认 30 天）

    Returns:
        JWT 字符串

    环境变量:
        WEATHER_JWT_SECRET: Ed25519 私钥（base64 编码）
        WEATHER_JWT_KID: 凭据 ID
        WEATHER_PROJECT_ID: 项目 ID（作为 JWT 的 sub 字段）
        WEATHER_JWT_EXPIRES_IN: 过期时间（秒），默认 2592000（30 天）
    """
    if not JWT_SECRET:
        raise ValueError("WEATHER_JWT_SECRET 环境变量未设置")
    if not JWT_KID:
        raise ValueError("WEATHER_JWT_KID 环境变量未设置")
    if not JWT_PROJECT_ID:
        raise ValueError("WEATHER_PROJECT_ID 环境变量未设置")

    # 从配置或参数获取过期时间
    if expires_in is None:
        expires_in = JWT_EXPIRES_IN

    # iat 设置为当前时间之前 30 秒（防止时间误差）
    iat = int(time.time()) - 30
    exp = iat + expires_in

    # Header（不包含 typ，避免与保留字段冲突）
    header = {
        "alg": "EdDSA",
        "kid": JWT_KID,
    }

    # Payload（不包含 typ/iss/aud/nbf 等保留字段）
    payload = {
        "sub": JWT_PROJECT_ID,
        "iat": iat,
        "exp": exp,
    }

    # 获取私钥（兼容 PKCS#8 格式）
    private_key = _get_private_key()

    # 使用 PyJWT + cryptography 生成 JWT
    token = jwt.encode(
        payload,
        private_key,
        algorithm="EdDSA",
        headers={"kid": JWT_KID},
    )

    return token


def generate_weather_jwt_manual(expires_in: int | None = None) -> str:
    """
    手动生成 JWT（不依赖 PyJWT 的 EdDSA 实现）

    按照标准流程:
    1. Header 和 Payload 分别 JSON 序列化后 Base64URL 编码
    2. 拼接为 header.payload
    3. 使用 Ed25519 签名
    4. 签名结果 Base64URL 编码
    5. 拼接为 header.payload.signature
    """
    if not JWT_SECRET:
        raise ValueError("WEATHER_JWT_SECRET 环境变量未设置")
    if not JWT_KID:
        raise ValueError("WEATHER_JWT_KID 环境变量未设置")
    if not JWT_PROJECT_ID:
        raise ValueError("WEATHER_PROJECT_ID 环境变量未设置")

    if expires_in is None:
        expires_in = JWT_EXPIRES_IN

    iat = int(time.time()) - 30
    exp = iat + expires_in

    header = {"alg": "EdDSA", "kid": JWT_KID}
    payload = {"sub": JWT_PROJECT_ID, "iat": iat, "exp": exp}

    # Header Base64URL 编码
    header_json = json.dumps(header, separators=(",", ":"))
    header_bytes = _base64url_encode(header_json.encode("utf-8"))

    # Payload Base64URL 编码
    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_bytes = _base64url_encode(payload_json.encode("utf-8"))

    # 签名
    message = f"{header_bytes}.{payload_bytes}".encode("utf-8")
    private_key = _get_private_key()
    signature = private_key.sign(message)
    signature_bytes = _base64url_encode(signature)

    return f"{header_bytes}.{payload_bytes}.{signature_bytes}"


@lru_cache(maxsize=1)
def get_cached_weather_jwt() -> str:
    """获取缓存的 JWT（使用配置的过期时间），避免频繁生成"""
    return generate_weather_jwt()
