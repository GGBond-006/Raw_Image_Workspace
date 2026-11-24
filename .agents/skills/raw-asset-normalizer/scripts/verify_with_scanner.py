# -*- coding: utf-8 -*-
"""
工作台端到端干跑校验脚本（raw-asset-normalizer Step 4）

直接调用 AutoShot 工作台真实源码：
- web.scanner.scan_product_folder()
- prompts.compile_all_jobs()

验证整理后的标准化素材目录能否在工作台「一次导入即全绿、零报错、槽位与任务 100% 精准」：
1. 校验 SPU 识别、颜色组识别与 color_id 是否和 base_skus 完全一致；
2. 校验 preflight 6 项预检结果（特别关注分辨率 >= 1000x1000 且无阻断项）；
3. 校验全部编译任务数量、各图类分布、每张任务的参考图文件是否真实存在；
4. 检查文案与提示词是否残留黑名单冲突词（如误把旧比例 32:1 或高配型号词带入）。
"""
import argparse
import json
import os
import sys
from collections import Counter
from typing import Any, Dict, List


def verify_folder(normalized_folder: str, workspace_dir: str = "E:/Projects/Raw_Image_Workspace") -> int:
    auto_gen_dir = os.path.join(os.path.abspath(workspace_dir), "auto_image_gen")
    if auto_gen_dir not in sys.path:
        sys.path.insert(0, auto_gen_dir)

    from web.scanner import scan_product_folder
    from prompts import compile_all_jobs

    scan = scan_product_folder(normalized_folder, auto_gen_dir)
    task_cfg = scan["task_config"]
    jobs = compile_all_jobs(task_cfg)

    errors: List[str] = []
    warnings: List[str] = []

    print("============================================================")
    print(f"SPU:     {scan['spu_code']} | Display: {scan['product_display_name']}")
    print(f"Folder:  {scan['folder_path']}")
    print(f"Stats:   {json.dumps(scan['stats'], ensure_ascii=False)}")
    print("============================================================")

    # 1. Preflight 检查
    pf = scan["preflight"]
    print("\n[1] Preflight 6-Item Checks:")
    for chk in pf["checks"]:
        print(f"  - [{chk['status'].upper():4s}] {chk['title']}: {chk['desc']}")
        if chk["status"] == "bad":
            errors.append(f"Preflight blocking: {chk['title']} - {chk['desc']}")
        elif chk["key"] == "resolution" and chk["status"] != "ok":
            errors.append(f"Resolution preflight not ok: {chk['desc']}")
    if not pf["ready"]:
        errors.append("Preflight ready is False!")

    # 2. Color & Slot 绑定检查
    print("\n[2] Color Groups & Slots:")
    scanned_color_ids = set()
    for cg in scan["color_groups"]:
        scanned_color_ids.add(cg["color_id"])
        print(f"  * {cg['color_id']} ({cg['color_name_cn']} / {cg['color_name_en']}) <- folder '{cg['folder_label']}' ({cg['count']} slots)")
        for s in cg["slots"]:
            if s["image"]:
                im = s["image"]
                print(f"      - {s['role']:12s} ({s['label']}): {im['name']} ({im['width']}x{im['height']}, {im['size_kb']}KB)")
            else:
                print(f"      - {s['role']:12s} ({s['label']}): [EMPTY / {s.get('reuse_note') or s.get('reused_from')}]")
        if cg.get("extra_images"):
            warnings.append(f"Color {cg['color_id']} has {len(cg['extra_images'])} extra unslotted images")

    # 3. color_id 与 base_skus 一致性校验（最容易导致属性图/俄语图丢失的隐形坑）
    print("\n[3] Base SKUs & Bundles:")
    for sku in task_cfg.get("base_skus", []):
        cid = sku.get("color_id")
        ok_mark = "OK" if cid in scanned_color_ids else "MISMATCH!"
        print(f"  - {sku['sku_code']} | color_id={cid} [{ok_mark}] | badge={sku.get('version_badge')}")
        if cid not in scanned_color_ids:
            errors.append(
                f"SKU {sku['sku_code']} color_id='{cid}' not in scanned color_groups {sorted(scanned_color_ids)}!"
            )
    for bp in task_cfg.get("bundled_packages", []):
        acc = bp.get("accessory_sku")
        img = bp.get("accessory_cutout_png")
        if acc and (not img or not os.path.isfile(img)):
            errors.append(f"Bundled package {bp['package_id']} ({acc}) missing cutout image: {img}")
        print(f"  - Bundle {bp['package_id']}: acc={acc} | title={bp.get('accessory_title_en')} | img_ok={bool(not acc or (img and os.path.isfile(img)))}")

    # 4. 编译任务与参考图路径完整性校验
    print(f"\n[4] Compiled Jobs Total: {len(jobs)}")
    cat_counts = Counter(j["category"] for j in jobs)
    for cat, cnt in sorted(cat_counts.items()):
        print(f"  - {cat}: {cnt}")

    missing_refs = []
    for j in jobs:
        for ref in j.get("reference_images", []):
            if not ref or not os.path.isfile(ref):
                missing_refs.append(f"{j['filename']} -> {ref}")
    if missing_refs:
        for m in missing_refs:
            errors.append(f"Missing reference image: {m}")

    # 5. 黑名单冲突词 & 跨品串词审查（覆盖文案与全部编译后 Prompt，排除“严禁出现…”禁令句自身）
    blacklist = task_cfg.get("product_meta", {}).get("blacklisted_terms") or []
    copy_blob = json.dumps(
        {
            "copywriting_en": task_cfg.get("copywriting_en"),
            "copywriting_ru": task_cfg.get("copywriting_ru"),
        },
        ensure_ascii=False,
    ).lower()
    for term in blacklist:
        if term and term.lower() in copy_blob:
            errors.append(f"Blacklisted term '{term}' found inside copywriting_en/ru!")

    # 检查编译出的每条 Prompt 正文（剥离“严禁出现以下错误或冲突词：...”之后检查）
    is_gx10 = "gx10" in (task_cfg.get("task_id", "") + task_cfg.get("product_meta", {}).get("display_name_cn", "")).lower()
    prompt_leaks = []
    for j in jobs:
        p_text = j.get("prompt") or ""
        p_clean = p_text.split("严禁出现以下错误或冲突词")[0].split("严禁沿用")[0]
        p_low = p_clean.lower()
        if not is_gx10 and "gx10" in p_low:
            prompt_leaks.append(f"{j['filename']} leaks 'GX10'")
        for term in blacklist:
            if term and term.lower() in p_low:
                # 若明确紧跟“严禁”字样则是负向指令，放行；否则报警
                idx = p_low.find(term.lower())
                ctx = p_clean[max(0, idx - 12):idx]
                if "严禁" not in ctx and "禁止" not in ctx and "不要" not in ctx:
                    prompt_leaks.append(f"{j['filename']} contains blacklisted '{term}'")
    for lk in prompt_leaks[:10]:
        errors.append(f"Prompt leak: {lk}")

    print("\n============================================================")
    if warnings:
        print(f"[WARNINGS ({len(warnings)})]:")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print(f"[FAILED ({len(errors)} errors)]:")
        for e in errors:
            print(f"  X {e}")
        return 1
    print("[PASS] All workbench checks succeeded! Ready to import into AutoShot Studio.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify normalized folder with real AutoShot scanner & prompt compiler.")
    parser.add_argument("normalized_folder", help="标准化后的商品素材目录路径")
    parser.add_argument("--workspace-dir", default="E:/Projects/Raw_Image_Workspace", help="工作区根目录")
    args = parser.parse_args()
    sys.exit(verify_folder(args.normalized_folder, args.workspace_dir))


if __name__ == "__main__":
    main()
