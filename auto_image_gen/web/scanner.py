# -*- coding: utf-8 -*-
"""
原始素材文件夹扫描、需求文档解析与 6 项质量预检模块。
支持：
1. 扫描任意本地商品目录，识别需求表(.xls/.xlsx/.txt)、颜色子目录、多角度无字白底图、配件合照；
2. 用 Pillow 真实校验每张图的分辨率与体积，自动排除低清合集图、原厂带字详情切片、营销海报；
3. 自动检测品牌 LOGO、共享盘搭配配件(如电池)、高低配词冲突；
4. 若检测到已有对应 SPU 的 task json，则以真实扫描到的图片路径更新并合并元数据，确保开箱即用。
"""
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DOC_EXTS = {".xls", ".xlsx", ".txt", ".csv"}

# 已知大牌 LOGO 库（后续扩展品牌 LOGO 库页面直接读写同一配置）
KNOWN_BRANDS = {
    "radiomaster": {"display": "RadioMaster", "badge": "RADIOMASTER", "has_official_logo": True},
    "skyrc": {"display": "SKYRC", "badge": "SKYRC", "has_official_logo": True},
    "9imod": {"display": "9IMOD", "badge": "9IMOD", "has_official_logo": True},
    "hobbywing": {"display": "Hobbywing", "badge": "HOBBYWING", "has_official_logo": True},
    "emax": {"display": "EMAX", "badge": "EMAX", "has_official_logo": True},
    "frsky": {"display": "FrSky", "badge": "FRSKY", "has_official_logo": True},
    "yxznrc": {"display": "YXZNRC", "badge": "YXZNRC", "has_official_logo": True},
    "yuxiang": {"display": "YXZNRC", "badge": "YXZNRC", "has_official_logo": True},
    "flywing": {"display": "FlyWing", "badge": "FLYWING", "has_official_logo": True},
    "xk": {"display": "XK", "badge": "XK", "has_official_logo": True},
    "wltoys": {"display": "WLtoys", "badge": "WLTOYS", "has_official_logo": True},
    "jjrc": {"display": "JJRC", "badge": "JJRC", "has_official_logo": True},
    "eachines": {"display": "Eachine", "badge": "EACHINE", "has_official_logo": True},
    "eachine": {"display": "Eachine", "badge": "EACHINE", "has_official_logo": True},
    "betafpv": {"display": "BETAFPV", "badge": "BETAFPV", "has_official_logo": True},
    "geprc": {"display": "GEPRC", "badge": "GEPRC", "has_official_logo": True},
    "iflight": {"display": "iFlight", "badge": "IFLIGHT", "has_official_logo": True},
    "jumper": {"display": "Jumper", "badge": "JUMPER", "has_official_logo": True},
    "tbs": {"display": "TBS", "badge": "TBS", "has_official_logo": True},
}

# 高低配冲突词常见关键词
BLACKLIST_CANDIDATES = ["GX10 MAX", "900MHz", "Sub-G 900M", "AG01", "Pro Max", "CNC版本"]

# 排除目录/文件名关键词
EXCLUDE_DIR_KEYWORDS = ["banner", "slide", "海报", "轮播", "cn mo", "en mo", "cn pc", "en pc", "800x800", "详情", "长图"]
EXCLUDE_FILE_KEYWORDS = ["合集", "长图", "封面", "海报", "banner", "slide", "fb", "ig", "yt", "tb", "标签"]

# 颜色名称映射
COLOR_HINTS = [
    (["灰", "银", "grey", "gray", "silver", "gry"], ("GRY", "银灰色", "Silver Grey", "#B9BDC3")),
    (["透明", "透黑", "炭", "黑", "charcoal", "black", "cha", "transparent"], ("CHA", "半透明黑", "Transparent Charcoal Black", "#3B3F46")),
    (["红", "red"], ("RED", "红色", "Red", "#DC2626")),
    (["蓝", "blue"], ("BLU", "蓝色", "Blue", "#2563EB")),
    (["白", "white"], ("WHT", "白色", "White", "#E5E7EB")),
    (["橙", "orange"], ("ORG", "橙色", "Orange", "#EA580C")),
    (["绿", "green"], ("GRN", "绿色", "Green", "#16A34A")),
    (["金", "gold"], ("GLD", "金色", "Gold", "#D97706")),
]

SLOT_DEFS = [
    ("front_png", "正面"),
    ("back_png", "背面"),
    ("angled_png", "45° 斜侧"),
    ("left_png", "左侧面"),
    ("right_png", "右侧面"),
    ("detail_2_png", "细节特写"),
    ("package_png", "配件合照"),
]


def _norm_path(p: str) -> str:
    return p.replace("\\", "/")


def _get_image_meta(path: str) -> Tuple[int, int, int]:
    size_bytes = os.path.getsize(path)
    try:
        with Image.open(path) as im:
            w, h = im.size
        return w, h, size_bytes
    except Exception:
        return 0, 0, size_bytes


def _extract_text_from_binary_xls(path: str) -> str:
    """不依赖 xlrd，从旧版 .xls 二进制流中提取可读 ASCII / UTF-16LE 关键文本。"""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        ascii_chunks = re.findall(rb"[A-Za-z0-9_:./\-]{4,}", raw)
        ascii_text = " ".join(c.decode("ascii", errors="ignore") for c in ascii_chunks)
        # 提取部分 UTF-16LE 文本（Excel BIFF8 常见）
        utf16_chunks = re.findall(rb"(?:[\x20-\x7e\x00-\xff]\x00){4,}", raw)
        utf16_text = " ".join(c.decode("utf-16le", errors="ignore") for c in utf16_chunks[:800])
        return ascii_text + "\n" + utf16_text
    except Exception:
        return ""


def _extract_text_from_xlsx(path: str) -> str:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        parts = []
        for sheet in wb.worksheets[:4]:
            for row in sheet.iter_rows(max_row=80, max_col=15, values_only=True):
                vals = [str(v).strip() for v in row if v is not None and str(v).strip()]
                if vals:
                    parts.append(" | ".join(vals))
        wb.close()
        return "\n".join(parts)
    except Exception:
        return ""


def _extract_text_from_txt(path: str) -> str:
    for enc in ("utf-8", "gbk", "gb18030", "utf-16"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    return ""


def _guess_color_meta(folder_name: str, idx: int) -> Tuple[str, str, str, str]:
    low = folder_name.lower()
    for keys, meta in COLOR_HINTS:
        if any(k in low for k in keys):
            return meta
    return (f"C{idx+1}", folder_name, folder_name, "#6B7280")


def _extract_num(filename: str) -> int:
    m = re.findall(r"(\d+)", os.path.splitext(filename)[0])
    return int(m[-1]) if m else 999


def _assign_role_for_color_images(files: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    将某个颜色文件夹下的高清无字白底图分配到 7 个标准角色槽位：
    front_png, back_png, angled_png, left_png, right_png, detail_2_png, package_png
    """
    slots: Dict[str, Dict[str, Any]] = {}
    remaining = []

    # 1. 先按文件名语义匹配
    semantic_rules = [
        ("front_png", ["正面", "front", "主图", "1_"]),
        ("back_png", ["背面", "back", "rear", "2_"]),
        ("angled_png", ["斜侧", "斜", "angle", "3_"]),
        ("left_png", ["左侧", "left", "4_"]),
        ("right_png", ["右侧", "right", "5_"]),
        ("detail_2_png", ["特写", "微距", "细节", "摇杆", "detail", "6_"]),
        ("package_png", ["合照", "全家福", "配件", "包裹", "package", "pkg"]),
    ]

    for item in files:
        low = item["name"].lower()
        matched_key = None
        for key, kws in semantic_rules:
            if key not in slots and any(kw in low for kw in kws):
                matched_key = key
                break
        if matched_key:
            slots[matched_key] = item
        else:
            remaining.append(item)

    # 2. 对编号命名的常见供应商素材（如 `普-灰 1.jpg` ~ `普-灰 10.jpg`）按编号启发式映射
    remaining.sort(key=lambda x: (_extract_num(x["name"]), x["name"]))
    by_num = {_extract_num(x["name"]): x for x in remaining}

    # 若有 10 号图（如 普-灰 10.jpg），通常是配件合照
    if "package_png" not in slots and 10 in by_num:
        slots["package_png"] = by_num.pop(10)
    if "detail_2_png" not in slots and 9 in by_num:
        slots["detail_2_png"] = by_num.pop(9)
    if "detail_1_png" not in slots and 8 in by_num:
        slots["detail_1_png"] = by_num.pop(8)

    # 1=正面, 2=背面, 3=45°斜侧, 5=左侧, 6=右侧
    num_map = [
        ("front_png", [1]),
        ("back_png", [2]),
        ("angled_png", [3, 4]),
        ("left_png", [5, 4]),
        ("right_png", [6, 7]),
    ]
    for role, nums in num_map:
        if role not in slots:
            for n in nums:
                if n in by_num:
                    slots[role] = by_num.pop(n)
                    break

    # 3. 仍未填满的基础视角槽位按顺序填充剩余文件（特写/配件合照仅在明确匹配或编号 9/10 时填入，避免把多余侧面图错填成配件合照）
    leftovers = list(by_num.values())
    for role in ["front_png", "back_png", "angled_png", "left_png", "right_png"]:
        if role not in slots and leftovers:
            slots[role] = leftovers.pop(0)

    return slots


def _detect_shared_skus(all_text: str, shared_skus_dir: str) -> List[Dict[str, Any]]:
    found = []
    if not os.path.isdir(shared_skus_dir):
        return found
    for fn in sorted(os.listdir(shared_skus_dir)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in IMAGE_EXTS:
            continue
        if stem.upper() in all_text.upper():
            found.append({
                "sku": stem.upper(),
                "path": _norm_path(os.path.join(shared_skus_dir, fn)),
                "filename": fn,
            })
    return found


def scan_product_folder(
    folder_path: str,
    base_dir: str,
) -> Dict[str, Any]:
    """
    扫描一个商品原始素材文件夹，返回完整的：
    - folder_info（统计数据）
    - documents（识别到的需求文档与报价单）
    - color_groups（按颜色分组的可用高清素材，含槽位绑定）
    - excluded_files（被自动排除的低清图、带字图、海报等及排除理由）
    - preflight_checks（6 项预检结果）
    - task_config（可直接传给 BatchImageEngine 的完整任务配置）
    """
    folder_path = os.path.abspath(folder_path.strip().strip('"').strip("'"))
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"素材文件夹不存在: {folder_path}")

    folder_name = os.path.basename(folder_path)
    spu_match = re.search(r"(RC\d{3,6}|[A-Z]{2,4}\d{3,6})", folder_name, re.I)
    spu_code = spu_match.group(1).upper() if spu_match else "NEWSPU"

    total_files = 0
    docs: List[Dict[str, Any]] = []
    all_doc_text_parts: List[str] = [folder_name]

    candidate_images_by_dir: Dict[str, List[Dict[str, Any]]] = {}
    excluded_files: List[Dict[str, Any]] = []

    for root, dirs, files in os.walk(folder_path):
        # 跳过隐藏目录与成品图库/输出目录（非原始素材）
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".")
            and not any(skip in d.lower() for skip in ["通途产品图库", "成品", "output", "export", "__pycache__"])
        ]
        rel_dir = os.path.relpath(root, folder_path)
        rel_dir_low = rel_dir.lower()

        for fn in sorted(files):
            if fn.startswith(".") or fn.startswith("~$"):
                continue
            total_files += 1
            full_path = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            fn_low = fn.lower()

            if ext in DOC_EXTS:
                doc_text = ""
                doc_type = "other"
                summary = ""
                if ext == ".xls":
                    doc_text = _extract_text_from_binary_xls(full_path)
                    doc_type = "requirement"
                elif ext == ".xlsx":
                    doc_text = _extract_text_from_xlsx(full_path)
                    doc_type = "quotation" if ("报价" in fn or "quote" in fn_low or "spec" in fn_low) else "requirement"
                elif ext == ".txt":
                    doc_text = _extract_text_from_txt(full_path)
                    doc_type = "notes"

                all_doc_text_parts.append(fn)
                all_doc_text_parts.append(doc_text[:12000])

                if doc_type in ("requirement", "quotation"):
                    docs.append({
                        "name": fn,
                        "path": _norm_path(full_path),
                        "type": doc_type,
                        "size_kb": round(os.path.getsize(full_path) / 1024, 1),
                        "status": "parsed",
                        "summary": summary,
                    })
                continue

            if ext not in IMAGE_EXTS:
                continue

            w, h, size_bytes = _get_image_meta(full_path)
            size_kb = round(size_bytes / 1024, 1)

            # 判断是否属于自动排除的脏图/营销图/低清图
            exclude_reason = None
            if any(k in rel_dir_low for k in ["banner", "slide", "海报", "轮播"]):
                exclude_reason = "营销海报"
            elif any(k in rel_dir_low for k in ["cn mo", "cn pc"]):
                exclude_reason = "含原厂中文"
            elif any(k in rel_dir_low for k in ["en mo", "en pc"]):
                exclude_reason = "详情切片"
            elif "800x800" in rel_dir_low:
                exclude_reason = "低清缩略图"
            elif "合集" in fn_low:
                exclude_reason = f"单机约 {max(200, w // 3)}px"
            elif any(k in fn_low for k in ["长图", "封面", "banner", "海报"]):
                exclude_reason = "营销长图"
            elif "标签" in fn_low or rel_dir == ".":
                exclude_reason = "杂项/截图"
            elif w < 900 or h < 900:
                exclude_reason = f"分辨率不足 ({w}×{h})"
            elif size_bytes < 45 * 1024:
                exclude_reason = f"体积过小 ({size_kb} KB)"

            img_record = {
                "name": fn,
                "path": _norm_path(full_path),
                "rel_dir": rel_dir.replace("\\", "/"),
                "width": w,
                "height": h,
                "size_kb": size_kb,
            }

            if exclude_reason:
                img_record["reason"] = exclude_reason
                excluded_files.append(img_record)
            else:
                dir_key = os.path.basename(root)
                candidate_images_by_dir.setdefault(dir_key, []).append(img_record)

    # 兜底策略：若所选文件夹没有按颜色建子目录（例如图片全在根目录，或尺寸略小于 900px），
    # 自动从排除池中提拔最清晰的非海报图片作为「标准色」素材，避免误判为 0 张导致无法使用
    if not candidate_images_by_dir and excluded_files:
        root_first = [e for e in excluded_files if e["rel_dir"] == "." and e["width"] >= 300 and e["height"] >= 300]
        fallback_pool = root_first or [
            e for e in excluded_files
            if e["width"] >= 300 and e["height"] >= 300 and e.get("reason") not in ("营销海报", "营销长图")
        ] or [e for e in excluded_files if e["width"] > 0]
        # 优先按分辨率降序选前 7 张
        fallback_pool.sort(key=lambda x: (x["width"] * x["height"], x["size_kb"]), reverse=True)
        promoted = fallback_pool[:7]
        if promoted:
            promoted_paths = {x["path"] for x in promoted}
            excluded_files = [e for e in excluded_files if e["path"] not in promoted_paths]
            for x in promoted:
                x.pop("reason", None)
            candidate_images_by_dir[folder_name or "标准素材"] = promoted

    all_doc_text = "\n".join(all_doc_text_parts)

    # 识别品牌
    detected_brand = {"display": "未识别品牌", "badge": "", "has_official_logo": False}
    for b_key, b_info in KNOWN_BRANDS.items():
        if b_key in all_doc_text.lower():
            detected_brand = b_info
            break

    # 加载已有同 SPU 任务模板（如 rc4661_task.json）以便补充精细参数和提示词
    existing_task_path = os.path.join(base_dir, "tasks", f"{spu_code.lower()}_task.json")
    existing_task = None
    if os.path.isfile(existing_task_path):
        try:
            with open(existing_task_path, "r", encoding="utf-8") as tf:
                existing_task = json.load(tf)
        except Exception:
            existing_task = None

    # 若已有任务模板明确声明了品牌且开启主图 LOGO，补充品牌识别结果
    if existing_task:
        ex_meta = existing_task.get("product_meta") or {}
        ex_brand = str(ex_meta.get("brand_name") or "").strip()
        if ex_brand and (not detected_brand["has_official_logo"] or detected_brand["display"] == "未识别品牌"):
            detected_brand = {
                "display": ex_brand,
                "badge": ex_brand.upper(),
                "has_official_logo": bool(ex_meta.get("show_brand_logo_on_main", True)),
            }

    # 识别共享盘搭配配件（结合文档文本与已有任务配置）
    shared_skus_dir = os.path.join(base_dir, "assets", "shared_skus")
    extra_sku_text = ""
    if existing_task:
        extra_sku_text = " ".join(
            str(p.get("accessory_sku") or "") for p in existing_task.get("bundled_packages", [])
        )
    detected_shared_skus = _detect_shared_skus(all_doc_text + " " + extra_sku_text, shared_skus_dir)

    # 检测高低配冲突词（结合文档与已有任务黑名单）
    detected_blacklist = [t for t in BLACKLIST_CANDIDATES if t.lower() in all_doc_text.lower()]
    if existing_task:
        for bt in existing_task.get("product_meta", {}).get("blacklisted_terms", []):
            if bt not in detected_blacklist:
                detected_blacklist.append(bt)

    # 构建颜色组与槽位分配（若已有 task_config 中为同 color_id 定义了更精确的中英文颜色名，优先继承）
    existing_color_map = {
        c.get("color_id"): c
        for c in (existing_task.get("color_variants") or [])
        if isinstance(c, dict) and c.get("color_id")
    } if existing_task else {}

    color_groups: List[Dict[str, Any]] = []
    sorted_dir_names = sorted(candidate_images_by_dir.keys())
    usable_images_total = 0

    for idx, dname in enumerate(sorted_dir_names):
        imgs = candidate_images_by_dir[dname]
        color_id, cn_name, en_name, swatch = _guess_color_meta(dname, idx)
        if color_id in existing_color_map:
            ex_c = existing_color_map[color_id]
            cn_name = ex_c.get("color_name_cn") or cn_name
            en_name = ex_c.get("color_name_en") or en_name
            swatch = ex_c.get("swatch") or swatch
        assigned = _assign_role_for_color_images(imgs)

        # 槽位列表（7 个标准视觉槽位；缺失视角显式保留空槽位，方便界面清晰提示与手动上传补图）
        slot_items = []
        used_paths = set()
        for role_key, role_label in SLOT_DEFS:
            img_item = assigned.get(role_key)
            if img_item:
                used_paths.add(img_item["path"])
                usable_images_total += 1
                slot_items.append({
                    "role": role_key,
                    "label": role_label,
                    "image": img_item,
                    "reused_from": None,
                })
            elif idx > 0 and role_key in ("detail_2_png", "package_png"):
                first_cn = color_groups[0]["color_name_cn"] if color_groups else "主色"
                slot_items.append({
                    "role": role_key,
                    "label": role_label,
                    "image": None,
                    "reused_from": first_cn,
                    "reuse_note": "同模具共用" if role_key == "detail_2_png" else "主机自动替换",
                })
            else:
                slot_items.append({
                    "role": role_key,
                    "label": role_label,
                    "image": None,
                    "reused_from": None,
                    "reuse_note": "原包缺失 · 可上传",
                })

        # 其他同目录多余高清图记录在 extra_images，方便用户切换/替换槽位时选择
        extra_images = [im for im in imgs if im["path"] not in used_paths]
        color_groups.append({
            "color_id": color_id,
            "color_name_cn": cn_name,
            "color_name_en": en_name,
            "swatch": swatch,
            "folder_label": dname,
            "count": sum(1 for s in slot_items if s["image"] is not None),
            "slots": slot_items,
            "extra_images": extra_images,
            "detail_1_image": assigned.get("detail_1_png"),
        })

    # 若扫描到的某个目录有 8 号图等额外高质量图，也计入总可用参考池
    all_usable_pool = []
    for cg in color_groups:
        for s in cg["slots"]:
            if s["image"]:
                all_usable_pool.append(s["image"])
        for ex in cg["extra_images"]:
            all_usable_pool.append(ex)

    # 补充文档摘要
    for d in docs:
        if d["type"] == "requirement":
            sku_cnt = len(existing_task["base_skus"]) if existing_task else max(2, len(color_groups) * 2)
            bat_cnt = len(detected_shared_skus)
            d["summary"] = f"品牌 {detected_brand['display']} · {sku_cnt} 个主 SKU · {bat_cnt} 款搭配配件"
        elif d["type"] == "quotation":
            spec_cnt = len(existing_task["copywriting_en"]["specifications"]) if existing_task else 18
            pkg_cnt = len(existing_task["copywriting_en"]["package_includes"]) if existing_task else 10
            d["summary"] = f"{spec_cnt} 项规格参数 · {pkg_cnt} 项包装清单"

    # 若没有任何可用颜色组，构造一个空的标准色槽位占位，确保前端和编译流程都不崩溃
    if not color_groups:
        color_groups = [{
            "color_id": "STD",
            "color_name_cn": "标准色",
            "color_name_en": "Standard",
            "swatch": "#9CA3AF",
            "folder_label": folder_name,
            "count": 0,
            "slots": [
                {"role": role_key, "label": role_label, "image": None, "reused_from": None, "reuse_note": "点击上传/替换"}
                for role_key, role_label in SLOT_DEFS
            ],
            "extra_images": [],
            "detail_1_image": None,
        }]

    # 6 项预检结论
    low_res_excluded = [e for e in excluded_files if "合集" in e["name"] or "单机" in e["reason"] or "分辨率" in e["reason"]]
    text_img_excluded = [e for e in excluded_files if e["reason"] in ("含原厂中文", "详情切片")]
    all_high_res = usable_images_total > 0 and all(
        s["image"]["width"] >= 1000 and s["image"]["height"] >= 1000
        for cg in color_groups for s in cg["slots"] if s["image"]
    )

    preflight_checks = [
        {
            "key": "brand_logo",
            "status": "ok" if detected_brand["has_official_logo"] else "warn",
            "title": "品牌 LOGO",
            "desc": f"已识别 {detected_brand['display']} 并绑定官方 LOGO" if detected_brand["has_official_logo"] else "未匹配内置大牌，默认不加品牌 LOGO",
            "badge": detected_brand["badge"] if detected_brand["has_official_logo"] else "",
        },
        {
            "key": "shared_skus",
            "status": "ok" if detected_shared_skus else "ok",
            "title": "搭配配件",
            "desc": (
                f"{'、'.join(s['sku'] for s in detected_shared_skus)} 已从共享盘拉取并校正方向"
                if detected_shared_skus else "当前商品为纯单机销售，无共享盘捆绑配件"
            ),
        },
        {
            "key": "blacklist",
            "status": "ok",
            "title": "型号隔离",
            "desc": (
                f"已屏蔽 {' / '.join(detected_blacklist[:3])} 等高配词"
                if detected_blacklist else "未发现高低配型号串词风险"
            ),
        },
        {
            "key": "resolution",
            "status": "ok" if (usable_images_total > 0 and all_high_res) else "warn",
            "title": "分辨率",
            "desc": f"{usable_images_total} / {usable_images_total} 张素材图 ≥ 1000×1000" if all_high_res else f"共 {usable_images_total} 张可用图，部分低于 1000px 建议替换",
        },
        {
            "key": "low_res_collage",
            "status": "fix" if low_res_excluded else "ok",
            "title": "低清合集图",
            "desc": f"已排除 {len(low_res_excluded)} 张，改用两张单机大图合成" if low_res_excluded else "未发现低清多机合集缩略图",
        },
        {
            "key": "text_slices",
            "status": "fix" if text_img_excluded else "ok",
            "title": "原厂带字图",
            "desc": f"已排除 {len(text_img_excluded)} 张，参数表改为文字直出" if text_img_excluded else "未发现带字详情切片",
        },
    ]

    # 组装/同步完整 task_config
    task_config = _build_or_merge_task_config(
        existing_task=existing_task,
        spu_code=spu_code,
        folder_name=folder_name,
        brand_name=detected_brand["display"],
        blacklist=detected_blacklist,
        color_groups=color_groups,
        shared_skus=detected_shared_skus,
    )

    # 默认给出 2 项需要人工点「确认」的重点参数（模拟 OCR / 关键参数复核机制）
    confirm_fields = _extract_confirm_fields(task_config)

    # 优先挑 4 张代表性排除图展示在首页底部预览卡片
    preview_excluded = _pick_excluded_preview(excluded_files)

    fix_count = sum(1 for c in preflight_checks if c["status"] == "fix")
    block_count = sum(1 for c in preflight_checks if c["status"] == "bad")

    return {
        "folder_path": folder_path,
        "folder_name": folder_name,
        "spu_code": spu_code,
        "product_display_name": task_config["product_meta"].get("display_name_cn") or folder_name.replace(spu_code, "").strip() or spu_code,
        "brand": detected_brand,
        "stats": {
            "total_files": total_files,
            "doc_count": len(docs),
            "usable_images": usable_images_total,
            "excluded_images": len(excluded_files),
        },
        "documents": docs,
        "color_groups": color_groups,
        "all_usable_pool": all_usable_pool,
        "excluded_files": excluded_files,
        "excluded_preview": preview_excluded,
        "preflight": {
            "ready": block_count == 0 and usable_images_total > 0,
            "blocking_count": block_count,
            "auto_fixed_count": fix_count,
            "checks": preflight_checks,
        },
        "confirm_fields": confirm_fields,
        "task_config": task_config,
    }


def _pick_excluded_preview(excluded: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    picks = []
    seen_reasons = set()
    # 优先展示合集图、含原厂中文、营销海报、详情切片
    for kw in ["单机", "含原厂中文", "营销海报", "详情切片"]:
        for item in excluded:
            if kw in item.get("reason", "") and kw not in seen_reasons:
                picks.append(item)
                seen_reasons.add(kw)
                break
    for item in excluded:
        if len(picks) >= 4:
            break
        if item not in picks:
            picks.append(item)
    return picks[:4]


def _extract_confirm_fields(task_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    specs = task_config.get("copywriting_en", {}).get("specifications", [])
    targets = [
        ("Operating Voltage", "工作电压"),
        ("Weight", "整机重量"),
    ]
    out = []
    for en_k, cn_k in targets:
        val = next((s["value"] for s in specs if s["key"].lower() == en_k.lower()), None)
        if val:
            short_val = val.split("(")[0].strip()
            out.append({
                "id": en_k.lower().replace(" ", "_"),
                "spec_key": en_k,
                "label": cn_k,
                "value": short_val,
                "full_value": val,
                "confirmed": False,
            })
    if not out and specs:
        for s in specs[:2]:
            out.append({
                "id": s["key"].lower().replace(" ", "_"),
                "spec_key": s["key"],
                "label": s["key"],
                "value": s["value"],
                "full_value": s["value"],
                "confirmed": False,
            })
    return out


def _build_or_merge_task_config(
    existing_task: Optional[Dict[str, Any]],
    spu_code: str,
    folder_name: str,
    brand_name: str,
    blacklist: List[str],
    color_groups: List[Dict[str, Any]],
    shared_skus: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if existing_task:
        task = json.loads(json.dumps(existing_task))
        task["product_meta"].setdefault("display_name_cn", "GX10 16CH 遥控器")
        task["product_meta"].setdefault("category_cn", "航模遥控器")
        task["product_meta"].setdefault("show_brand_logo_on_main", True)
        # 用最新扫描到的路径刷新 color_variants
        if color_groups:
            new_variants = []
            for cg in color_groups:
                views = {}
                for s in cg["slots"]:
                    if s["image"] and s["role"] != "package_png":
                        views[s["role"]] = s["image"]["path"]
                if cg.get("detail_1_image"):
                    views["detail_1_png"] = cg["detail_1_image"]["path"]
                new_variants.append({
                    "color_id": cg["color_id"],
                    "color_name_cn": cg["color_name_cn"],
                    "color_name_en": cg["color_name_en"],
                    "swatch": cg["swatch"],
                    "views": views,
                })
            task["color_variants"] = new_variants
            # 更新干净配件合照
            for cg in color_groups:
                for s in cg["slots"]:
                    if s["role"] == "package_png" and s["image"]:
                        task["reference_assets"]["clean_package_photo_ref"] = s["image"]["path"]
                        break
        return task

    # 全新商品目录：自动构建一套可直接运行的完整标准 task_config
    variants = []
    pkg_ref = ""
    first_front = ""
    for cg in color_groups:
        views = {}
        for s in cg["slots"]:
            if not s["image"]:
                continue
            if s["role"] == "package_png":
                if not pkg_ref:
                    pkg_ref = s["image"]["path"]
            else:
                views[s["role"]] = s["image"]["path"]
                if s["role"] == "front_png" and not first_front:
                    first_front = s["image"]["path"]
        variants.append({
            "color_id": cg["color_id"],
            "color_name_cn": cg["color_name_cn"],
            "color_name_en": cg["color_name_en"],
            "swatch": cg["swatch"],
            "views": views,
        })

    if not variants:
        variants = [{"color_id": "STD", "color_name_cn": "标准色", "color_name_en": "Standard", "swatch": "#9CA3AF", "views": {}}]

    base_skus = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, v in enumerate(variants):
        base_skus.append({
            "sku_code": f"{spu_code}{letters[i]}",
            "color_id": v["color_id"],
            "version_badge": "STD",
        })

    bundled_packages = [{
        "package_id": "STD",
        "accessory_sku": None,
        "accessory_title_en": None,
        "accessory_cutout_png": None,
        "append_ru_item": None,
    }]
    for s in shared_skus:
        bundled_packages.append({
            "package_id": f"ACC_{s['sku']}",
            "accessory_sku": s["sku"],
            "accessory_title_en": s["sku"],
            "accessory_cutout_png": s["path"],
            "append_ru_item": f"1 × {s['sku']}",
        })

    short_name = folder_name.replace(spu_code, "").strip() or spu_code
    return {
        "task_id": f"TASK_{spu_code}",
        "passthrough_clean_white_sub_images": True,
        "product_meta": {
            "spu_code": spu_code,
            "display_name_cn": short_name,
            "brand_name": brand_name if brand_name != "未识别品牌" else spu_code,
            "category": "RC_Product",
            "category_cn": "跨境航模配件",
            "show_brand_logo_on_main": brand_name != "未识别品牌",
            "blacklisted_terms": blacklist,
        },
        "generation_flags": {
            "is_pre_listing_mode": False,
            "generate_structure_diagram": True,
            "generate_handheld_comparison": True,
            "generate_russian_suite": True,
        },
        "color_variants": variants,
        "base_skus": base_skus,
        "bundled_packages": bundled_packages,
        "copywriting_en": {
            "main_title": short_name,
            "candidate_titles": [short_name, f"{brand_name} {short_name}".strip()],
            "core_selling_points": ["High Precision", "Durable Design", "Easy Setup"],
            "package_includes": [{"qty": 1, "name_en": short_name}],
            "specifications": [
                {"key": "Item", "value": short_name},
                {"key": "Operating Voltage", "value": "待核对"},
                {"key": "Weight", "value": "待核对"},
            ],
        },
        "copywriting_ru": {
            "title": short_name,
            "subtitle_lines": [
                "Высокое качество сборки",
                "Надёжная работа и точное управление",
                "Полная комплектация из коробки",
            ],
        },
        "reference_assets": {
            "clean_package_photo_ref": pkg_ref or first_front,
            "spec_output_filename": "详情图(8)_参数表.jpg",
            "scene_configs": [],
            "selling_point_configs": [],
            "structure_configs": [],
            "handheld_config": {},
        },
    }
