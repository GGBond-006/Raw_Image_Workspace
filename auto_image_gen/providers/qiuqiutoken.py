import base64
import mimetypes
import os
import time
from typing import Dict, Any, Optional, List
import requests

from .base import BaseImageProvider, ImageGenRequest, ImageGenResponse


class QiuQiuTokenProvider(BaseImageProvider):
    """
    球球Token 图像 API 适配器（OpenAI GPT-Image 兼容接口）
    默认使用 size="auto"，配合中文像素级排版提示词驱动原生 1:1 (1254x1254) 或 3:4 (1086x1448) 无损画布。
    """

    def _get_gateway_urls(self) -> List[str]:
        urls = [self.config.get("base_url", "https://api.qiuqiutoken.net/v1").rstrip("/")]
        for fb in self.config.get("fallback_urls", []):
            fb_clean = fb.rstrip("/")
            if fb_clean not in urls:
                urls.append(fb_clean)
        return urls

    def generate(self, req: ImageGenRequest) -> ImageGenResponse:
        if not self.api_token:
            raise ValueError(
                "未配置球球Token API 令牌！请通过命令行 `--token sk-...` 传入，"
                "或设置环境变量 `QIUQIU_API_TOKEN`，或在 `config/providers.json` 中填写 `api_key`。"
            )

        defaults = self.config.get("default_params", {})
        model = req.model or self.config.get("default_model", "gpt-image-2")
        quality = req.quality or defaults.get("quality", "high")
        input_fidelity = req.input_fidelity or defaults.get("input_fidelity", "high")
        moderation = defaults.get("moderation", "low")
        api_size = req.size or "auto"
        timeout = self.config.get("timeout_seconds", 180)

        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }

        has_refs = bool(req.reference_images)
        for img_path in req.reference_images:
            if not os.path.isfile(img_path):
                raise FileNotFoundError(f"参考图文件不存在: {img_path}")

        gateways = self._get_gateway_urls()
        last_err: Optional[Exception] = None
        t0 = time.time()

        for gw_url in gateways:
            endpoint = f"{gw_url}/images/edits" if has_refs else f"{gw_url}/images/generations"
            try:
                if has_refs:
                    form_data = [
                        ("model", (None, model)),
                        ("prompt", (None, req.prompt)),
                        ("size", (None, api_size)),
                        ("quality", (None, quality)),
                        ("input_fidelity", (None, input_fidelity)),
                        ("background", (None, req.background)),
                        ("output_format", (None, "png")),
                        ("moderation", (None, moderation)),
                        ("n", (None, "1")),
                    ]
                    open_files = []
                    try:
                        for ref_path in req.reference_images:
                            mime_type, _ = mimetypes.guess_type(ref_path)
                            mime_type = mime_type or "image/jpeg"
                            f_obj = open(ref_path, "rb")
                            open_files.append(f_obj)
                            form_data.append(
                                ("image[]", (os.path.basename(ref_path), f_obj, mime_type))
                            )
                        if req.mask_image and os.path.isfile(req.mask_image):
                            f_mask = open(req.mask_image, "rb")
                            open_files.append(f_mask)
                            form_data.append(
                                ("mask", (os.path.basename(req.mask_image), f_mask, "image/png"))
                            )

                        resp = requests.post(
                            endpoint,
                            headers=headers,
                            files=form_data,
                            timeout=timeout,
                        )
                    finally:
                        for f_obj in open_files:
                            f_obj.close()
                else:
                    payload = {
                        "model": model,
                        "prompt": req.prompt,
                        "size": api_size,
                        "quality": quality,
                        "background": req.background,
                        "output_format": "png",
                        "moderation": moderation,
                        "n": 1,
                    }
                    payload.update(req.extra_params)
                    resp = requests.post(
                        endpoint,
                        headers={**headers, "Content-Type": "application/json"},
                        json=payload,
                        timeout=timeout,
                    )

                if resp.status_code != 200:
                    err_text = resp.text[:500]
                    if resp.status_code in (400, 401, 403):
                        raise RuntimeError(f"球球Token API 返回 HTTP {resp.status_code}: {err_text}")
                    raise RuntimeError(f"网关 {gw_url} 返回 HTTP {resp.status_code}: {err_text}")

                resp_json = resp.json()
                data_list = resp_json.get("data", [])
                if not data_list:
                    raise RuntimeError(f"球球Token API 响应缺少 data 字段: {resp_json}")

                first_item = data_list[0]
                if "b64_json" in first_item and first_item["b64_json"]:
                    raw_img_bytes = base64.b64decode(first_item["b64_json"])
                elif "url" in first_item and first_item["url"]:
                    dl_resp = requests.get(first_item["url"], timeout=60)
                    dl_resp.raise_for_status()
                    raw_img_bytes = dl_resp.content
                else:
                    raise RuntimeError(f"球球Token API 响应未包含 b64_json 或 url: {first_item}")

                final_bytes, raw_w, raw_h = self.normalize_image_size(
                    raw_bytes=raw_img_bytes,
                    target_width=req.target_width,
                    target_height=req.target_height,
                    resize_mode=req.resize_mode,
                    output_format=req.output_format,
                )

                elapsed = round(time.time() - t0, 2)
                return ImageGenResponse(
                    image_bytes=final_bytes,
                    provider_id=self.provider_id,
                    model_used=model,
                    endpoint_used=endpoint,
                    raw_width=raw_w,
                    raw_height=raw_h,
                    final_width=req.target_width,
                    final_height=req.target_height,
                    elapsed_seconds=elapsed,
                )

            except Exception as e:
                last_err = e
                if "HTTP 40" in str(e):
                    raise
                print(f"[警告] 线路 {endpoint} 请求异常 ({e})，尝试切换下一备用网关...")

        raise RuntimeError(f"所有球球Token网关线路均请求失败，最后错误: {last_err}")
