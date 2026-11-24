# AutoShot 生图工作台导入契约与避坑清单

本文件总结 `auto_image_gen/web/scanner.py` 与 `auto_image_gen/prompts/templates.py` 的真实代码约束，确保整理后的素材目录 100% 被工作台准确解析。

---

## 1. SPU 编号识别规则
- 代码正则：`re.search(r"(RC\d{3,6}|[A-Z]{2,4}\d{3,6})", folder_name, re.I)`
- **要求**：标准化输出目录名必须以标准 SPU 开头（例如 `RC4646 F08S直升机`）。
- 注意：不要把带颜色/版本后缀的 SKU 写成目录前缀导致误判（例如 `RC4646A` 正则只匹配数字部分，会提取出 `RC4646`，这没问题；但统一命名为 `RC4646 F08S直升机` 最清晰）。

## 2. 颜色目录名与 `color_id` 强绑定规则（最关键避坑点！）
`scanner.py` 扫描完颜色子目录后，会用子目录名重新覆盖 `task_config["color_variants"]` 的 `color_id`！
如果 `task_config["base_skus"][].color_id` 与这里推导出的 `color_id` 不一致，**属性图与俄语主图将全部丢失（编译为 0 张）**！

`scanner.py` 的 `COLOR_HINTS` 顺序匹配表（按目录名小写命中第一条）：

| 目录名包含关键词（任一） | 推导出的 `color_id` | 默认中文名 | 默认英文名 |
| :--- | :--- | :--- | :--- |
| `灰`、`银`、`grey`、`gray`、`silver`、`gry` | `GRY` | 银灰色 | Silver Grey |
| `透明`、`透黑`、`炭`、`黑`、`charcoal`、`black`、`cha`、`transparent` | `CHA` | 半透明黑 | Transparent Charcoal Black |
| `红`、`red` | `RED` | 红色 | Red |
| `蓝`、`blue` | `BLU` | 蓝色 | Blue |
| `白`、`white` | `WHT` | 白色 | White |
| `橙`、`orange` | `ORG` | 橙色 | Orange |
| `绿`、`green` | `GRN` | 绿色 | Green |
| `金`、`gold` | `GLD` | 金色 | Gold |
| *(均未命中上述关键词)* | `C1`、`C2`…（按目录名排序序号） | 原目录名 | 原目录名 |

**实操规范**：
- 红白消防涂装等以红色为主体的配色，子目录命名为 `红白消防涂装` 或 `红色_红白涂装` → 命中 `红` → `color_id = "RED"`；
- 若某目录名同时含“红”和“白”，因为 `红` 排在 `白` 之前，会命中 `RED`；
- 编写 `normalize_plan.json` 时，务必使 `colors[].color_id`、`base_skus[].color_id` 与子目录名推导出的 `color_id` 完全一致，并用 `verify_with_scanner.py` 自动验证。

## 3. 图片硬性门槛与自动排除机制
- **入池硬阈值**：`width >= 900` 且 `height >= 900` 且 `file_size >= 45 KB`。
- **预检绿灯标准**：`width >= 1000` 且 `height >= 1000`。
- **禁止放入颜色目录的杂图**：带字主图、中文详情图、英文详情切片、超长拼图、海报、低清合集图。
- **隐藏目录隔离技巧**：`scanner.py` 会直接跳过以 `.` 开头的子目录。因此把需要被 `task.json` 的 `scene_configs` / `selling_point_configs` / `structure_configs` 引用的原厂英文卖点图、详情切片放到 `<标准目录>/.raw_refs/` 下，既保证引用路径自包含在标准化目录内，又绝不污染颜色槽位扫描。

## 4. 标准 7 槽位语义文件名
为避免数字启发式错槽，本技能统一按以下语义文件名落盘（100% 命中 `scanner.py` 语义规则第一优先级）：

| 槽位 Key | 标准化文件名 | 作用 |
| :--- | :--- | :--- |
| `front_png` | `1_正面_front.jpg` | 主图 1~5、白底副图 1、750×1000 广告图、俄语主图 1/3 |
| `back_png` | `2_背面_back.jpg` | 白底副图 4、背面结构图参考 |
| `angled_png` | `3_斜侧_angled.jpg` | FCFT 主图 6、俄语主图 2、场景图参考 |
| `left_png` | `4_左侧_left.jpg` | 白底副图 2 |
| `right_png` | `5_右侧_right.jpg` | 白底副图 3 |
| `detail_2_png` | `6_细节_detail.jpg` | 核心部件特写卖点图 |
| `package_png` | `7_配件合照_package.jpg` | 英文包裹图、SKU 属性图、俄语包裹图 |
| `detail_1_png`（可选） | `8_补充特写.jpg` | 额外特写参考 |

## 5. 文档与共享盘配件联动
- **根目录文档**：将开发部需求表（`.xls`/`.xlsx`）、报价单（`.xls`/`.xlsx`）及清洗后的 `{SPU}_清洗后产品资料.txt`（UTF-8）留在标准目录根部，供工作台首页展示文档解析卡片及检索品牌/共享盘配件 SKU。
- **共享盘配件图**：存放于 `auto_image_gen/assets/shared_skus/{SKU}.png`（全大写文件名，如 `RC3670-DC.png`）。只要根部文档文本中出现该 SKU 编号，且 `task.json` 的 `bundled_packages` 指向它，工作台即可自动挂载。
- **Task JSON 路径**：`auto_image_gen/tasks/{spu_code.lower()}_task.json`。`scanner.py` 扫描该 SPU 目录时会自动加载此文件作为权威参数与提示词配置。
