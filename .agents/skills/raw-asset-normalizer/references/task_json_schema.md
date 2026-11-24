# `normalize_plan.json` 与 `task_config` 结构规范

`build_normalized_pack.py` 接收一个 `normalize_plan.json` 文件，输出标准化素材目录和 `auto_image_gen/tasks/{spu_lower}_task.json`。

## 1. 路径引用占位符（在 `task_config` 中可用）
为了避免手工写错目标路径，`task_config` 中任意字符串字段都可以使用以下占位符，脚本会自动替换为落盘后的真实绝对路径：
- `@slot:<color_id>:<role>`：引用某颜色的标准化槽位图（如 `@slot:RED:front_png`、`@slot:RED:left_png`）
- `@pkg`：引用标准化后的配件合照（`7_配件合照_package.jpg`）
- `@ref:<alias>`：引用归档到 `.raw_refs/` 的原厂参考图（对应 `raw_reference_copies` 的 key）
- `@shared:<SKU>`：引用 `auto_image_gen/assets/shared_skus/{SKU}.png`

## 2. `normalize_plan.json` 完整模板

```json
{
  "workspace_dir": "E:/Projects/Raw_Image_Workspace",
  "spu_code": "RC4646",
  "output_folder_name": "RC4646 F08S直升机",
  "clean_target_before_build": true,
  "copy_documents": [
    "E:/DownLoad/.../RC4646 图片需求.xls",
    "E:/DownLoad/.../F08S直升机 报价资料 -.xls"
  ],
  "clean_notes_txt": "UTF-8 清洗后的完整英文标题、卖点、规格参数、配件清单与开发部要求摘要...",
  "colors": [
    {
      "color_id": "RED",
      "folder_name": "红白涂装",
      "color_name_cn": "红白消防涂装",
      "color_name_en": "Red & White Fire Rescue",
      "swatch": "#DC2626",
      "slots": {
        "front_png": "E:/.../白底/画板 2.jpg",
        "back_png": "E:/.../白底/画板 4.jpg",
        "angled_png": "E:/.../白底/画板 1.jpg",
        "left_png": "E:/.../白底/画板 8.jpg",
        "right_png": "E:/.../白底/画板 5.jpg",
        "detail_2_png": "E:/.../白底/画板 7.jpg",
        "package_png": "E:/.../英文主图sku/sku (1).jpg"
      }
    }
  ],
  "raw_reference_copies": {
    "sku_heli_tx": "E:/.../英文主图sku/sku (2).jpg",
    "sp_battery": "E:/.../英文主图sku/主图 (6).jpg",
    "sp_inverted": "E:/.../英文主图sku/主图 (7).jpg",
    "sp_cnc_motor": "E:/.../英文主图sku/主图 (8).jpg"
  },
  "shared_skus_prepare": [
    {
      "sku": "RC3670-DC",
      "source_image": "E:/.../英文主图sku/sku (1).jpg",
      "crop_box_ratio": [0.76, 0.72, 0.96, 0.89],
      "overwrite": false
    }
  ],
  "task_config": {
    "task_id": "TASK_RC4646_F08S",
    "passthrough_clean_white_sub_images": true,
    "product_meta": {
      "spu_code": "RC4646",
      "display_name_cn": "F08S Bell-206 GPS 无副翼遥控直升机",
      "brand_name": "YXZNRC",
      "category": "RC_Helicopter",
      "category_cn": "航模遥控直升机",
      "show_brand_logo_on_main": true,
      "blacklisted_terms": ["32:1", "1/32", "8通道", "8CH"]
    },
    "generation_flags": {
      "is_pre_listing_mode": false,
      "generate_structure_diagram": true,
      "generate_handheld_comparison": true,
      "generate_russian_suite": true
    },
    "color_variants": [],
    "base_skus": [
      { "sku_code": "RC4646A", "color_id": "RED", "version_badge": "RTF 1B" }
    ],
    "bundled_packages": [
      {
        "package_id": "STD_1BAT",
        "accessory_sku": null,
        "accessory_title_en": null,
        "accessory_cutout_png": null,
        "append_ru_item": null
      },
      {
        "package_id": "BAT_2X",
        "accessory_sku": "RC3670-DC",
        "accessory_title_en": "2× 7.4V 1200mAh Smart Li-Po Battery",
        "accessory_cutout_png": "@shared:RC3670-DC",
        "append_ru_item": "2 × Умный аккумулятор 7.4V 1200mAh"
      }
    ],
    "copywriting_en": {
      "main_title": "F08S Bell-206 Helicopter",
      "candidate_titles": ["F08S Bell-206 Helicopter", "YXZNRC F08S 6CH GPS Helicopter"],
      "core_selling_points": ["1/27 Scale", "GPS Positioning", "Brushless Motor", "6CH", "13min Flight Time"],
      "package_includes": [
        { "qty": 1, "name_en": "F08S RC Helicopter" }
      ],
      "specifications": [
        { "key": "Model", "value": "F08S (Bell-206 RC Helicopter)" },
        { "key": "Operating Voltage", "value": "7.4V 1200mAh 25C Li-Po" },
        { "key": "Weight", "value": "228g (Aircraft)" }
      ]
    },
    "copywriting_ru": {
      "title": "F08S Bell-206 Вертолет",
      "subtitle_lines": [
        "Масштаб 1/27 · GPS и оптическое позиционирование",
        "Бесколлекторные двигатели · 6 каналов",
        "Время полёта до 13 минут"
      ],
      "badges_1": ["GPS", "6CH", "1/27", "13min"],
      "badges_2": ["Бесколлекторный", "6-осевой гироскоп", "6CH", "GPS", "1/27"],
      "badges_3": ["GPS", "1/27", "6-осевой гироскоп"],
      "package_title": "Комплектация F08S",
      "package_includes": [
        "1 × Вертолёт F08S",
        "1 × Пульт ДУ 6CH"
      ]
    },
    "reference_assets": {
      "clean_package_photo_ref": "@pkg",
      "spec_output_filename": "详情图(8)_参数表.jpg",
      "scene_configs": [],
      "selling_point_configs": [],
      "structure_configs": [],
      "handheld_config": {}
    }
  }
}
```

## 3. 注意事项
- `specifications` 中尽量包含 `Operating Voltage` 和 `Weight` 两项标准 key（工作台 `_extract_confirm_fields` 会优先抓这两项展示为第 2 步的「待人工确认重点参数」）。
- 若需求表要求**双电和三电**且单电池 SKU 为 `RC3670-DC`，可在 `bundled_packages` 中配置：
  - 标准单电版：`accessory_sku: null` → 输出 `RC4646A.jpg`
  - 双电版（含 1 块加购电池）：`accessory_sku: "RC3670-DC"` → 输出 `RC4646A_RC3670-DC.jpg`
  - 三电版（含 2 块加购电池）：`accessory_sku: "RC3670-DC_2"`（或按公司通途 SKU 命名习惯，如 `RC3670-DCx2`，待运营核对确认）
- 在 `scene_configs` / `selling_point_configs` / `structure_configs` / `handheld_config` 中撰写中文像素级提示词时，务必贴合当前实际商品品类（如遥控直升机、车模、电调、遥控器等），严禁照搬其他商品（如 GX10）的部件词！
