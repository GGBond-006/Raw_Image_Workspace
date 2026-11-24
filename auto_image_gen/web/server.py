# -*- coding: utf-8 -*-
"""
AutoShot 生图台 —— 本地 Web 后端服务（基于 Python 标准库 ThreadingHTTPServer，零额外依赖）
对接：
- web/scanner.py（原始素材文件夹扫描与 6 项预检）
- prompts/templates.py（12 类标准套图中文像素级提示词编译）
- providers/（多平台生图 API 网关，当前接入球球Token gpt-image-2）
"""
import base64
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import csv
import io
import json
import mimetypes
import os
import re
import shutil
import string
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
SECRETS_PATH = os.path.join(BASE_DIR, "config", "local_secrets.json")
CUSTOM_TEMPLATES_PATH = os.path.join(BASE_DIR, "config", "custom_templates.json")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PIL import Image
from providers import get_provider, load_providers_config, ImageGenRequest
from prompts import compile_all_jobs
from web.scanner import scan_product_folder


# ---------------- 工具函数 ----------------

def _read_json(path: str, default: Any) -> Any:
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_provider_token(provider_id: str) -> str:
    secrets = _read_json(SECRETS_PATH, {})
    tok = (secrets.get(provider_id) or {}).get("api_key", "")
    if tok:
        return tok
    cfg = load_providers_config()
    p_cfg = cfg.get("providers", {}).get(provider_id, {})
    env_key = p_cfg.get("api_key_env", "")
    return p_cfg.get("api_key") or (os.environ.get(env_key, "") if env_key else "")


def _mask_token(tok: str) -> str:
    if not tok:
        return ""
    if len(tok) <= 10:
        return "*" * len(tok)
    return tok[:6] + "••••••••" + tok[-4:]


def _short_tag_for_job(job: Dict[str, Any]) -> str:
    cat = job.get("category", "")
    fname = job.get("filename", "")
    if job.get("store_tag"):
        return job["store_tag"].replace("店铺", "")
    if cat.startswith("02_"):
        return "白底副图"
    if cat.startswith("03_"):
        return "包裹图"
    if cat.startswith("04_"):
        return "属性图"
    if cat.startswith("05_"):
        return "场景图"
    if cat.startswith("06_"):
        return "参数表" if "参数" in fname else "卖点图"
    if cat.startswith("07_"):
        return "广告图"
    if cat.startswith("08_"):
        return "结构图"
    if cat.startswith("09_"):
        return "手持对比"
    if cat.startswith("10_"):
        return "俄语主图"
    if cat.startswith("11_"):
        return "俄语包裹"
    return "套图"


def _tab_group_for_job(job: Dict[str, Any]) -> str:
    cat = job.get("category", "")
    if cat.startswith("01_"):
        return "main"
    if cat.startswith("02_"):
        return "sub"
    if cat.startswith("04_"):
        return "sku"
    if cat.startswith(("10_", "11_", "12_")):
        return "ru"
    return "detail"


def _scope_group_for_job(job: Dict[str, Any]) -> str:
    cat = job.get("category", "")
    if cat.startswith(("08_", "09_")):
        return "optional"
    if cat.startswith(("10_", "11_", "12_")):
        return "russian"
    return "general"


def _default_review_state(job: Dict[str, Any]) -> str:
    # 文字密集型图（参数表、部分俄语主图/包裹图）默认标为待复核，便于人工重点验收
    fname = job.get("filename", "")
    if "参数表" in fname or fname in ("RC4661C俄文1.jpg", "RC4661B_RC4226A俄文4.jpg"):
        return "review"
    return "approved"


# ---------------- 核心会话状态管理 ----------------

class StudioManager:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.scan_data: Optional[Dict[str, Any]] = None
        self.task_config: Optional[Dict[str, Any]] = None
        self.confirm_fields: List[Dict[str, Any]] = []
        self.provider_id: str = "qiuqiutoken"
        self.model_name: str = "gpt-image-2"
        self.quality: str = "high"

        self.jobs: List[Dict[str, Any]] = []
        self.job_records: Dict[str, Dict[str, Any]] = {}
        self.output_dir: str = ""

        # 批量任务运行状态（支持多线程并发调用生图 API）
        self.batch_running: bool = False
        self.batch_stop_requested: bool = False
        self.batch_total: int = 0
        self.batch_completed: int = 0
        self.batch_failed: int = 0
        self.batch_current: Optional[str] = None
        self.batch_running_files: set = set()
        self.batch_concurrency: int = max(1, min(6, int(os.environ.get("AUTOSHOT_CONCURRENCY", "3"))))
        self.batch_started_at: float = 0.0
        self.batch_elapsed_total: float = 0.0
        self.single_running_files: set = set()
        self.last_error: str = ""

        # 默认尝试自动载入 RC4661 示例目录（如果存在）
        default_folder = os.path.join(WORKSPACE_DIR, "RC4661 GX10遥控器")
        if os.path.isdir(default_folder):
            self.load_folder(default_folder)

    def list_providers(self) -> List[Dict[str, Any]]:
        cfg = load_providers_config()
        out = []
        for pid, p in cfg.get("providers", {}).items():
            tok = _get_provider_token(pid)
            models = p.get("models") or [p.get("default_model", "gpt-image-2"), "gpt-image-1.5", "gpt-image-1"]
            out.append({
                "id": pid,
                "display_name": p.get("display_name", pid).split("(")[0].strip(),
                "full_name": p.get("display_name", pid),
                "default_model": p.get("default_model", "gpt-image-2"),
                "models": models,
                "has_token": bool(tok),
                "token_masked": _mask_token(tok),
                "base_url": p.get("base_url", ""),
                "status": "online" if tok else "unconfigured",
            })
        return out

    def load_folder(self, folder_path: str) -> Dict[str, Any]:
        with self.lock:
            prev_scan = self.scan_data
            prev_cfg = self.task_config
            prev_conf = self.confirm_fields
            prev_out = self.output_dir
            prev_jobs = self.jobs
            prev_recs = self.job_records
            try:
                scanned = scan_product_folder(folder_path, BASE_DIR)
                self.scan_data = scanned
                self.task_config = scanned["task_config"]
                self.confirm_fields = scanned["confirm_fields"]
                spu = self.task_config["product_meta"]["spu_code"]
                self.output_dir = os.path.join(BASE_DIR, "outputs", spu)
                os.makedirs(self.output_dir, exist_ok=True)
                self._recompile_jobs(preserve_custom=False)
                return self.get_full_state()
            except Exception:
                # 失败时原子回滚，绝不损坏原有任务状态
                self.scan_data = prev_scan
                self.task_config = prev_cfg
                self.confirm_fields = prev_conf
                self.output_dir = prev_out
                self.jobs = prev_jobs
                self.job_records = prev_recs
                raise

    def _versions_dir(self) -> str:
        d = os.path.join(self.output_dir, ".versions")
        os.makedirs(d, exist_ok=True)
        return d

    def _meta_store_path(self) -> str:
        return os.path.join(self.output_dir, ".studio_meta.json")

    def _save_meta_store(self) -> None:
        if not self.output_dir:
            return
        payload = {
            "provider_id": self.provider_id,
            "model_name": self.model_name,
            "quality": self.quality,
            "records": {
                fn: {
                    "review_status": r.get("review_status", "approved"),
                    "custom_prompt": r.get("custom_prompt"),
                    "custom_refs": r.get("custom_refs"),
                    "active_version": r.get("active_version", 1),
                    "versions": r.get("versions", []),
                    "elapsed_seconds": r.get("elapsed_seconds"),
                    "provider_id": r.get("provider_id"),
                    "model_name": r.get("model_name"),
                }
                for fn, r in self.job_records.items()
            },
        }
        _write_json(self._meta_store_path(), payload)

    def _recompile_jobs(self, preserve_custom: bool = True) -> None:
        if not self.task_config:
            self.jobs = []
            return
        # 编译全量任务以获得各分组精确张数，并按当前 flags 编译实际选中 jobs
        self.jobs = compile_all_jobs(self.task_config)

        # 读取历史 generation_report.json 和 .studio_meta.json
        report_map: Dict[str, Dict[str, Any]] = {}
        report_path = os.path.join(self.output_dir, "generation_report.json")
        rep = _read_json(report_path, {})
        for item in rep.get("results", []):
            report_map[item["filename"]] = item

        saved_meta = _read_json(self._meta_store_path(), {}).get("records", {})
        old_records = self.job_records if preserve_custom else {}

        new_records: Dict[str, Dict[str, Any]] = {}
        for job in self.jobs:
            fn = job["filename"]
            out_path = os.path.join(self.output_dir, fn)
            exists = os.path.isfile(out_path)
            prev = old_records.get(fn) or saved_meta.get(fn) or {}
            rep_item = report_map.get(fn, {})

            actual_w, actual_h = job["target_width"], job["target_height"]
            if exists:
                try:
                    with Image.open(out_path) as im:
                        actual_w, actual_h = im.size
                except Exception:
                    pass

            versions = list(prev.get("versions") or [])
            # 过滤掉磁盘上不存在的旧版本记录
            versions = [v for v in versions if os.path.isfile(v.get("path", ""))]
            if exists and not versions:
                versions = [{
                    "ver": 1,
                    "path": out_path.replace("\\", "/"),
                    "ts": int(os.path.getmtime(out_path)),
                    "elapsed": rep_item.get("elapsed_seconds", 21.4),
                    "provider_id": rep_item.get("provider", self.provider_id),
                    "model_name": rep_item.get("model", self.model_name),
                    "prompt": rep_item.get("prompt") or job["prompt"],
                }]

            active_ver = prev.get("active_version") or (versions[-1]["ver"] if versions else 0)
            custom_prompt = prev.get("custom_prompt")
            custom_refs = prev.get("custom_refs")

            status = "done" if exists else "pending"
            if fn in self.single_running_files or fn in self.batch_running_files or self.batch_current == fn:
                status = "running"

            new_records[fn] = {
                "filename": fn,
                "category": job["category"],
                "tag": _short_tag_for_job(job),
                "tab_group": _tab_group_for_job(job),
                "scope_group": _scope_group_for_job(job),
                "target_width": job["target_width"],
                "target_height": job["target_height"],
                "actual_width": actual_w if exists else 0,
                "actual_height": actual_h if exists else 0,
                "resize_mode": job.get("resize_mode", "exact_resize"),
                "passthrough_if_clean_white": bool(job.get("passthrough_if_clean_white")),
                "default_prompt": job["prompt"],
                "custom_prompt": custom_prompt,
                "prompt": custom_prompt if custom_prompt is not None else job["prompt"],
                "prompt_modified": custom_prompt is not None and custom_prompt != job["prompt"],
                "default_refs": [p.replace("\\", "/") for p in job.get("reference_images", [])],
                "custom_refs": custom_refs,
                "reference_images": custom_refs if custom_refs is not None else [p.replace("\\", "/") for p in job.get("reference_images", [])],
                "status": status,
                "review_status": prev.get("review_status") or _default_review_state(job),
                "output_path": out_path.replace("\\", "/") if exists else "",
                "elapsed_seconds": prev.get("elapsed_seconds") or rep_item.get("elapsed_seconds"),
                "provider_id": prev.get("provider_id") or rep_item.get("provider") or self.provider_id,
                "model_name": prev.get("model_name") or rep_item.get("model") or self.model_name,
                "versions": versions,
                "active_version": active_ver,
                "error": "",
                "mtime": int(os.path.getmtime(out_path) * 1000) if exists else 0,
            }

        self.job_records = new_records

    def compute_scope_counts(self) -> Dict[str, int]:
        if not self.task_config:
            return {"general": 0, "optional": 0, "russian": 0, "selected_total": 0}
        # 计算全打开时的每组准确张数
        full_cfg = json.loads(json.dumps(self.task_config))
        full_cfg["generation_flags"] = {
            "is_pre_listing_mode": False,
            "generate_structure_diagram": True,
            "generate_handheld_comparison": True,
            "generate_russian_suite": True,
        }
        all_jobs = compile_all_jobs(full_cfg)
        general = sum(1 for j in all_jobs if _scope_group_for_job(j) == "general")
        optional = sum(1 for j in all_jobs if _scope_group_for_job(j) == "optional")
        russian = sum(1 for j in all_jobs if _scope_group_for_job(j) == "russian")
        flags = self.task_config.get("generation_flags", {})
        use_opt = bool(flags.get("generate_structure_diagram") or flags.get("generate_handheld_comparison"))
        use_ru = bool(flags.get("generate_russian_suite"))
        selected_total = general + (optional if use_opt else 0) + (russian if use_ru else 0)
        return {
            "general": general,
            "optional": optional,
            "russian": russian,
            "selected_total": selected_total,
        }

    def update_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            if not self.task_config:
                raise ValueError("尚未加载任何素材任务")

            if "generation_flags" in payload:
                self.task_config["generation_flags"].update(payload["generation_flags"])

            if "product_meta" in payload:
                self.task_config["product_meta"].update(payload["product_meta"])

            if "copywriting_en" in payload:
                self.task_config["copywriting_en"].update(payload["copywriting_en"])

            if "copywriting_ru" in payload:
                self.task_config["copywriting_ru"].update(payload["copywriting_ru"])

            if "confirm_field" in payload:
                cid = payload["confirm_field"].get("id")
                confirmed = bool(payload["confirm_field"].get("confirmed", True))
                new_val = payload["confirm_field"].get("value")
                for cf in self.confirm_fields:
                    if cf["id"] == cid:
                        cf["confirmed"] = confirmed
                        if new_val is not None:
                            cf["value"] = new_val
                            # 同步写回规格表
                            for sp in self.task_config["copywriting_en"]["specifications"]:
                                if sp["key"].lower() == cf["spec_key"].lower():
                                    sp["value"] = new_val
                                    break

            if payload.get("confirm_all"):
                for cf in self.confirm_fields:
                    cf["confirmed"] = True

            if "provider_id" in payload:
                self.provider_id = payload["provider_id"]
            if "model_name" in payload:
                self.model_name = payload["model_name"]
            if "quality" in payload:
                self.quality = payload["quality"]

            # 槽位拖拽交换
            if "swap_slots" in payload and self.scan_data:
                sw = payload["swap_slots"]
                color_id = sw["color_id"]
                role_a = sw["role_a"]
                role_b = sw["role_b"]
                self._swap_color_slots(color_id, role_a, role_b)

            # 槽位单图替换
            if "replace_slot" in payload and self.scan_data:
                rp = payload["replace_slot"]
                self._replace_color_slot(rp["color_id"], rp["role"], rp["image_path"])

            # 从排除列表恢复图片
            if "restore_excluded" in payload and self.scan_data:
                path = payload["restore_excluded"].replace("\\", "/")
                self._restore_excluded_image(path)

            self._recompile_jobs(preserve_custom=True)
            self._save_meta_store()
            return self.get_full_state()

    def _sync_color_groups_to_task(self) -> None:
        if not self.scan_data or not self.task_config:
            return
        variants = []
        for cg in self.scan_data["color_groups"]:
            views = {}
            for s in cg["slots"]:
                if s["image"] and s["role"] != "package_png":
                    views[s["role"]] = s["image"]["path"]
                elif s["role"] == "package_png" and s["image"]:
                    self.task_config["reference_assets"]["clean_package_photo_ref"] = s["image"]["path"]
            if cg.get("detail_1_image"):
                views["detail_1_png"] = cg["detail_1_image"]["path"]
            variants.append({
                "color_id": cg["color_id"],
                "color_name_cn": cg["color_name_cn"],
                "color_name_en": cg["color_name_en"],
                "swatch": cg["swatch"],
                "views": views,
            })
        self.task_config["color_variants"] = variants

    def _swap_color_slots(self, color_id: str, role_a: str, role_b: str) -> None:
        if role_a == role_b:
            return
        for cg in self.scan_data["color_groups"]:
            if cg["color_id"] == color_id:
                slot_a = next((s for s in cg["slots"] if s["role"] == role_a), None)
                slot_b = next((s for s in cg["slots"] if s["role"] == role_b), None)
                if slot_a and slot_b:
                    slot_a["image"], slot_b["image"] = slot_b["image"], slot_a["image"]
                    slot_a["reused_from"], slot_b["reused_from"] = slot_b["reused_from"], slot_a["reused_from"]
                break
        self._sync_color_groups_to_task()

    def _replace_color_slot(self, color_id: str, role: str, image_path: str) -> None:
        image_path = os.path.abspath(image_path)
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"图片不存在: {image_path}")
        with Image.open(image_path) as im:
            w, h = im.size
        size_kb = round(os.path.getsize(image_path) / 1024, 1)
        new_img = {
            "name": os.path.basename(image_path),
            "path": image_path.replace("\\", "/"),
            "rel_dir": os.path.basename(os.path.dirname(image_path)),
            "width": w,
            "height": h,
            "size_kb": size_kb,
        }
        for cg in self.scan_data["color_groups"]:
            if cg["color_id"] == color_id:
                target = next((s for s in cg["slots"] if s["role"] == role), None)
                if target:
                    target["image"] = new_img
                    target["reused_from"] = None
                cg["count"] = sum(1 for s in cg["slots"] if s["image"] is not None)
                break
        if all(x["path"] != new_img["path"] for x in self.scan_data["all_usable_pool"]):
            self.scan_data["all_usable_pool"].append(new_img)
        self._sync_color_groups_to_task()

    def _restore_excluded_image(self, img_path: str) -> None:
        excluded = self.scan_data.get("excluded_files", [])
        found = next((x for x in excluded if x["path"] == img_path), None)
        if not found:
            return
        self.scan_data["excluded_files"] = [x for x in excluded if x["path"] != img_path]
        self.scan_data["excluded_preview"] = self.scan_data["excluded_files"][:4]
        self.scan_data["stats"]["excluded_images"] = len(self.scan_data["excluded_files"])
        self.scan_data["all_usable_pool"].append(found)

    def _execute_single_job_internal(
        self,
        filename: str,
        prompt_override: Optional[str] = None,
        refs_override: Optional[List[str]] = None,
        provider_id: Optional[str] = None,
        model_name: Optional[str] = None,
        quality: Optional[str] = None,
        force_api: bool = False,
    ) -> Dict[str, Any]:
        with self.lock:
            rec = self.job_records.get(filename)
            if not rec:
                raise ValueError(f"未找到任务图片: {filename}")
            prompt = prompt_override if prompt_override is not None else rec["prompt"]
            refs = refs_override if refs_override is not None else rec["reference_images"]
            pid = provider_id or self.provider_id
            mdl = model_name or self.model_name
            qual = quality or self.quality
            target_w = rec["target_width"]
            target_h = rec["target_height"]
            resize_mode = rec["resize_mode"]
            passthrough = rec["passthrough_if_clean_white"]
            out_path = os.path.join(self.output_dir, filename)
            rec["status"] = "running"
            rec["error"] = ""
            if prompt_override is not None:
                rec["custom_prompt"] = prompt_override
                rec["prompt"] = prompt_override
                rec["prompt_modified"] = (prompt_override != rec["default_prompt"])
            if refs_override is not None:
                rec["custom_refs"] = [r.replace("\\", "/") for r in refs_override]
                rec["reference_images"] = rec["custom_refs"]

        token = _get_provider_token(pid)
        provider = get_provider(provider_id=pid, api_token=token)
        t0 = time.time()

        try:
            # 归档已有版本，保证历史版本可对比切换
            with self.lock:
                rec = self.job_records[filename]
                versions = rec["versions"]
                stem, ext = os.path.splitext(filename)
                v_dir = self._versions_dir()
                if os.path.isfile(out_path) and not versions:
                    v1_path = os.path.join(v_dir, f"{stem}_v1{ext}")
                    shutil.copyfile(out_path, v1_path)
                    versions.append({
                        "ver": 1,
                        "path": v1_path.replace("\\", "/"),
                        "ts": int(os.path.getmtime(out_path)),
                        "elapsed": rec.get("elapsed_seconds") or 20.0,
                        "provider_id": rec.get("provider_id") or pid,
                        "model_name": rec.get("model_name") or mdl,
                        "prompt": rec["default_prompt"],
                    })
                elif os.path.isfile(out_path) and len(versions) == 1 and versions[0]["path"].replace("\\", "/") == out_path.replace("\\", "/"):
                    # 把原先直接指向主文件的 v1 备份进 .versions 目录，防止被新图覆盖
                    v1_path = os.path.join(v_dir, f"{stem}_v1{ext}")
                    shutil.copyfile(out_path, v1_path)
                    versions[0]["path"] = v1_path.replace("\\", "/")

            # 白底直通模式（仅在批量首次且未手动单图重绘时使用）
            if passthrough and not force_api and len(refs) == 1 and os.path.isfile(refs[0]):
                with open(refs[0], "rb") as rf:
                    raw_b = rf.read()
                img_bytes, _, _ = provider.normalize_image_size(
                    raw_bytes=raw_b,
                    target_width=target_w,
                    target_height=target_h,
                    resize_mode=resize_mode or "pad_white",
                    output_format="jpeg",
                )
                elapsed = round(time.time() - t0, 2)
                actual_w, actual_h = target_w, target_h
                used_model = "passthrough"
            else:
                req = ImageGenRequest(
                    prompt=prompt,
                    target_width=target_w,
                    target_height=target_h,
                    reference_images=refs,
                    model=mdl,
                    quality=qual,
                    resize_mode=resize_mode,
                    output_format="jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "png",
                )
                resp = provider.generate(req)
                img_bytes = resp.image_bytes
                elapsed = resp.elapsed_seconds
                actual_w, actual_h = resp.final_width, resp.final_height
                used_model = resp.model_used

            with open(out_path, "wb") as out_f:
                out_f.write(img_bytes)

            with self.lock:
                rec = self.job_records[filename]
                next_ver = (max((v["ver"] for v in rec["versions"]), default=0) + 1)
                stem, ext = os.path.splitext(filename)
                ver_path = os.path.join(self._versions_dir(), f"{stem}_v{next_ver}{ext}")
                shutil.copyfile(out_path, ver_path)

                rec["versions"].append({
                    "ver": next_ver,
                    "path": ver_path.replace("\\", "/"),
                    "ts": int(time.time()),
                    "elapsed": elapsed,
                    "provider_id": pid,
                    "model_name": used_model,
                    "prompt": prompt,
                })
                rec["active_version"] = next_ver
                rec["status"] = "done"
                rec["output_path"] = out_path.replace("\\", "/")
                rec["actual_width"] = actual_w
                rec["actual_height"] = actual_h
                rec["elapsed_seconds"] = elapsed
                rec["provider_id"] = pid
                rec["model_name"] = used_model
                rec["mtime"] = int(time.time() * 1000)
                rec["error"] = ""
                self._save_meta_store()
                return dict(rec)

        except Exception as e:
            with self.lock:
                rec = self.job_records[filename]
                rec["status"] = "done" if os.path.isfile(out_path) else "failed"
                rec["error"] = str(e)
            raise

    def regenerate_single(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        fn = payload["filename"]
        with self.lock:
            if fn in self.single_running_files:
                raise RuntimeError(f"{fn} 正在生成中，请稍候")
            self.single_running_files.add(fn)
        try:
            return self._execute_single_job_internal(
                filename=fn,
                prompt_override=payload.get("prompt"),
                refs_override=payload.get("reference_images"),
                provider_id=payload.get("provider_id"),
                model_name=payload.get("model_name"),
                quality=payload.get("quality"),
                force_api=True,
            )
        finally:
            with self.lock:
                self.single_running_files.discard(fn)

    def start_batch(self, mode: str = "missing", filenames: Optional[List[str]] = None) -> Dict[str, Any]:
        with self.lock:
            if self.batch_running:
                raise RuntimeError("当前已有批量生图任务正在执行中")

            if mode == "selected" and filenames:
                queue = [f for f in filenames if f in self.job_records]
            elif mode == "sample":
                # 挑 3 张未生成或代表图（主图、卖点、俄语各 1）
                queue = []
                for f, r in self.job_records.items():
                    if r["status"] != "done":
                        queue.append(f)
                        if len(queue) >= 3:
                            break
                if not queue:
                    queue = list(self.job_records.keys())[:3]
            elif mode == "all":
                queue = list(self.job_records.keys())
            else:
                # missing：仅生成尚未完成的图
                queue = [f for f, r in self.job_records.items() if r["status"] != "done"]

            if not queue:
                return {"started": False, "message": "所选范围内的图片均已生成完毕", "queue_size": 0}

            self.batch_running = True
            self.batch_stop_requested = False
            self.batch_total = len(queue)
            self.batch_completed = 0
            self.batch_failed = 0
            self.batch_running_files = set()
            self.batch_current = None
            self.batch_started_at = time.time()
            self.last_error = ""

            # 预先将首批并发任务标为 running，确保前端启动瞬间即可看到多卡并行转圈
            workers = min(self.batch_concurrency, len(queue))
            initial_batch = queue[:workers]
            for fn in initial_batch:
                self.batch_running_files.add(fn)
                if fn in self.job_records:
                    self.job_records[fn]["status"] = "running"
                    self.job_records[fn]["error"] = ""
            self.batch_current = "、".join(initial_batch)

            t = threading.Thread(target=self._batch_worker, args=(queue, mode == "selected", workers), daemon=True)
            t.start()
            return {"started": True, "queue_size": len(queue), "concurrency": workers}

    def _refresh_batch_current_locked(self) -> None:
        active = sorted(self.batch_running_files)
        if not active:
            self.batch_current = None
        elif len(active) <= 3:
            self.batch_current = "、".join(active)
        else:
            self.batch_current = f"{'、'.join(active[:3])} 等 {len(active)} 张"

    def _run_one_batch_item(self, fn: str, force_api: bool) -> None:
        with self.lock:
            self.batch_running_files.add(fn)
            if fn in self.job_records:
                self.job_records[fn]["status"] = "running"
                self.job_records[fn]["error"] = ""
            self._refresh_batch_current_locked()
        try:
            self._execute_single_job_internal(filename=fn, force_api=force_api)
            with self.lock:
                self.batch_completed += 1
        except Exception as e:
            with self.lock:
                self.batch_failed += 1
                self.last_error = f"{fn}: {e}"
        finally:
            with self.lock:
                self.batch_running_files.discard(fn)
                self._refresh_batch_current_locked()

    def _batch_worker(self, queue: List[str], force_api: bool, workers: int) -> None:
        """滑动窗口多线程并发调度：同时保持最多 workers 张在生图，支持随时优雅暂停。"""
        idx = 0
        total = len(queue)
        in_flight = set()
        try:
            with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
                while idx < total or in_flight:
                    with self.lock:
                        stop_now = self.batch_stop_requested

                    # 未暂停时补满并发窗口
                    while not stop_now and idx < total and len(in_flight) < workers:
                        fn = queue[idx]
                        idx += 1
                        with self.lock:
                            self.batch_running_files.add(fn)
                            if fn in self.job_records:
                                self.job_records[fn]["status"] = "running"
                                self.job_records[fn]["error"] = ""
                            self._refresh_batch_current_locked()
                        fut = pool.submit(self._run_one_batch_item, fn, force_api)
                        in_flight.add(fut)
                        with self.lock:
                            stop_now = self.batch_stop_requested

                    if not in_flight:
                        break

                    done_futs, in_flight = wait(in_flight, return_when=FIRST_COMPLETED)
                    for df in done_futs:
                        try:
                            df.result()
                        except Exception:
                            pass
        finally:
            with self.lock:
                # 清理因暂停尚未执行而被预标为 running 的残留状态
                for fn in list(self.batch_running_files):
                    rec = self.job_records.get(fn)
                    if rec and rec.get("status") == "running":
                        rec["status"] = "done" if rec.get("output_path") and os.path.isfile(rec["output_path"]) else "pending"
                self.batch_running_files.clear()
                self.batch_elapsed_total = round(time.time() - self.batch_started_at, 1)
                self.batch_running = False
                self.batch_current = None
                self.export_tongtool_csv()

    def stop_batch(self) -> Dict[str, Any]:
        with self.lock:
            self.batch_stop_requested = True
            return {"stopping": True}

    def switch_version(self, filename: str, ver: int) -> Dict[str, Any]:
        with self.lock:
            rec = self.job_records.get(filename)
            if not rec:
                raise ValueError("未找到图片")
            target = next((v for v in rec["versions"] if v["ver"] == ver), None)
            if not target or not os.path.isfile(target["path"]):
                raise FileNotFoundError("对应版本文件不存在")
            out_path = os.path.join(self.output_dir, filename)
            shutil.copyfile(target["path"], out_path)
            rec["active_version"] = ver
            rec["prompt"] = target.get("prompt") or rec["prompt"]
            rec["mtime"] = int(time.time() * 1000)
            self._save_meta_store()
            return dict(rec)

    def set_review_status(self, filename: str, review_status: str) -> Dict[str, Any]:
        with self.lock:
            rec = self.job_records.get(filename)
            if not rec:
                raise ValueError("未找到图片")
            rec["review_status"] = review_status
            self._save_meta_store()
            return dict(rec)

    def set_review_batch(self, filenames: List[str], review_status: str) -> int:
        with self.lock:
            cnt = 0
            for fn in filenames:
                rec = self.job_records.get(fn)
                if rec and rec.get("status") == "done":
                    rec["review_status"] = review_status
                    cnt += 1
            if cnt:
                self._save_meta_store()
            return cnt

    def save_uploaded_image(self, filename: str, data_b64: str) -> str:
        with self.lock:
            up_dir = os.path.join(self.output_dir or os.path.join(BASE_DIR, "outputs", "UPLOAD"), ".uploaded")
            os.makedirs(up_dir, exist_ok=True)
            safe_name = re.sub(r"[^A-Za-z0-9._\-\u4e00-\u9fff]+", "_", os.path.basename(filename or "upload.png"))
            if not os.path.splitext(safe_name)[1]:
                safe_name += ".png"
            out_path = os.path.join(up_dir, f"{int(time.time())}_{safe_name}")
            if "," in data_b64:
                data_b64 = data_b64.split(",", 1)[1]
            raw = base64.b64decode(data_b64)
            with open(out_path, "wb") as f:
                f.write(raw)
            return out_path.replace("\\", "/")

    def save_prompt_template(self, filename: str, prompt: str) -> Dict[str, Any]:
        with self.lock:
            rec = self.job_records.get(filename)
            if not rec:
                raise ValueError("未找到图片")
            cat = rec["category"]
            templates = _read_json(CUSTOM_TEMPLATES_PATH, {})
            templates[cat] = {
                "category": cat,
                "tag": rec["tag"],
                "sample_filename": filename,
                "prompt": prompt,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            _write_json(CUSTOM_TEMPLATES_PATH, templates)
            return {"saved": True, "category": cat}

    def export_tongtool_csv(self) -> str:
        csv_path = os.path.join(self.output_dir, "图片组对应关系.csv")
        rows = []
        jobs_list = list(self.job_records.values())
        for idx, j in enumerate(jobs_list, start=1):
            rows.append(["A", 1, "GROUP_ALL", idx, "A", j["filename"], j["filename"], j["category"]])
        d_jobs = [j for j in jobs_list if j["category"].startswith(("03_", "05_", "06_", "08_", "09_"))]
        for idx, j in enumerate(d_jobs, start=1):
            rows.append(["D", 2, "GROUP_DETAIL", idx, "D", j["filename"], j["filename"], j["category"]])
        v_jobs = [j for j in jobs_list if j["category"].startswith("04_")]
        for idx, j in enumerate(v_jobs, start=1):
            rows.append(["V", 3, "GROUP_SKU_VARIANT", idx, "V", j["filename"], j["filename"], j["category"]])
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as cf:
            writer = csv.writer(cf)
            writer.writerow(["group_type", "group_sort", "group_id", "sort", "image_type", "name", "filename", "category"])
            writer.writerows(rows)
        return csv_path

    def build_tongtool_zip_bytes(self) -> tuple[str, bytes]:
        with self.lock:
            csv_path = self.export_tongtool_csv()
            spu = self.task_config["product_meta"]["spu_code"] if self.task_config else "EXPORT"
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                if os.path.isfile(csv_path):
                    zf.write(csv_path, arcname=f"{spu}/图片组对应关系.csv")
                manifest = []
                for fn, rec in self.job_records.items():
                    fp = os.path.join(self.output_dir, fn)
                    if os.path.isfile(fp):
                        zf.write(fp, arcname=f"{spu}/{fn}")
                        manifest.append({
                            "filename": fn,
                            "category": rec["category"],
                            "size": f"{rec['actual_width']}x{rec['actual_height']}",
                            "review_status": rec["review_status"],
                        })
                zf.writestr(
                    f"{spu}/图片清单.json",
                    json.dumps({"spu": spu, "count": len(manifest), "files": manifest}, ensure_ascii=False, indent=2),
                )
            return f"{spu}_通途ERP图库包.zip", buf.getvalue()

    def get_full_state(self) -> Dict[str, Any]:
        with self.lock:
            jobs_list = list(self.job_records.values())
            done_cnt = sum(1 for j in jobs_list if j["status"] == "done")
            approved_cnt = sum(1 for j in jobs_list if j["status"] == "done" and j["review_status"] == "approved")
            review_cnt = sum(1 for j in jobs_list if j["status"] == "done" and j["review_status"] == "review")
            pending_cnt = sum(1 for j in jobs_list if j["status"] in ("pending", "failed"))
            compliant_cnt = sum(
                1 for j in jobs_list
                if j["status"] == "done" and j["actual_width"] == j["target_width"] and j["actual_height"] == j["target_height"]
            )
            compliance_pct = round((compliant_cnt / done_cnt) * 100) if done_cnt else 100

            return {
                "scan": self.scan_data,
                "task_config": self.task_config,
                "confirm_fields": self.confirm_fields,
                "scope_counts": self.compute_scope_counts(),
                "providers": self.list_providers(),
                "selected_provider": self.provider_id,
                "selected_model": self.model_name,
                "selected_quality": self.quality,
                "output_dir": self.output_dir,
                "jobs": jobs_list,
                "summary": {
                    "total": len(jobs_list),
                    "done": done_cnt,
                    "approved": approved_cnt,
                    "review": review_cnt,
                    "pending": pending_cnt,
                    "compliance_pct": compliance_pct,
                },
                "batch": {
                    "running": self.batch_running,
                    "stop_requested": self.batch_stop_requested,
                    "total": self.batch_total,
                    "completed": self.batch_completed,
                    "failed": self.batch_failed,
                    "current": self.batch_current,
                    "running_files": sorted(self.batch_running_files),
                    "concurrency": self.batch_concurrency,
                    "elapsed": round(time.time() - self.batch_started_at, 1) if self.batch_running else self.batch_elapsed_total,
                    "last_error": self.last_error,
                },
            }


STUDIO = StudioManager()

# 轻量缩略图内存缓存：{(path, mtime, max_w): (bytes, mime)}
_THUMB_CACHE: Dict[tuple, tuple] = {}
_THUMB_LOCK = threading.Lock()


def _get_image_bytes_cached(img_path: str, max_w: int = 0) -> tuple:
    mime, _ = mimetypes.guess_type(img_path)
    mime = mime or "image/jpeg"
    if max_w <= 0:
        with open(img_path, "rb") as f:
            return f.read(), mime
    mtime = int(os.path.getmtime(img_path))
    key = (img_path, mtime, max_w)
    with _THUMB_LOCK:
        hit = _THUMB_CACHE.get(key)
        if hit:
            return hit
    try:
        with Image.open(img_path) as im:
            im.thumbnail((max_w, max_w), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            if im.mode in ("RGBA", "LA", "P"):
                im.save(buf, format="PNG", optimize=True)
                out_bytes, out_mime = buf.getvalue(), "image/png"
            else:
                im.convert("RGB").save(buf, format="JPEG", quality=86)
                out_bytes, out_mime = buf.getvalue(), "image/jpeg"
    except Exception:
        with open(img_path, "rb") as f:
            return f.read(), mime
    with _THUMB_LOCK:
        if len(_THUMB_CACHE) > 400:
            _THUMB_CACHE.clear()
        _THUMB_CACHE[key] = (out_bytes, out_mime)
    return out_bytes, out_mime


# ---------------- Windows 原生弹窗助手（独立子进程，规避多线程 tkinter 冲突） ----------------

def _pick_folder_dialog(initial_dir: str = "") -> str:
    init = initial_dir if (initial_dir and os.path.isdir(initial_dir)) else WORKSPACE_DIR
    script = (
        "import sys, tkinter as tk; from tkinter import filedialog; "
        "r = tk.Tk(); r.withdraw(); r.attributes('-topmost', True); r.lift(); r.focus_force(); "
        "p = filedialog.askdirectory(title='选择商品原始素材文件夹', initialdir=sys.argv[1]); "
        "r.destroy(); print(p or '')"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script, init],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=180,
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def _pick_image_dialog(initial_dir: str = "") -> str:
    init = initial_dir if (initial_dir and os.path.isdir(initial_dir)) else WORKSPACE_DIR
    script = (
        "import sys, tkinter as tk; from tkinter import filedialog; "
        "r = tk.Tk(); r.withdraw(); r.attributes('-topmost', True); r.lift(); r.focus_force(); "
        "p = filedialog.askopenfilename(title='选择参考图片', initialdir=sys.argv[1], "
        "filetypes=[('图片文件', '*.jpg;*.jpeg;*.png;*.webp;*.bmp'), ('所有文件', '*.*')]); "
        "r.destroy(); print(p or '')"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script, init],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=180,
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def _list_windows_drives() -> List[Dict[str, str]]:
    drives = []
    for ch in string.ascii_uppercase:
        d = f"{ch}:\\"
        if os.path.exists(d):
            drives.append({"name": f"本地磁盘 ({ch}:)", "path": d})
    return drives


def _list_local_fs(target_path: str = "", include_images: bool = False) -> Dict[str, Any]:
    """内置本地目录与图片浏览器，不依赖系统弹窗即可浏览任意盘符、文件夹与图片。"""
    img_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    target_path = (target_path or "").strip().strip('"').strip("'")
    drives = _list_windows_drives()

    # 快捷入口（工作区、桌面、下载、文档）
    user_home = os.path.expanduser("~")
    shortcuts = [
        {"label": "工作区", "path": WORKSPACE_DIR},
        {"label": "桌面", "path": os.path.join(user_home, "Desktop")},
        {"label": "下载", "path": os.path.join(user_home, "Downloads")},
    ]
    shortcuts = [s for s in shortcuts if os.path.isdir(s["path"])]

    if not target_path or not os.path.isdir(target_path):
        target_path = WORKSPACE_DIR if os.path.isdir(WORKSPACE_DIR) else (drives[0]["path"] if drives else user_home)

    target_path = os.path.abspath(target_path)
    parent = os.path.dirname(target_path)
    if parent == target_path:
        parent = ""

    folders: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []
    try:
        entries = sorted(os.scandir(target_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        for e in entries:
            if e.name.startswith(".") or e.name in ("$RECYCLE.BIN", "System Volume Information", "__pycache__"):
                continue
            try:
                if e.is_dir():
                    folders.append({"name": e.name, "path": e.path})
                elif include_images and os.path.splitext(e.name)[1].lower() in img_exts:
                    size_kb = round(e.stat().st_size / 1024, 1)
                    images.append({
                        "name": e.name,
                        "path": e.path.replace("\\", "/"),
                        "size_kb": size_kb,
                    })
            except PermissionError:
                continue
    except PermissionError:
        pass

    return {
        "current_path": target_path,
        "parent_path": parent,
        "drives": drives,
        "shortcuts": shortcuts,
        "folders": folders[:200],
        "images": images[:200],
    }


# ---------------- HTTP 路由处理器 ----------------

class AutoShotHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        # 仅打印 API 写操作或错误，保持控制台干净
        msg = fmt % args
        if "/api/local-image" in msg or "/api/generate/status" in msg:
            return
        print(f"[Web] {self.address_string()} - {msg}")

    def _send_json(self, data: Any, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _send_bytes(self, content: bytes, content_type: str, filename: Optional[str] = None, cache: str = "no-cache") -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", cache)
        if filename:
            encoded = urllib.parse.quote(filename)
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{encoded}")
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        try:
            if path in ("/", "/index.html"):
                self._serve_static("index.html")
                return
            if path.startswith("/static/"):
                self._serve_static(path[len("/static/"):])
                return

            if path == "/api/bootstrap":
                self._send_json(STUDIO.get_full_state())
                return

            if path == "/api/generate/status":
                self._send_json(STUDIO.get_full_state())
                return

            if path == "/api/local-image":
                img_path = qs.get("path", [""])[0]
                if not img_path or not os.path.isfile(img_path):
                    self.send_error(404, "Image not found")
                    return
                max_w = int(qs.get("w", ["0"])[0] or "0")
                data, mime = _get_image_bytes_cached(img_path, max_w=max_w)
                self._send_bytes(data, mime, cache="private, max-age=300")
                return

            if path == "/api/download-image":
                img_path = qs.get("path", [""])[0]
                if not img_path or not os.path.isfile(img_path):
                    self.send_error(404, "Image not found")
                    return
                mime, _ = mimetypes.guess_type(img_path)
                with open(img_path, "rb") as f:
                    data = f.read()
                self._send_bytes(data, mime or "application/octet-stream", filename=os.path.basename(img_path))
                return

            if path == "/api/fs/list":
                req_path = qs.get("path", [""])[0]
                inc_img = qs.get("images", ["0"])[0] in ("1", "true", "yes")
                self._send_json(_list_local_fs(req_path, include_images=inc_img))
                return

            if path == "/api/export/tongtool":
                zip_name, zip_bytes = STUDIO.build_tongtool_zip_bytes()
                self._send_bytes(zip_bytes, "application/zip", filename=zip_name)
                return

            self.send_error(404, "Not found")
        except Exception as e:
            traceback.print_exc()
            self._send_json({"error": str(e)}, status=500)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json_body()

            if path == "/api/pick-folder":
                init_dir = body.get("initial_dir") or (STUDIO.scan_data["folder_path"] if STUDIO.scan_data else WORKSPACE_DIR)
                selected = _pick_folder_dialog(init_dir)
                self._send_json({"folder_path": selected})
                return

            if path == "/api/pick-image":
                init_dir = body.get("initial_dir") or (STUDIO.scan_data["folder_path"] if STUDIO.scan_data else WORKSPACE_DIR)
                selected = _pick_image_dialog(init_dir)
                self._send_json({"image_path": selected.replace("\\", "/") if selected else ""})
                return

            if path == "/api/scan":
                folder = body.get("folder_path", "").strip()
                if not folder:
                    self._send_json({"error": "请提供有效的本地文件夹路径"}, status=400)
                    return
                state = STUDIO.load_folder(folder)
                self._send_json(state)
                return

            if path == "/api/task/update":
                state = STUDIO.update_task(body)
                self._send_json(state)
                return

            if path == "/api/provider/config":
                pid = body.get("provider_id", "qiuqiutoken")
                api_key = body.get("api_key", "").strip()
                secrets = _read_json(SECRETS_PATH, {})
                secrets.setdefault(pid, {})
                if api_key:
                    secrets[pid]["api_key"] = api_key
                _write_json(SECRETS_PATH, secrets)
                if body.get("model_name"):
                    STUDIO.model_name = body["model_name"]
                if body.get("quality"):
                    STUDIO.quality = body["quality"]
                self._send_json({"ok": True, "providers": STUDIO.list_providers()})
                return

            if path == "/api/generate/start":
                mode = body.get("mode", "missing")
                filenames = body.get("filenames")
                res = STUDIO.start_batch(mode=mode, filenames=filenames)
                self._send_json({**res, "state": STUDIO.get_full_state()})
                return

            if path == "/api/generate/stop":
                res = STUDIO.stop_batch()
                self._send_json(res)
                return

            if path == "/api/generate/single":
                rec = STUDIO.regenerate_single(body)
                self._send_json({"record": rec, "state": STUDIO.get_full_state()})
                return

            if path == "/api/job/version":
                rec = STUDIO.switch_version(body["filename"], int(body["ver"]))
                self._send_json({"record": rec, "state": STUDIO.get_full_state()})
                return

            if path == "/api/job/review":
                rec = STUDIO.set_review_status(body["filename"], body["review_status"])
                self._send_json({"record": rec, "state": STUDIO.get_full_state()})
                return

            if path == "/api/job/review-batch":
                cnt = STUDIO.set_review_batch(body.get("filenames", []), body["review_status"])
                self._send_json({"updated": cnt, "state": STUDIO.get_full_state()})
                return

            if path == "/api/upload-image":
                saved = STUDIO.save_uploaded_image(body.get("filename", "image.png"), body.get("data_b64", ""))
                self._send_json({"image_path": saved})
                return

            if path == "/api/template/save":
                res = STUDIO.save_prompt_template(body["filename"], body["prompt"])
                self._send_json(res)
                return

            if path == "/api/open-folder":
                target = body.get("path") or STUDIO.output_dir
                if target and os.path.exists(target):
                    subprocess.Popen(["explorer", os.path.normpath(target)])
                    self._send_json({"ok": True})
                else:
                    self._send_json({"error": "目录不存在"}, status=404)
                return

            self.send_error(404, "Not found")
        except Exception as e:
            traceback.print_exc()
            self._send_json({"error": str(e)}, status=500)

    def _serve_static(self, rel_path: str) -> None:
        safe_path = os.path.normpath(os.path.join(STATIC_DIR, rel_path))
        if not safe_path.startswith(STATIC_DIR) or not os.path.isfile(safe_path):
            self.send_error(404, "Static file not found")
            return
        mime, _ = mimetypes.guess_type(safe_path)
        if safe_path.endswith(".js"):
            mime = "application/javascript; charset=utf-8"
        elif safe_path.endswith(".css"):
            mime = "text/css; charset=utf-8"
        elif safe_path.endswith(".html"):
            mime = "text/html; charset=utf-8"
        with open(safe_path, "rb") as f:
            data = f.read()
        self._send_bytes(data, mime or "application/octet-stream", cache="no-store")


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), AutoShotHandler)
    print("============================================================")
    print(f"  AutoShot 生图台已启动 -> http://{host}:{port}")
    print(f"  工作目录: {BASE_DIR}")
    print("  按 Ctrl+C 停止服务")
    print("============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")
        server.server_close()


if __name__ == "__main__":
    p = int(os.environ.get("AUTOSHOT_PORT", "8765"))
    run_server(port=p)
