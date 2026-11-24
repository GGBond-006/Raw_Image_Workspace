/* ==========================================================================
   AutoShot 生图台 · 三步交互逻辑与真实后端联调
   ========================================================================== */
const ICONS = {
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  alert: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  folder: '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
  image: '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
  grid: '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
  tag: '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1"/>',
  sparkles: '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 3v4"/><path d="M21 5h-4"/>',
  cpu: '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
  "chev-r": '<path d="m9 18 6-6-6-6"/>',
  "arrow-r": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  "arrow-l": '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
  file: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M8 13h8M8 17h8M8 9h2"/>',
  sheet: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M8 13h2M14 13h2M8 17h2M14 17h2"/>',
  clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
  plus: '<path d="M5 12h14M12 5v14"/>',
  zap: '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
  ban: '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
  bookmark: '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
  move: '<path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"/>',
  lock: '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  maximize: '<path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/>',
  pause: '<rect width="4" height="16" x="6" y="4" rx="1"/><rect width="4" height="16" x="14" y="4" rx="1"/>',
  play: '<polygon points="6 3 20 12 6 21 6 3"/>',
};

function ic(name, size = 16, sw = 1.8) {
  return `<svg class="ic" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ""}</svg>`;
}

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function imgUrl(path, cacheKey = "", thumbW = 0) {
  if (!path) return "";
  return `/api/local-image?path=${encodeURIComponent(path)}${thumbW ? `&w=${thumbW}` : ""}${cacheKey ? `&t=${cacheKey}` : ""}`;
}

function downloadUrl(path) {
  return `/api/download-image?path=${encodeURIComponent(path)}`;
}

async function api(url, opts = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ---------------- 前端状态 ----------------
const appState = {
  step: 1,
  data: null,
  activeColorId: null,
  activeTab: "all",
  selectedFilename: null,
  checkedFiles: new Set(),
  inspectorDraft: {}, // { filename: { prompt, refs, provider_id, model_name } }
  singleBusyFile: null,
  singleBusySeconds: 0,
  singleTimer: null,
  pollTimer: null,
  dragRole: null,
};

// ---------------- Toast / 灯箱 / 弹窗 ----------------
function toast(msg, type = "default") {
  const stack = document.getElementById("toastStack");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  const iconName = type === "ok" ? "check" : type === "warn" ? "alert" : type === "bad" ? "ban" : "sparkles";
  el.innerHTML = `${ic(iconName, 15, 2.2)}<span>${esc(msg)}</span>`;
  stack.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transition = "opacity .25s";
    setTimeout(() => el.remove(), 260);
  }, 3000);
}

function openLightbox(path, title = "", meta = "", cacheKey = "") {
  if (!path) return;
  document.getElementById("lbTitle").textContent = title || path.split("/").pop();
  document.getElementById("lbMeta").textContent = meta || "";
  document.getElementById("lbImg").src = imgUrl(path, cacheKey);
  document.getElementById("lbDownload").href = downloadUrl(path);
  document.getElementById("lightbox").classList.remove("hidden");
}

function closeLightbox() {
  document.getElementById("lightbox").classList.add("hidden");
}

function openModal({ title, bodyHtml, footerHtml = "", large = false }) {
  const box = document.getElementById("modalBox");
  box.className = `modal ${large ? "modal-lg" : ""}`;
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalBody").innerHTML = bodyHtml;
  document.getElementById("modalFooter").innerHTML = footerHtml;
  document.getElementById("modalBackdrop").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("modalBackdrop").classList.add("hidden");
}

// ---------------- 初始化图标与静态事件 ----------------
function hydrateStaticIcons() {
  document.getElementById("logoMark").innerHTML = ic("sparkles", 18, 2);
  document.querySelectorAll(".ic-slot").forEach((el) => {
    el.innerHTML = ic(el.dataset.ic, Number(el.dataset.sz || 16), 1.8);
  });
}

function bindGlobalEvents() {
  // 左侧步骤切换
  document.querySelectorAll("#stepper .st").forEach((btn) => {
    btn.addEventListener("click", () => goStep(Number(btn.dataset.step)));
  });

  // 左侧主导航
  document.querySelectorAll(".sb-nav .nav").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.nav;
      if (target === "tasks") return;
      if (target === "providers") {
        openProviderModal();
        return;
      }
      const names = {
        dashboard: "工作台",
        assets: "素材库",
        brands: "品牌 LOGO 库",
        templates: "提示词模板",
      };
      toast(`「${names[target]}」将在核心三步体验确认后开放`, "default");
    });
  });

  document.getElementById("sidebarProviderCard").addEventListener("click", openProviderModal);
  document.getElementById("openProviderModalBtn").addEventListener("click", openProviderModal);
  document.getElementById("sbSearchBtn").addEventListener("click", openQuickSearchModal);

  // 第三步页头按钮
  document.getElementById("btnOpenOutputDir").addEventListener("click", async () => {
    try {
      await api("/api/open-folder", { method: "POST", body: JSON.stringify({}) });
      toast("已在资源管理器中打开输出目录", "ok");
    } catch (e) {
      toast(e.message, "bad");
    }
  });

  document.getElementById("btnExportTongtool").addEventListener("click", () => {
    const a = document.createElement("a");
    a.href = "/api/export/tongtool";
    a.download = "";
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast("正在打包导出通途 ERP 图库包（含 图片组对应关系.csv）", "ok");
  });

  // 弹窗与灯箱关闭
  document.getElementById("modalCloseBtn").addEventListener("click", closeModal);
  document.getElementById("modalBackdrop").addEventListener("click", (e) => {
    if (e.target.id === "modalBackdrop") closeModal();
  });
  document.getElementById("lbCloseBtn").addEventListener("click", closeLightbox);
  document.getElementById("lbStage").addEventListener("click", (e) => {
    if (e.target.id === "lbStage") closeLightbox();
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeLightbox();
      closeModal();
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openQuickSearchModal();
    }
  });
}

// ---------------- 步骤切换与全局刷新 ----------------
function goStep(step) {
  if (!appState.data?.scan && step > 1) {
    toast("请先导入并扫描商品素材文件夹", "warn");
    return;
  }
  appState.step = step;
  renderAll();
}

function renderAll() {
  renderChrome();
  document.getElementById("stepView1").classList.toggle("hidden", appState.step !== 1);
  document.getElementById("stepView2").classList.toggle("hidden", appState.step !== 2);
  document.getElementById("stepView3").classList.toggle("hidden", appState.step !== 3);
  document.getElementById("step3HeaderActions").classList.toggle("hidden", appState.step !== 3);
  document.getElementById("bottomFooter").classList.toggle("hidden", appState.step === 3);

  if (appState.step === 1) renderStep1();
  if (appState.step === 2) renderStep2();
  if (appState.step === 3) renderStep3();
  renderFooter();
}

function renderChrome() {
  const d = appState.data;
  if (!d) return;

  // 页头标题
  const spu = d.scan?.spu_code || "未加载";
  const pname = d.scan?.product_display_name || "请选择素材文件夹";
  const brand = d.task_config?.product_meta?.brand_name || "";
  document.getElementById("hdSpu").textContent = spu;
  document.getElementById("hdTitle").textContent = pname;
  const bp = document.getElementById("hdBrandPill");
  bp.textContent = brand || "未识别品牌";
  bp.classList.toggle("hidden", !brand);

  // 步骤条状态
  document.querySelectorAll("#stepper .st").forEach((btn) => {
    const s = Number(btn.dataset.step);
    const numEl = btn.querySelector(".n");
    btn.classList.remove("on", "done");
    if (s < appState.step) {
      btn.classList.add("done");
      numEl.innerHTML = ic("check", 13, 2.6);
    } else if (s === appState.step) {
      btn.classList.add("on");
      numEl.textContent = String(s);
    } else {
      numEl.textContent = String(s);
    }
  });
  document.getElementById("stLine1").classList.toggle("done", appState.step > 1);
  document.getElementById("stLine2").classList.toggle("done", appState.step > 2);

  // 侧边栏平台状态
  const prov = (d.providers || []).find((p) => p.id === d.selected_provider) || d.providers?.[0];
  if (prov) {
    document.getElementById("sbProviderName").textContent = prov.display_name;
    document.getElementById("sbProviderMeta").textContent = `${d.selected_model} · 平均 21s / 张`;
    const badge = document.getElementById("sbProviderStatus");
    badge.className = `row sb-st-badge ${prov.has_token ? "" : "warn"}`;
    badge.innerHTML = `<span class="dot"></span>${prov.has_token ? "正常" : "未配令牌"}`;
  }

  // 最近任务
  const recent = document.getElementById("recentTasksList");
  recent.innerHTML = `
    <button class="recent on">
      <span class="dot" style="background:${d.batch?.running ? "#F59E0B" : "#6366F1"}"></span>
      <span class="ell">${esc(spu)} · ${esc(pname)}</span>
    </button>
    <button class="recent" id="btnAddNewTaskFolder">
      <span class="ic-slot" style="color:#9CA3AF">${ic("plus", 13, 2)}</span>
      <span class="ell" style="color:#6B7280">导入其他商品文件夹...</span>
    </button>
  `;
  document.getElementById("btnAddNewTaskFolder").addEventListener("click", handlePickFolder);
}

function renderFooter() {
  const ft = document.getElementById("bottomFooter");
  const d = appState.data;
  if (!d || appState.step === 3) return;

  if (appState.step === 1) {
    ft.innerHTML = `
      <div class="row" style="gap:8px;color:#6B7280;font-size:12.5px">
        ${ic("shield", 15)}
        <span>系统已自动过滤海报、详情切片和低清缩略图，不会用于生图</span>
      </div>
      <div class="row" style="margin-left:auto;gap:10px">
        <button class="btn btn-s btn-lg" id="s1EnterPathBtn">手动输入路径</button>
        <button class="btn btn-p btn-lg" id="s1NextBtn">下一步：核对参数 ${ic("arrow-r", 15, 2.2)}</button>
      </div>
    `;
    document.getElementById("s1EnterPathBtn").addEventListener("click", openPathInputModal);
    document.getElementById("s1NextBtn").addEventListener("click", () => goStep(2));
  } else if (appState.step === 2) {
    const pendingConfirms = (d.confirm_fields || []).filter((f) => !f.confirmed).length;
    const total = d.scope_counts?.selected_total || 0;
    const hint = pendingConfirms > 0
      ? `还有 <b style="color:#B45309">${pendingConfirms} 项参数</b>待确认　<button class="btn-link" id="btnConfirmAllInline">一键全部确认</button>`
      : `<span class="row" style="gap:5px;color:#047857;font-weight:600">${ic("check", 14, 2.5)} 全部参数已确认，可开始生成</span>`;

    ft.innerHTML = `
      <button class="btn btn-g btn-lg" id="s2PrevBtn">${ic("arrow-l", 15, 2)}上一步</button>
      <div class="row" style="margin-left:auto;gap:16px">
        <span class="card-d">${hint}</span>
        <button class="btn btn-p btn-lg" id="s2StartBtn">${ic("sparkles", 15, 2)}开始生成 ${total} 张</button>
      </div>
    `;
    document.getElementById("s2PrevBtn").addEventListener("click", () => goStep(1));
    document.getElementById("btnConfirmAllInline")?.addEventListener("click", async () => {
      await updateTask({ confirm_all: true }, "已确认全部待核对参数");
    });
    document.getElementById("s2StartBtn").addEventListener("click", openLaunchDialog);
  }
}

// ==========================================================================
// 第一步：导入素材
// ==========================================================================
function renderStep1() {
  const root = document.getElementById("stepView1");
  const prevS1Scroll = root.querySelector(".s1-scroll")?.scrollTop || 0;
  const scan = appState.data?.scan;
  if (!scan) {
    root.innerHTML = `
      <div class="card" style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">
        <div class="fold-ic" style="width:56px;height:56px">${ic("folder", 26)}</div>
        <div style="font-size:16px;font-weight:700">选择商品原始素材文件夹</div>
        <div class="card-d">支持直接拖入或选择包含《图片需求.xls》和高清白底图的本地目录</div>
        <div class="row" style="gap:10px;margin-top:6px">
          <button class="btn btn-p btn-lg" id="emptyPickBtn">${ic("upload", 15)}选择本地文件夹</button>
          <button class="btn btn-s btn-lg" id="emptyInputBtn">输入文件夹路径</button>
        </div>
      </div>`;
    document.getElementById("emptyPickBtn").addEventListener("click", handlePickFolder);
    document.getElementById("emptyInputBtn").addEventListener("click", openPathInputModal);
    return;
  }

  const docsHtml = (scan.documents || []).map((doc) => {
    const isSheet = doc.type === "requirement";
    return `
      <div class="doc">
        <div class="doc-ic" style="background:${isSheet ? "#ECFDF5" : "#EFF6FF"};color:${isSheet ? "#059669" : "#2563EB"}">
          ${ic(isSheet ? "sheet" : "file", 18)}
        </div>
        <div style="flex:1;min-width:0">
          <div class="ell" style="font-weight:600" title="${esc(doc.name)}">${esc(doc.name)}</div>
          <div class="card-d ell">${esc(doc.summary || `${doc.size_kb} KB`)}</div>
        </div>
        <span class="pill p-ok">${ic("check", 12, 2.6)}已解析</span>
      </div>`;
  }).join("") || `<div class="card-d">未发现需求文档，已根据图片目录结构自动初始化任务</div>`;

  const colorsHtml = (scan.color_groups || []).map((cg) => {
    const cells = cg.slots.map((slot) => {
      if (slot.image) {
        return `
          <div class="tcell">
            <div class="thumb" data-lb-path="${esc(slot.image.path)}" data-lb-title="${esc(slot.image.name)}" data-lb-meta="${slot.image.width}×${slot.image.height} · ${slot.image.size_kb} KB">
              <img src="${imgUrl(slot.image.path, "", 320)}" />
            </div>
            <div class="tcap ell">${esc(slot.label)}</div>
            <div class="tmeta mono">${slot.image.width}×${slot.image.height}</div>
          </div>`;
      }
      const isReuse = Boolean(slot.reused_from);
      return `
        <div class="tcell">
          <div class="ghost">${ic(isReuse ? "link" : "image", 16)}<span>${isReuse ? `复用${esc(slot.reused_from)}` : "待补充"}</span></div>
          <div class="tcap ell" style="color:#9CA3AF">${esc(slot.label)}</div>
          <div class="tmeta">${esc(slot.reuse_note || (isReuse ? "自动共用" : "原包缺失"))}</div>
        </div>`;
    }).join("");

    return `
      <div class="s1-sec">
        <div class="s1-sec-hd">
          <span class="swatch" style="background:${cg.swatch}"></span>
          <span class="sec-t">${esc(cg.color_name_cn)} · ${esc(cg.color_id)}</span>
          <span class="pill p-gray">${cg.count} 张</span>
          <span class="card-d" style="margin-left:auto">文件夹：${esc(cg.folder_label)}</span>
        </div>
        <div class="thumbs-7">${cells}</div>
      </div>`;
  }).join("");

  const excludedHtml = (scan.excluded_preview || []).map((ex) => `
    <div class="exi" data-lb-path="${esc(ex.path)}" data-lb-title="${esc(ex.name)}" data-lb-meta="已自动排除 · ${esc(ex.reason)} (${ex.width}×${ex.height})">
      <div class="thumb"><img src="${imgUrl(ex.path, "", 160)}" /></div>
      <div style="min-width:0">
        <div class="ell" style="font-size:12px;font-weight:600;color:#4B5563" title="${esc(ex.name)}">${esc(ex.name)}</div>
        <div class="row" style="gap:4px;font-size:11px;color:#B91C1C">${ic("ban", 11, 2)}<span class="ell">${esc(ex.reason)}</span></div>
      </div>
    </div>
  `).join("");

  const checksHtml = (scan.preflight?.checks || []).map((c) => {
    const tone = c.status === "ok"
      ? { bg: "#ECFDF5", fg: "#059669", icon: "check" }
      : c.status === "fix"
        ? { bg: "#FFFBEB", fg: "#D97706", icon: "refresh" }
        : { bg: "#FFFBEB", fg: "#D97706", icon: "alert" };
    const rightBadge = c.badge ? `<span class="logo-chip">${esc(c.badge)}</span>` : "";
    return `
      <div class="chk">
        <div class="chk-ic" style="background:${tone.bg};color:${tone.fg}">${ic(tone.icon, 14, 2.4)}</div>
        <div style="flex:1;min-width:0">
          <div class="chk-t">${esc(c.title)}</div>
          <div class="chk-d">${esc(c.desc)}</div>
        </div>
        ${rightBadge}
      </div>`;
  }).join("");

  root.innerHTML = `
    <div class="s1-layout">
      <section class="card s1-left">
        <div class="card-hd">
          <div class="fold-ic">${ic("folder", 20)}</div>
          <div style="min-width:0;flex:1">
            <div class="card-t ell">${esc(scan.folder_name)}</div>
            <div class="card-d mono ell" title="${esc(scan.folder_path)}">${esc(scan.folder_path)}</div>
          </div>
          <div class="row" style="gap:8px;flex-shrink:0">
            <button class="btn btn-s" id="s1RescanBtn">${ic("refresh", 14)}重新扫描</button>
            <button class="btn btn-s" id="s1PickFolderBtn">${ic("upload", 14)}更换文件夹</button>
          </div>
        </div>

        <div class="stats">
          <div class="stat"><div class="k">扫描文件</div><div class="v">${scan.stats.total_files}</div></div>
          <div class="stat"><div class="k">识别文档</div><div class="v">${scan.stats.doc_count}</div></div>
          <div class="stat"><div class="k">可用素材图</div><div class="v" style="color:#059669">${scan.stats.usable_images}</div></div>
          <div class="stat"><div class="k">自动排除</div><div class="v" style="color:#9CA3AF">${scan.stats.excluded_images}</div></div>
        </div>

        <div class="s1-scroll">
          <div class="s1-sec">
            <div class="s1-sec-hd"><span class="sec-t">需求文档</span></div>
            <div class="docs">${docsHtml}</div>
          </div>

          ${colorsHtml}

          <div class="s1-sec" style="padding-bottom:10px">
            <div class="s1-sec-hd">
              <span class="sec-t">已自动排除</span>
              <span class="pill p-gray">${scan.stats.excluded_images} 张</span>
              <button class="btn-link" id="s1ViewAllExcluded" style="margin-left:auto">查看全部</button>
            </div>
            <div class="ex-grid">${excludedHtml}</div>
          </div>
        </div>
      </section>

      <div class="s1-right">
        <section class="card">
          <div class="hero ${scan.preflight.ready ? "" : "warn"}">
            <div class="hero-ic">${ic(scan.preflight.ready ? "check" : "alert", 22, 2.6)}</div>
            <div>
              <div style="font-size:15px;font-weight:700">${scan.preflight.ready ? "素材已就绪" : "需要补充素材"}</div>
              <div class="card-d">${scan.preflight.blocking_count} 项阻塞 · ${scan.preflight.auto_fixed_count} 项已自动修正 · 可进入下一步</div>
            </div>
          </div>
          ${checksHtml}
        </section>

        <section class="card">
          <div class="card-hd" style="padding:13px 20px">
            <div class="card-t">人工只需整理 3 件事</div>
            <span class="pill p-brand" style="margin-left:auto">约 1–2 分钟</span>
          </div>
          <div class="howto">
            <div class="hstep"><div class="hn">1</div><div>按颜色建子文件夹，例如 <b>颜色1_银灰色</b></div></div>
            <div class="hstep"><div class="hn">2</div><div>每色放 5–7 张 <b>≥1000px 无字白底图</b></div></div>
            <div class="hstep"><div class="hn">3</div><div>放 1 张<b>无字配件合照</b>，其余文件原样保留</div></div>
            <div class="tree mono"><b>${esc(scan.folder_name)}/</b>
├─ ${esc(scan.documents[0]?.name || "RCxxxx 图片需求.xls")}
├─ ${esc(scan.documents[1]?.name || "产品报价单.xlsx")}
├─ <b>颜色1_银灰色/</b>   <i>正面 背面 斜侧 … 合照</i>
├─ <b>颜色2_半透明黑/</b> <i>正面 背面 斜侧 …</i>
└─ 供应商原始资料/   <i>原样放入，自动过滤</i></div>
          </div>
        </section>
      </div>
    </div>`;

  const newS1Scroll = root.querySelector(".s1-scroll");
  if (newS1Scroll) newS1Scroll.scrollTop = prevS1Scroll;

  document.getElementById("s1RescanBtn").addEventListener("click", () => scanFolder(scan.folder_path));
  document.getElementById("s1PickFolderBtn").addEventListener("click", handlePickFolder);
  document.getElementById("s1ViewAllExcluded").addEventListener("click", openExcludedModal);
  root.querySelectorAll("[data-lb-path]").forEach((el) => {
    el.addEventListener("click", () => openLightbox(el.dataset.lbPath, el.dataset.lbTitle, el.dataset.lbMeta));
  });
}

// ==========================================================================
// 第二步：核对参数
// ==========================================================================
function renderStep2() {
  const root = document.getElementById("stepView2");
  const d = appState.data;
  const cfg = d?.task_config;
  const scan = d?.scan;
  if (!cfg || !scan) return;

  // 保存当前左右两个 .s2-body 与主容器滚动条位置，防止点击「确认」等操作后跳回顶部
  const prevS2Scrolls = Array.from(root.querySelectorAll(".s2-body")).map((el) => el.scrollTop);
  const viewRoot = document.getElementById("viewRoot");
  const prevViewScroll = viewRoot ? viewRoot.scrollTop : 0;

  const flags = cfg.generation_flags;
  const counts = d.scope_counts;
  const useOpt = Boolean(flags.generate_structure_diagram || flags.generate_handheld_comparison);
  const useRu = Boolean(flags.generate_russian_suite);
  const meta = cfg.product_meta;
  const en = cfg.copywriting_en;
  const ru = cfg.copywriting_ru;

  if (!appState.activeColorId || !scan.color_groups.some((c) => c.color_id === appState.activeColorId)) {
    appState.activeColorId = scan.color_groups[0]?.color_id || null;
  }
  const activeColor = scan.color_groups.find((c) => c.color_id === appState.activeColorId) || scan.color_groups[0];

  const pendingConfirms = (d.confirm_fields || []).filter((f) => !f.confirmed).length;

  const confirmRowsHtml = (d.confirm_fields || []).map((cf) => `
    <div class="kv ${cf.confirmed ? "ok-row" : "warn"}">
      <span class="k">${esc(cf.label)}</span>
      <input class="kv-edit" data-cf-input="${esc(cf.id)}" value="${esc(cf.value)}" />
      <button class="btn btn-sm ${cf.confirmed ? "btn-g" : "btn-s"}" data-cf-btn="${esc(cf.id)}">
        ${cf.confirmed ? `${ic("check", 12, 2.6)}已确认` : "确认"}
      </button>
    </div>
  `).join("");

  const otherSpecCount = Math.max(0, (en.specifications?.length || 0) - (d.confirm_fields?.length || 0));
  const gimbalSpec = (en.specifications || []).find((s) => s.key.toLowerCase() === "gimbal");

  const pkgPreview = (en.package_includes || []).slice(0, 4).map((it) => `${it.qty} × ${it.name_en}`);
  const pkgMore = Math.max(0, (en.package_includes?.length || 0) - 4);

  // 颜色切换 Segmented Control
  const segHtml = scan.color_groups.map((cg) => `
    <button class="${cg.color_id === activeColor?.color_id ? "on" : ""}" data-color-tab="${esc(cg.color_id)}">
      <span class="swatch" style="background:${cg.swatch};width:12px;height:12px"></span>
      <span>${esc(cg.color_name_cn)} · ${cg.count}</span>
    </button>
  `).join("");

  // 7 个参考图槽位（支持拖拽交换 + 点击替换/查看大图）
  const slotsHtml = (activeColor?.slots || []).map((s) => {
    if (s.image) {
      return `
        <div class="slot-card" draggable="true" data-slot-role="${esc(s.role)}">
          <div class="thumb">
            <img src="${imgUrl(s.image.path, "", 320)}" draggable="false" />
            <span class="slot-role">${esc(s.label.replace("45° ", "").replace("面", "").replace("摇杆", "").replace("细节", "").replace("配件", ""))}</span>
            <span class="slot-ok">${ic("check", 10, 3)}</span>
            <div class="slot-actions">
              <button class="slot-act-btn" data-slot-view="${esc(s.image.path)}" data-slot-name="${esc(s.image.name)}">预览</button>
              <button class="slot-act-btn" data-slot-replace="${esc(s.role)}">替换</button>
            </div>
          </div>
          <div class="ell" style="font-size:12px;font-weight:600;margin-top:6px" title="${esc(s.image.name)}">${esc(s.image.name)}</div>
          <div class="tmeta mono">${s.image.width}×${s.image.height}</div>
        </div>`;
    }
    const isReuse = Boolean(s.reused_from);
    return `
      <div class="slot-card" data-slot-role="${esc(s.role)}">
        <div class="ghost" style="cursor:pointer" data-slot-replace="${esc(s.role)}" title="${isReuse ? "点击可上传本色专属图片" : "点击上传补充该视角图片"}">
          ${ic(isReuse ? "link" : "upload", 15)}
          <span>${isReuse ? `复用${esc(s.reused_from)}` : "点击补图"}</span>
        </div>
        <div class="ell" style="font-size:12px;font-weight:600;margin-top:6px;color:#9CA3AF">${esc(s.label)}</div>
        <div class="tmeta">${esc(s.reuse_note || (isReuse ? "点击可指定" : "原包缺失"))}</div>
      </div>`;
  }).join("");

  // SKU 属性图组合矩阵
  const pkgs = cfg.bundled_packages || [];
  const colorMap = {};
  (cfg.color_variants || []).forEach((c) => { colorMap[c.color_id] = c; });

  const mxHeaders = pkgs.map((p) => {
    if (!p.accessory_sku) return `<th>单机</th>`;
    const thumb = p.accessory_cutout_png ? `<span class="bat"><img src="${imgUrl(p.accessory_cutout_png)}" /></span>` : "";
    return `<th>${thumb}+ ${esc(p.accessory_sku)}</th>`;
  }).join("");

  const mxRows = (cfg.base_skus || []).map((sku) => {
    const cv = colorMap[sku.color_id] || {};
    const cells = pkgs.map((p) => {
      const fn = p.accessory_sku ? `${sku.sku_code}_${p.accessory_sku}.jpg` : `${sku.sku_code}.jpg`;
      return `<td><span class="fn mono">${ic("check", 12, 2.6)}${esc(fn)}</span></td>`;
    }).join("");
    return `
      <tr>
        <td>
          <div class="row" style="gap:10px">
            <span class="swatch" style="background:${cv.swatch || "#9CA3AF"}"></span>
            <div style="line-height:1.3">
              <div class="mono" style="font-weight:700;color:#111827">${esc(sku.sku_code)}</div>
              <div style="color:#9CA3AF;font-size:11px">${esc(cv.color_name_cn || sku.color_id)} · ${esc(sku.version_badge)}</div>
            </div>
          </div>
        </td>
        ${cells}
      </tr>`;
  }).join("");

  const provList = d.providers || [];
  const curProv = provList.find((p) => p.id === d.selected_provider) || provList[0];
  const models = curProv?.models || ["gpt-image-2"];
  const concurrency = Math.max(1, d.batch?.concurrency || 3);
  const estMin = Math.max(1, Math.round((counts.selected_total * 21) / (60 * concurrency)));

  root.innerHTML = `
    <div class="s2-wrap">
      <!-- 顶部出图范围 -->
      <section class="card scope">
        <div class="scope-lbl">
          <div class="card-t">出图范围</div>
          <div class="card-d">勾选本次要生成的套图</div>
        </div>

        <div class="opt on locked">
          <div class="cb">${ic("check", 12, 3)}</div>
          <div>
            <div class="row" style="gap:6px;font-weight:700">
              通用套图
              <span class="pill p-gray" style="height:18px;font-size:10.5px">${ic("lock", 10, 2.2)}必选</span>
            </div>
            <div class="card-d">主图 6 · 副图 8 · 包裹 · 属性 12 · 场景 · 卖点 · 广告</div>
          </div>
          <div class="opt-n">${counts.general}<small>张</small></div>
        </div>

        <button class="opt ${useOpt ? "on" : ""}" id="toggleOptSuite">
          <div class="cb ${useOpt ? "" : "off"}">${ic("check", 12, 3)}</div>
          <div>
            <div style="font-weight:700">结构图 + 手持对比</div>
            <div class="card-d">样品未到可取消，后续补图</div>
          </div>
          <div class="opt-n">${counts.optional}<small>张</small></div>
        </button>

        <button class="opt ${useRu ? "on" : ""}" id="toggleRuSuite">
          <div class="cb ${useRu ? "" : "off"}">${ic("check", 12, 3)}</div>
          <div>
            <div style="font-weight:700">俄语套图 <span class="mono" style="font-weight:500;color:#6B7280;font-size:12px">900×1200</span></div>
            <div class="card-d">俄语主图 · 俄语包裹图</div>
          </div>
          <div class="opt-n">${counts.russian}<small>张</small></div>
        </button>

        <div class="total-box">
          <div style="font-size:12px;color:#9CA3AF">本次合计</div>
          <div style="font-size:26px;font-weight:700;line-height:1.2">${counts.selected_total} <span style="font-size:13px;font-weight:500;color:#D1D5DB">张</span></div>
        </div>
      </section>

      <div class="s2-grid">
        <!-- 左：商品信息 -->
        <section class="card s2-card">
          <div class="card-hd">
            <div class="card-t">商品信息</div>
            <span class="pill p-brand">${ic("sparkles", 12, 2)}自动提取</span>
            ${pendingConfirms > 0
              ? `<span class="pill p-warn" style="margin-left:auto">${ic("alert", 12, 2.2)}${pendingConfirms} 项待确认</span>`
              : `<span class="pill p-ok" style="margin-left:auto">${ic("check", 12, 2.6)}已全部确认</span>`}
          </div>

          <div class="s2-body">
            <div class="f-row">
              <div class="lbl">品牌</div>
              <div class="row" style="gap:10px">
                <span class="logo-chip">${esc((meta.brand_name || "").toUpperCase())}</span>
                <span style="font-weight:600">${esc(meta.brand_name)}</span>
                <div class="row" style="margin-left:auto;gap:8px;font-size:12.5px;color:#374151">
                  <span>主图显示 LOGO</span>
                  <button class="switch ${meta.show_brand_logo_on_main !== false ? "on" : ""}" id="toggleBrandLogo" aria-label="主图显示品牌LOGO"></button>
                </div>
              </div>
            </div>

            <div class="f-row" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
              <div><div class="lbl">SPU</div><div class="mono" style="font-weight:700">${esc(meta.spu_code)}</div></div>
              <div><div class="lbl">类目</div><div>${esc(meta.category_cn || meta.category)}</div></div>
            </div>

            <div class="f-row">
              <div class="row lbl" style="justify-content:space-between">
                <span>英文标题</span>
                <button class="btn-link" id="btnEditCopyEn">编辑文案</button>
              </div>
              <div class="chips">
                ${(en.candidate_titles || []).map((t) => `<span class="chip">${esc(t)}</span>`).join("")}
              </div>
            </div>

            <div class="f-row">
              <div class="lbl">核心卖点</div>
              <div class="chips">
                ${(en.core_selling_points || []).map((t) => `<span class="chip">${esc(t)}</span>`).join("")}
              </div>
            </div>

            <div class="f-row">
              <div class="lbl">俄语标题</div>
              <div style="font-size:12.5px;color:#374151;line-height:1.55">
                ${esc(ru?.title || "")} — ${esc((ru?.subtitle_lines || []).slice(0, 2).join(" · "))}
              </div>
            </div>

            <div class="f-row">
              <div class="row lbl" style="justify-content:space-between">
                <span>包装清单 · ${en.package_includes?.length || 0} 项</span>
                <button class="btn-link" id="btnEditPackage">展开编辑</button>
              </div>
              <div style="font-size:12.5px;color:#374151;line-height:1.7">
                ${esc(pkgPreview.slice(0, 2).join("　"))}<br />
                ${esc(pkgPreview.slice(2, 4).join("　"))} ${pkgMore > 0 ? `<span class="faint">+${pkgMore} 项</span>` : ""}
              </div>
            </div>

            <div class="f-row">
              <div class="lbl">关键参数 · ${en.specifications?.length || 0} 项</div>
              <div style="display:flex;flex-direction:column;gap:5px">
                ${confirmRowsHtml}
                ${gimbalSpec ? `<div class="kv"><span class="k">摇杆</span><span class="ell">${esc(gimbalSpec.value.split("(")[0].trim())}</span><span class="faint" style="margin-left:auto;font-size:11.5px">+${otherSpecCount} 项已校验</span></div>` : ""}
              </div>
            </div>
          </div>
        </section>

        <!-- 右：参考图槽位 + SKU 矩阵 + 平台选择 -->
        <section class="card s2-card">
          <div class="card-hd">
            <div class="card-t">参考图槽位</div>
            <div class="seg">${segHtml}</div>
            <div class="row" style="margin-left:auto;gap:6px;font-size:12px;color:#9CA3AF">
              ${ic("move", 13)}拖拽可互换槽位，悬停可替换
            </div>
          </div>

          <div class="s2-body">
            <div style="padding:16px 20px">
              <div class="slots-7">${slotsHtml}</div>
            </div>

            <div style="padding:4px 20px 16px">
              <div class="row" style="gap:8px;margin-bottom:10px">
                <span class="sec-t">SKU 属性图组合</span>
                <span class="pill p-gray">${(cfg.base_skus || []).length} × ${pkgs.length} = ${(cfg.base_skus || []).length * pkgs.length} 张</span>
                <span class="card-d" style="margin-left:auto">命名规则 <span class="mono" style="color:#374151">主SKU_配件SKU.jpg</span></span>
              </div>
              <table class="mx">
                <thead><tr><th style="width:185px">主 SKU</th>${mxHeaders}</tr></thead>
                <tbody>${mxRows}</tbody>
              </table>
            </div>
          </div>

          <div class="plat-bar">
            <div class="plat-grid">
              <div>
                <div class="row lbl" style="justify-content:space-between">
                  <span>生图平台</span>
                  <button class="btn-link" id="s2ConfigTokenBtn" style="font-size:11px">配置令牌</button>
                </div>
                <select class="field-select" id="s2ProviderSelect">
                  ${provList.map((p) => `<option value="${esc(p.id)}" ${p.id === d.selected_provider ? "selected" : ""}>${esc(p.display_name)}</option>`).join("")}
                </select>
              </div>
              <div>
                <div class="lbl">模型</div>
                <select class="field-select mono" id="s2ModelSelect">
                  ${models.map((m) => `<option value="${esc(m)}" ${m === d.selected_model ? "selected" : ""}>${esc(m)}</option>`).join("")}
                </select>
              </div>
              <div>
                <div class="lbl">质量</div>
                <select class="field-select" id="s2QualitySelect">
                  ${["high", "medium", "low"].map((q) => `<option value="${q}" ${q === d.selected_quality ? "selected" : ""}>${q}</option>`).join("")}
                </select>
              </div>
              <div style="padding-bottom:4px">
                <div class="row" style="gap:6px;font-size:12px;color:#6B7280">${ic("clock", 13)}预计约 ${estMin} 分钟（${concurrency} 路并发）</div>
                <div class="row" style="gap:6px;font-size:12px;color:#6B7280;margin-top:2px">${ic("zap", 13)}${counts.selected_total} 次调用 · 可随时暂停</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>`;

  // 立即恢复左右面板与主滚动区位置，确保点「确认」等操作时页面纹丝不动
  const newS2Bodies = root.querySelectorAll(".s2-body");
  prevS2Scrolls.forEach((top, i) => {
    if (newS2Bodies[i]) newS2Bodies[i].scrollTop = top;
  });
  if (viewRoot) viewRoot.scrollTop = prevViewScroll;

  // 绑定第二步事件
  document.getElementById("toggleOptSuite").addEventListener("click", () => {
    const next = !useOpt;
    updateTask({
      generation_flags: {
        generate_structure_diagram: next,
        generate_handheld_comparison: next,
      },
    });
  });

  document.getElementById("toggleRuSuite").addEventListener("click", () => {
    updateTask({ generation_flags: { generate_russian_suite: !useRu } });
  });

  document.getElementById("toggleBrandLogo").addEventListener("click", () => {
    const next = meta.show_brand_logo_on_main === false;
    updateTask({ product_meta: { show_brand_logo_on_main: next } }, next ? "主图将显示品牌 LOGO" : "已关闭主图品牌 LOGO");
  });

  document.getElementById("btnEditCopyEn").addEventListener("click", openCopyEditModal);
  document.getElementById("btnEditPackage").addEventListener("click", openPackageEditModal);
  document.getElementById("s2ConfigTokenBtn").addEventListener("click", openProviderModal);

  // 确认关键参数
  root.querySelectorAll("[data-cf-btn]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.cfBtn;
      const input = root.querySelector(`[data-cf-input="${id}"]`);
      const cf = d.confirm_fields.find((x) => x.id === id);
      updateTask({
        confirm_field: { id, confirmed: !cf?.confirmed, value: input ? input.value.trim() : cf?.value },
      });
    });
  });

  // 切换颜色标签
  root.querySelectorAll("[data-color-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      appState.activeColorId = btn.dataset.colorTab;
      renderStep2();
    });
  });

  // 槽位拖拽交换
  root.querySelectorAll(".slot-card[draggable='true']").forEach((card) => {
    card.addEventListener("dragstart", (e) => {
      appState.dragRole = card.dataset.slotRole;
      card.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
    });
    card.addEventListener("dragend", () => {
      card.classList.remove("dragging");
      root.querySelectorAll(".slot-card").forEach((c) => c.classList.remove("drag-over"));
      appState.dragRole = null;
    });
    card.addEventListener("dragover", (e) => {
      e.preventDefault();
      if (appState.dragRole && appState.dragRole !== card.dataset.slotRole) {
        card.classList.add("drag-over");
      }
    });
    card.addEventListener("dragleave", () => card.classList.remove("drag-over"));
    card.addEventListener("drop", async (e) => {
      e.preventDefault();
      card.classList.remove("drag-over");
      const targetRole = card.dataset.slotRole;
      if (appState.dragRole && targetRole && appState.dragRole !== targetRole) {
        await updateTask({
          swap_slots: { color_id: activeColor.color_id, role_a: appState.dragRole, role_b: targetRole },
        }, "已互换参考图槽位");
      }
    });
  });

  // 槽位预览 & 替换
  root.querySelectorAll("[data-slot-view]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openLightbox(btn.dataset.slotView, btn.dataset.slotName);
    });
  });
  root.querySelectorAll("[data-slot-replace]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const role = btn.dataset.slotReplace;
      openImagePickerModal({
        title: `替换「${activeColor.color_name_cn}」参考图槽位`,
        onSelect: async (imagePath) => {
          await updateTask({
            replace_slot: { color_id: activeColor.color_id, role, image_path: imagePath },
          }, "已替换该槽位参考图");
        },
      });
    });
  });

  // 平台/模型/质量选择
  document.getElementById("s2ProviderSelect").addEventListener("change", (e) => {
    updateTask({ provider_id: e.target.value });
  });
  document.getElementById("s2ModelSelect").addEventListener("change", (e) => {
    updateTask({ model_name: e.target.value });
  });
  document.getElementById("s2QualitySelect").addEventListener("change", (e) => {
    updateTask({ quality: e.target.value });
  });
}

// ==========================================================================
// 第三步：生成与验收
// ==========================================================================
function _isJobRunning(j, batchOverride = null) {
  const batch = batchOverride || appState.data?.batch || {};
  const runningList = batch.running_files || [];
  return j.status === "running" || appState.singleBusyFile === j.filename || runningList.includes(j.filename);
}

function _buildCardInnerHtml(j, batchOverride = null) {
  const isChecked = appState.checkedFiles.has(j.filename);
  const isRunning = _isJobRunning(j, batchOverride);
  const isDone = j.status === "done";
  const isWarn = isDone && j.review_status === "review";
  const sizeText = j.target_width === j.target_height ? `${j.target_width}²` : `${j.target_width}×${j.target_height}`;

  let imgBody = "";
  if (isRunning) {
    imgBody = `<div class="gi-placeholder"><div class="spinner"></div><span style="color:#4F46E5;font-weight:600">生图中...</span></div>`;
  } else if (isDone && j.output_path) {
    imgBody = `<img src="${imgUrl(j.output_path, j.mtime, 360)}" />`;
  } else if (j.status === "failed") {
    imgBody = `<div class="gi-placeholder" style="color:#B91C1C">${ic("alert", 20)}<span>生成失败</span></div>`;
  } else {
    imgBody = `<div class="gi-placeholder">${ic("image", 20)}<span>待生成</span></div>`;
  }

  let statusHtml = `<span class="row" style="gap:4px;color:#9CA3AF"><span class="dot" style="background:#D1D5DB;width:6px;height:6px"></span>待生成</span>`;
  if (isRunning) {
    statusHtml = `<span class="row" style="gap:4px;color:#4F46E5"><span class="dot" style="background:#4F46E5;width:6px;height:6px"></span>生成中</span>`;
  } else if (isWarn) {
    statusHtml = `<span class="row" style="gap:4px;color:#B45309"><span class="dot" style="background:#F59E0B;width:6px;height:6px"></span>待复核</span>`;
  } else if (isDone) {
    statusHtml = `<span class="row" style="gap:4px;color:#047857"><span class="dot" style="background:#10B981;width:6px;height:6px"></span>通过</span>`;
  } else if (j.status === "failed") {
    statusHtml = `<span class="row" style="gap:4px;color:#B91C1C"><span class="dot" style="background:#EF4444;width:6px;height:6px"></span>失败</span>`;
  }

  return `
    <div class="img">
      ${imgBody}
      <span class="gtag">${esc(j.tag)}</span>
      <button class="gcheck ${isChecked ? "checked" : ""}" data-job-check="${esc(j.filename)}" title="勾选用于批量重绘">
        ${ic("check", 11, 3)}
      </button>
      ${isWarn ? `<span class="gwarn-pill">${ic("alert", 10, 2.4)}待复核</span>` : ""}
    </div>
    <div class="cap">
      <div class="nm ell" title="${esc(j.filename)}">${esc(j.filename)}</div>
      <div class="mt">
        <span class="mono">${sizeText}</span>
        ${statusHtml}
      </div>
    </div>`;
}

function _jobSig(j, batchOverride = null) {
  return `${j.status}|${j.review_status}|${j.mtime}|${j.active_version}|${_isJobRunning(j, batchOverride) ? 1 : 0}`;
}

function _formatBatchStatusText(batch, sum) {
  if (batch.running) {
    const rf = batch.running_files || (batch.current ? [batch.current] : []);
    const activeCnt = rf.length || Math.min(batch.concurrency || 1, Math.max(1, (batch.total || 0) - (batch.completed || 0)));
    const namesStr = rf.length > 0 ? rf.join("、") : (batch.current || "准备中...");
    return {
      title: `正在并发生成 (${batch.completed}/${batch.total} · ${activeCnt} 张并行)`,
      sub: `并行中：${namesStr} · 已用时 ${Math.round(batch.elapsed || 0)}s`,
    };
  }
  return {
    title: sum.pending === 0 ? "生成完成" : `已生成 ${sum.done} / ${sum.total} 张`,
    sub: sum.pending === 0
      ? `${sum.done} / ${sum.total} · 全部就绪，可随时单图微调重绘`
      : `剩余 ${sum.pending} 张待生成，可点击右侧补齐或单张生成`,
  };
}

function renderStep3() {
  const root = document.getElementById("stepView3");
  const d = appState.data;
  if (!d) return;

  // 保存现有滚动条位置，彻底杜绝任何操作把用户滚回最顶端
  const prevGalScroll = root.querySelector(".gal-scroll")?.scrollTop || 0;
  const prevInspScroll = root.querySelector(".insp-scroll")?.scrollTop || 0;

  const jobs = d.jobs || [];
  const sum = d.summary || { total: 0, done: 0, approved: 0, review: 0, pending: 0, compliance_pct: 100 };
  const batch = d.batch || {};

  // 默认选中第一张已完成图片（优先属性图 RC4661A_RC4226A.jpg，与原型体验一致）
  if (!appState.selectedFilename || !jobs.some((j) => j.filename === appState.selectedFilename)) {
    const preferred = jobs.find((j) => j.filename === "RC4661A_RC4226A.jpg")
      || jobs.find((j) => j.status === "done")
      || jobs[0];
    appState.selectedFilename = preferred ? preferred.filename : null;
  }

  // 标签统计
  const tabDefs = [
    { key: "all", label: "全部", count: jobs.length },
    { key: "main", label: "主图", count: jobs.filter((j) => j.tab_group === "main").length },
    { key: "sub", label: "副图", count: jobs.filter((j) => j.tab_group === "sub").length },
    { key: "sku", label: "属性图", count: jobs.filter((j) => j.tab_group === "sku").length },
    { key: "detail", label: "详情", count: jobs.filter((j) => j.tab_group === "detail").length },
    { key: "ru", label: "俄语", count: jobs.filter((j) => j.tab_group === "ru").length },
    { key: "review", label: "待复核", count: sum.review, warn: true },
    { key: "pending", label: "未生成", count: sum.pending },
  ];

  const filtered = jobs.filter((j) => {
    if (appState.activeTab === "all") return true;
    if (appState.activeTab === "review") return j.status === "done" && j.review_status === "review";
    if (appState.activeTab === "pending") return j.status !== "done";
    return j.tab_group === appState.activeTab;
  });
  // 「全部」视图优先展示正在生成与已完成成品图，待生成卡片统一排在后面，首屏更整齐
  if (appState.activeTab === "all") {
    const rank = (j) => (_isJobRunning(j, batch) ? 0 : j.status === "done" ? 1 : 2);
    filtered.sort((a, b) => rank(a) - rank(b));
  }

  const pct = sum.total ? Math.round((sum.done / sum.total) * 100) : 0;
  const { title: statusTitle, sub: statusSub } = _formatBatchStatusText(batch, sum);

  const tabsHtml = tabDefs.map((t) => `
    <button class="tab ${appState.activeTab === t.key ? "on" : ""}" data-tab="${t.key}" style="${t.warn ? "color:#B45309" : ""}">
      <span>${t.label}</span>
      <span class="c" data-tab-count="${t.key}" style="${t.warn ? "background:#FFFBEB;color:#B45309" : ""}">${t.count}</span>
    </button>
  `).join("");

  const gridHtml = filtered.map((j) => {
    const isSel = j.filename === appState.selectedFilename;
    return `
      <div class="gi ${isSel ? "sel" : ""}" data-job-card="${esc(j.filename)}" data-state-sig="${esc(_jobSig(j, batch))}">
        ${_buildCardInnerHtml(j, batch)}
      </div>`;
  }).join("") || `<div style="grid-column:1/-1;text-align:center;padding:48px;color:#9CA3AF">该分类下暂无图片</div>`;

  // 多选悬浮批量操作条
  const selCnt = appState.checkedFiles.size;
  const bulkBarHtml = selCnt > 0 ? `
    <div class="bulk-bar" id="bulkActionBar">
      <span class="bulk-cnt">已选中 <b>${selCnt}</b> 张</span>
      <button class="bulk-btn bulk-btn-p" id="bulkRegenBtn" ${batch.running ? "disabled" : ""}>
        ${ic("refresh", 14, 2.2)}<span>批量重绘所选 (${selCnt})</span>
      </button>
      <button class="bulk-btn bulk-btn-s" id="bulkApproveBtn">${ic("check", 13, 2.6)}标为通过</button>
      <button class="bulk-btn bulk-btn-s" id="bulkReviewBtn">${ic("alert", 13, 2.2)}标为待复核</button>
      <button class="bulk-btn bulk-btn-g" id="bulkClearBtn">取消选择</button>
    </div>` : "";

  // 右侧检查器
  const selJob = jobs.find((j) => j.filename === appState.selectedFilename);
  const inspHtml = selJob ? buildInspectorHtml(selJob, d) : `<div class="card s3-insp" style="align-items:center;justify-content:center;color:#9CA3AF">点击左侧任意图片查看详情</div>`;

  // 汇总栏采用紧凑双行布局，1280px 窄屏与 1920px 宽屏下均绝不挤竖排、绝不裁切
  root.innerHTML = `
    <div class="s3-layout">
      <section class="card s3-left">
        <div class="sum-bar" id="s3SumBar">
          <div class="sum-row">
            <div id="s3StatusIcon" style="width:28px;height:28px;border-radius:50%;flex-shrink:0;background:${batch.running ? "#EEF2FF" : "#ECFDF5"};color:${batch.running ? "#4F46E5" : "#059669"};display:flex;align-items:center;justify-content:center">
              ${batch.running ? `<div class="spinner" style="width:14px;height:14px"></div>` : ic("check", 15, 2.6)}
            </div>
            <div id="s3StatusTitle" style="font-weight:700;font-size:14px;white-space:nowrap">${esc(statusTitle)}</div>
            <div class="progress-track">
              <i id="s3ProgressFill" class="progress-fill ${batch.running ? "running" : ""}" style="width:${pct}%"></i>
            </div>
            <div id="s3BatchActionSlot" style="flex-shrink:0">
              ${batch.running
                ? `<button class="btn btn-danger btn-sm" id="btnStopBatch">${ic("pause", 12, 2.2)}暂停</button>`
                : sum.pending > 0
                  ? `<button class="btn btn-p btn-sm" id="btnGenMissing">${ic("play", 12, 2.2)}补齐剩余 ${sum.pending} 张</button>`
                  : ""}
            </div>
          </div>
          <div class="sum-row" style="justify-content:space-between">
            <div id="s3StatusSub" class="card-d ell">${esc(statusSub)}</div>
            <div class="row" style="gap:6px;flex-shrink:0">
              <span id="s3PillApproved" class="pill p-ok">${sum.approved} 通过</span>
              <span id="s3PillReview" class="pill p-warn">${sum.review} 待复核</span>
              <span id="s3PillCompliance" class="pill p-gray">合规 ${sum.compliance_pct}%</span>
            </div>
          </div>
        </div>

        <div class="tabs-bar">${tabsHtml}</div>

        <div class="gal-scroll" style="${selCnt > 0 ? "padding-bottom:76px" : ""}">
          <div class="gal">${gridHtml}</div>
        </div>
        ${bulkBarHtml}
      </section>

      ${inspHtml}
    </div>`;

  // 还原滚动条位置
  const newGal = root.querySelector(".gal-scroll");
  if (newGal) newGal.scrollTop = prevGalScroll;
  const newInsp = root.querySelector(".insp-scroll");
  if (newInsp) newInsp.scrollTop = prevInspScroll;

  bindStep3Events(root, jobs, selJob, d);
}

function bindStep3Events(root, jobs, selJob, d) {
  document.getElementById("btnStopBatch")?.addEventListener("click", async () => {
    await api("/api/generate/stop", { method: "POST", body: JSON.stringify({}) });
    toast("已发送暂停指令，当前图片完成后停止", "warn");
  });

  document.getElementById("btnGenMissing")?.addEventListener("click", async () => {
    try {
      const res = await api("/api/generate/start", { method: "POST", body: JSON.stringify({ mode: "missing" }) });
      appState.data = res.state;
      startPolling();
      renderAll();
      toast(`已启动补齐队列（共 ${res.queue_size} 张），您可以继续浏览和检查已生成图片`, "ok");
    } catch (e) {
      toast(e.message, "bad");
    }
  });

  // 悬浮批量操作条事件
  document.getElementById("bulkRegenBtn")?.addEventListener("click", async () => {
    const files = Array.from(appState.checkedFiles);
    if (!files.length) return;
    try {
      const res = await api("/api/generate/start", {
        method: "POST",
        body: JSON.stringify({ mode: "selected", filenames: files }),
      });
      appState.data = res.state;
      appState.checkedFiles.clear();
      startPolling();
      renderAll();
      toast(`已开始后台重绘所选的 ${files.length} 张图片，您可以继续浏览其他图片`, "ok");
    } catch (e) {
      toast(e.message, "bad");
    }
  });
  document.getElementById("bulkApproveBtn")?.addEventListener("click", () => handleBatchReview("approved"));
  document.getElementById("bulkReviewBtn")?.addEventListener("click", () => handleBatchReview("review"));
  document.getElementById("bulkClearBtn")?.addEventListener("click", () => {
    appState.checkedFiles.clear();
    renderChrome();
    renderStep3();
  });

  root.querySelectorAll("[data-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      appState.activeTab = btn.dataset.tab;
      renderStep3();
    });
  });

  root.querySelectorAll("[data-job-card]").forEach((card) => bindSingleCardEvents(card));

  if (selJob) bindInspectorEvents(selJob, d);
}

function bindSingleCardEvents(card) {
  const fn = card.dataset.jobCard;
  const chkBtn = card.querySelector("[data-job-check]");
  if (chkBtn) {
    chkBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (appState.checkedFiles.has(fn)) appState.checkedFiles.delete(fn);
      else appState.checkedFiles.add(fn);
      renderChrome();
      renderStep3();
    });
  }
  card.onclick = () => {
    appState.selectedFilename = fn;
    renderStep3();
  };
  card.ondblclick = () => {
    const j = (appState.data?.jobs || []).find((x) => x.filename === fn);
    if (j?.output_path) openLightbox(j.output_path, j.filename, `${j.actual_width}×${j.actual_height}`, j.mtime);
  };
}

// 批量生成期间的无感局部更新：绝不销毁滚动容器、绝不重置滚动条、绝不打断右侧检查器与输入焦点！
function patchStep3Live(prevData, nextData) {
  const root = document.getElementById("stepView3");
  if (!root || !root.querySelector(".s3-layout")) {
    renderStep3();
    return;
  }

  const jobs = nextData.jobs || [];
  const sum = nextData.summary || { total: 0, done: 0, approved: 0, review: 0, pending: 0, compliance_pct: 100 };
  const batch = nextData.batch || {};
  const pct = sum.total ? Math.round((sum.done / sum.total) * 100) : 0;

  // 1. 局部更新进度条与汇总指标
  const titleEl = document.getElementById("s3StatusTitle");
  const subEl = document.getElementById("s3StatusSub");
  const fillEl = document.getElementById("s3ProgressFill");
  const iconEl = document.getElementById("s3StatusIcon");

  if (titleEl && subEl) {
    const st = _formatBatchStatusText(batch, sum);
    titleEl.textContent = st.title;
    subEl.textContent = st.sub;
  }
  if (fillEl) {
    fillEl.style.width = `${pct}%`;
    fillEl.classList.toggle("running", Boolean(batch.running));
  }
  if (iconEl) {
    const wasRun = Boolean(prevData?.batch?.running);
    if (wasRun !== Boolean(batch.running)) {
      iconEl.style.background = batch.running ? "#EEF2FF" : "#ECFDF5";
      iconEl.style.color = batch.running ? "#4F46E5" : "#059669";
      iconEl.innerHTML = batch.running ? `<div class="spinner" style="width:16px;height:16px"></div>` : ic("check", 17, 2.6);
      const slot = document.getElementById("s3BatchActionSlot");
      if (slot) {
        slot.innerHTML = batch.running
          ? `<button class="btn btn-danger btn-sm" id="btnStopBatch">${ic("pause", 12, 2.2)}暂停</button>`
          : sum.pending > 0
            ? `<button class="btn btn-p btn-sm" id="btnGenMissing">${ic("play", 12, 2.2)}补齐剩余 ${sum.pending} 张</button>`
            : "";
        document.getElementById("btnStopBatch")?.addEventListener("click", async () => {
          await api("/api/generate/stop", { method: "POST", body: JSON.stringify({}) });
          toast("已发送暂停指令，当前图片完成后停止", "warn");
        });
        document.getElementById("btnGenMissing")?.addEventListener("click", async () => {
          const res = await api("/api/generate/start", { method: "POST", body: JSON.stringify({ mode: "missing" }) });
          appState.data = res.state;
          startPolling();
          renderAll();
        });
      }
    }
  }

  const apEl = document.getElementById("s3PillApproved");
  const rvEl = document.getElementById("s3PillReview");
  const cpEl = document.getElementById("s3PillCompliance");
  if (apEl) apEl.textContent = `${sum.approved} 通过`;
  if (rvEl) rvEl.textContent = `${sum.review} 待复核`;
  if (cpEl) cpEl.textContent = `尺寸合规 ${sum.compliance_pct}%`;

  // 2. 局部更新分类 Tab 计数
  const counts = {
    all: jobs.length,
    main: jobs.filter((j) => j.tab_group === "main").length,
    sub: jobs.filter((j) => j.tab_group === "sub").length,
    sku: jobs.filter((j) => j.tab_group === "sku").length,
    detail: jobs.filter((j) => j.tab_group === "detail").length,
    ru: jobs.filter((j) => j.tab_group === "ru").length,
    review: sum.review,
    pending: sum.pending,
  };
  Object.entries(counts).forEach(([k, v]) => {
    const el = root.querySelector(`[data-tab-count="${k}"]`);
    if (el) el.textContent = String(v);
  });

  // 3. 仅局部替换状态实际发生变化的卡片，完全不碰滚动条和其他卡片
  const jobMap = {};
  jobs.forEach((j) => { jobMap[j.filename] = j; });
  root.querySelectorAll("[data-job-card]").forEach((card) => {
    const fn = card.dataset.jobCard;
    const j = jobMap[fn];
    if (!j) return;
    const nextSig = _jobSig(j, batch);
    if (card.dataset.stateSig !== nextSig) {
      card.dataset.stateSig = nextSig;
      card.innerHTML = _buildCardInnerHtml(j, batch);
      bindSingleCardEvents(card);
    }
  });

  // 4. 若当前右侧检查器选中的正好是刚刚完成的那张图，且用户不在输入提示词，才更新右侧预览
  if (appState.selectedFilename) {
    const prevSel = (prevData?.jobs || []).find((x) => x.filename === appState.selectedFilename);
    const nextSel = jobMap[appState.selectedFilename];
    const activeEl = document.activeElement;
    const editingPrompt = activeEl && activeEl.id === "inspPromptArea";
    if (nextSel && prevSel && _jobSig(prevSel) !== _jobSig(nextSel) && !editingPrompt) {
      renderStep3();
    }
  }
}

async function handleBatchReview(status) {
  const files = Array.from(appState.checkedFiles);
  if (!files.length) return;
  try {
    const res = await api("/api/job/review-batch", {
      method: "POST",
      body: JSON.stringify({ filenames: files, review_status: status }),
    });
    appState.data = res.state;
    appState.checkedFiles.clear();
    renderChrome();
    renderStep3();
    toast(`已将 ${res.updated} 张已完成图片标记为「${status === "approved" ? "已通过" : "待复核"}」`, "ok");
  } catch (e) {
    toast(e.message, "bad");
  }
}

function getDraft(job, d) {
  if (!appState.inspectorDraft[job.filename]) {
    appState.inspectorDraft[job.filename] = {
      prompt: job.prompt,
      refs: [...(job.reference_images || [])],
      provider_id: job.provider_id || d.selected_provider,
      model_name: job.model_name || d.selected_model,
    };
  }
  return appState.inspectorDraft[job.filename];
}

function buildInspectorHtml(job, d) {
  const draft = getDraft(job, d);
  const isBusy = appState.singleBusyFile === job.filename || job.status === "running";
  const isModified = draft.prompt !== job.default_prompt;
  const provList = d.providers || [];
  const curProv = provList.find((p) => p.id === draft.provider_id) || provList[0];
  const models = curProv?.models || ["gpt-image-2"];

  const previewHtml = isBusy
    ? `<div class="gi-placeholder"><div class="spinner" style="width:32px;height:32px"></div><div style="color:#4F46E5;font-weight:600;margin-top:4px">正在调用 ${esc(draft.model_name)} 生成中 (${appState.singleBusySeconds}s)...</div><div class="card-d">生成完成后将自动生成新版本供对比</div></div>`
    : job.output_path
      ? `<img src="${imgUrl(job.output_path, job.mtime)}" id="inspMainImg" />
         <div class="prev-tools">
           <button class="prev-tool-btn" id="inspFullscreenBtn" title="高清灯箱放大">${ic("maximize", 14)}</button>
           <a class="prev-tool-btn" href="${downloadUrl(job.output_path)}" download title="下载单图">${ic("download", 14)}</a>
         </div>`
      : `<div class="gi-placeholder">${ic("image", 28)}<div>该图片尚未生成</div><div class="card-d">点击下方按钮立即单独生成此图</div></div>`;

  const versHtml = (job.versions || []).map((v) => `
    <button class="vt ${v.ver === job.active_version ? "on" : ""}" data-ver="${v.ver}" title="切换到 v${v.ver} (${v.elapsed || "-"}s)">
      <img src="${imgUrl(v.path, v.ts)}" />
      <span>v${v.ver}</span>
    </button>
  `).join("");

  const refsHtml = (draft.refs || []).map((r, idx) => `
    <div class="ref-item" title="${esc(r.split("/").pop())}">
      <img src="${imgUrl(r)}" data-ref-preview="${esc(r)}" />
      <button class="ref-del" data-ref-del="${idx}" title="移除此参考图">×</button>
    </div>
  `).join("");

  // 显性双态验收状态切换器：当前状态直接高饱和高亮，无需猜当前是什么状态
  const isRev = job.review_status === "review";
  const reviewControl = job.status === "done"
    ? `<div class="review-seg" title="点击直接切换验收状态">
         <button class="${!isRev ? "active-ok" : ""}" data-set-review="approved">${ic("check", 12, 2.6)}已通过</button>
         <button class="${isRev ? "active-warn" : ""}" data-set-review="review">${ic("alert", 12, 2.2)}待复核</button>
       </div>`
    : `<span class="pill p-gray">未生成</span>`;

  return `
    <section class="card s3-insp">
      <div class="card-hd" style="padding:13px 20px">
        <div style="min-width:0;flex:1">
          <div class="card-t mono ell" style="font-size:13.5px" title="${esc(job.filename)}">${esc(job.filename)}</div>
          <div class="card-d ell">${esc(job.tag)} · ${esc(job.category)}</div>
        </div>
        ${reviewControl}
      </div>

      <div class="insp-scroll">
        <div class="insp-sec">
          <div class="prev-box" id="inspPreviewBox">${previewHtml}</div>
          <div class="ver-row">
            <span class="lbl" style="margin:0 4px 0 0">版本</span>
            ${versHtml || `<span class="faint" style="font-size:12px">暂无版本</span>`}
            <div class="meta-pair">
              <div class="meta-box">
                <div class="k">尺寸</div>
                <div class="v mono">${job.actual_width || job.target_width}×${job.actual_height || job.target_height}</div>
              </div>
              <div class="meta-box">
                <div class="k">耗时</div>
                <div class="v">${job.elapsed_seconds ? `${job.elapsed_seconds} s` : "--"}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="insp-sec">
          <div class="row lbl" style="justify-content:space-between">
            <span>参考图 (${draft.refs.length} 张联合输入)</span>
            <button class="btn-link" id="inspAddFromPoolBtn">从素材池选图</button>
          </div>
          <div class="refs-row">
            ${refsHtml}
            <button class="ref-add" id="inspAddLocalRefBtn" title="从本地文件夹选择参考图">${ic("plus", 16)}</button>
          </div>
        </div>

        <div class="insp-sec" style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div>
            <div class="lbl">平台</div>
            <select class="field-select" id="inspProviderSel">
              ${provList.map((p) => `<option value="${esc(p.id)}" ${p.id === draft.provider_id ? "selected" : ""}>${esc(p.display_name)}</option>`).join("")}
            </select>
          </div>
          <div>
            <div class="lbl">模型</div>
            <select class="field-select mono" id="inspModelSel">
              ${models.map((m) => `<option value="${esc(m)}" ${m === draft.model_name ? "selected" : ""}>${esc(m)}</option>`).join("")}
            </select>
          </div>
        </div>

        <div class="insp-sec">
          <div class="row lbl" style="justify-content:space-between">
            <span>提示词（中文像素级设计指令）</span>
            <div class="row" style="gap:8px">
              ${isModified ? `<span class="pill p-warn" style="height:18px;font-size:10.5px">已修改</span><button class="btn-link" id="inspResetPrompt">还原默认</button>` : ""}
            </div>
          </div>
          <textarea class="prompt-area" id="inspPromptArea">${esc(draft.prompt)}</textarea>
          ${job.error ? `<div class="pill p-bad" style="margin-top:8px;height:auto;padding:4px 8px;white-space:normal">${esc(job.error)}</div>` : ""}
        </div>
      </div>

      <div class="insp-foot">
        <button class="btn btn-p btn-lg" style="flex:1" id="inspRegenBtn" ${isBusy ? "disabled" : ""}>
          ${isBusy
            ? `<div class="spinner-sm"></div><span>生成中 ${appState.singleBusySeconds}s...</span>`
            : `${ic("refresh", 15, 2)}<span>${job.status === "done" ? "重新生成此图 · 约 20s" : "立即生成此图 · 约 20s"}</span>`}
        </button>
        <button class="btn btn-s btn-lg" id="inspSaveTplBtn">${ic("bookmark", 15)}存为模板</button>
      </div>
    </section>`;
}

function bindInspectorEvents(job, d) {
  const draft = getDraft(job, d);

  document.getElementById("inspFullscreenBtn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    openLightbox(job.output_path, job.filename, `${job.actual_width}×${job.actual_height} · v${job.active_version}`, job.mtime);
  });
  document.getElementById("inspMainImg")?.addEventListener("click", () => {
    openLightbox(job.output_path, job.filename, `${job.actual_width}×${job.actual_height} · v${job.active_version}`, job.mtime);
  });

  // 显性双态验收状态切换（已通过 / 待复核）
  document.querySelectorAll("[data-set-review]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const next = btn.dataset.setReview;
      if (next === job.review_status) return;
      try {
        const res = await api("/api/job/review", {
          method: "POST",
          body: JSON.stringify({ filename: job.filename, review_status: next }),
        });
        appState.data = res.state;
        renderStep3();
        toast(next === "approved" ? `${job.filename} 状态已设为「已通过」` : `${job.filename} 状态已设为「待复核」`, "ok");
      } catch (e) {
        toast(e.message, "bad");
      }
    });
  });

  // 版本切换
  document.querySelectorAll("[data-ver]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const ver = Number(btn.dataset.ver);
      if (ver === job.active_version) return;
      try {
        const res = await api("/api/job/version", {
          method: "POST",
          body: JSON.stringify({ filename: job.filename, ver }),
        });
        appState.data = res.state;
        delete appState.inspectorDraft[job.filename];
        renderStep3();
        toast(`已切换至 v${ver} 并同步为主输出文件`, "ok");
      } catch (e) {
        toast(e.message, "bad");
      }
    });
  });

  // 参考图预览/删除/添加
  document.querySelectorAll("[data-ref-preview]").forEach((img) => {
    img.addEventListener("click", () => openLightbox(img.dataset.refPreview, img.dataset.refPreview.split("/").pop(), "输入参考图"));
  });
  document.querySelectorAll("[data-ref-del]").forEach((btn) => {
    btn.addEventListener("click", () => {
      draft.refs.splice(Number(btn.dataset.refDel), 1);
      renderStep3();
    });
  });
  document.getElementById("inspAddLocalRefBtn")?.addEventListener("click", () => {
    openImagePickerModal({
      title: `为 ${job.filename} 添加参考图`,
      onSelect: (imagePath) => {
        if (!draft.refs.includes(imagePath)) {
          draft.refs.push(imagePath);
          renderStep3();
          toast("已添加参考图", "ok");
        }
      },
    });
  });
  document.getElementById("inspAddFromPoolBtn")?.addEventListener("click", () => openRefPoolModal(job, draft));

  document.getElementById("inspProviderSel")?.addEventListener("change", (e) => {
    draft.provider_id = e.target.value;
    renderStep3();
  });
  document.getElementById("inspModelSel")?.addEventListener("change", (e) => {
    draft.model_name = e.target.value;
  });

  const area = document.getElementById("inspPromptArea");
  area?.addEventListener("input", () => {
    const wasMod = draft.prompt !== job.default_prompt;
    draft.prompt = area.value;
    const nowMod = draft.prompt !== job.default_prompt;
    if (wasMod !== nowMod) renderStep3();
  });

  document.getElementById("inspResetPrompt")?.addEventListener("click", () => {
    draft.prompt = job.default_prompt;
    renderStep3();
  });

  // 单图真实重新生成
  document.getElementById("inspRegenBtn")?.addEventListener("click", async () => {
    if (appState.singleBusyFile) {
      toast("已有一张图片正在重绘，请稍候完成", "warn");
      return;
    }
    appState.singleBusyFile = job.filename;
    appState.singleBusySeconds = 0;
    renderStep3();
    appState.singleTimer = setInterval(() => {
      appState.singleBusySeconds += 1;
      const btn = document.getElementById("inspRegenBtn");
      if (btn) btn.innerHTML = `<div class="spinner-sm"></div><span>生成中 ${appState.singleBusySeconds}s...</span>`;
      const prev = document.getElementById("inspPreviewBox");
      if (prev && prev.querySelector(".spinner")) {
        const div = prev.querySelector("div > div:nth-child(2)");
        if (div) div.textContent = `正在调用 ${draft.model_name} 生成中 (${appState.singleBusySeconds}s)...`;
      }
    }, 1000);

    try {
      const res = await api("/api/generate/single", {
        method: "POST",
        body: JSON.stringify({
          filename: job.filename,
          prompt: draft.prompt,
          reference_images: draft.refs,
          provider_id: draft.provider_id,
          model_name: draft.model_name,
          quality: d.selected_quality,
        }),
      });
      appState.data = res.state;
      delete appState.inspectorDraft[job.filename];
      toast(`${job.filename} 重新生成完成（已保存为 v${res.record.active_version}，用时 ${res.record.elapsed_seconds}s）`, "ok");
    } catch (e) {
      toast(`重绘失败：${e.message}`, "bad");
    } finally {
      clearInterval(appState.singleTimer);
      appState.singleBusyFile = null;
      appState.singleBusySeconds = 0;
      renderAll();
    }
  });

  document.getElementById("inspSaveTplBtn")?.addEventListener("click", async () => {
    try {
      await api("/api/template/save", {
        method: "POST",
        body: JSON.stringify({ filename: job.filename, prompt: draft.prompt }),
      });
      toast(`已保存为「${job.tag}」类提示词模板`, "ok");
    } catch (e) {
      toast(e.message, "bad");
    }
  });
}

// ==========================================================================
// 弹窗与业务操作
// ==========================================================================
async function updateTask(payload, successMsg = "") {
  try {
    appState.data = await api("/api/task/update", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderAll();
    if (successMsg) toast(successMsg, "ok");
  } catch (e) {
    toast(e.message, "bad");
  }
}

async function scanFolder(folderPath) {
  try {
    toast("正在扫描素材文件夹与执行 6 项质量预检...", "default");
    appState.data = await api("/api/scan", {
      method: "POST",
      body: JSON.stringify({ folder_path: folderPath }),
    });
    appState.activeColorId = null;
    appState.selectedFilename = null;
    appState.checkedFiles.clear();
    appState.inspectorDraft = {};
    renderAll();
    toast(`扫描完成：识别 ${appState.data.scan.stats.usable_images} 张可用高清素材`, "ok");
  } catch (e) {
    toast(`扫描失败：${e.message}`, "bad");
  }
}

async function handlePickFolder() {
  openFolderBrowserModal(appState.data?.scan?.folder_path || "");
}

async function openFolderBrowserModal(initialPath = "") {
  let currentPath = initialPath;

  const loadAndRender = async (targetPath) => {
    openModal({
      title: "选择本地商品素材文件夹",
      large: true,
      bodyHtml: `<div style="padding:32px;text-align:center;color:#6B7280">正在读取本地目录...</div>`,
      footerHtml: `<button class="btn btn-s" id="mCancel">取消</button>`,
    });
    try {
      const info = await api(`/api/fs/list?path=${encodeURIComponent(targetPath || "")}`);
      currentPath = info.current_path;
      const shortcutsHtml = [
        ...(info.shortcuts || []).map((s) => `<button class="fs-chip" data-fs-go="${esc(s.path)}">${ic("folder", 13)}${esc(s.label)}</button>`),
        ...(info.drives || []).map((dr) => `<button class="fs-chip" data-fs-go="${esc(dr.path)}">${esc(dr.name)}</button>`),
      ].join("");

      const rowsHtml = [
        info.parent_path ? `<button class="fs-row" data-fs-go="${esc(info.parent_path)}">${ic("arrow-l", 14)}<span>返回上级目录</span></button>` : "",
        ...(info.folders || []).map((f) => `<button class="fs-row" data-fs-go="${esc(f.path)}"><span style="color:#EA580C">${ic("folder", 15)}</span><span class="ell">${esc(f.name)}</span></button>`),
      ].filter(Boolean).join("") || `<div class="card-d" style="padding:20px;text-align:center">该目录下没有子文件夹，可直接点击下方「选择此文件夹并扫描」</div>`;

      openModal({
        title: "选择本地商品素材文件夹",
        large: true,
        bodyHtml: `
          <div class="fs-shortcuts">${shortcutsHtml}</div>
          <div class="fs-toolbar">
            <input class="field-input mono" id="fsPathInput" value="${esc(currentPath)}" placeholder="粘贴或输入本地目录路径..." />
            <button class="btn btn-s" id="fsGoPathBtn">进入</button>
            <button class="btn btn-s" id="fsNativeDialogBtn" title="呼出 Windows 原生目录选择器">${ic("upload", 14)}系统弹窗选择</button>
          </div>
          <div class="fs-list">${rowsHtml}</div>
          <div class="card-d" style="margin-top:10px">点击任意文件夹可进入查看子目录；到达目标商品文件夹后，点击右下角主按钮立即扫描。</div>
        `,
        footerHtml: `
          <button class="btn btn-s" id="mCancel">取消</button>
          <button class="btn btn-p" id="mConfirmFolder">${ic("check", 14, 2.5)}选择此文件夹并扫描</button>
        `,
      });

      document.getElementById("mCancel").addEventListener("click", closeModal);
      document.getElementById("mConfirmFolder").addEventListener("click", async () => {
        const p = document.getElementById("fsPathInput").value.trim();
        if (!p) return;
        closeModal();
        await scanFolder(p);
      });
      document.getElementById("fsGoPathBtn").addEventListener("click", () => {
        const p = document.getElementById("fsPathInput").value.trim();
        if (p) loadAndRender(p);
      });
      document.getElementById("fsPathInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter") loadAndRender(e.target.value.trim());
      });
      document.getElementById("fsNativeDialogBtn").addEventListener("click", async () => {
        toast("正在呼出 Windows 系统文件夹选择框...", "default");
        const res = await api("/api/pick-folder", { method: "POST", body: JSON.stringify({ initial_dir: currentPath }) });
        if (res.folder_path) {
          closeModal();
          await scanFolder(res.folder_path);
        }
      });
      document.querySelectorAll("[data-fs-go]").forEach((btn) => {
        btn.addEventListener("click", () => loadAndRender(btn.dataset.fsGo));
      });
    } catch (e) {
      toast(`读取目录失败：${e.message}`, "bad");
      closeModal();
    }
  };

  loadAndRender(currentPath);
}

function openImagePickerModal({ title = "选择替换图片", onSelect }) {
  let mode = "browse"; // browse | pool
  let curDir = appState.data?.scan?.folder_path || "";

  const mount = async () => {
    let bodyInner = "";
    if (mode === "pool") {
      const pool = [
        ...(appState.data?.scan?.all_usable_pool || []),
        ...(appState.data?.scan?.excluded_files || []).slice(0, 30),
      ];
      bodyInner = `
        <div class="fs-img-grid">
          ${pool.map((im) => `
            <div class="tcell" style="cursor:pointer" data-pick-img="${esc(im.path)}">
              <div class="thumb"><img src="${imgUrl(im.path, "", 200)}" loading="lazy" /></div>
              <div class="tcap ell" title="${esc(im.name)}">${esc(im.name)}</div>
              <div class="tmeta mono">${im.width || ""}×${im.height || ""}</div>
            </div>`).join("") || `<div class="card-d" style="grid-column:1/-1;padding:24px;text-align:center">素材池暂无图片</div>`}
        </div>`;
    } else {
      const info = await api(`/api/fs/list?images=1&path=${encodeURIComponent(curDir)}`);
      curDir = info.current_path;
      const shortcutsHtml = [
        ...(info.shortcuts || []).map((s) => `<button class="fs-chip" data-img-dir="${esc(s.path)}">${esc(s.label)}</button>`),
        ...(info.drives || []).map((dr) => `<button class="fs-chip" data-img-dir="${esc(dr.path)}">${esc(dr.name)}</button>`),
      ].join("");

      const dirChips = [
        info.parent_path ? `<button class="fs-chip" data-img-dir="${esc(info.parent_path)}">${ic("arrow-l", 12)}上级目录</button>` : "",
        ...(info.folders || []).slice(0, 24).map((f) => `<button class="fs-chip" data-img-dir="${esc(f.path)}">${ic("folder", 12)}${esc(f.name)}</button>`),
      ].filter(Boolean).join("");

      const imgsHtml = (info.images || []).map((im) => `
        <div class="tcell" style="cursor:pointer" data-pick-img="${esc(im.path)}">
          <div class="thumb"><img src="${imgUrl(im.path, "", 220)}" loading="lazy" /></div>
          <div class="tcap ell" title="${esc(im.name)}">${esc(im.name)}</div>
          <div class="tmeta">${im.size_kb} KB</div>
        </div>`).join("") || `<div class="card-d" style="grid-column:1/-1;padding:28px;text-align:center">当前目录暂无图片，请点击上方子文件夹进入或直接上传本地文件</div>`;

      bodyInner = `
        <div class="fs-shortcuts">${shortcutsHtml}</div>
        <div class="fs-toolbar">
          <input class="field-input mono" id="imgDirInput" value="${esc(curDir)}" />
          <button class="btn btn-s" id="imgDirGoBtn">进入</button>
        </div>
        ${dirChips ? `<div class="fs-shortcuts" style="margin-bottom:10px">${dirChips}</div>` : ""}
        <div class="fs-img-grid">${imgsHtml}</div>`;
    }

    openModal({
      title,
      large: true,
      bodyHtml: `
        <div class="row" style="justify-content:space-between;margin-bottom:14px;gap:10px">
          <div class="seg">
            <button class="${mode === "browse" ? "on" : ""}" id="tabImgBrowse">浏览本机图片</button>
            <button class="${mode === "pool" ? "on" : ""}" id="tabImgPool">当前任务素材池</button>
          </div>
          <div class="row" style="gap:8px">
            <label class="btn btn-p btn-sm" style="cursor:pointer">
              ${ic("upload", 13)}<span>从电脑上传图片</span>
              <input type="file" id="nativeFileUpload" accept="image/*" style="display:none" />
            </label>
          </div>
        </div>
        ${bodyInner}
      `,
      footerHtml: `<button class="btn btn-s" id="mCancel">关闭</button>`,
    });

    document.getElementById("mCancel").addEventListener("click", closeModal);
    document.getElementById("tabImgBrowse").addEventListener("click", () => { mode = "browse"; mount(); });
    document.getElementById("tabImgPool").addEventListener("click", () => { mode = "pool"; mount(); });

    // 浏览器原生文件选择框上传（100% 可用，点击即弹系统选图窗口）
    document.getElementById("nativeFileUpload").addEventListener("change", (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const res = await api("/api/upload-image", {
            method: "POST",
            body: JSON.stringify({ filename: file.name, data_b64: reader.result }),
          });
          closeModal();
          await onSelect(res.image_path);
        } catch (err) {
          toast(`上传图片失败：${err.message}`, "bad");
        }
      };
      reader.readAsDataURL(file);
    });

    document.getElementById("imgDirGoBtn")?.addEventListener("click", () => {
      const v = document.getElementById("imgDirInput").value.trim();
      if (v) { curDir = v; mount(); }
    });
    document.getElementById("imgDirInput")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target.value.trim()) { curDir = e.target.value.trim(); mount(); }
    });
    document.querySelectorAll("[data-img-dir]").forEach((btn) => {
      btn.addEventListener("click", () => { curDir = btn.dataset.imgDir; mount(); });
    });
    document.querySelectorAll("[data-pick-img]").forEach((el) => {
      el.addEventListener("click", async () => {
        const p = el.dataset.pickImg;
        closeModal();
        await onSelect(p);
      });
    });
  };

  mount();
}

function openPathInputModal() {
  openFolderBrowserModal(appState.data?.scan?.folder_path || "");
}

function openExcludedModal() {
  const list = appState.data?.scan?.excluded_files || [];
  openModal({
    title: `已自动排除的文件（${list.length} 张）`,
    large: true,
    bodyHtml: `
      <div class="card-d" style="margin-bottom:12px">以下图片因属于低清合集、原厂带字详情切片或营销海报已被自动过滤。如确需使用，可点击「恢复」。</div>
      <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px">
        ${list.map((ex) => `
          <div class="exi" style="justify-content:space-between;gap:8px">
            <div class="row" style="gap:8px;min-width:0;flex:1">
              <div class="thumb" data-m-lb="${esc(ex.path)}" data-m-title="${esc(ex.name)}"><img src="${imgUrl(ex.path, "", 160)}" loading="lazy" /></div>
              <div style="min-width:0;flex:1">
                <div class="ell" style="font-size:12px;font-weight:600" title="${esc(ex.name)}">${esc(ex.name)}</div>
                <div class="card-d ell" style="font-size:11px;color:#B91C1C">${esc(ex.reason)} · ${ex.width}×${ex.height}</div>
              </div>
            </div>
            <button class="btn btn-sm btn-s" style="flex-shrink:0" data-restore="${esc(ex.path)}">恢复</button>
          </div>`).join("")}
      </div>
    `,
    footerHtml: `<button class="btn btn-p" id="mCloseEx">关闭</button>`,
  });
  document.getElementById("mCloseEx").addEventListener("click", closeModal);
  document.querySelectorAll("[data-m-lb]").forEach((el) => {
    el.addEventListener("click", () => openLightbox(el.dataset.mLb, el.dataset.mTitle));
  });
  document.querySelectorAll("[data-restore]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await updateTask({ restore_excluded: btn.dataset.restore }, "已恢复至可用素材池（可在第二步/第三步选图中使用）");
      openExcludedModal();
    });
  });
}

function openCopyEditModal() {
  const en = appState.data.task_config.copywriting_en;
  const ru = appState.data.task_config.copywriting_ru;
  openModal({
    title: "编辑商品标题与核心卖点",
    bodyHtml: `
      <div style="display:flex;flex-direction:column;gap:14px">
        <div>
          <div class="lbl">英文候选标题（每行一条）</div>
          <textarea class="prompt-area" id="mEnTitles" style="min-height:80px">${esc((en.candidate_titles || []).join("\n"))}</textarea>
        </div>
        <div>
          <div class="lbl">英文核心卖点（每行一条）</div>
          <textarea class="prompt-area" id="mEnSp" style="min-height:90px">${esc((en.core_selling_points || []).join("\n"))}</textarea>
        </div>
        <div>
          <div class="lbl">俄语主标题</div>
          <input class="field-input" id="mRuTitle" value="${esc(ru?.title || "")}" />
        </div>
        <div>
          <div class="lbl">俄语三行副标题（每行一条）</div>
          <textarea class="prompt-area" id="mRuSub" style="min-height:80px">${esc((ru?.subtitle_lines || []).join("\n"))}</textarea>
        </div>
      </div>
    `,
    footerHtml: `
      <button class="btn btn-s" id="mCancel">取消</button>
      <button class="btn btn-p" id="mSaveCopy">保存修改</button>
    `,
  });
  document.getElementById("mCancel").addEventListener("click", closeModal);
  document.getElementById("mSaveCopy").addEventListener("click", async () => {
    const titles = document.getElementById("mEnTitles").value.split("\n").map((s) => s.trim()).filter(Boolean);
    const sps = document.getElementById("mEnSp").value.split("\n").map((s) => s.trim()).filter(Boolean);
    const ruTitle = document.getElementById("mRuTitle").value.trim();
    const ruSub = document.getElementById("mRuSub").value.split("\n").map((s) => s.trim()).filter(Boolean);
    closeModal();
    await updateTask({
      copywriting_en: { candidate_titles: titles, main_title: titles[0] || en.main_title, core_selling_points: sps },
      copywriting_ru: { title: ruTitle, subtitle_lines: ruSub },
    }, "文案已更新并同步重新编译提示词");
  });
}

function openPackageEditModal() {
  const items = [...(appState.data.task_config.copywriting_en.package_includes || [])];
  const renderRows = () => items.map((it, i) => `
    <div class="row" style="gap:8px;margin-bottom:8px">
      <input class="field-input mono" style="width:68px;text-align:center" type="number" min="1" data-pkg-qty="${i}" value="${it.qty}" />
      <input class="field-input" style="flex:1" data-pkg-name="${i}" value="${esc(it.name_en)}" />
      <button class="btn btn-sm btn-s" data-pkg-del="${i}">删除</button>
    </div>`).join("");

  const mount = () => {
    openModal({
      title: `编辑包装清单（共 ${items.length} 项）`,
      bodyHtml: `
        <div id="pkgRows">${renderRows()}</div>
        <button class="btn btn-s btn-sm" id="pkgAddBtn" style="margin-top:6px">${ic("plus", 13)}新增清单项</button>
      `,
      footerHtml: `
        <button class="btn btn-s" id="mCancel">取消</button>
        <button class="btn btn-p" id="mSavePkg">保存清单</button>
      `,
    });
    const syncInputs = () => {
      document.querySelectorAll("[data-pkg-qty]").forEach((el) => {
        items[Number(el.dataset.pkgQty)].qty = Math.max(1, Number(el.value) || 1);
      });
      document.querySelectorAll("[data-pkg-name]").forEach((el) => {
        items[Number(el.dataset.pkgName)].name_en = el.value.trim();
      });
    };
    document.getElementById("pkgAddBtn").addEventListener("click", () => {
      syncInputs();
      items.push({ qty: 1, name_en: "" });
      mount();
    });
    document.querySelectorAll("[data-pkg-del]").forEach((btn) => {
      btn.addEventListener("click", () => {
        syncInputs();
        items.splice(Number(btn.dataset.pkgDel), 1);
        mount();
      });
    });
    document.getElementById("mCancel").addEventListener("click", closeModal);
    document.getElementById("mSavePkg").addEventListener("click", async () => {
      syncInputs();
      const cleaned = items.filter((x) => x.name_en);
      closeModal();
      await updateTask({ copywriting_en: { package_includes: cleaned } }, "包装清单已保存");
    });
  };
  mount();
}

function openLaunchDialog() {
  const d = appState.data;
  const sum = d.summary;
  const total = d.scope_counts.selected_total;
  const pendingConfirms = (d.confirm_fields || []).filter((f) => !f.confirmed).length;

  openModal({
    title: `启动生图任务（本次合计 ${total} 张）`,
    bodyHtml: `
      ${pendingConfirms > 0 ? `<div class="pill p-warn" style="margin-bottom:12px;height:auto;padding:8px 12px;width:100%">${ic("alert", 14)} 还有 ${pendingConfirms} 项关键参数未点确认，您也可以在生图后再单独调整。</div>` : ""}
      ${sum.done > 0 ? `
        <button class="choice-card primary" data-launch="view">
          <div class="choice-ic">${ic("grid", 18)}</div>
          <div>
            <div style="font-weight:700">直接进入验收看板（已有 ${sum.done} 张成品图）</div>
            <div class="card-d">立即查看已出图效果，体验单图改词、换模型重绘与版本对比</div>
          </div>
        </button>` : ""}
      ${sum.pending > 0 ? `
        <button class="choice-card" data-launch="missing">
          <div class="choice-ic">${ic("play", 18)}</div>
          <div>
            <div style="font-weight:700">仅补齐未生成的图片（剩余 ${sum.pending} 张）</div>
            <div class="card-d">自动跳过已生成的 ${sum.done} 张，仅调用 API 补全缺失套图</div>
          </div>
        </button>` : ""}
      <button class="choice-card" data-launch="sample">
        <div class="choice-ic">${ic("zap", 18)}</div>
        <div>
          <div style="font-weight:700">快速试跑 3 张代表图（省额度体验实时进度）</div>
          <div class="card-d">实时调用 ${esc(d.selected_model)} 连续生成 3 张并实时刷新看板</div>
        </div>
      </button>
      <button class="choice-card" data-launch="all">
        <div class="choice-ic" style="background:#F3F4F6;color:#374151">${ic("refresh", 18)}</div>
        <div>
          <div style="font-weight:700">全量重新生成全部 ${total} 张</div>
          <div class="card-d">按当前参数全部重新调用 API，旧图自动保留为历史版本</div>
        </div>
      </button>
    `,
    footerHtml: `<button class="btn btn-s" id="mCancel">返回核对</button>`,
  });
  document.getElementById("mCancel").addEventListener("click", closeModal);
  document.querySelectorAll("[data-launch]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const mode = btn.dataset.launch;
      closeModal();
      if (mode === "view") {
        goStep(3);
        return;
      }
      try {
        const res = await api("/api/generate/start", {
          method: "POST",
          body: JSON.stringify({ mode }),
        });
        appState.data = res.state;
        goStep(3);
        startPolling();
        toast(`批量生图已启动（队列 ${res.queue_size} 张）`, "ok");
      } catch (e) {
        toast(e.message, "bad");
      }
    });
  });
}

function openProviderModal() {
  const d = appState.data;
  const prov = (d?.providers || [])[0] || { id: "qiuqiutoken", display_name: "球球Token", token_masked: "", base_url: "" };
  openModal({
    title: "生图平台与 API 令牌配置",
    bodyHtml: `
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="doc" style="background:#FAFAFB">
          <div class="doc-ic" style="background:#EEF2FF;color:#4F46E5">${ic("cpu", 18)}</div>
          <div style="flex:1">
            <div style="font-weight:700">${esc(prov.full_name || prov.display_name)}</div>
            <div class="card-d mono">${esc(prov.base_url)}</div>
          </div>
          <span class="pill ${prov.has_token ? "p-ok" : "p-warn"}">${prov.has_token ? "已配置令牌" : "未配置"}</span>
        </div>
        <div>
          <div class="lbl">当前令牌（留空则保持现有令牌不变）</div>
          <input class="field-input mono" id="mTokenInput" type="password" placeholder="${esc(prov.token_masked || "请输入 sk-...")}" />
          <div class="card-d" style="margin-top:6px">令牌仅保存在本机 <span class="mono">config/local_secrets.json</span>，不会上传至第三方。</div>
        </div>
      </div>
    `,
    footerHtml: `
      <button class="btn btn-s" id="mCancel">关闭</button>
      <button class="btn btn-p" id="mSaveToken">保存配置</button>
    `,
  });
  document.getElementById("mCancel").addEventListener("click", closeModal);
  document.getElementById("mSaveToken").addEventListener("click", async () => {
    const tok = document.getElementById("mTokenInput").value.trim();
    try {
      const res = await api("/api/provider/config", {
        method: "POST",
        body: JSON.stringify({ provider_id: prov.id, api_key: tok }),
      });
      appState.data.providers = res.providers;
      closeModal();
      renderAll();
      toast("平台配置已保存", "ok");
    } catch (e) {
      toast(e.message, "bad");
    }
  });
}

function openRefPoolModal(job, draft) {
  const pool = appState.data?.scan?.all_usable_pool || [];
  const skus = (appState.data?.task_config?.bundled_packages || [])
    .filter((p) => p.accessory_cutout_png)
    .map((p) => ({ name: `${p.accessory_sku}.png`, path: p.accessory_cutout_png, width: 1000, height: 1000 }));
  const all = [...pool, ...skus];

  openModal({
    title: `为 ${job.filename} 增选参考图`,
    large: true,
    bodyHtml: `
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px">
        ${all.map((im) => {
          const added = draft.refs.includes(im.path);
          return `
            <div class="tcell" style="cursor:pointer" data-pick-ref="${esc(im.path)}">
              <div class="thumb" style="${added ? "border-color:#4F46E5;box-shadow:0 0 0 2px #E0E7FF" : ""}">
                <img src="${imgUrl(im.path)}" loading="lazy" />
                ${added ? `<span class="slot-ok">${ic("check", 10, 3)}</span>` : ""}
              </div>
              <div class="tcap ell">${esc(im.name)}</div>
              <div class="tmeta mono">${im.width}×${im.height}</div>
            </div>`;
        }).join("")}
      </div>
    `,
    footerHtml: `<button class="btn btn-p" id="mDoneRef">完成</button>`,
  });
  document.getElementById("mDoneRef").addEventListener("click", () => {
    closeModal();
    renderStep3();
  });
  document.querySelectorAll("[data-pick-ref]").forEach((el) => {
    el.addEventListener("click", () => {
      const p = el.dataset.pickRef;
      const idx = draft.refs.indexOf(p);
      if (idx >= 0) draft.refs.splice(idx, 1);
      else draft.refs.push(p);
      openRefPoolModal(job, draft);
    });
  });
}

function openQuickSearchModal() {
  const jobs = appState.data?.jobs || [];
  openModal({
    title: "快速定位图片 (Ctrl+K)",
    bodyHtml: `
      <input class="field-input" id="qsInput" placeholder="输入文件名、SKU 编码或图类（如 RC4661A、俄文、参数表）..." autofocus />
      <div id="qsList" style="margin-top:12px;max-height:320px;overflow-y:auto;display:flex;flex-direction:column;gap:4px"></div>
    `,
  });
  const input = document.getElementById("qsInput");
  const listEl = document.getElementById("qsList");
  const renderList = (q = "") => {
    const kw = q.trim().toLowerCase();
    const hits = jobs.filter((j) => !kw || j.filename.toLowerCase().includes(kw) || j.tag.toLowerCase().includes(kw) || j.category.toLowerCase().includes(kw)).slice(0, 15);
    listEl.innerHTML = hits.map((j) => `
      <button class="recent" data-qs-jump="${esc(j.filename)}" style="height:38px;justify-content:space-between">
        <span class="row" style="gap:8px;min-width:0">
          <span class="pill p-gray">${esc(j.tag)}</span>
          <span class="mono ell" style="font-weight:600;color:#111827">${esc(j.filename)}</span>
        </span>
        <span class="pill ${j.status === "done" ? "p-ok" : "p-gray"}">${j.status === "done" ? "已生成" : "待生成"}</span>
      </button>
    `).join("") || `<div class="card-d" style="padding:16px;text-align:center">未找到匹配项</div>`;
    listEl.querySelectorAll("[data-qs-jump]").forEach((btn) => {
      btn.addEventListener("click", () => {
        appState.selectedFilename = btn.dataset.qsJump;
        appState.activeTab = "all";
        closeModal();
        goStep(3);
      });
    });
  };
  renderList();
  input.addEventListener("input", () => renderList(input.value));
  setTimeout(() => input.focus(), 30);
}

// ---------------- 批量进度轮询（无感局部刷新，绝不滚回顶部、绝不打断输入） ----------------
function startPolling() {
  if (appState.pollTimer) return;
  appState.pollTimer = setInterval(async () => {
    try {
      const prev = appState.data;
      const next = await api("/api/generate/status");
      const wasRunning = prev?.batch?.running;
      appState.data = next;
      if (appState.step === 3) patchStep3Live(prev, next);
      renderChrome();
      if (wasRunning && !next.batch?.running) {
        stopPolling();
        if (appState.step === 3) renderStep3();
        toast(`批量任务结束：本次成功 ${next.batch.completed} 张${next.batch.failed ? `，失败 ${next.batch.failed} 张` : ""}`, next.batch.failed ? "warn" : "ok");
      }
    } catch (_) {
      // 忽略瞬时网络抖动
    }
  }, 1000);
}

function stopPolling() {
  if (appState.pollTimer) {
    clearInterval(appState.pollTimer);
    appState.pollTimer = null;
  }
}

// ---------------- 启动引导 ----------------
async function bootstrap() {
  hydrateStaticIcons();
  bindGlobalEvents();
  try {
    appState.data = await api("/api/bootstrap");
    if (appState.data?.batch?.running) startPolling();
    renderAll();
  } catch (e) {
    toast(`初始化失败：${e.message}`, "bad");
  }
}

bootstrap();
