# -*- coding: utf-8 -*-
"""交互界面视觉原型 V2：浅色 SaaS 风格，统一设计系统（侧边栏 + 步骤条 + 卡片）。"""
import os
import shutil
import subprocess

UI_DIR = r"e:\Projects\Raw_Image_Workspace\UI交互界面预览"
ART_DIR = r"C:\Users\paidaxing\.gemini\antigravity\brain\46126701-e9cb-488c-9a99-f40915eb9569"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
os.makedirs(UI_DIR, exist_ok=True)

SRC = r"E:\Projects\Raw_Image_Workspace\RC4661 GX10遥控器\GX10"
OUT = r"E:\Projects\Raw_Image_Workspace\auto_image_gen\outputs\RC4661"
SKU = r"E:\Projects\Raw_Image_Workspace\auto_image_gen\assets\shared_skus"


def u(p):
    return "file:///" + p.replace("\\", "/")


def gry(i):
    return u(rf"{SRC}\普-灰\普-灰 {i}.jpg")


def cha(i):
    return u(rf"{SRC}\普-透明\普-透明 {i}.jpg")


def out(name):
    return u(rf"{OUT}\{name}")


BAT1 = u(rf"{SKU}\RC4226A.png")
BAT2 = u(rf"{SKU}\RC3473.png")

# ---------------- 图标（线性图标，统一 1.8 描边） ----------------
ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "folder": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "grid": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "tag": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1"/>',
    "sparkles": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 3v4"/><path d="M21 5h-4"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "chev-r": '<path d="m9 18 6-6-6-6"/>',
    "chev-d": '<path d="m6 9 6 6 6-6"/>',
    "arrow-r": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "arrow-l": '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M8 13h8M8 17h8M8 9h2"/>',
    "sheet": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M8 13h2M14 13h2M8 17h2M14 17h2"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "plus": '<path d="M5 12h14M12 5v14"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "ban": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "more": '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
    "bookmark": '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
    "move": '<path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "maximize": '<path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/>',
}


def ic(name, size=16, sw=1.8, style=""):
    return (f'<svg class="ic" style="{style}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


# ---------------- 设计系统 CSS（普通字符串，单花括号） ----------------
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1600px;height:1000px;overflow:hidden}
body{font-family:"Segoe UI","Microsoft YaHei UI","Microsoft YaHei",sans-serif;font-size:13px;line-height:1.5;color:#111827;background:#F5F6F8;display:flex;-webkit-font-smoothing:antialiased}
.ic{flex-shrink:0;display:block}
.mono{font-family:"Cascadia Mono",Consolas,monospace}
.muted{color:#6B7280}.faint{color:#9CA3AF}
.row{display:flex;align-items:center}
.ell{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* 侧边栏 */
.sb{width:224px;height:1000px;background:#FFFFFF;border-right:1px solid #ECEEF2;display:flex;flex-direction:column;padding:18px 12px 14px}
.sb-logo{display:flex;align-items:center;gap:10px;padding:0 8px 16px}
.logo-mark{width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#6366F1 0%,#8B5CF6 100%);display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 2px 8px rgba(99,102,241,.35)}
.sb-title{font-weight:700;font-size:14.5px;letter-spacing:.2px;line-height:1.2}
.sb-sub{font-size:11px;color:#9CA3AF;line-height:1.3}
.sb-search{display:flex;align-items:center;gap:8px;height:34px;border:1px solid #ECEEF2;border-radius:8px;padding:0 10px;color:#9CA3AF;font-size:12.5px;margin:0 2px 8px;background:#FAFAFB}
.sb-search .kbd{margin-left:auto;font-size:10.5px;border:1px solid #E5E7EB;border-radius:4px;padding:0 5px;color:#9CA3AF;background:#fff}
.sb-sec{font-size:11px;color:#9CA3AF;font-weight:600;padding:14px 10px 6px;letter-spacing:.4px}
.nav{display:flex;align-items:center;gap:10px;height:34px;padding:0 10px;border-radius:8px;color:#4B5563;font-size:13px}
.nav.on{background:#EEF2FF;color:#4338CA;font-weight:600}
.nav .cnt{margin-left:auto;font-size:11px;background:#F3F4F6;color:#6B7280;border-radius:10px;padding:0 7px;line-height:18px;font-weight:600}
.nav.on .cnt{background:#E0E7FF;color:#4338CA}
.recent{display:flex;align-items:center;gap:9px;height:32px;padding:0 10px;border-radius:8px;color:#4B5563;font-size:12.5px}
.recent.on{background:#F5F6F8;color:#111827;font-weight:600}
.recent .dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.sb-foot{margin-top:auto;display:flex;flex-direction:column;gap:10px}
.status-card{border:1px solid #ECEEF2;border-radius:10px;padding:11px 12px;background:#FAFAFB}
.user{display:flex;align-items:center;gap:10px;padding:6px 6px 0}
.avatar{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#F59E0B,#EF4444);color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}

/* 主区 */
.main{flex:1;display:flex;flex-direction:column;min-width:0;height:1000px}
.hd{height:64px;flex-shrink:0;background:#fff;border-bottom:1px solid #ECEEF2;display:flex;align-items:center;padding:0 28px;gap:20px}
.crumb{display:flex;align-items:center;gap:6px;color:#9CA3AF;font-size:12px;line-height:1.2}
.hd-title{font-size:16px;font-weight:700;color:#111827;display:flex;align-items:center;gap:10px;line-height:1.3;margin-top:2px}
.stepper{display:flex;align-items:center;gap:12px;margin-left:auto}
.st{display:flex;align-items:center;gap:9px;font-size:13px;color:#9CA3AF}
.st .n{width:24px;height:24px;border-radius:50%;border:1.5px solid #D1D5DB;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;background:#fff}
.st.on{color:#111827;font-weight:600}
.st.on .n{border-color:#4F46E5;background:#4F46E5;color:#fff;box-shadow:0 0 0 4px #E0E7FF}
.st.done{color:#374151}
.st.done .n{border-color:#4F46E5;background:#EEF2FF;color:#4F46E5}
.st-line{width:40px;height:2px;border-radius:2px;background:#E5E7EB}
.st-line.done{background:#A5B4FC}
.vsep{width:1px;height:28px;background:#ECEEF2}
.content{flex:1;padding:20px 28px;min-height:0}
.ft{height:68px;flex-shrink:0;background:#fff;border-top:1px solid #ECEEF2;display:flex;align-items:center;padding:0 28px;gap:12px}

/* 通用组件 */
.card{background:#fff;border:1px solid #ECEEF2;border-radius:14px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.card-hd{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid #F1F2F5}
.card-t{font-size:14px;font-weight:700;color:#111827;line-height:1.35}
.card-d{font-size:12px;color:#6B7280;line-height:1.4}
.sec-t{font-size:12.5px;font-weight:700;color:#374151;display:flex;align-items:center;gap:8px}
.btn{height:34px;padding:0 14px;border-radius:8px;font-size:13px;font-weight:600;display:inline-flex;align-items:center;justify-content:center;gap:7px;border:1px solid transparent;font-family:inherit;white-space:nowrap}
.btn-p{background:#4F46E5;color:#fff;box-shadow:0 1px 2px rgba(79,70,229,.35),inset 0 1px 0 rgba(255,255,255,.18)}
.btn-s{background:#fff;color:#374151;border-color:#E5E7EB;box-shadow:0 1px 2px rgba(16,24,40,.05)}
.btn-g{background:transparent;color:#6B7280}
.btn-lg{height:40px;padding:0 20px;font-size:13.5px;border-radius:9px}
.btn-sm{height:28px;padding:0 10px;font-size:12px;border-radius:7px}
.pill{display:inline-flex;align-items:center;gap:5px;height:22px;padding:0 8px;border-radius:6px;font-size:11.5px;font-weight:600;white-space:nowrap}
.p-ok{background:#ECFDF5;color:#047857}
.p-warn{background:#FFFBEB;color:#B45309}
.p-bad{background:#FEF2F2;color:#B91C1C}
.p-brand{background:#EEF2FF;color:#4338CA}
.p-gray{background:#F3F4F6;color:#4B5563}
.thumb{background:#F7F8FA;border:1px solid #EEF0F3;border-radius:10px;overflow:hidden;display:flex;align-items:center;justify-content:center;position:relative}
.thumb img{width:100%;height:100%;object-fit:contain}
.swatch{width:14px;height:14px;border-radius:4px;border:1px solid rgba(0,0,0,.12);flex-shrink:0}
.chip{display:inline-flex;align-items:center;height:26px;padding:0 10px;border-radius:7px;background:#F5F6F8;border:1px solid #EEF0F3;font-size:12px;color:#374151;white-space:nowrap}
.switch{width:32px;height:18px;border-radius:10px;background:#4F46E5;position:relative;flex-shrink:0}
.switch::after{content:"";position:absolute;right:2px;top:2px;width:14px;height:14px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.2)}
.select{height:36px;border:1px solid #E5E7EB;border-radius:8px;display:flex;align-items:center;gap:8px;padding:0 10px 0 12px;font-size:13px;color:#111827;background:#fff;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.select .ic:last-child{margin-left:auto;color:#9CA3AF}
.lbl{font-size:12px;color:#6B7280;font-weight:600;margin-bottom:6px}
.logo-chip{display:inline-flex;align-items:center;height:26px;padding:0 10px;border-radius:6px;background:#111827;color:#fff;font-weight:800;font-style:italic;font-size:12px;letter-spacing:.6px}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}
"""


def sidebar():
    return f"""
<aside class="sb">
  <div class="sb-logo">
    <div class="logo-mark">{ic('sparkles', 18, 2)}</div>
    <div><div class="sb-title">AutoShot 生图台</div><div class="sb-sub">跨境电商批量套图</div></div>
  </div>
  <div class="sb-search">{ic('search', 14)}<span>搜索 SKU / 任务</span><span class="kbd">Ctrl K</span></div>
  <div class="nav">{ic('grid')}<span>工作台</span></div>
  <div class="nav on">{ic('layers')}<span>生图任务</span><span class="cnt">3</span></div>
  <div class="nav">{ic('image')}<span>素材库</span></div>
  <div class="nav">{ic('tag')}<span>品牌 LOGO 库</span></div>
  <div class="nav">{ic('file')}<span>提示词模板</span></div>
  <div class="nav">{ic('cpu')}<span>生图平台</span></div>
  <div class="sb-sec">最近任务</div>
  <div class="recent on"><span class="dot" style="background:#6366F1"></span><span class="ell">RC4661 · GX10 遥控器</span></div>
  <div class="recent"><span class="dot" style="background:#10B981"></span><span class="ell">RC5102 · SKYRC 充电器</span></div>
  <div class="recent"><span class="dot" style="background:#10B981"></span><span class="ell">RC3980 · Pocket 遥控器</span></div>
  <div class="recent"><span class="dot" style="background:#D1D5DB"></span><span class="ell">RC4120 · 9IMOD 电调</span></div>
  <div class="sb-foot">
    <div class="status-card">
      <div class="row" style="justify-content:space-between;font-size:11.5px;color:#6B7280;font-weight:600"><span>生图平台</span><span class="row" style="gap:5px;color:#047857"><span class="dot" style="background:#10B981"></span>正常</span></div>
      <div style="font-size:13px;font-weight:700;margin-top:4px">球球Token</div>
      <div class="mono" style="font-size:11px;color:#9CA3AF">gpt-image-2 · 平均 21s / 张</div>
    </div>
    <div class="user"><div class="avatar">王</div><div style="line-height:1.3"><div style="font-size:12.5px;font-weight:600">王晓 · 运营</div><div style="font-size:11px;color:#9CA3AF">美工组</div></div><div style="margin-left:auto;color:#9CA3AF">{ic('sliders', 15)}</div></div>
  </div>
</aside>"""


def header(step, right=""):
    def st(i, label):
        if i < step:
            return f'<div class="st done"><div class="n">{ic("check", 13, 2.6)}</div>{label}</div>'
        if i == step:
            return f'<div class="st on"><div class="n">{i}</div>{label}</div>'
        return f'<div class="st"><div class="n">{i}</div>{label}</div>'

    l1 = "done" if step > 1 else ""
    l2 = "done" if step > 2 else ""
    return f"""
<header class="hd">
  <div>
    <div class="crumb">生图任务 {ic('chev-r', 12)} RC4661</div>
    <div class="hd-title">GX10 16CH 遥控器 <span class="pill p-gray">RadioMaster</span></div>
  </div>
  <div class="stepper">
    {st(1, '导入素材')}<div class="st-line {l1}"></div>
    {st(2, '核对参数')}<div class="st-line {l2}"></div>
    {st(3, '生成与验收')}
  </div>
  {right}
</header>"""


def page(body_css, main_html):
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>" + CSS + body_css +
            "</style></head><body>" + sidebar() + "<main class='main'>" + main_html + "</main></body></html>")


# ======================================================================
# 第一步：导入素材
# ======================================================================
CSS1 = """
.layout{display:grid;grid-template-columns:1fr 400px;gap:20px;height:100%}
.fold{width:42px;height:42px;border-radius:10px;background:#FFF7ED;color:#EA580C;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #F1F2F5}
.stat{padding:12px 20px;border-right:1px solid #F1F2F5}
.stat:last-child{border-right:none}
.stat .k{font-size:12px;color:#6B7280}
.stat .v{font-size:20px;font-weight:700;line-height:1.3;font-family:"Segoe UI",sans-serif}
.sec{padding:14px 20px 4px}
.sec-hd{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.docs{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.doc{display:flex;align-items:center;gap:12px;border:1px solid #EEF0F3;border-radius:10px;padding:10px 12px}
.doc-ic{width:34px;height:34px;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.thumbs{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
.tcell .thumb{aspect-ratio:1/1}
.tcap{margin-top:6px;font-size:12px;font-weight:600;color:#374151;line-height:1.3}
.tmeta{font-size:11px;color:#9CA3AF;line-height:1.3}
.ghost{aspect-ratio:1/1;border:1.5px dashed #D1D5DB;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:#9CA3AF;font-size:11px;text-align:center;padding:6px;background:#FAFAFB}
.badge-res{position:absolute;left:6px;bottom:6px;background:rgba(17,24,39,.72);color:#fff;font-size:10px;border-radius:4px;padding:0 5px;line-height:16px}
.ex{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.exi{display:flex;gap:10px;align-items:center;border:1px solid #F3F4F6;border-radius:10px;padding:8px;background:#FCFCFD}
.exi .thumb{width:44px;height:44px;border-radius:7px;flex-shrink:0}
.exi .thumb img{filter:grayscale(1);opacity:.55;object-fit:cover}
.hero{display:flex;gap:14px;align-items:center;padding:18px 20px;background:linear-gradient(180deg,#F0FDF4 0%,#FFFFFF 100%);border-bottom:1px solid #F1F2F5;border-radius:14px 14px 0 0}
.hero-ic{width:42px;height:42px;border-radius:50%;background:#10B981;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 6px #D1FAE5}
.chk{display:flex;gap:12px;align-items:flex-start;padding:11px 20px;border-bottom:1px solid #F5F6F8}
.chk:last-child{border-bottom:none}
.chk-ic{width:24px;height:24px;border-radius:7px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.chk-t{font-size:13px;font-weight:600;line-height:1.4}
.chk-d{font-size:12px;color:#6B7280;line-height:1.45}
.howto{padding:14px 20px 16px}
.hstep{display:flex;gap:10px;align-items:flex-start;margin-bottom:9px}
.hn{width:20px;height:20px;border-radius:50%;background:#EEF2FF;color:#4F46E5;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.tree{margin-top:4px;background:#F8F9FB;border:1px solid #EEF0F3;border-radius:10px;padding:10px 14px;font-size:11.5px;line-height:1.75;color:#4B5563;white-space:pre}
.tree b{color:#111827;font-weight:600}
.tree i{color:#9CA3AF;font-style:normal}
"""


def tcell(img, cap, meta="1000×1000"):
    return f"""<div class="tcell"><div class="thumb"><img src="{img}"></div>
    <div class="tcap">{cap}</div><div class="tmeta">{meta}</div></div>"""


def exi(img, name, reason):
    return f"""<div class="exi"><div class="thumb"><img src="{img}"></div>
    <div style="min-width:0"><div class="ell" style="font-size:12px;font-weight:600;color:#4B5563">{name}</div>
    <div class="row" style="gap:4px;font-size:11px;color:#B91C1C">{ic('ban', 11, 2)}{reason}</div></div></div>"""


def chk(kind, title, desc, right=""):
    color = {"ok": ("#ECFDF5", "#059669", "check"), "fix": ("#FFFBEB", "#D97706", "refresh")}[kind]
    return f"""<div class="chk"><div class="chk-ic" style="background:{color[0]};color:{color[1]}">{ic(color[2], 14, 2.4)}</div>
    <div style="flex:1;min-width:0"><div class="chk-t">{title}</div><div class="chk-d">{desc}</div></div>{right}</div>"""


step1_main = header(1) + f"""
<div class="content"><div class="layout">
  <!-- 左：素材文件夹解析结果 -->
  <section class="card" style="display:flex;flex-direction:column;overflow:hidden">
    <div class="card-hd">
      <div class="fold">{ic('folder', 20)}</div>
      <div style="min-width:0">
        <div class="card-t">RC4661 GX10遥控器</div>
        <div class="card-d mono ell">E:\\Projects\\Raw_Image_Workspace\\RC4661 GX10遥控器</div>
      </div>
      <div class="row" style="margin-left:auto;gap:8px">
        <button class="btn btn-s">{ic('refresh', 14)}重新扫描</button>
        <button class="btn btn-s">{ic('upload', 14)}更换文件夹</button>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><div class="k">扫描文件</div><div class="v">86</div></div>
      <div class="stat"><div class="k">识别文档</div><div class="v">2</div></div>
      <div class="stat"><div class="k">可用素材图</div><div class="v" style="color:#059669">12</div></div>
      <div class="stat"><div class="k">自动排除</div><div class="v" style="color:#9CA3AF">72</div></div>
    </div>

    <div class="sec">
      <div class="sec-hd"><span class="sec-t">需求文档</span></div>
      <div class="docs">
        <div class="doc"><div class="doc-ic" style="background:#ECFDF5;color:#059669">{ic('sheet', 18)}</div>
          <div style="flex:1;min-width:0"><div style="font-weight:600">RC4661 图片需求.xls</div><div class="card-d">品牌 RadioMaster · 4 个主 SKU · 2 款搭配电池</div></div>
          <span class="pill p-ok">{ic('check', 12, 2.6)}已解析</span></div>
        <div class="doc"><div class="doc-ic" style="background:#EFF6FF;color:#2563EB">{ic('file', 18)}</div>
          <div style="flex:1;min-width:0"><div style="font-weight:600">GX10 报价单.xlsx</div><div class="card-d">21 项规格参数 · 13 项包装清单</div></div>
          <span class="pill p-ok">{ic('check', 12, 2.6)}已解析</span></div>
      </div>
    </div>

    <div class="sec">
      <div class="sec-hd"><span class="swatch" style="background:#B9BDC3"></span><span class="sec-t">银灰色 · GRY</span>
        <span class="pill p-gray">7 张</span><span class="card-d" style="margin-left:auto">文件夹：颜色1_银灰色</span></div>
      <div class="thumbs">
        {tcell(gry(1), '正面')}{tcell(gry(2), '背面')}{tcell(gry(3), '45° 斜侧')}
        {tcell(gry(5), '左侧面')}{tcell(gry(6), '右侧面')}{tcell(gry(9), '摇杆特写')}
        {tcell(gry(10), '配件合照')}
      </div>
    </div>

    <div class="sec">
      <div class="sec-hd"><span class="swatch" style="background:#3B3F46"></span><span class="sec-t">半透明黑 · CHA</span>
        <span class="pill p-gray">5 张</span><span class="card-d" style="margin-left:auto">文件夹：颜色2_半透明黑</span></div>
      <div class="thumbs">
        {tcell(cha(1), '正面')}{tcell(cha(2), '背面')}{tcell(cha(3), '45° 斜侧')}
        {tcell(cha(5), '左侧面')}{tcell(cha(6), '右侧面')}
        <div class="tcell"><div class="ghost">{ic('link', 16)}<span>复用银灰色</span></div><div class="tcap" style="color:#9CA3AF">摇杆特写</div><div class="tmeta">同模具共用</div></div>
        <div class="tcell"><div class="ghost">{ic('link', 16)}<span>复用银灰色</span></div><div class="tcap" style="color:#9CA3AF">配件合照</div><div class="tmeta">主机自动替换</div></div>
      </div>
    </div>

    <div class="sec" style="padding-bottom:18px">
      <div class="sec-hd"><span class="sec-t">已自动排除</span><span class="pill p-gray">72 张</span>
        <span class="card-d" style="margin-left:auto;color:#4F46E5;font-weight:600">查看全部</span></div>
      <div class="ex">
        {exi(u(SRC + r'\GX10 合集.jpg'), 'GX10 合集.jpg', '单机仅 350px')}
        {exi(u(SRC + r'\GX10\CN MO\CN MO 13.jpg'), 'CN MO 13.jpg', '含原厂中文')}
        {exi(u(SRC + r'\3.GX10 Slide&Banner 海报&轮播图\1200x900 FB.jpg'), '1200x900 FB.jpg', '营销海报')}
        {exi(u(SRC + r'\GX10\CN MO\CN MO 1.jpg'), 'CN MO 1~16.jpg', '详情切片')}
      </div>
    </div>
  </section>

  <!-- 右：预检结果 + 整理规范 -->
  <div style="display:flex;flex-direction:column;gap:20px;min-height:0">
    <section class="card">
      <div class="hero">
        <div class="hero-ic">{ic('check', 22, 2.6)}</div>
        <div><div style="font-size:15px;font-weight:700">素材已就绪</div>
        <div class="card-d">0 项阻塞 · 2 项已自动修正 · 可进入下一步</div></div>
      </div>
      {chk('ok', '品牌 LOGO', '已识别 RadioMaster 并绑定官方 LOGO', '<span class="logo-chip">RADIOMASTER</span>')}
      {chk('ok', '搭配配件', 'RC4226A、RC3473 已从共享盘拉取并校正方向')}
      {chk('ok', '型号隔离', '已屏蔽 GX10 MAX / 900MHz / AG01 等高配词')}
      {chk('ok', '分辨率', '12 / 12 张素材图 ≥ 1000×1000')}
      {chk('fix', '低清合集图', '已排除 1 张，改用两张单机大图合成')}
      {chk('fix', '原厂带字图', '已排除 16 张，参数表改为文字直出')}
    </section>

    <section class="card" style="flex:1">
      <div class="card-hd" style="padding:14px 20px"><div class="card-t">人工只需整理 3 件事</div><span class="pill p-brand" style="margin-left:auto">约 1–2 分钟</span></div>
      <div class="howto">
        <div class="hstep"><div class="hn">1</div><div>按颜色建子文件夹，例如 <b>颜色1_银灰色</b></div></div>
        <div class="hstep"><div class="hn">2</div><div>每色放 5–7 张 <b>≥1000px 无字白底图</b></div></div>
        <div class="hstep"><div class="hn">3</div><div>放 1 张<b>无字配件合照</b>，其余文件原样保留</div></div>
<div class="tree mono"><b>RC4661 GX10遥控器/</b>
├─ RC4661 图片需求.xls
├─ GX10 报价单.xlsx
├─ <b>颜色1_银灰色/</b>   <i>正面 背面 斜侧 … 合照</i>
├─ <b>颜色2_半透明黑/</b> <i>正面 背面 斜侧 …</i>
└─ 供应商原始资料/   <i>原样放入，自动过滤</i></div>
      </div>
    </section>
  </div>
</div></div>
<footer class="ft">
  <div class="row" style="gap:8px;color:#6B7280;font-size:12.5px">{ic('shield', 15)}<span>系统已自动过滤海报、详情切片和低清缩略图，不会用于生图</span></div>
  <div class="row" style="margin-left:auto;gap:10px">
    <button class="btn btn-s btn-lg">取消</button>
    <button class="btn btn-p btn-lg">下一步：核对参数 {ic('arrow-r', 15, 2.2)}</button>
  </div>
</footer>"""

# ======================================================================
# 第二步：核对参数
# ======================================================================
CSS2 = """
.wrap{display:flex;flex-direction:column;gap:16px;height:100%}
.scope{display:flex;align-items:stretch;gap:12px;padding:14px 16px}
.scope-lbl{width:132px;display:flex;flex-direction:column;justify-content:center;padding-left:4px}
.opt{flex:1;display:flex;gap:12px;align-items:flex-start;border:1px solid #E5E7EB;border-radius:11px;padding:12px 14px;background:#fff}
.opt.on{border-color:#C7D2FE;background:#F8F9FF;box-shadow:0 0 0 1px #C7D2FE inset}
.cb{width:18px;height:18px;border-radius:5px;background:#4F46E5;color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.cb.off{background:#fff;border:1.5px solid #D1D5DB}
.opt-n{margin-left:auto;font-size:18px;font-weight:700;line-height:1.2;white-space:nowrap}
.opt-n small{font-size:12px;color:#6B7280;font-weight:500;margin-left:2px}
.total{width:150px;border-radius:11px;background:#111827;color:#fff;display:flex;flex-direction:column;justify-content:center;padding:0 18px}
.grid2{display:grid;grid-template-columns:430px 1fr;gap:16px;flex:1;min-height:0}
.f{padding:12px 20px;border-bottom:1px solid #F5F6F8}
.f:last-child{border-bottom:none}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.kv{display:flex;align-items:center;height:34px;border-radius:8px;padding:0 10px;font-size:12.5px}
.kv .k{width:78px;color:#6B7280}
.kv.warn{background:#FFFBEB}
.slots{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
.slot .thumb{aspect-ratio:1/1}
.slot-role{position:absolute;left:6px;top:6px;background:#fff;border:1px solid #EEF0F3;border-radius:5px;font-size:10.5px;font-weight:600;padding:0 5px;line-height:17px;color:#374151}
.slot-ok{position:absolute;right:6px;top:6px;width:16px;height:16px;border-radius:50%;background:#10B981;color:#fff;display:flex;align-items:center;justify-content:center}
.seg{display:flex;background:#F3F4F6;border-radius:9px;padding:3px;gap:2px}
.seg div{height:28px;padding:0 12px;border-radius:7px;display:flex;align-items:center;gap:7px;font-size:12.5px;color:#6B7280;font-weight:600}
.seg div.on{background:#fff;color:#111827;box-shadow:0 1px 2px rgba(16,24,40,.08)}
table.mx{width:100%;border-collapse:separate;border-spacing:0;font-size:12px}
.mx th{font-weight:600;color:#6B7280;text-align:left;padding:8px 12px;background:#FAFAFB;border-bottom:1px solid #F1F2F5}
.mx th:first-child{border-radius:8px 0 0 0}.mx th:last-child{border-radius:0 8px 0 0}
.mx td{padding:8px 12px;border-bottom:1px solid #F5F6F8;vertical-align:middle}
.mx tr:last-child td{border-bottom:none}
.fn{display:inline-flex;align-items:center;gap:6px;color:#374151}
.fn .ic{color:#10B981}
.bat{width:30px;height:22px;border-radius:5px;background:#F7F8FA;border:1px solid #EEF0F3;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;vertical-align:middle;margin-right:6px}
.bat img{width:100%;height:100%;object-fit:contain}
.plat{display:grid;grid-template-columns:1.1fr 1fr .8fr 1.2fr;gap:12px;align-items:end}
"""


def slot(img, role, name, size="1000×1000"):
    return f"""<div class="slot"><div class="thumb"><img src="{img}"><span class="slot-role">{role}</span>
    <span class="slot-ok">{ic('check', 10, 3)}</span></div>
    <div class="ell" style="font-size:12px;font-weight:600;margin-top:6px">{name}</div>
    <div class="tmeta" style="font-size:11px;color:#9CA3AF">{size}</div></div>"""


def mx_row(code, color, sw, variant):
    cells = "".join(
        f'<td><span class="fn mono">{ic("check", 12, 2.6)}{code}{suf}.jpg</span></td>'
        for suf in ["", "_RC4226A", "_RC3473"])
    return f"""<tr><td><div class="row" style="gap:10px"><span class="swatch" style="background:{sw}"></span>
    <div style="line-height:1.3"><div class="mono" style="font-weight:700;color:#111827">{code}</div>
    <div style="color:#9CA3AF;font-size:11px">{color} · {variant}</div></div></div></td>{cells}</tr>"""


step2_main = header(2) + f"""
<div class="content"><div class="wrap">
  <!-- 出图范围 -->
  <section class="card scope">
    <div class="scope-lbl"><div class="card-t">出图范围</div><div class="card-d">勾选本次要生成的套图</div></div>
    <div class="opt on"><div class="cb">{ic('check', 12, 3)}</div>
      <div><div class="row" style="gap:6px;font-weight:700">通用套图 <span class="pill p-gray" style="height:18px;font-size:10.5px">{ic('lock', 10, 2.2)}必选</span></div>
      <div class="card-d">主图 6 · 副图 8 · 包裹 · 属性 12 · 场景 · 卖点 · 广告</div></div>
      <div class="opt-n">36<small>张</small></div></div>
    <div class="opt on"><div class="cb">{ic('check', 12, 3)}</div>
      <div><div style="font-weight:700">结构图 + 手持对比</div><div class="card-d">样品未到可取消，后续补图</div></div>
      <div class="opt-n">3<small>张</small></div></div>
    <div class="opt on"><div class="cb">{ic('check', 12, 3)}</div>
      <div><div style="font-weight:700">俄语套图 <span class="mono" style="font-weight:500;color:#6B7280;font-size:12px">900×1200</span></div><div class="card-d">俄语主图 12 · 俄语包裹图 6</div></div>
      <div class="opt-n">18<small>张</small></div></div>
    <div class="total"><div style="font-size:12px;color:#9CA3AF">本次合计</div><div style="font-size:26px;font-weight:700;line-height:1.2">57 <span style="font-size:13px;font-weight:500;color:#D1D5DB">张</span></div></div>
  </section>

  <div class="grid2">
    <!-- 左：商品信息 -->
    <section class="card" style="overflow:hidden">
      <div class="card-hd"><div class="card-t">商品信息</div><span class="pill p-brand">{ic('sparkles', 12, 2)}自动提取</span>
        <span class="pill p-warn" style="margin-left:auto">{ic('alert', 12, 2.2)}2 项待确认</span></div>
      <div class="f">
        <div class="lbl">品牌</div>
        <div class="row" style="gap:10px"><span class="logo-chip">RADIOMASTER</span><span style="font-weight:600">RadioMaster</span>
          <div class="row" style="margin-left:auto;gap:8px;font-size:12.5px;color:#374151">主图显示 LOGO<div class="switch"></div></div></div>
      </div>
      <div class="f" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div><div class="lbl">SPU</div><div class="mono" style="font-weight:700">RC4661</div></div>
        <div><div class="lbl">类目</div><div>航模遥控器</div></div>
      </div>
      <div class="f"><div class="lbl">英文标题</div>
        <div class="chips"><span class="chip">GX10 16CH Transmitter</span><span class="chip">GX10 16CH Radio</span><span class="chip">GX10 Radio</span></div></div>
      <div class="f"><div class="lbl">核心卖点</div>
        <div class="chips"><span class="chip">ELRS 2.4GHz</span><span class="chip">16CH</span><span class="chip">X4-V2 Hall Gimbal</span><span class="chip">2.8" IPS 触屏</span></div></div>
      <div class="f"><div class="lbl">俄语标题</div>
        <div style="font-size:12.5px;color:#374151;line-height:1.55">GX10 Radio — Встроенный сенсорный IPS-экран 2,8″ · Поддержка EdgeTX</div></div>
      <div class="f"><div class="row lbl" style="justify-content:space-between"><span>包装清单 · 13 项</span><span style="color:#4F46E5">展开编辑</span></div>
        <div style="font-size:12.5px;color:#374151;line-height:1.7">1 × GX10 Radio Controller　1 × Carry Case<br>1 × Gimbal Protector　1 × Replaceable Antenna <span class="faint">+9 项</span></div></div>
      <div class="f"><div class="lbl">关键参数 · 21 项</div>
        <div class="kv warn"><span class="k">工作电压</span><span style="font-weight:600">6.6 – 8.4V DC</span><button class="btn btn-sm btn-s" style="margin-left:auto">确认</button></div>
        <div class="kv warn" style="margin-top:4px"><span class="k">整机重量</span><span style="font-weight:600">456 g</span><button class="btn btn-sm btn-s" style="margin-left:auto">确认</button></div>
        <div class="kv"><span class="k">摇杆</span><span>X4-V2 Hall</span><span class="faint" style="margin-left:auto;font-size:11.5px">+18 项已校验</span></div>
      </div>
    </section>

    <!-- 右：参考图槽位 + SKU 组合 + 平台 -->
    <section class="card" style="display:flex;flex-direction:column;overflow:hidden">
      <div class="card-hd">
        <div class="card-t">参考图槽位</div>
        <div class="seg"><div class="on"><span class="swatch" style="background:#B9BDC3;width:12px;height:12px"></span>银灰色 · 7</div><div><span class="swatch" style="background:#3B3F46;width:12px;height:12px"></span>半透明黑 · 5</div></div>
        <div class="row" style="margin-left:auto;gap:6px;font-size:12px;color:#9CA3AF">{ic('move', 13)}拖拽图片可替换槽位</div>
      </div>
      <div style="padding:16px 20px">
        <div class="slots">
          {slot(gry(1), '正面', '普-灰 1.jpg')}{slot(gry(2), '背面', '普-灰 2.jpg')}{slot(gry(3), '斜侧', '普-灰 3.jpg')}
          {slot(gry(5), '左侧', '普-灰 5.jpg')}{slot(gry(6), '右侧', '普-灰 6.jpg')}{slot(gry(9), '特写', '普-灰 9.jpg')}
          {slot(gry(10), '合照', '普-灰 10.jpg')}
        </div>
      </div>
      <div style="padding:4px 20px 14px">
        <div class="row" style="gap:8px;margin-bottom:10px"><span class="sec-t">SKU 属性图组合</span><span class="pill p-gray">4 × 3 = 12 张</span>
          <span class="card-d" style="margin-left:auto">命名规则 <span class="mono" style="color:#374151">主SKU_配件SKU.jpg</span></span></div>
        <table class="mx">
          <tr><th style="width:190px">主 SKU</th><th>单机</th><th><span class="bat"><img src="{BAT1}"></span>+ RC4226A</th><th><span class="bat"><img src="{BAT2}"></span>+ RC3473</th></tr>
          {mx_row('RC4661A', '银灰', '#B9BDC3', 'FCC')}
          {mx_row('RC4661B', '银灰', '#B9BDC3', 'LBT')}
          {mx_row('RC4661C', '半透明黑', '#3B3F46', 'FCC')}
          {mx_row('RC4661D', '半透明黑', '#3B3F46', 'LBT')}
        </table>
      </div>
      <div style="margin-top:auto;padding:14px 20px 18px;border-top:1px solid #F1F2F5;background:#FCFCFD">
        <div class="plat">
          <div><div class="lbl">生图平台</div><div class="select"><span class="dot" style="background:#10B981"></span>球球Token{ic('chev-d', 14)}</div></div>
          <div><div class="lbl">模型</div><div class="select"><span class="mono">gpt-image-2</span>{ic('chev-d', 14)}</div></div>
          <div><div class="lbl">质量</div><div class="select">high{ic('chev-d', 14)}</div></div>
          <div style="padding-bottom:6px"><div class="row" style="gap:6px;font-size:12px;color:#6B7280">{ic('clock', 13)}预计约 20 分钟</div><div class="row" style="gap:6px;font-size:12px;color:#6B7280;margin-top:2px">{ic('zap', 13)}57 次调用 · 可随时暂停</div></div>
        </div>
      </div>
    </section>
  </div>
</div></div>
<footer class="ft">
  <button class="btn btn-g btn-lg">{ic('arrow-l', 15, 2)}上一步</button>
  <div class="row" style="margin-left:auto;gap:14px">
    <span class="card-d">还有 <b style="color:#B45309">2 项参数</b>待确认，确认后可开始</span>
    <button class="btn btn-p btn-lg">{ic('sparkles', 15, 2)}开始生成 57 张</button>
  </div>
</footer>"""

# ======================================================================
# 第三步：生成与验收
# ======================================================================
CSS3 = """
.layout{display:grid;grid-template-columns:1fr 420px;gap:20px;height:100%}
.sum{display:flex;align-items:center;gap:16px;padding:16px 20px;border-bottom:1px solid #F1F2F5}
.bar{flex:1;height:8px;border-radius:8px;background:#EEF0F3;overflow:hidden}
.bar i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#6366F1,#10B981);border-radius:8px}
.tabs{display:flex;align-items:center;gap:22px;padding:0 20px;border-bottom:1px solid #F1F2F5;height:46px}
.tab{height:46px;display:flex;align-items:center;gap:6px;font-size:13px;color:#6B7280;font-weight:600;border-bottom:2px solid transparent;margin-bottom:-1px}
.tab.on{color:#111827;border-bottom-color:#4F46E5}
.tab .c{font-size:11px;background:#F3F4F6;color:#6B7280;border-radius:9px;padding:0 6px;line-height:17px}
.tab.on .c{background:#EEF2FF;color:#4338CA}
.gal{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;padding:16px 20px}
.gi{border:1px solid #EEF0F3;border-radius:11px;overflow:hidden;background:#fff;position:relative}
.gi .img{aspect-ratio:1/1;background:#F5F6F8;display:flex;align-items:center;justify-content:center}
.gi .img img{width:100%;height:100%;object-fit:contain}
.gi .cap{padding:7px 10px 8px}
.gi .nm{font-size:12px;font-weight:600;color:#111827}
.gi .mt{display:flex;align-items:center;justify-content:space-between;font-size:11px;color:#9CA3AF;margin-top:1px}
.gi.sel{border-color:#4F46E5;box-shadow:0 0 0 3px #E0E7FF}
.gtag{position:absolute;left:7px;top:7px;background:rgba(17,24,39,.72);color:#fff;font-size:10.5px;font-weight:600;border-radius:5px;padding:0 6px;line-height:18px}
.gwarn{position:absolute;right:7px;top:7px;background:#F59E0B;color:#fff;font-size:10.5px;font-weight:600;border-radius:5px;padding:0 6px;line-height:18px;display:flex;align-items:center;gap:3px}
.gcb{position:absolute;right:7px;top:7px;width:18px;height:18px;border-radius:5px;background:#4F46E5;color:#fff;display:flex;align-items:center;justify-content:center}
.insp-sec{padding:12px 20px;border-bottom:1px solid #F5F6F8}
.prev{height:252px;background:#F5F6F8;border-radius:12px;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;border:1px solid #EEF0F3}
.prev img{height:100%;object-fit:contain}
.prev-tools{position:absolute;right:10px;top:10px;display:flex;gap:6px}
.prev-tools div{width:28px;height:28px;border-radius:7px;background:rgba(255,255,255,.9);border:1px solid #E5E7EB;display:flex;align-items:center;justify-content:center;color:#4B5563}
.ver{display:flex;gap:8px;align-items:center;margin-top:10px}
.vt{width:44px;height:44px;border-radius:8px;border:1px solid #EEF0F3;overflow:hidden;background:#F5F6F8;position:relative}
.vt img{width:100%;height:100%;object-fit:contain}
.vt.on{border:2px solid #4F46E5}
.vt span{position:absolute;left:2px;bottom:2px;font-size:9.5px;background:rgba(17,24,39,.75);color:#fff;border-radius:3px;padding:0 3px;line-height:13px}
.meta{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.meta>div{background:#FAFAFB;border:1px solid #F1F2F5;border-radius:8px;padding:6px 10px}
.meta .k{font-size:11px;color:#9CA3AF}
.meta .v{font-size:12.5px;font-weight:600}
.refs{display:flex;gap:8px}
.ref{width:52px;height:52px;border-radius:8px;border:1px solid #EEF0F3;overflow:hidden;background:#F7F8FA}
.ref img{width:100%;height:100%;object-fit:contain}
.ref-add{width:52px;height:52px;border-radius:8px;border:1.5px dashed #D1D5DB;display:flex;align-items:center;justify-content:center;color:#9CA3AF}
.prompt{height:150px;border:1px solid #E5E7EB;border-radius:10px;padding:10px 12px;font-size:12px;line-height:1.7;color:#374151;background:#FCFCFD;overflow:hidden;box-shadow:0 0 0 3px #EEF2FF;border-color:#A5B4FC}
.prompt mark{background:#FEF3C7;color:#92400E;border-radius:3px;padding:0 2px}
"""


def gi(img, name, size, tag, sel=False, warn=False):
    flag = ""
    if sel:
        flag = f'<span class="gcb">{ic("check", 11, 3)}</span>'
    elif warn:
        flag = f'<span class="gwarn">{ic("alert", 10, 2.4)}待复核</span>'
    status = ('<span class="row" style="gap:4px;color:#B45309"><span class="dot" style="background:#F59E0B;width:6px;height:6px"></span>待复核</span>' if warn
              else '<span class="row" style="gap:4px;color:#047857"><span class="dot" style="background:#10B981;width:6px;height:6px"></span>通过</span>')
    return f"""<div class="gi {'sel' if sel else ''}"><div class="img"><img src="{img}"></div>
    <span class="gtag">{tag}</span>{flag}
    <div class="cap"><div class="nm ell">{name}</div><div class="mt"><span class="mono">{size}</span>{status}</div></div></div>"""


right3 = f"""<div class="vsep"></div>
<div class="row" style="gap:10px">
  <button class="btn btn-s">{ic('refresh', 14)}重绘所选 (1)</button>
  <button class="btn btn-p">{ic('download', 14, 2)}导出通途图库包</button>
</div>"""

step3_main = header(3, right3) + f"""
<div class="content"><div class="layout">
  <section class="card" style="display:flex;flex-direction:column;overflow:hidden">
    <div class="sum">
      <div class="row" style="gap:10px"><div style="width:32px;height:32px;border-radius:50%;background:#ECFDF5;color:#059669;display:flex;align-items:center;justify-content:center">{ic('check', 17, 2.6)}</div>
        <div style="line-height:1.35"><div style="font-weight:700;font-size:14px">生成完成</div><div class="card-d">57 / 57 · 用时 18 分 32 秒</div></div></div>
      <div class="bar"><i></i></div>
      <span class="pill p-ok">54 通过</span><span class="pill p-warn">3 待复核</span>
      <span class="pill p-gray">尺寸合规 100%</span>
    </div>
    <div class="tabs">
      <div class="tab on">全部<span class="c">57</span></div>
      <div class="tab">主图<span class="c">6</span></div>
      <div class="tab">白底副图<span class="c">8</span></div>
      <div class="tab">属性图<span class="c">12</span></div>
      <div class="tab">详情 / 卖点<span class="c">13</span></div>
      <div class="tab">俄语<span class="c">18</span></div>
      <div class="tab" style="color:#B45309">待复核<span class="c" style="background:#FFFBEB;color:#B45309">3</span></div>
      <div class="row" style="margin-left:auto;gap:6px;font-size:12px;color:#6B7280">{ic('grid', 14)}网格视图</div>
    </div>
    <div class="gal">
      {gi(out('主图1.jpg'), '主图1.jpg', '1000²', '9imod')}
      {gi(out('主图2.jpg'), '主图2.jpg', '1000²', 'Moonhobby')}
      {gi(out('主图4.jpg'), '主图4.jpg', '1000²', '9imod 全托')}
      {gi(out('主图6.jpg'), '主图6.jpg', '1000²', 'FCFT')}
      {gi(out('zt(1).jpg'), 'zt(1).jpg', '1000²', '白底副图')}
      {gi(out('包裹图.jpg'), '包裹图.jpg', '1000²', '包裹图')}
      {gi(out('RC4661A_RC4226A.jpg'), 'RC4661A_RC4226A.jpg', '1000²', '属性图', sel=True)}
      {gi(out('详情图(1)_场景图.jpg'), '详情图(1)_场景图.jpg', '1000²', '场景图')}
      {gi(out('详情图(6)_卖点_霍尔摇杆.jpg'), '详情图(6)_霍尔摇杆.jpg', '1000²', '卖点图')}
      {gi(out('详情图(8)_参数表.jpg'), '详情图(8)_参数表.jpg', '1000²', '参数表', warn=True)}
      {gi(out('详情图(9)_结构图_正面.jpg'), '详情图(9)_结构正面.jpg', '1000²', '结构图')}
      {gi(out('详情图(11)_手持实拍对比图.jpg'), '详情图(11)_手持.jpg', '1000²', '手持对比')}
      {gi(out('750X1000.jpg'), '750X1000.jpg', '750×1000', '广告图')}
      {gi(out('RC4661C俄文1.jpg'), 'RC4661C俄文1.jpg', '900×1200', '俄语主图', warn=True)}
      {gi(out('RC4661B_RC4226A俄文4.jpg'), 'RC4661B_RC4226A俄文4.jpg', '900×1200', '俄语包裹', warn=True)}
    </div>
  </section>

  <!-- 右：单图检查器 -->
  <section class="card" style="display:flex;flex-direction:column;overflow:hidden">
    <div class="card-hd" style="padding:14px 20px">
      <div style="min-width:0"><div class="card-t mono ell" style="font-size:13.5px">RC4661A_RC4226A.jpg</div>
      <div class="card-d">属性图 · 银灰 FCC + RC4226A 电池</div></div>
      <div class="row" style="margin-left:auto;gap:4px;color:#9CA3AF">{ic('more', 18)}{ic('x', 18)}</div>
    </div>
    <div class="insp-sec">
      <div class="prev"><img src="{out('RC4661A_RC4226A.jpg')}">
        <div class="prev-tools"><div>{ic('maximize', 14)}</div><div>{ic('download', 14)}</div></div></div>
      <div class="ver">
        <span class="lbl" style="margin:0 6px 0 0">版本</span>
        <div class="vt"><img src="{out('RC4661A_RC4226A.jpg')}" style="filter:saturate(.6) brightness(1.05)"><span>v1</span></div>
        <div class="vt on"><img src="{out('RC4661A_RC4226A.jpg')}"><span>v2</span></div>
        <div class="meta" style="margin-left:auto;grid-template-columns:auto auto;gap:6px">
          <div><div class="k">尺寸</div><div class="v mono">1000×1000</div></div>
          <div><div class="k">耗时</div><div class="v">21.6 s</div></div>
        </div>
      </div>
    </div>
    <div class="insp-sec">
      <div class="lbl">参考图</div>
      <div class="refs">
        <div class="ref"><img src="{gry(10)}"></div><div class="ref"><img src="{BAT1}"></div>
        <div class="ref-add">{ic('plus', 16)}</div>
        <div class="card-d" style="align-self:center;margin-left:6px;line-height:1.5">配件合照 + 共享电池<br>多图联合输入</div>
      </div>
    </div>
    <div class="insp-sec" style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <div><div class="lbl">平台</div><div class="select"><span class="dot" style="background:#10B981"></span>球球Token{ic('chev-d', 14)}</div></div>
      <div><div class="lbl">模型</div><div class="select"><span class="mono">gpt-image-2</span>{ic('chev-d', 14)}</div></div>
    </div>
    <div class="insp-sec" style="border-bottom:none;flex:1">
      <div class="row lbl" style="justify-content:space-between"><span>提示词</span><span class="pill p-warn" style="height:18px;font-size:10.5px">已修改</span></div>
      <div class="prompt">制作一张 1000 × 1000 px、1:1 方版的电商 SKU 属性图。以图1 银灰色 GX10 配件合照和图2 两节 18650 锂电池为合成素材，保持外观与细节可辨识。顶部通栏 82 px，左 78% 深石墨底排白色粗体「GX10 16CH Radio」，右 22% <mark>亮红色斜切块排「FCC」</mark>。右上方横排「18650 Lipo Battery」，下方<mark>水平正立</mark>放置两节电池……</div>
    </div>
    <div style="padding:14px 20px 18px;display:flex;gap:10px;border-top:1px solid #F1F2F5">
      <button class="btn btn-p btn-lg" style="flex:1">{ic('refresh', 15, 2)}重新生成此图 · 约 20s</button>
      <button class="btn btn-s btn-lg">{ic('bookmark', 15)}存为模板</button>
    </div>
  </section>
</div></div>"""

PAGES = [
    ("v2_step1.html", page(CSS1, step1_main), "UI_步骤1_素材投递与智能预检.png"),
    ("v2_step2.html", page(CSS2, step2_main), "UI_步骤2_1分钟参数与图片槽位核对.png"),
    ("v2_step3.html", page(CSS3, step3_main), "UI_步骤3_批量生图看板与单图重绘.png"),
]

for html_name, html, png_name in PAGES:
    html_path = os.path.join(UI_DIR, html_name)
    png_path = os.path.join(UI_DIR, png_name)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--allow-file-access-from-files",
        "--hide-scrollbars", "--force-device-scale-factor=2", "--window-size=1600,1000",
        f"--screenshot={png_path}", u(html_path),
    ], check=True, capture_output=True)
    shutil.copyfile(png_path, os.path.join(ART_DIR, png_name))
    print("Rendered:", png_path)
