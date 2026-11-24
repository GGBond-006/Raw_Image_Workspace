import io
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from PIL import Image


@dataclass
class ImageGenRequest:
    """统一的跨平台生图请求结构"""
    prompt: str
    target_width: int = 1000
    target_height: int = 1000
    reference_images: List[str] = field(default_factory=list)
    mask_image: Optional[str] = None
    model: Optional[str] = None
    size: str = "auto"                    # 默认使用 auto，让提示词中的精确尺寸/比例驱动原生 1:1 或 3:4 画布
    quality: Optional[str] = None         # low / medium / high / auto
    input_fidelity: Optional[str] = None  # high / low
    background: str = "opaque"            # opaque / transparent / auto
    output_format: str = "jpeg"           # jpeg / png / webp
    resize_mode: str = "smart_crop"       # smart_crop / exact_resize / pad_white
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageGenResponse:
    """统一的跨平台生图响应结构"""
    image_bytes: bytes
    provider_id: str
    model_used: str
    endpoint_used: str
    raw_width: int
    raw_height: int
    final_width: int
    final_height: int
    elapsed_seconds: float


class BaseImageProvider(ABC):
    """多平台生图模型 API 抽象基类"""

    def __init__(self, provider_id: str, config: Dict[str, Any], api_token: Optional[str] = None):
        self.provider_id = provider_id
        self.config = config
        self.api_token = (
            api_token
            or config.get("api_key")
            or os.environ.get(config.get("api_key_env", "QIUQIU_API_TOKEN"), "")
        )

    @abstractmethod
    def generate(self, req: ImageGenRequest) -> ImageGenResponse:
        """执行文生图或参考图受控生图"""
        pass

    @staticmethod
    def normalize_image_size(
        raw_bytes: bytes,
        target_width: int,
        target_height: int,
        resize_mode: str = "smart_crop",
        output_format: str = "jpeg",
        background_color: tuple = (255, 255, 255),
    ) -> tuple[bytes, int, int]:
        """
        将 API 返回的高清原图（如 1254x1254 或 1086x1448）高保真转换为目标像素尺寸
        （如 1000x1000、750x1000、900x1200），采用 subsampling=0 保持文字与丝印最高锐度。
        """
        with Image.open(io.BytesIO(raw_bytes)) as im:
            raw_w, raw_h = im.size

            fmt = output_format.upper()
            if fmt == "JPG":
                fmt = "JPEG"

            if fmt == "JPEG" and im.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", im.size, background_color)
                if im.mode == "P":
                    im = im.convert("RGBA")
                bg.paste(im, mask=im.split()[-1] if "A" in im.mode else None)
                im = bg
            elif fmt == "JPEG" and im.mode != "RGB":
                im = im.convert("RGB")

            raw_ratio = raw_w / max(1, raw_h)
            target_ratio = target_width / max(1, target_height)

            if (raw_w, raw_h) == (target_width, target_height):
                out_im = im
            elif abs(raw_ratio - target_ratio) < 0.02 or resize_mode == "exact_resize":
                # 宽高比一致（如 1254x1254 -> 1000x1000，或 1086x1448 -> 900x1200 / 750x1000），直接全图等比缩放，0 裁切！
                out_im = im.resize((target_width, target_height), Image.Resampling.LANCZOS)
            elif resize_mode == "pad_white":
                scale = min(target_width / raw_w, target_height / raw_h)
                new_w = max(1, int(round(raw_w * scale)))
                new_h = max(1, int(round(raw_h * scale)))
                resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                canvas_mode = "RGB" if fmt == "JPEG" else ("RGBA" if "A" in im.mode else "RGB")
                canvas_bg = background_color if canvas_mode == "RGB" else (*background_color, 255)
                out_im = Image.new(canvas_mode, (target_width, target_height), canvas_bg)
                offset_x = (target_width - new_w) // 2
                offset_y = (target_height - new_h) // 2
                out_im.paste(resized, (offset_x, offset_y))
            else:
                scale = max(target_width / raw_w, target_height / raw_h)
                new_w = max(1, int(round(raw_w * scale)))
                new_h = max(1, int(round(raw_h * scale)))
                resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                left = (new_w - target_width) // 2
                top = (new_h - target_height) // 2
                out_im = resized.crop((left, top, left + target_width, top + target_height))

            buf = io.BytesIO()
            if fmt == "JPEG":
                # subsampling=0 (4:4:4) + quality=98 确保细小文字与红色/蓝色边缘绝不发虚
                out_im.save(buf, format="JPEG", quality=98, subsampling=0)
            elif fmt == "WEBP":
                out_im.save(buf, format="WEBP", quality=98)
            else:
                out_im.save(buf, format=fmt)
            return buf.getvalue(), raw_w, raw_h
