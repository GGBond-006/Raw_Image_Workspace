# -*- coding: utf-8 -*-
"""
原始商品素材目录探测脚本（raw-asset-normalizer Step 1）

功能：
1. 递归扫描任意供应商/开发部原始素材目录，统计全部文件（图片、Excel、TXT、视频等）；
2. 用 Pillow 分析每张图片的真实宽高、文件体积、宽高比，并计算边缘白底纯度（判断是否干净白底图）；
3. 自动解析目录内的 .xls（优先调用本地 Excel/WPS COM，失败回退二进制提取）、.xlsx（openpyxl）、.txt（自动探测编码）；
4. 为候选白底图与候选英文主图/详情图生成带编号的 Contact Sheet 拼图，方便 Agent 快速视觉审核与槽位分配；
5. 输出结构化 raw_inventory.json 供后续整理与 task.json 生成使用。
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DOC_EXTS = {".xls", ".xlsx", ".txt", ".csv", ".md"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}


def _norm(p: str) -> str:
    return p.replace("\\", "/")


def _estimate_white_border_ratio(im: Image.Image) -> float:
    """估算图片四周边框区域接近纯白（RGB均>=240）的像素占比，用于快速识别白底图。"""
    try:
        small = im.convert("RGB").resize((120, 120), Image.Resampling.BILINEAR)
        px = small.load()
        total = 0
        white = 0
        margin = 8
        for y in range(120):
            for x in range(120):
                if x < margin or x >= 120 - margin or y < margin or y >= 120 - margin:
                    r, g, b = px[x, y]
                    total += 1
                    if r >= 238 and g >= 238 and b >= 238:
                        white += 1
        return round(white / total, 3) if total else 0.0
    except Exception:
        return 0.0


def _read_txt_auto(path: str) -> Dict[str, Any]:
    with open(path, "rb") as f:
        raw = f.read()
    text = ""
    used_enc = "unknown"
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "utf-16"):
        try:
            text = raw.decode(enc)
            used_enc = enc
            break
        except Exception:
            continue
    if not text:
        text = raw.decode("utf-8", errors="ignore")
    # 检查是否存在常见的编码损坏问号（如 11?13, Bell?206）
    garbled_q_count = len(re.findall(r"[A-Za-z0-9]\?[A-Za-z0-9]", text))
    return {
        "encoding": used_enc,
        "garbled_question_marks": garbled_q_count,
        "text": text,
    }


def _read_xlsx(path: str) -> Dict[str, Any]:
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = {}
    for ws in wb.worksheets:
        rows = []
        for r_idx, row in enumerate(ws.iter_rows(max_row=200, max_col=25, values_only=True), start=1):
            cells = []
            for c_idx, v in enumerate(row, start=1):
                if v is not None and str(v).strip():
                    s = re.sub(r"\s+", " ", str(v).strip())
                    cells.append(f"[{c_idx}]{s}")
            if cells:
                rows.append(f"R{r_idx}: " + " | ".join(cells))
        if rows:
            sheets[ws.title] = rows
    wb.close()
    return {"method": "openpyxl", "sheets": sheets}


def _read_xls_via_com(path: str) -> Optional[Dict[str, Any]]:
    """通过 Windows PowerShell + Excel/WPS COM 精准解析二进制 .xls 的每个 Sheet 和单元格文本。"""
    if os.name != "nt":
        return None
    ps_script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$FilePath = $env:RAW_NORM_XLS_PATH
$result = @{ method = ""; sheets = @{} }
foreach ($prog in @('Excel.Application', 'KET.Application', 'ET.Application')) {
    $app = $null
    try {
        $app = New-Object -ComObject $prog
        $app.Visible = $false
        $app.DisplayAlerts = $false
        $wb = $app.Workbooks.Open($FilePath, 0, $true)
        $result.method = $prog
        foreach ($ws in $wb.Worksheets) {
            $ur = $ws.UsedRange
            $maxR = [Math]::Min($ur.Rows.Count, 200)
            $maxC = [Math]::Min($ur.Columns.Count, 25)
            $rows = @()
            for ($r = 1; $r -le $maxR; $r++) {
                $cells = @()
                for ($c = 1; $c -le $maxC; $c++) {
                    $t = $ws.Cells.Item($r, $c).Text
                    if ($t -and $t.Trim() -ne '') {
                        $clean = ($t.Trim() -replace '\r?\n', ' / ')
                        if ($clean -notmatch '^=DISPIMG\(') {
                            $cells += "[$c]$clean"
                        } else {
                            $cells += "[$c]<EMBEDDED_IMAGE>"
                        }
                    }
                }
                if ($cells.Count -gt 0) {
                    $rows += ("R{0}: {1}" -f $r, ($cells -join ' | '))
                }
            }
            if ($rows.Count -gt 0) {
                $result.sheets[$ws.Name] = $rows
            }
        }
        $wb.Close($false)
        $app.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($app) | Out-Null
        $result | ConvertTo-Json -Depth 5 -Compress
        exit 0
    } catch {
        if ($app) {
            try { $app.Quit() } catch {}
        }
    }
}
exit 1
"""
    try:
        env = os.environ.copy()
        env["RAW_NORM_XLS_PATH"] = os.path.abspath(path)
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            env=env,
            timeout=60,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
            for ln in reversed(lines):
                if ln.startswith("{"):
                    return json.loads(ln)
    except Exception:
        pass
    return None


def _read_xls_fallback_binary(path: str) -> Dict[str, Any]:
    with open(path, "rb") as f:
        raw = f.read()
    ascii_chunks = re.findall(rb"[A-Za-z0-9_:./\-\+\(\)]{4,}", raw)
    ascii_text = " ".join(c.decode("ascii", errors="ignore") for c in ascii_chunks[:1500])
    utf16_chunks = re.findall(rb"(?:[\x20-\x7e\x00-\xff]\x00){4,}", raw)
    utf16_text = " ".join(c.decode("utf-16le", errors="ignore") for c in utf16_chunks[:1000])
    return {
        "method": "binary_fallback",
        "sheets": {"RAW_TEXT": [ascii_text[:6000], utf16_text[:6000]]},
    }


def _read_doc(path: str) -> Dict[str, Any]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt" or ext == ".md" or ext == ".csv":
        return {"kind": ext.lstrip("."), **_read_txt_auto(path)}
    if ext == ".xlsx":
        try:
            return {"kind": "xlsx", **_read_xlsx(path)}
        except Exception as e:
            return {"kind": "xlsx", "error": str(e)}
    if ext == ".xls":
        com_res = _read_xls_via_com(path)
        if com_res:
            return {"kind": "xls", **com_res}
        return {"kind": "xls", **_read_xls_fallback_binary(path)}
    return {"kind": "unknown"}


def _classify_image_bucket(rel_path: str, w: int, h: int, white_ratio: float) -> str:
    low = rel_path.lower()
    aspect = (w / h) if h else 0.0
    if h >= 3000 or (w > 0 and h / max(w, 1) > 2.8):
        return "long_strip_detail"
    if any(k in low for k in ["中文", "cn mo", "cn pc"]):
        return "cn_marketing_or_detail"
    if any(k in low for k in ["白底", "white", "普-", "无字"]) or (white_ratio >= 0.88 and 0.75 <= aspect <= 1.35 and "详情" not in low):
        return "white_bg_candidate"
    if any(k in low for k in ["英文", "en mo", "en pc", "sku", "主图"]):
        if "详情" in low:
            return "en_detail_slice"
        return "en_main_or_sku_ref"
    if any(k in low for k in ["banner", "slide", "海报", "轮播", "合集", "标签"]):
        return "marketing_excluded"
    return "other_image"


def _make_contact_sheet(
    images: List[Dict[str, Any]],
    out_path: str,
    title: str,
    cols: int = 4,
    cell_w: int = 340,
    cell_h: int = 380,
) -> Optional[str]:
    if not images:
        return None
    rows = math.ceil(len(images) / cols)
    header_h = 44
    canvas = Image.new("RGB", (cols * cell_w, header_h + rows * cell_h), (244, 245, 248))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
        font_title = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 18)
    except Exception:
        font = ImageFont.load_default()
        font_title = font

    draw.rectangle([0, 0, cols * cell_w, header_h], fill=(30, 41, 59))
    draw.text((14, 10), f"{title} ({len(images)} images)", fill=(255, 255, 255), font=font_title)

    for idx, item in enumerate(images):
        r = idx // cols
        c = idx % cols
        x0 = c * cell_w
        y0 = header_h + r * cell_h
        draw.rectangle([x0 + 6, y0 + 6, x0 + cell_w - 6, y0 + cell_h - 6], fill=(255, 255, 255), outline=(203, 213, 225))
        try:
            with Image.open(item["abs_path"]) as im:
                im = im.convert("RGB")
                im.thumbnail((cell_w - 24, cell_h - 86), Image.Resampling.LANCZOS)
                px = x0 + (cell_w - im.width) // 2
                py = y0 + 14 + ((cell_h - 86) - im.height) // 2
                canvas.paste(im, (px, py))
        except Exception:
            draw.text((x0 + 20, y0 + 80), "LOAD ERROR", fill=(220, 38, 38), font=font)

        label_1 = f"[{item['id']}] {item['name']}"
        label_2 = f"{item['width']}x{item['height']} | {item['size_kb']}KB | W:{int(item['white_ratio']*100)}%"
        label_3 = item["rel_dir"][:34]
        draw.text((x0 + 12, y0 + cell_h - 66), label_1[:32], fill=(15, 23, 42), font=font)
        draw.text((x0 + 12, y0 + cell_h - 46), label_2, fill=(71, 85, 105), font=font)
        draw.text((x0 + 12, y0 + cell_h - 26), label_3, fill=(100, 116, 139), font=font)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path, format="JPEG", quality=88)
    return _norm(out_path)


def inspect_folder(raw_dir: str, out_dir: str) -> Dict[str, Any]:
    raw_dir = os.path.abspath(raw_dir.strip().strip('"').strip("'"))
    if not os.path.isdir(raw_dir):
        raise FileNotFoundError(f"原始素材目录不存在: {raw_dir}")

    os.makedirs(out_dir, exist_ok=True)
    folder_name = os.path.basename(raw_dir)
    spu_match = re.search(r"(RC\d{3,6}|[A-Z]{2,4}\d{3,6})", folder_name, re.I)
    spu_guess = spu_match.group(1).upper() if spu_match else "NEWSPU"

    documents = []
    images = []
    videos = []
    others = []

    img_counter = 1
    for root, dirs, files in os.walk(raw_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "通途产品图库"))
        rel_dir = os.path.relpath(root, raw_dir).replace("\\", "/")
        for fn in sorted(files):
            if fn.startswith(".") or fn.startswith("~$"):
                continue
            fp = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            size_kb = round(os.path.getsize(fp) / 1024, 1)
            rel_path = fn if rel_dir == "." else f"{rel_dir}/{fn}"

            if ext in DOC_EXTS:
                parsed = _read_doc(fp)
                documents.append({
                    "name": fn,
                    "rel_path": rel_path,
                    "abs_path": _norm(fp),
                    "size_kb": size_kb,
                    "parsed": parsed,
                })
            elif ext in IMAGE_EXTS:
                w, h, white_ratio = 0, 0, 0.0
                try:
                    with Image.open(fp) as im:
                        w, h = im.size
                        white_ratio = _estimate_white_border_ratio(im)
                except Exception:
                    pass
                bucket = _classify_image_bucket(rel_path, w, h, white_ratio)
                images.append({
                    "id": f"IMG_{img_counter:03d}",
                    "name": fn,
                    "rel_dir": rel_dir,
                    "rel_path": rel_path,
                    "abs_path": _norm(fp),
                    "width": w,
                    "height": h,
                    "size_kb": size_kb,
                    "white_ratio": white_ratio,
                    "bucket": bucket,
                    "needs_upscale_for_workbench": (w < 1000 or h < 1000 or size_kb < 45),
                })
                img_counter += 1
            elif ext in VIDEO_EXTS:
                videos.append({"name": fn, "rel_path": rel_path, "size_kb": size_kb})
            else:
                others.append({"name": fn, "rel_path": rel_path, "size_kb": size_kb})

    # 生成分组 Contact Sheet，便于 Agent 一眼完成视觉核对
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for im in images:
        buckets.setdefault(im["bucket"], []).append(im)

    sheets = {}
    sheet_specs = [
        ("white_bg_candidate", "contact_white_bg.jpg", "White Background Candidates"),
        ("en_main_or_sku_ref", "contact_en_main_sku.jpg", "EN Main & SKU References"),
        ("en_detail_slice", "contact_en_detail.jpg", "EN Detail Slices"),
        ("other_image", "contact_other.jpg", "Other Images"),
    ]
    for bkey, fname, title in sheet_specs:
        items = buckets.get(bkey, [])
        if items:
            sheets[bkey] = _make_contact_sheet(items[:24], os.path.join(out_dir, fname), title)

    inventory = {
        "raw_dir": _norm(raw_dir),
        "folder_name": folder_name,
        "spu_guess": spu_guess,
        "summary": {
            "documents": len(documents),
            "images_total": len(images),
            "videos": len(videos),
            "bucket_counts": {k: len(v) for k, v in buckets.items()},
        },
        "contact_sheets": sheets,
        "documents": documents,
        "images": images,
        "videos": videos,
        "others": others,
    }

    inv_path = os.path.join(out_dir, "raw_inventory.json")
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    print(f"[OK] Inventory written to: {_norm(inv_path)}")
    print(f"SPU guess: {spu_guess} | Docs: {len(documents)} | Images: {len(images)} | Videos: {len(videos)}")
    print("Buckets:", json.dumps(inventory["summary"]["bucket_counts"], ensure_ascii=False))
    if sheets:
        print("Contact sheets:")
        for k, v in sheets.items():
            print(f"  - {k}: {v}")
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect raw supplier/dev product folder for AutoShot workbench.")
    parser.add_argument("raw_dir", help="原始商品素材文件夹路径")
    parser.add_argument("--out-dir", required=True, help="探测报告与拼图输出目录")
    args = parser.parse_args()
    inspect_folder(args.raw_dir, args.out_dir)


if __name__ == "__main__":
    main()
