import json
import os
from typing import Optional, Dict, Any
from .base import BaseImageProvider, ImageGenRequest, ImageGenResponse
from .qiuqiutoken import QiuQiuTokenProvider

PROVIDER_CLASSES = {
    "QiuQiuTokenProvider": QiuQiuTokenProvider,
}


def load_providers_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    if not config_path:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "providers.json"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_provider(
    provider_id: Optional[str] = None,
    api_token: Optional[str] = None,
    config_path: Optional[str] = None,
) -> BaseImageProvider:
    cfg = load_providers_config(config_path)
    pid = provider_id or cfg.get("default_provider", "qiuqiutoken")
    providers_map = cfg.get("providers", {})
    if pid not in providers_map:
        raise ValueError(f"未知的生图平台标识: {pid}，已配置平台: {list(providers_map.keys())}")

    p_cfg = providers_map[pid]
    cls_name = p_cfg.get("adapter_class", "QiuQiuTokenProvider")
    cls = PROVIDER_CLASSES.get(cls_name)
    if not cls:
        raise ValueError(f"未注册的适配器类: {cls_name}")

    return cls(provider_id=pid, config=p_cfg, api_token=api_token)
