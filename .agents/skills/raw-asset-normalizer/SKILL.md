---
name: raw-asset-normalizer
description: >-
  将供应商提供的原始杂乱素材文件夹及/或开发部手动整理的资料（需求表 .xls/.xlsx、报价单、1.txt、多层级原厂图包等）
  自动化清洗、视觉审图分类、参数冲突消歧，转换为 AutoShot 生图工作台可直接无错导入的标准素材目录与对应的
  auto_image_gen/tasks/{spu}_task.json 配置文件。
  当用户提到“整理原始素材”、“处理供应商素材包”、“把文件夹转成工作台可识别格式”、“导入素材解析出错”或给出一个原始商品文件夹路径准备导入生图台时，激活本技能。
---

# 原始商品素材标准化处理（AutoShot 工作台专用）

本技能通过 **「确定性脚本探测 + 多模态视觉审图与文案消歧 + 标准化落盘 + 工作台真机校验」** 四步闭环，把任意杂乱的供应商原包和开发部零散资料，加工成 AutoShot 生图台一键导入全绿、零报错、槽位与属性 100% 精准的标准包。

> **铁律**：绝不修改、重命名或删除用户的原始素材目录；所有标准化产出均新建到工作区（`E:/Projects/Raw_Image_Workspace/{SPU} {商品简称}`）和 `auto_image_gen/tasks/{spu_lower}_task.json`。

---

## 核心工作流（4 步闭环）

### 第 1 步：探测原始目录并生成视觉拼图
运行 [inspect_raw_folder.py](./scripts/inspect_raw_folder.py) 全面解析原始文件夹：

```powershell
python "e:\Projects\Raw_Image_Workspace\.agents\skills\raw-asset-normalizer\scripts\inspect_raw_folder.py" "<原始素材目录路径>" --out-dir "<scratch临时目录>"
```

脚本会产出：
1. `raw_inventory.json`：完整文件清单、每张图的宽高/体积/白底纯度，以及自动解析好的 `.xls`（Excel/WPS COM 精准读表）、`.xlsx`、`.txt` 全文内容。
2. 最多 4 张带编号的缩略图拼图（Contact Sheets）：`contact_white_bg.jpg`、`contact_en_main_sku.jpg`、`contact_en_detail.jpg`、`contact_other.jpg`。

---

### 第 2 步：人工级视觉审图 + 多源资料冲突消歧
读取 `raw_inventory.json` 并用 `read_file` 查看生成的 Contact Sheet 拼图（必要时看关键原图），完成两项核心判断：

#### A. 多源资料优先级与冲突消歧（严格遵循以下权威顺位）
1. **最高优先级：开发部手工整理的《图片需求.xls/.xlsx》与开发部备注**（例如文件夹名括注、需求表中的 `LOGO:`、`置入图片文字`、`改为1/27`、`做双电和三电，单电池SKU为：RC3670-DC`、`俄语图` 页签文案）。
2. **次高优先级：开发部整理的英文文案 `1.txt` / 刊登文本**（注意修复因 GBK/UTF-8 转换造成的乱码问号，如 `Bell?206` → `Bell-206`、`11?13` → `11-13`、`2511?1200KV` → `2511-1200KV`）。
3. **参考补充：供应商报价单（`报价资料.xls/.xlsx`）与原厂英文详情图**。
4. **冲突词拉黑**：凡是供应商原图或报价单中与开发部要求冲突的错误词/旧型号/高配词（例如原厂图误写 `32:1`、`1/32`，而需求表要求 `1/27`；或报价单混入高配 `MAX`、`8通道` 等冲突描述），全部写入 `product_meta.blacklisted_terms`，防止生图模型照抄错字！

#### B. 视觉审图与 7 槽位选图规则（严格遵循「宁缺毋滥，绝不张冠李戴」）
逐颜色挑选干净、清晰、无中文字/促销水印的白底图绑定至 7 个标准槽位（详见 [workbench_contract.md](./references/workbench_contract.md)）。
**核心铁律：原厂未提供某个真实视角或局部特写时，该槽位必须留空（不填入 `slots`），绝不允许拿斜侧图冒充背面、拿整机图冒充局部特写、或拿主机+遥控器合照冒充补充特写！**
* `front_png`（正面）：**必须是真正的正面/正机头视图**（如遥控器正面、直升机正前方机头视角）。若该品类（如直升机/车模/飞机）正前方视图过窄、不适合做电商主图首图，请在 `task_config.reference_assets.hero_main_view` 中设为 `"angled_png"`（让主图 1~5 用 45° 斜侧展示全貌，白底副图正面仍严格使用 `front_png`）。
* `back_png`（背面）：**必须是真正的背面/尾部视图**；若原包未拍背面图，**直接留空**，在最终报告中提示运营“原包缺背面白底图，可按需补拍上传”。
* `angled_png`（45°斜侧）：清晰静态的 45° 立体斜侧白底图（优先选静态展桨/静态清晰图而非动态模糊图）。
* `left_png`（左侧面）：正左侧面全貌白底图（机头/主体朝左，完整展示侧面结构与涂装）。
* `right_png`（右侧面）：正右侧面或右侧主体全貌白底图（机头/主体朝右，与左侧面方向相反）。
* `detail_2_png`（细节特写）：**必须是局部微距/关键部件特写白底图**（如摇杆特写、旋翼头特写、电池仓特写）；若原包无干净白底局部特写，**直接留空**。
* `detail_1_png`（补充特写，可选）：仅当存在第二张独立的局部微距特写白底图时才填入，**严禁把整机图、合照或遥控器图塞进此槽位**。
* `package_png`（配件合照）：全套包装内配件的白底全家福合照（优先无字图；若供应商仅有带英文标注的全家福如 `sku (1).jpg`，可作 `package_png` 并在提示词中指令移除旧字重排）。
* **其余非槽位白底图与原厂英文卖点/详情参考图**：多余角度的白底图（如动态旋翼、仰视图、主机+遥控器合照）及 3~6 张最有代表性的英文卖点图、场景图、结构图，统一归入 `raw_reference_copies`（脚本会自动存入隐藏目录 `.raw_refs/`，供 `task_config` 精准引用且绝不污染颜色槽位）。
* **共享盘搭配配件（如双电/三电电池）**：若需求表指定了捆绑配件 SKU（如 `RC3670-DC`），先检查 `auto_image_gen/assets/shared_skus/` 是否已有该图；若暂无，从供应商白底全家福或单电池卖点图中指定 `crop_box_ratio` 裁剪出端正白底单图存入 `shared_skus/{SKU}.png`（若无法从现有图干净裁剪，则在结果报告中明确提醒运营补图）。

---

### 第 3 步：编写 `normalize_plan.json` 并一键生成标准包
参照 [task_json_schema.md](./references/task_json_schema.md) 将第 2 步的决策写成 `normalize_plan.json`，重点核对以下硬约束（详见 [workbench_contract.md](./references/workbench_contract.md)）：
1. **SPU 目录名**：必须包含提取出的 SPU 编号（如 `RC4646 F08S直升机`）。
2. **`color_id` 强一致**：颜色子文件夹名必须能让 `scanner.py` 推导出与 `base_skus[].color_id` **完全一致**的 `color_id`！
3. **白底图尺寸达标**：脚本会自动把 `< 1000px` 或 `< 45KB` 的白底图高质量缩放/标准化至 `>= 1000×1000` 且 `>= 50KB`，确保工作台 6 项预检全绿。
4. **SKU 与套餐精确建模**：完整填入 `base_skus`、`bundled_packages`、`copywriting_en`、`copywriting_ru` 以及定制化的 `scene_configs`、`selling_point_configs`、`structure_configs`、`handheld_config`。

运行 [build_normalized_pack.py](./scripts/build_normalized_pack.py)：

```powershell
python "e:\Projects\Raw_Image_Workspace\.agents\skills\raw-asset-normalizer\scripts\build_normalized_pack.py" "<scratch临时目录>/normalize_plan.json"
```

---

### 第 4 步：调用工作台真机引擎闭环校验
运行 [verify_with_scanner.py](./scripts/verify_with_scanner.py)，直接调用工作台真实的 `web.scanner.scan_product_folder()` 和 `prompts.compile_all_jobs()` 验证：

```powershell
python "e:\Projects\Raw_Image_Workspace\.agents\skills\raw-asset-normalizer\scripts\verify_with_scanner.py" "<标准化输出目录路径>"
```

**验收通过标准（必须全部满足）**：
- 退出码为 `0`（`[PASS]`）；
- 预检 6 项无阻断项，且分辨率预检为 `OK`（全部 ≥ 1000×1000）；
- 每个 `base_sku` 的 `color_id` 全部命中扫描到的颜色组（无 `MISMATCH`）；
- 编译出的所有生图任务的参考图路径 100% 存在；
- 向用户输出简明整理报告：标准化目录路径、已解决的参数冲突、槽位选图清单、套餐与 SKU 数量、以及仍需运营复核的细节（如外置电池图是否建议实拍替换等）。
