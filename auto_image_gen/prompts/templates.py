# -*- coding: utf-8 -*-
"""
12 类标准套图提示词（Prompt）母版库（V3.0 - 全品类通用数据驱动版）
核心设计原则：
1. 100% 由 task_config 动态驱动，严禁在母版中硬编码特定商品型号（如 GX10）、特定品类部件或固定电池型号；
2. 提示词首句明确指定目标像素尺寸与画布比例（1000 × 1000 px 1:1 方版 / 750 × 1000 px 3:4 竖版 / 900 × 1200 px 3:4 竖版）；
3. 根据 product_meta.category / appearance_lock_desc 自动生成贴合当前品类的外观细节锁定描述，并自动注入 blacklisted_terms 防串词禁令；
4. 所有包裹清单、属性图配件、俄语标签与俄语清单均动态读取 task_config，同时兼容自定义精细描述字段。
"""

from typing import Dict, Any, List, Tuple


# 按品类提供默认外观锁定描述与拍摄场景提示（当 product_meta 未单独覆写时自动生效）
CATEGORY_DEFAULTS: Dict[str, Dict[str, str]] = {
    "RC_Transmitter": {
        "noun_cn": "遥控器",
        "appearance_lock": "外壳颜色、屏幕、双摇杆、金属拨杆、按键布局和机身刻字",
        "side_lock": "立体角度、外壳质感、摇杆高度、拨杆和机身刻字",
        "outdoor_bg": "深海蓝到星空暗蓝的科技感室外航模飞行场背景（地平线处有柔和晨曦微光）",
        "real_front_bg": "真实的户外木质航模工作台与阳光草地环境",
        "real_side_bg": "真实的现代化室内电子工作台环境",
    },
    "RC_Helicopter": {
        "noun_cn": "遥控直升机",
        "appearance_lock": "机身涂装配色、编号标识、座舱玻璃、主旋翼头与桨叶、尾桨及起落架细节",
        "side_lock": "立体机身比例、涂装纹理、旋翼结构、尾撑与滑撬脚架细节",
        "outdoor_bg": "深海蓝到晴空微光的科技感户外航模飞行场上空背景（远景有柔和山峦与蓝天光晕）",
        "real_front_bg": "真实的户外阳光草地航模飞行场环境",
        "real_side_bg": "真实的户外开阔起降草坪与浅蓝天空环境",
    },
    "RC_Car": {
        "noun_cn": "遥控模型车",
        "appearance_lock": "车壳涂装配色、灯组细节、轮毂轮胎胎纹、避震悬挂与底盘结构",
        "side_lock": "侧面车身比例、轮毂立体感、悬架行程与车壳拉花细节",
        "outdoor_bg": "深蓝灰到冷蓝科技感的户外越野赛道背景（带柔和地面反光与速度氛围）",
        "real_front_bg": "真实的户外砂石/草地越野赛道环境",
        "real_side_bg": "真实的户外柏油路面或模型工作室展示台环境",
    },
    "RC_Drone": {
        "noun_cn": "无人机/穿越机",
        "appearance_lock": "碳纤机架结构、电机与桨叶、镜头云台、外壳涂装与机身标识",
        "side_lock": "机身立体结构、机臂厚度、电机细节与天线布局",
        "outdoor_bg": "深海蓝到星空暗蓝的科技感户外飞行场上空背景",
        "real_front_bg": "真实的户外飞行草地木质桌面环境",
        "real_side_bg": "真实的室内航模电子工作台环境",
    },
    "RC_Product": {
        "noun_cn": "产品主机",
        "appearance_lock": "外壳颜色、机身结构轮廓、涂装质感、核心部件与机身标识刻字",
        "side_lock": "立体侧面结构、材质纹理、接口/部件轮廓与机身标识",
        "outdoor_bg": "深海蓝到星空暗蓝的科技感商业摄影背景（地平线处有柔和冷蓝光晕）",
        "real_front_bg": "真实的户外木质工作台与自然光草地环境",
        "real_side_bg": "真实的现代化室内工作台环境",
    },
}


def _first_view_img(views: Dict[str, Any]) -> str:
    if not views:
        return ""
    for k in ("front_png", "angled_png", "back_png", "left_png", "right_png", "detail_1_png", "detail_2_png"):
        if views.get(k):
            return views[k]
    for v in views.values():
        if isinstance(v, str) and v:
            return v
    return ""


def _hero_view_img(task: Dict[str, Any], views: Dict[str, Any]) -> str:
    """获取用于主图/属性图/俄语主图的主力展示图（默认 front_png；直升机/车模等可配 hero_main_view='angled_png'）。"""
    if not views:
        return ""
    pref = (task.get("reference_assets") or {}).get("hero_main_view")
    if pref and views.get(pref):
        return views[pref]
    return _first_view_img(views)


def _cat_profile(task: Dict[str, Any]) -> Dict[str, str]:
    meta = task.get("product_meta") or {}
    cat = meta.get("category") or "RC_Product"
    base = dict(CATEGORY_DEFAULTS.get(cat, CATEGORY_DEFAULTS["RC_Product"]))
    if meta.get("appearance_lock_desc"):
        base["appearance_lock"] = meta["appearance_lock_desc"]
    if meta.get("side_lock_desc"):
        base["side_lock"] = meta["side_lock_desc"]
    if meta.get("product_noun_cn"):
        base["noun_cn"] = meta["product_noun_cn"]
    return base


def _product_short_name(task: Dict[str, Any]) -> str:
    meta = task.get("product_meta") or {}
    copy_en = task.get("copywriting_en") or {}
    return (
        copy_en.get("main_title")
        or meta.get("display_name_cn")
        or meta.get("spu_code")
        or "Product"
    )


def _blacklist_clause(task: Dict[str, Any], allow_russian: bool = False) -> str:
    terms = [str(t).strip() for t in (task.get("product_meta") or {}).get("blacklisted_terms") or [] if str(t).strip()]
    base_forbid = "严禁出现中文" if not allow_russian else "俄语、型号和版本原样排版，严禁出现中文"
    if not terms:
        return f"{base_forbid}。"
    joined = "、".join(terms[:8])
    return f"{base_forbid}，严禁出现以下错误或冲突词：{joined}。"


def _primary_pkg_color_id(task: Dict[str, Any]) -> str:
    ref_assets = task.get("reference_assets") or {}
    if ref_assets.get("package_photo_color_id"):
        return ref_assets["package_photo_color_id"]
    variants = task.get("color_variants") or []
    return variants[0]["color_id"] if variants else ""


def _split_two_columns(items: List[str]) -> Tuple[str, str]:
    if not items:
        return "", ""
    mid = (len(items) + 1) // 2
    return "\n".join(items[:mid]), "\n".join(items[mid:])


def build_main_6_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    01. 【必选】主图（速卖通 6 张定向首图，1000 × 1000 px，1:1 方版）
    """
    variants = task.get("color_variants") or []
    if not variants:
        return []
    meta = task["product_meta"]
    copy_en = task["copywriting_en"]
    prof = _cat_profile(task)
    forbid = _blacklist_clause(task)

    show_logo = meta.get("show_brand_logo_on_main", True)
    brand = (meta.get("brand_name") or "").upper() if show_logo else ""
    brand_line_1 = f"顶部居中排品牌名「{brand}」，字号约 26 px。其下" if brand else "顶部居中"
    titles = copy_en.get("candidate_titles") or [copy_en.get("main_title") or meta.get("spu_code", "Product")]
    title_1 = titles[0]
    title_2 = titles[1] if len(titles) > 1 else title_1
    sp_list = list(copy_en.get("core_selling_points") or ["High Quality", "Durable Design", "Ready to Use"])
    while len(sp_list) < 3:
        sp_list.append(sp_list[-1])

    c0 = variants[0]
    c0_name = c0.get("color_name_cn", "标准色")
    views_0 = c0.get("views") or {}
    front_0 = _hero_view_img(task, views_0)
    if not front_0:
        return []
    # 主图6（FCFT侧面/斜侧）优先挑选与主图1不同的侧面/斜侧视角，避免两张图撞视角
    angled_0 = next(
        (views_0.get(k) for k in ("angled_png", "left_png", "right_png", "front_png") if views_0.get(k) and views_0.get(k) != front_0),
        views_0.get("angled_png") or front_0,
    )
    prod_name = _product_short_name(task)

    return [
        {
            "filename": "主图1.jpg",
            "category": "01_主图_速卖通定向",
            "store_tag": "9imod店铺",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": [front_0],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的速卖通商品主图。以输入的{c0_name} {prod_name} 主视角白底图为唯一商品素材，"
                f"抠取原物并合成，严格保持原图角度与{prof['appearance_lock']}100%清晰锐利。\n\n"
                f"背景用{prof['outdoor_bg']}，背景层均匀铺设半透明斜向阵列「9imod」店铺名水印（白色，不透明度约 14%，不遮挡商品主体）。\n\n"
                f"{brand_line_1}主标题「{title_1}」用 62–70 px 白色粗体（其中核心型号用亮天蓝色高亮）。"
                f"副标题用 24–28 px 白色半粗体单行居中显示：\n"
                f"{' | '.join(sp_list[:3])}\n\n"
                f"画面中下部居中放置商品主体，实际宽度约 640–700 px，底部加真实接触阴影与微弱倒影，保持机身每一处细节原样清晰。{forbid}"
            ),
        },
        {
            "filename": "主图2.jpg",
            "category": "01_主图_速卖通定向",
            "store_tag": "Moonhobby店铺",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": [front_0],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的 Moonhobby 店铺专属主图。以输入的{c0_name} {prod_name} 白底图为唯一商品素材，"
                f"抠取原物并合成，保持原图角度与{prof['appearance_lock']} 100% 清晰不变形。\n\n"
                f"背景用干净的冰白到浅天蓝柔和渐变。画布四周边缘设计一圈亮色调（亮天蓝与活力橙撞色）的现代几何装饰边框（边框厚约 24 px），"
                f"顶部边框中央蓝底铭牌居中排白色粗体店铺名「Moonhobby」（字号约 30 px）。\n\n"
                f"画框内部左上角排主标题「{title_2}」（52–60 px 深海军蓝粗体），其下并排两个胶囊形卖点标签：「{sp_list[0]}」（蓝底白字）与「{sp_list[1]}」（橙底白字）。\n\n"
                f"画面中央偏下放置商品主体，实际宽约 640–690 px，底部加柔和接触阴影。画框右下角放置一枚精致的金色盾牌品质徽章，内部清晰排英文「Quality Assurance」。{forbid}"
            ),
        },
        {
            "filename": "主图3.jpg",
            "category": "01_主图_速卖通定向",
            "store_tag": "ROCKET全托店铺",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "pad_white",
            "passthrough_if_clean_white": True,
            "reference_images": [front_0],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的纯白底商品主图。以输入的{c0_name} {prod_name} 白底图为唯一商品素材，"
                f"保持原图角度与{prof['appearance_lock']} 100% 原样清晰。"
                f"背景为纯白（#FFFFFF），商品居中放置，实际宽约 760–820 px，底部仅有极淡的自然接触阴影。严禁添加任何文字、边框、LOGO 或水印。"
            ),
        },
        {
            "filename": "主图4.jpg",
            "category": "01_主图_速卖通定向",
            "store_tag": "9imod全托店铺",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": [front_0],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的 9imod 全托店铺专属主图。以输入的{c0_name} {prod_name} 白底图为唯一商品素材，"
                f"抠取原物并合成，保持原图角度与{prof['appearance_lock']} 100% 原样清晰。\n\n"
                f"背景用纯净的浅灰白渐变。画布四周边缘加上一圈醒目的正红色（#E60012）实心边框（边框宽约 26 px），"
                f"顶部红框中央加宽铭牌居中排白色粗体店铺名「9imod」（字号约 32 px）。\n\n"
                f"画框内顶部居中排主标题「{title_1}」（54–62 px 纯黑粗体），其下用 22–26 px 深灰半粗体排三项核心卖点：\n"
                f"{'   |   '.join(sp_list[:3])}\n\n"
                f"画面中下部居中放置商品主体，实际宽约 650–700 px，底部加轻柔接触阴影。{forbid}"
            ),
        },
        {
            "filename": "主图5.jpg",
            "category": "01_主图_速卖通定向",
            "store_tag": "SKYRC店铺",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": [front_0],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的正面实物单反实拍风格主图。以输入的{c0_name} {prod_name} 主视角白底图为唯一商品素材，"
                f"抠取原物并合成在前景中央（实际宽约 720–780 px），保持原图角度与{prof['appearance_lock']} 100% 锐利清晰。\n\n"
                f"背景为{prof['real_front_bg']}，使用大光圈镜头景深效果对背景做强烈的高斯模糊虚化（焦外光斑柔和自然），"
                f"商品底部与环境有真实的物理接触阴影和环境漫反射光。\n\n"
                f"全图严禁出现任何边框、文字、LOGO、角标或电商排版元素，呈现纯粹的高清实物摄影效果。"
            ),
        },
        {
            "filename": "主图6.jpg",
            "category": "01_主图_速卖通定向",
            "store_tag": "FCFT店铺",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": [angled_0],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的侧面/斜侧面实物单反实拍风格主图。以输入的{c0_name} {prod_name} 斜侧面/侧面白底图为唯一商品素材，"
                f"抠取原物并合成在前景中央（实际宽约 700–760 px），保持原图{prof['side_lock']} 100% 锐利清晰。\n\n"
                f"背景为{prof['real_side_bg']}，使用大光圈浅景深效果对背景做强烈的高斯模糊虚化，商品底部有真实的自然接触阴影或自然悬停光影。\n\n"
                f"全图严禁出现任何边框、文字、LOGO、角标或电商排版元素，呈现纯粹的高清侧面实物摄影效果。"
            ),
        },
    ]


def build_sub_white_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    02. 【必选】副图（多角度纯白底图，4 张/颜色，1000 × 1000 px，1:1 方版）
    """
    prof = _cat_profile(task)
    jobs = []
    idx = 1
    for c in task["color_variants"]:
        views = c["views"]
        c_name = c["color_name_cn"]
        slot_paths = [
            ("正面", views.get("front_png")),
            ("左侧面", views.get("left_png") or views.get("angled_png") or views.get("detail_1_png")),
            ("右侧面", views.get("right_png") or views.get("detail_1_png") or views.get("detail_2_png")),
            ("背面", views.get("back_png")),
        ]
        for view_label, ref_path in slot_paths:
            if not ref_path:
                continue
            jobs.append({
                "filename": f"zt({idx}).jpg",
                "category": "02_副图_白底多角度",
                "color_id": c["color_id"],
                "view_label": view_label,
                "target_width": 1000,
                "target_height": 1000,
                "resize_mode": "pad_white",
                "passthrough_if_clean_white": task.get("passthrough_clean_white_sub_images", True),
                "reference_images": [ref_path],
                "prompt": (
                    f"制作一张 1000 × 1000 px、1:1 方版的纯白底商品副图。以输入的{c_name}{view_label}图为唯一商品素材，"
                    f"抠取原物并置于纯白背景（#FFFFFF）中央，占画布宽高约 80%，保持原图外观与{prof['appearance_lock']} 100% 不变。严禁添加任何文字、边框或水印。"
                ),
            })
            idx += 1
    return jobs


def build_package_en_prompt(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    03. 【必选】包裹图（英文配件清单图，1000 × 1000 px，1:1 方版）
    """
    copy_en = task["copywriting_en"]
    prod_name = _product_short_name(task)
    forbid = _blacklist_clause(task)

    pkg_ref = (task.get("reference_assets") or {}).get("clean_package_photo_ref") or ""
    if not pkg_ref:
        variants = task.get("color_variants") or []
        pkg_ref = _first_view_img(variants[0].get("views") or {}) if variants else ""
    if not pkg_ref:
        return []

    pkg_items = copy_en.get("package_includes") or []
    items = [f"{x['qty']} × {x['name_en']}" for x in pkg_items]
    left_col, right_col = _split_two_columns(items)

    custom_visual = copy_en.get("package_visual_desc") or (
        f"画面上部使用上传的 {prod_name} 标准配件白底合照作为唯一合成素材，保持原有商品主机及所有配件的外观、比例、表面标识和可辨识度；"
        f"移除原图中可能自带的旧文字标签，以干净整齐的平铺构图展示清单中的全部真实物品与数量，保持小配件边缘清晰锐利。"
    )

    return [{
        "filename": "包裹图.jpg",
        "category": "03_包裹图_英文清单",
        "target_width": 1000,
        "target_height": 1000,
        "resize_mode": "exact_resize",
        "reference_images": [pkg_ref],
        "prompt": (
            f"制作一张 1000 × 1000 px、1:1 方版的 {prod_name} 英文包裹清单图。背景用干净的暖白或浅灰，标题「PACKAGE INCLUDES」顶部居中，用 52–60 px 深石墨灰粗体。\n\n"
            f"{custom_visual}\n\n"
            f"配件区下方留出足够位置，用左右两栏整齐排英文清单。正文字号 18–20 px 深灰半粗体，长条目自然对齐：\n\n"
            f"左栏：\n{left_col}\n\n"
            f"右栏：\n{right_col}\n\n"
            f"所有配件以输入合照与上述清单为准，英文原样准确排版，{forbid}"
        ),
    }]


def build_sku_attribute_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    04. 【必选】属性图（SKU 变体组合图，V × P 张，1000 × 1000 px，1:1 方版）
    全动态支持单机/单电、多颜色替换、以及任意捆绑配件（电池/充电器等）组合。
    """
    jobs = []
    copy_en = task["copywriting_en"]
    prof = _cat_profile(task)
    forbid = _blacklist_clause(task)
    main_title = copy_en.get("main_title") or task["product_meta"].get("spu_code", "Product")
    colors_map = {c["color_id"]: c for c in (task.get("color_variants") or [])}
    pkg_ref = (task.get("reference_assets") or {}).get("clean_package_photo_ref") or ""
    primary_cid = _primary_pkg_color_id(task)

    pkg_items = copy_en.get("package_includes") or []
    acc_items_summary = "、".join(f"{x['qty']}×{x['name_en']}" for x in pkg_items[1:]) if len(pkg_items) > 1 else "全部标准配件"

    for sku in task.get("base_skus") or []:
        sku_code = sku["sku_code"]
        color_obj = colors_map.get(sku["color_id"])
        if not color_obj:
            continue
        color_cn = color_obj["color_name_cn"]
        front_img = _hero_view_img(task, color_obj.get("views") or {})
        use_pkg = pkg_ref or front_img
        if not use_pkg:
            continue
        badge = sku.get("version_badge", "STD")
        is_primary_color = (sku["color_id"] == primary_cid) or (not front_img) or (front_img == use_pkg)

        for pkg in task.get("bundled_packages") or []:
            acc_sku = pkg.get("accessory_sku")
            if acc_sku:
                out_filename = f"{sku_code}_{acc_sku}.jpg"
                acc_title = pkg.get("accessory_title_en") or acc_sku
                acc_img = pkg.get("accessory_cutout_png")
                acc_visual = pkg.get("accessory_visual_desc") or f"输入的配套配件（{acc_title}），保持外观、数量与表面文字正向清晰可读，严禁颠倒"

                if is_primary_color:
                    ref_imgs = [r for r in [front_img, use_pkg, acc_img] if r]
                    # 去重保持顺序
                    ref_imgs = list(dict.fromkeys(ref_imgs))
                    src_desc = f"以输入的{color_cn} {main_title} 主机图、标准配件合照和搭配配件图（{acc_title}）为合成素材"
                else:
                    ref_imgs = list(dict.fromkeys([r for r in [front_img, use_pkg, acc_img] if r]))
                    src_desc = f"以输入的图1（{color_cn} {main_title} 主视角白底图）、标准配件合照和搭配配件图（{acc_title}）为合成素材，并将主机替换为图1的{color_cn}款式"

                layout_instruction = (
                    f"横幅下方主画面分为上下两部分：\n"
                    f"上部左侧（占宽约 50%）放置{color_cn} {main_title} {prof['noun_cn']}主体（实际宽约 440–480 px，严格保持{prof['appearance_lock']}清晰）；\n"
                    f"上部右侧（占宽约 46%）上方用 28–34 px 黑色粗体排套餐配件标题「{acc_title}」，其下端正展示{acc_visual}；\n"
                    f"下部区域用带细深灰圆角边框（圆角 10 px）的白色卡片网格，整齐排列标准包装内的其余配件（{acc_items_summary}），"
                    f"每张小卡片内的配件图案与卡片底部 14–16 px 深灰英文名称严格一一对应（不展示外包装彩盒）。"
                )
            else:
                out_filename = f"{sku_code}.jpg"
                if is_primary_color:
                    ref_imgs = list(dict.fromkeys([r for r in [front_img, use_pkg] if r]))
                    src_desc = f"以输入的{color_cn} {main_title} 主机白底图与标准配件合照为合成素材"
                else:
                    ref_imgs = list(dict.fromkeys([r for r in [front_img, use_pkg] if r]))
                    src_desc = f"以输入的图1（{color_cn} {main_title} 白底图）和图2（标准配件合照）为合成素材，并将主机替换为图1的{color_cn}款式"

                layout_instruction = (
                    f"横幅下方主画面：\n"
                    f"上部居中醒目放置{color_cn} {main_title} {prof['noun_cn']}主体（实际宽约 520–580 px，保持{prof['appearance_lock']}清晰）；\n"
                    f"下部区域用带细深灰圆角边框（圆角 10 px）的白色卡片网格，整齐排列标准套餐内的全部配件（{acc_items_summary}），"
                    f"每张小卡片底部居中用 14–16 px 深灰字体标注对应英文名称（不展示外包装彩盒）。"
                )

            jobs.append({
                "filename": out_filename,
                "category": "04_属性图_SKU组合",
                "sku_code": f"{sku_code}_{acc_sku}" if acc_sku else sku_code,
                "target_width": 1000,
                "target_height": 1000,
                "resize_mode": "exact_resize",
                "reference_images": ref_imgs,
                "prompt": (
                    f"制作一张 1000 × 1000 px、1:1 方版的电商 SKU 属性规格图。{src_desc}，保持所有商品和配件的外观、细节和可辨识度。\n\n"
                    f"画布背景为干净的纯白色（#FFFFFF）。顶部通栏高约 82 px，左 76% 为深石墨黑底色（#262626）居中偏左排 42–50 px 白色粗体「{main_title}」；"
                    f"右 24% 为亮红色斜切色块（#FF0000）居中排 38–46 px 白色粗体版本标识「{badge}」。\n\n"
                    f"{layout_instruction}\n\n"
                    f"整体排版紧凑清晰，英文拼写准确，{forbid}"
                ),
            })
    return jobs


def build_scene_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    05. 【必选】场景图（装机/真实使用图，1~2 张，1000 × 1000 px，1:1 方版）
    """
    jobs = []
    scenes = task["reference_assets"].get("scene_configs", [])
    for idx, sc in enumerate(scenes, start=1):
        jobs.append({
            "filename": sc.get("output_filename", f"详情图_场景({idx}).jpg"),
            "category": "05_场景图_真实使用",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": sc["reference_images"],
            "prompt": sc["prompt"],
        })
    return jobs


def build_selling_point_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    06. 【必选】卖点图（核心功能与参数拆解，3~6 张，1000 × 1000 px，1:1 方版）
    """
    forbid = _blacklist_clause(task)
    jobs = []
    sp_configs = task["reference_assets"].get("selling_point_configs", [])
    for sp in sp_configs:
        jobs.append({
            "filename": sp["output_filename"],
            "category": "06_卖点图_功能与参数",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": sp.get("reference_images", []),
            "prompt": sp["prompt"],
        })

    specs = task["copywriting_en"].get("specifications", [])
    if specs:
        rows_lines = "\n".join([f"{r['key']} : {r['value']}" for r in specs])
        jobs.append({
            "filename": task["reference_assets"].get("spec_output_filename", "详情图_参数表.jpg"),
            "category": "06_卖点图_功能与参数",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": [],
            "prompt": (
                f"制作一张 1000 × 1000 px、1:1 方版的英文产品规格参数表图。背景为干净的纯白色（#FFFFFF）。\n\n"
                f"顶部居中排主标题「SPECIFICATIONS」，用 48–54 px 蓝灰色（#7A8299）无衬线粗体。\n\n"
                f"标题下方居中排版一张双列规格表（表宽约 880 px），每行之间用 1 px 浅灰水平细线分隔。"
                f"左列占宽 38% 用 18–20 px 纯黑粗体左对齐，右列占宽 62% 用 18–20 px 深灰常规体左对齐，按顺序原样逐行排版以下参数：\n"
                f"{rows_lines}\n\n"
                f"所有英文与数字原样精准排版，字迹清晰锐利，{forbid}"
            ),
        })
    return jobs


def build_ad_750x1000_prompt(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    07. 【必选】750×1000 广告图（全 SKU 白底合集，1 张，750 × 1000 px，3:4 竖版）
    """
    variants = task.get("color_variants") or []
    prof = _cat_profile(task)
    prod_name = _product_short_name(task)

    valid_pairs = []
    for c in variants:
        f_img = _hero_view_img(task, c.get("views") or {})
        if f_img:
            valid_pairs.append((c.get("color_name_cn", "标准色"), f_img, c.get("views") or {}))
    if not valid_pairs:
        return []

    if len(valid_pairs) == 1:
        c_name, f_img, views = valid_pairs[0]
        # 单色商品：优先把主力视图与侧面/全套组合图在 3:4 竖版中上下饱满呈现
        second_img = next(
            (views.get(k) for k in ("left_png", "right_png", "front_png", "angled_png") if views.get(k) and views.get(k) != f_img),
            "",
        )
        if second_img and second_img != f_img:
            ref_imgs = [f_img, second_img]
            body_desc = (
                f"以输入的两张{c_name} {prod_name} 白底图为唯一商品素材，抠取原物并合成在纯白色背景（#FFFFFF）上。\n\n"
                f"画面分为上下两半：上半部居中放置图1主视角 {prof['noun_cn']}（实际宽约 620–660 px），"
                f"下半部居中放置图2侧面/全套主力视图（实际宽约 620–660 px），完整显示机身与细节，"
                f"严格保持原图角度与{prof['appearance_lock']}清晰。"
            )
        else:
            ref_imgs = [f_img]
            body_desc = (
                f"以输入的{c_name} {prod_name} 白底图为唯一商品素材，抠取原物并居中饱满放置在纯白色背景（#FFFFFF）中央，"
                f"实际宽约 640–680 px，严格保持原图角度与{prof['appearance_lock']}清晰。"
            )
    else:
        ref_imgs = [p[1] for p in valid_pairs]
        color_list_cn = "、".join(f"{p[0]}款" for p in valid_pairs)
        body_desc = (
            f"以输入的 {len(valid_pairs)} 张全色系正面白底图（{color_list_cn}）为唯一商品素材，抠取原物并合成在纯白色背景（#FFFFFF）上。\n\n"
            f"画面按竖版 3:4 比例上下均匀排布全部 {len(valid_pairs)} 款配色的 {prod_name} {prof['noun_cn']}，"
            f"每款主体大小协调一致（实际宽约 600–650 px），严格保持各配色原图的角度与{prof['appearance_lock']}清晰。"
        )

    return [{
        "filename": "750X1000.jpg",
        "category": "07_广告图_750x1000",
        "target_width": 750,
        "target_height": 1000,
        "resize_mode": "exact_resize",
        "reference_images": ref_imgs,
        "prompt": (
            f"制作一张 750 × 1000 px、3:4 竖版的纯白底商品合集广告图。{body_desc}\n\n"
            f"全图严禁添加任何文字、LOGO、边框或阴影杂物。"
        ),
    }]


def build_optional_structure_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    08. 【可选】结构图（部件功能引线图，0~2 张，1000 × 1000 px，1:1 方版）
    """
    if not task.get("generation_flags", {}).get("generate_structure_diagram", True):
        return []
    struct_configs = task["reference_assets"].get("structure_configs", [])
    jobs = []
    for st in struct_configs:
        jobs.append({
            "filename": st["output_filename"],
            "category": "08_可选_结构图",
            "target_width": 1000,
            "target_height": 1000,
            "resize_mode": "exact_resize",
            "reference_images": st["reference_images"],
            "prompt": st["prompt"],
        })
    return jobs


def build_optional_handheld_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    09. 【可选】实拍对比图（手持/体积参照图，0~1 张，1000 × 1000 px，1:1 方版）
    """
    if not task.get("generation_flags", {}).get("generate_handheld_comparison", True):
        return []
    hh = task["reference_assets"].get("handheld_config")
    if not hh:
        return []
    return [{
        "filename": hh["output_filename"],
        "category": "09_可选_实拍对比手持图",
        "target_width": 1000,
        "target_height": 1000,
        "resize_mode": "exact_resize",
        "reference_images": hh["reference_images"],
        "prompt": hh["prompt"],
    }]


def build_russian_suite_prompts(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    10 & 11. 【按需开启】俄语区专属套图（900 × 1200 px，3:4 竖版）
    完全由 task_config.copywriting_ru 与 copywriting_en 动态生成，不硬编码特定型号或配件！
    """
    if not task.get("generation_flags", {}).get("generate_russian_suite", True):
        return []

    jobs = []
    meta = task["product_meta"]
    prof = _cat_profile(task)
    forbid_ru = _blacklist_clause(task, allow_russian=True)
    show_logo = meta.get("show_brand_logo_on_main", True)
    brand = (meta.get("brand_name") or "").upper() if show_logo else ""
    brand_line = f"顶部通栏居中排「{brand}」，字号约 28 px。" if brand else ""

    copy_en = task.get("copywriting_en") or {}
    ru = task.get("copywriting_ru") or {}
    prod_name = _product_short_name(task)
    ru_title = ru.get("title") or prod_name
    ru_lines = "\n".join(ru.get("subtitle_lines") or [
        "Высокое качество сборки и надёжность",
        "Точное управление и стабильная работа",
        "Полная комплектация из коробки",
    ])
    sp_fallback = list(copy_en.get("core_selling_points") or ["High Quality", "Brushless", "2.4GHz"])

    colors_map = {c["color_id"]: c for c in (task.get("color_variants") or [])}
    primary_cid = _primary_pkg_color_id(task)

    # (1) 俄语主图 01~03：每个基础主 SKU 生成 3 张 (900 × 1200 px)
    for sku in task.get("base_skus") or []:
        sku_code = sku["sku_code"]
        badge = sku.get("version_badge") or ""
        c_obj = colors_map.get(sku["color_id"])
        if not c_obj:
            continue
        c_cn = c_obj["color_name_cn"]
        views_c = c_obj.get("views") or {}
        front_img = _hero_view_img(task, views_c)
        if not front_img:
            continue
        angled_img = next(
            (views_c.get(k) for k in ("angled_png", "left_png", "right_png", "front_png") if views_c.get(k) and views_c.get(k) != front_img),
            views_c.get("angled_png") or front_img,
        )

        def _fmt_badges(custom_key: str, default_items: List[str], include_badge: bool = True) -> List[str]:
            raw_list = list(ru.get(custom_key) or default_items)
            out = [str(x).replace("{badge}", badge).strip() for x in raw_list if str(x).strip()]
            if include_badge and badge and badge not in out and not ru.get(custom_key):
                out.append(badge)
            return out

        badges_1 = _fmt_badges("badges_1", sp_fallback[:3], include_badge=True)
        badges_2 = _fmt_badges("badges_2", sp_fallback[:4], include_badge=True)
        badges_3 = _fmt_badges("badges_3", sp_fallback[:3], include_badge=False)

        # 俄文 1：左 72% 主图 + 右 28% 纵向卖点分隔线版式
        jobs.append({
            "filename": f"{sku_code}俄文1.jpg",
            "category": "10_俄语主图_900x1200",
            "target_width": 900,
            "target_height": 1200,
            "resize_mode": "exact_resize",
            "reference_images": [front_img],
            "prompt": (
                f"制作一张 900 × 1200 px、3:4 竖版的 Ozon 商品主图。以输入的{c_cn} {prod_name} 主视角白底图为唯一商品素材，"
                f"抠取原物并合成，保持原图角度与{prof['appearance_lock']}清晰不变形。\n\n"
                f"背景用深石墨灰到深蓝灰的哑光渐变。商品背后加柔和的冷蓝光晕，右栏用均匀的深色，底部加轻柔接触阴影。\n\n"
                f"{brand_line}主标题「{ru_title}」用 64–74 px 白色粗体。其下用 22–26 px 白色字居中排版，按三行显示：\n"
                f"{ru_lines}\n\n"
                f"标题区下方划分为左 72% 和右 28%。左侧商品实际宽约 580–620 px，完整展示主体，垂直位置与右栏视觉居中。"
                f"右侧纵向等距排列以下卖点，使用约 24–28 px 白色半粗体和细浅蓝分隔线：\n"
                f"{chr(10).join(badges_1)}\n\n"
                f"{forbid_ru}底部延续背景，留出净空。"
            ),
        })

        # 俄文 2：斜侧视图 + 右侧胶囊卖点卡片版式
        jobs.append({
            "filename": f"{sku_code}俄文2.jpg",
            "category": "10_俄语主图_900x1200",
            "target_width": 900,
            "target_height": 1200,
            "resize_mode": "exact_resize",
            "reference_images": [angled_img],
            "prompt": (
                f"制作一张 900 × 1200 px、3:4 竖版的 Ozon 商品主图。以输入的{c_cn} {prod_name} 斜侧面白底图为唯一商品素材，"
                f"抠取原物并合成，保持原图{prof['side_lock']}清晰不变形。\n\n"
                f"背景用深海军蓝到暗石板蓝的科技感哑光渐变，商品后方加柔和的冰蓝背光光晕，底部加自然接触阴影。\n\n"
                f"{brand_line}主标题「{ru_title}」用 64–74 px 白色粗体。其下用 22–26 px 白色字居中排版，按三行显示：\n"
                f"{ru_lines}\n\n"
                f"标题区下方划分为左 70% 和右 30%。左侧放置斜侧面商品主体，实际宽约 560–600 px，完整展示主体结构。"
                f"右侧纵向等距排列圆角胶囊卖点框（深蓝半透明底配浅蓝细边框，22–26 px 白色半粗体）：\n"
                f"{chr(10).join(badges_2)}\n\n"
                f"{forbid_ru}底部延续背景，留出净空。"
            ),
        })

        # 俄文 3：居中大图主体 + 底部横向卖点铭牌版式
        jobs.append({
            "filename": f"{sku_code}俄文3.jpg",
            "category": "10_俄语主图_900x1200",
            "target_width": 900,
            "target_height": 1200,
            "resize_mode": "exact_resize",
            "reference_images": [front_img],
            "prompt": (
                f"制作一张 900 × 1200 px、3:4 竖版的 Ozon 商品主图。以输入的{c_cn} {prod_name} 主视角白底图为唯一商品素材，"
                f"抠取原物并合成，保持原图角度与{prof['appearance_lock']}清晰不变形。\n\n"
                f"背景用深炭灰到午夜蓝的极简渐变，商品背后有柔和的科技蓝环形光晕，底部加轻柔接触阴影。\n\n"
                f"{brand_line}主标题「{ru_title}」用 64–74 px 白色粗体。其下用 22–26 px 白色字居中排版，按三行显示：\n"
                f"{ru_lines}\n\n"
                f"画面中部居中放置商品主体，实际宽约 640–680 px，完整展示所有外观细节。"
                f"商品下方横向等距并排醒目的深蓝底浅蓝边圆角卖点铭牌（字号 24–28 px 白色粗体）：\n"
                f"{'   |   '.join(badges_3[:4])}\n\n"
                f"{forbid_ru}底部延续背景，留出净空。"
            ),
        })

    # (2) 俄语包裹图（俄文4）：动态按 copywriting_ru.package_includes 排版
    rep_skus_by_color = {}
    for sku in task.get("base_skus") or []:
        rep_skus_by_color[sku["color_id"]] = sku["sku_code"]

    pkg_ref = (task.get("reference_assets") or {}).get("clean_package_photo_ref") or ""
    ru_pkg_title = ru.get("package_title") or f"Комплектация {meta.get('spu_code', '')}".strip()
    base_ru_pkg_items = list(ru.get("package_includes") or [])
    if not base_ru_pkg_items:
        base_ru_pkg_items = [f"{x['qty']} × {x['name_en']}" for x in (copy_en.get("package_includes") or [])]

    for color_id, rep_sku in rep_skus_by_color.items():
        c_obj = colors_map.get(color_id)
        if not c_obj:
            continue
        c_cn = c_obj["color_name_cn"]
        front_img = _hero_view_img(task, c_obj.get("views") or {})
        use_pkg = pkg_ref or front_img
        if not use_pkg:
            continue
        is_primary_color = (color_id == primary_cid) or (not front_img) or (front_img == use_pkg)

        for pkg in task.get("bundled_packages") or []:
            acc_sku = pkg.get("accessory_sku")
            append_ru = pkg.get("append_ru_item")
            cur_items = list(base_ru_pkg_items)
            if append_ru:
                cur_items.append(append_ru)
            left_col, right_col = _split_two_columns(cur_items)

            if not acc_sku:
                out_fname = f"{rep_sku}俄文4.jpg"
                refs = [use_pkg] if is_primary_color else list(dict.fromkeys([front_img, use_pkg]))
                color_replace_note = (
                    f"画面上部使用上传的{c_cn} {prod_name} 标准配件白底合照作为合成素材"
                    if is_primary_color
                    else f"画面上部使用上传的图2标准配件白底合照作为合成素材，并将主机替换为图1的{c_cn} {prod_name}"
                )
                pkg_summary_note = f"这张图对应{c_cn} {prod_name} 标准配置套装，移除原图多余旧标注文字，所有配件以输入合照与清单为准。"
            else:
                out_fname = f"{rep_sku}_{acc_sku}俄文4.jpg"
                acc_img = pkg.get("accessory_cutout_png")
                acc_title = pkg.get("accessory_title_en") or acc_sku
                refs = list(dict.fromkeys([r for r in ([use_pkg, acc_img] if is_primary_color else [front_img, use_pkg, acc_img]) if r]))
                color_replace_note = (
                    f"画面上部使用上传的{c_cn} {prod_name} 标准配件白底合照与搭配配件图（{acc_title}）作为合成素材"
                    if is_primary_color
                    else f"画面上部使用上传的标准配件白底合照、{c_cn} {prod_name} 主图与搭配配件图（{acc_title}）作为合成素材（主机使用{c_cn}款）"
                )
                pkg_summary_note = f"这张图对应{c_cn} {prod_name} 加配套餐（{acc_title}），在配件区醒目位置正向清晰展示全部配套配件与对应数量（保持表面文字正向清晰）。"

            jobs.append({
                "filename": out_fname,
                "category": "11_俄语包裹图_900x1200",
                "target_width": 900,
                "target_height": 1200,
                "resize_mode": "exact_resize",
                "reference_images": refs,
                "prompt": (
                    f"制作一张 900 × 1200 px、3:4 竖版的 {prod_name} 俄语包裹清单图。背景用干净的暖白或浅灰，标题「{ru_pkg_title}」顶部居中，用 52–60 px 深石墨灰粗体。\n\n"
                    f"{color_replace_note}，保持原有商品主机及全部配件的外观、比例和可辨识度，沿用真实配件与数量，保持小配件边缘清晰锐利。\n\n"
                    f"配件区下方留出足够位置，用左右两栏排俄语清单。正文字号 18–22 px，长条目自然换行：\n\n"
                    f"左栏：\n{left_col}\n\n"
                    f"右栏：\n{right_col}\n\n"
                    f"{pkg_summary_note}{forbid_ru}"
                ),
            })

    return jobs


def compile_all_jobs(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """汇总编译单个产品的全部标准生图任务清单"""
    all_jobs = []
    all_jobs.extend(build_main_6_prompts(task))
    all_jobs.extend(build_sub_white_prompts(task))
    all_jobs.extend(build_package_en_prompt(task))
    all_jobs.extend(build_sku_attribute_prompts(task))
    all_jobs.extend(build_scene_prompts(task))
    all_jobs.extend(build_selling_point_prompts(task))
    all_jobs.extend(build_ad_750x1000_prompt(task))
    all_jobs.extend(build_optional_structure_prompts(task))
    all_jobs.extend(build_optional_handheld_prompts(task))
    all_jobs.extend(build_russian_suite_prompts(task))
    return all_jobs
