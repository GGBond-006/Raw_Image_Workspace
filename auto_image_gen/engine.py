import csv
import json
import os
import shutil
import time
from typing import Dict, Any, List, Optional

from providers import get_provider, ImageGenRequest
from prompts import compile_all_jobs


class BatchImageEngine:
    """
    批量自动化生图执行引擎
    负责：
    1. 读取单品任务 JSON 配置并编译出 12 类标准套图任务队列（Jobs）
    2. 按需过滤要执行的图片（支持单张测试、按类别测试、抽样测试或全量生成）
    3. 调用所选平台与模型的生图 API（如球球Token gpt-image-2）
    4. 保存成品图、生图日志（含每张图的实际 Prompt 与耗时），并生成通途 ERP 映射表
    """

    def __init__(
        self,
        task_json_path: str,
        output_dir: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_name: Optional[str] = None,
        api_token: Optional[str] = None,
        quality: Optional[str] = None,
    ):
        with open(task_json_path, "r", encoding="utf-8") as f:
            self.task = json.load(f)

        self.spu_code = self.task["product_meta"]["spu_code"]
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(task_json_path)))
        self.output_dir = output_dir or os.path.join(base_dir, "outputs", self.spu_code)
        os.makedirs(self.output_dir, exist_ok=True)

        self.provider_id = provider_id
        self.model_name = model_name
        self.api_token = api_token
        self.quality = quality
        self.jobs = compile_all_jobs(self.task)

    def filter_jobs(self, filter_expr: Optional[str] = None) -> List[Dict[str, Any]]:
        if not filter_expr or filter_expr.lower() == "all":
            return self.jobs

        # 特殊快捷预设：`sample` —— 从每个核心类别各抽 1 张代表图进行快速省钱测试！
        if filter_expr.lower() == "sample":
            seen_cats = set()
            sampled = []
            for j in self.jobs:
                cat = j["category"]
                # 对属性图优先抽带电池组合的那张（如 RC4661A_RC4226A.jpg）以便测试多图合成与下划线命名
                if cat == "04_属性图_SKU组合" and "_" not in j["filename"]:
                    continue
                if cat not in seen_cats:
                    seen_cats.add(cat)
                    sampled.append(j)
            return sampled

        keywords = [k.strip().lower() for k in filter_expr.split(",") if k.strip()]
        matched = []
        for j in self.jobs:
            fname = j["filename"].lower()
            cat = j["category"].lower()
            if any(k in fname or k in cat for k in keywords):
                matched.append(j)
        return matched

    def validate_reference_files(self, jobs: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        target_jobs = jobs if jobs is not None else self.jobs
        missing = []
        for j in target_jobs:
            for ref in j.get("reference_images", []):
                if not os.path.isfile(ref):
                    missing.append(f"{j['filename']} -> 缺少参考图: {ref}")
        return missing

    def run(self, filter_expr: Optional[str] = None, force_api: bool = False) -> Dict[str, Any]:
        selected_jobs = self.filter_jobs(filter_expr)
        if not selected_jobs:
            raise ValueError(f"没有匹配过滤条件 '{filter_expr}' 的生图任务！")

        missing = self.validate_reference_files(selected_jobs)
        if missing:
            raise FileNotFoundError("存在缺失的参考图文件:\n" + "\n".join(missing))

        provider = get_provider(provider_id=self.provider_id, api_token=self.api_token)
        results = []
        failures = []

        print(f"============================================================")
        print(f"开始执行生图任务: SPU={self.spu_code} | 平台={provider.provider_id} | 待生成张数={len(selected_jobs)}/{len(self.jobs)}")
        print(f"输出目录: {self.output_dir}")
        print(f"============================================================")

        for idx, job in enumerate(selected_jobs, start=1):
            fname = job["filename"]
            cat = job["category"]
            out_path = os.path.join(self.output_dir, fname)
            refs = job.get("reference_images", [])

            print(f"\n[{idx}/{len(selected_jobs)}] 正在生成: {fname} ({cat}) | 目标尺寸: {job['target_width']}x{job['target_height']}")
            print(f"  参考图 ({len(refs)}张): {[os.path.basename(r) for r in refs]}")

            # 若开启了原厂纯白底副图直通模式且未强制调 API
            if job.get("passthrough_if_clean_white") and not force_api and len(refs) == 1:
                with open(refs[0], "rb") as rf:
                    raw_b = rf.read()
                norm_bytes, rw, rh = provider.normalize_image_size(
                    raw_bytes=raw_b,
                    target_width=job["target_width"],
                    target_height=job["target_height"],
                    resize_mode=job.get("resize_mode", "pad_white"),
                    output_format="jpeg",
                )
                with open(out_path, "wb") as out_f:
                    out_f.write(norm_bytes)
                print(f"  [直通完成] 原厂合规白底图已标准化保存至 -> {out_path}")
                results.append({
                    "filename": fname,
                    "category": cat,
                    "status": "passthrough",
                    "output_path": out_path,
                    "final_size": f"{job['target_width']}x{job['target_height']}",
                    "prompt": job["prompt"],
                })
                continue

            req = ImageGenRequest(
                prompt=job["prompt"],
                target_width=job["target_width"],
                target_height=job["target_height"],
                reference_images=refs,
                model=self.model_name,
                quality=self.quality,
                resize_mode=job.get("resize_mode", "smart_crop"),
                output_format="jpeg" if fname.lower().endswith((".jpg", ".jpeg")) else "png",
            )

            try:
                resp = provider.generate(req)
                with open(out_path, "wb") as out_f:
                    out_f.write(resp.image_bytes)
                print(
                    f"  [成功] 模型={resp.model_used} | 原生尺寸={resp.raw_width}x{resp.raw_height} -> "
                    f"标准尺寸={resp.final_width}x{resp.final_height} | 耗时={resp.elapsed_seconds}s"
                )
                results.append({
                    "filename": fname,
                    "category": cat,
                    "status": "success",
                    "provider": resp.provider_id,
                    "model": resp.model_used,
                    "endpoint": resp.endpoint_used,
                    "raw_size": f"{resp.raw_width}x{resp.raw_height}",
                    "final_size": f"{resp.final_width}x{resp.final_height}",
                    "elapsed_seconds": resp.elapsed_seconds,
                    "output_path": out_path,
                    "reference_images": refs,
                    "prompt": job["prompt"],
                })
            except Exception as e:
                print(f"  [失败] {fname}: {e}")
                failures.append({
                    "filename": fname,
                    "category": cat,
                    "error": str(e),
                    "prompt": job["prompt"],
                })

        # 保存本次执行报告与 Prompt 快照，方便对照输出图片微调提示词
        report_path = os.path.join(self.output_dir, "generation_report.json")
        report_data = {
            "spu_code": self.spu_code,
            "provider": provider.provider_id,
            "total_selected": len(selected_jobs),
            "succeeded": len(results),
            "failed": len(failures),
            "results": results,
            "failures": failures,
        }
        with open(report_path, "w", encoding="utf-8") as rf:
            json.dump(report_data, rf, ensure_ascii=False, indent=2)

        self.export_tongtool_mapping_csv()
        print(f"\n============================================================")
        print(f"任务执行完毕: 成功 {len(results)} 张, 失败 {len(failures)} 张")
        print(f"生图日志与提示词报告: {report_path}")
        print(f"============================================================")
        return report_data

    def export_tongtool_mapping_csv(self) -> str:
        """导出通途 ERP 图片组对应关系表"""
        csv_path = os.path.join(self.output_dir, "图片组对应关系.csv")
        rows = []
        # 1. Group A: 全部图片
        for idx, j in enumerate(self.jobs, start=1):
            rows.append(["A", 1, "GROUP_ALL", idx, "A", j["filename"], j["filename"], j["category"]])
        # 2. Group D: 详情图组 (包裹图 + 场景图 + 卖点图 + 可选结构图 + 可选手持图)
        d_jobs = [
            j for j in self.jobs
            if j["category"].startswith(("03_", "05_", "06_", "08_", "09_"))
        ]
        for idx, j in enumerate(d_jobs, start=1):
            rows.append(["D", 2, "GROUP_DETAIL", idx, "D", j["filename"], j["filename"], j["category"]])
        # 3. Group V: SKU 属性图组
        v_jobs = [j for j in self.jobs if j["category"].startswith("04_")]
        for idx, j in enumerate(v_jobs, start=1):
            rows.append(["V", 3, "GROUP_SKU_VARIANT", idx, "V", j["filename"], j["filename"], j["category"]])

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as cf:
            writer = csv.writer(cf)
            writer.writerow(["group_type", "group_sort", "group_id", "sort", "image_type", "name", "filename", "category"])
            writer.writerows(rows)
        return csv_path
