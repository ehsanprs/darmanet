(() => {
  "use strict";

  const PAGE = 24;
  const INSURERS = [
    { key: "تامین اجتماعی", cls: "tamin", color: "var(--ins-tamin)" },
    { key: "خدمات درمانی", cls: "salamat", color: "var(--ins-salamat)", label: "خدمات درمانی (سلامت)" },
    { key: "نیروهای مسلح", cls: "artesh", color: "var(--ins-artesh)" },
  ];

  // Stroke icons (24x24 viewBox).
  const ICONS = {
    tooth: "M7 3C5 3 3.5 4.6 3.5 7c0 2.5 1.2 4 1.8 6.5.5 2.2.7 7.5 2.7 7.5 1.6 0 1.5-5 4-5s2.4 5 4 5c2 0 2.2-5.3 2.7-7.5.6-2.5 1.8-4 1.8-6.5 0-2.4-1.5-4-3.5-4-1.8 0-3 1-5 1S8.8 3 7 3z",
    flask: "M9 3h6M10 3v6l-5.5 9.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3M7 15h10",
    scan: "M4 8V5a1 1 0 0 1 1-1h3m8 0h3a1 1 0 0 1 1 1v3m0 8v3a1 1 0 0 1-1 1h-3m-8 0H5a1 1 0 0 1-1-1v-3M9 12a3 3 0 1 0 6 0 3 3 0 1 0-6 0",
    activity: "M3 12h4l3-8 4 16 3-8h4",
    stetho: "M6 3v6a4 4 0 0 0 8 0V3M10 13v2a5 5 0 0 0 10 0v-2M18.5 11a1.5 1.5 0 1 0 3 0 1.5 1.5 0 1 0-3 0",
    pill: "M10.5 20.5a5 5 0 0 1-7-7l6-6a5 5 0 0 1 7 7zM8.5 8.5l7 7",
    hospital: "M4 21V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v16M2 21h20M12 7v6M9 10h6M10 21v-4h4v4",
    glasses: "M2 15a3.5 3.5 0 1 0 7 0 3.5 3.5 0 1 0-7 0m13 0a3.5 3.5 0 1 0 7 0 3.5 3.5 0 1 0-7 0M9 15a3 3 0 0 1 6 0M2.5 13 5 6h2m14.5 7L19 6h-2",
    heart: "M12 20s-7-4.5-9-9a4.5 4.5 0 0 1 9-3 4.5 4.5 0 0 1 9 3c-2 4.5-9 9-9 9zM7 12h2.5l1.5-2.5 2 4 1.5-1.5H17",
    endo: "M3 5h7a3.5 3.5 0 0 1 0 7H8a3.5 3.5 0 0 0 0 7h9m0 0a2 2 0 1 0 4 0 2 2 0 1 0-4 0",
    clinic: "M5 4h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zm7 4v8m-4-4h8",
    scissors: "M3 6a3 3 0 1 0 6 0 3 3 0 1 0-6 0m0 12a3 3 0 1 0 6 0 3 3 0 1 0-6 0M20 4 8.1 15.9m6.4-1.4L20 20M8.1 8.1 12 12",
    siren: "M7 18v-6a5 5 0 0 1 10 0v6M5 21h14v-3H5zM12 3V1M4.2 6.2 3 5m16.8 1.2L21 5",
    homecare: "M3 11l9-7 9 7M5 9.5V20h14V9.5M12 17s-3-1.8-3-3.7a1.6 1.6 0 0 1 3-.8 1.6 1.6 0 0 1 3 .8c0 1.9-3 3.7-3 3.7z",
    doctor: "M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
    pin: "M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21zm0-9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
    phone: "M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2",
    copy: "M9 9h11v11H9zM5 15H4V4h11v1",
    search: "M4 11a7 7 0 1 0 14 0 7 7 0 1 0-14 0m16.5 9.5L16 16",
    x: "M6 6l12 12M18 6 6 18",
    grid: "M4 4h6v6H4zm10 0h6v6h-6zM4 14h6v6H4zm10 0h6v6h-6z",
  };

  const TYPE_STYLE = {
    "دندانپزشکی": ["tooth", "#0891b2"],
    "آزمایشگاه": ["flask", "#7c3aed"],
    "فیزیوتراپی": ["activity", "#16a34a"],
    "تصویربرداری": ["scan", "#2563eb"],
    "درمانگاه": ["stetho", "#0d9488"],
    "داروخانه": ["pill", "#db2777"],
    "بیمارستان": ["hospital", "#dc2626"],
    "عینک سازی": ["glasses", "#9333ea"],
    "بخش گوارش (آندوسکوپی و کولونوسکوپی)": ["endo", "#ca8a04"],
    "بخش گوارش (آندوسکوپی)": ["endo", "#ca8a04"],
    "کلینیک": ["clinic", "#0f766e"],
    "مرکز جراحی محدود": ["scissors", "#475569"],
    "کلینیک قلب": ["heart", "#e11d48"],
    "خدمات اورژانس": ["siren", "#ea580c"],
    "مطب": ["doctor", "#4f46e5"],
    "خدمات پرستاری در منزل": ["homecare", "#65a30d"],
  };

  const $ = (id) => document.getElementById(id);
  const el = {
    q: $("q"), clearQ: $("clearQ"), province: $("province"), city: $("city"),
    typeChips: $("typeChips"), typeList: $("typeList"), insuranceList: $("insuranceList"),
    onlineOnly: $("onlineOnly"), phoneOnly: $("phoneOnly"),
    onlineCount: $("onlineCount"), phoneCount: $("phoneCount"),
    resultCount: $("resultCount"), activeFilters: $("activeFilters"),
    cards: $("cards"), sentinel: $("sentinel"), empty: $("empty"),
    sort: $("sort"), filters: $("filters"), backdrop: $("backdrop"),
    openFilters: $("openFilters"), closeFilters: $("closeFilters"),
    applyFilters: $("applyFilters"), resetAll: $("resetAll"), emptyReset: $("emptyReset"),
    filterBadge: $("filterBadge"), exportCsv: $("exportCsv"), updated: $("updated"),
    toast: $("toast"), results: $("results"),
  };

  // ---------- Helpers ----------
  const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
  const toFa = (s) => String(s).replace(/\d/g, (d) => FA_DIGITS[d]);
  const faNum = (n) => toFa(n.toLocaleString("en-US").replace(/,/g, "٬"));
  const collator = new Intl.Collator("fa");
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const icon = (name, cls = "icon") =>
    `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[name] || ICONS.clinic}"/></svg>`;

  function normalize(s) {
    return String(s || "")
      .replace(/[يى]/g, "ی").replace(/ك/g, "ک").replace(/[ةۀ]/g, "ه").replace(/[أإآ]/g, "ا")
      .replace(/[۰-۹]/g, (d) => d.charCodeAt(0) - 0x06f0)
      .replace(/[٠-٩]/g, (d) => d.charCodeAt(0) - 0x0660)
      .replace(/[‌‏ً-ٟ]/g, " ")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  function formatPhone(num) {
    if (num.startsWith("09")) return `${num.slice(0, 4)} ${num.slice(4, 7)} ${num.slice(7)}`;
    return `${num.slice(0, 3)}-${num.slice(3)}`;
  }

  function highlight(text, tokens) {
    let html = escapeHtml(text);
    if (tokens.length) {
      const parts = tokens
        .filter((t) => t.length > 1 || /\d/.test(t))
        .map((t) => [...t].map((ch) => ch.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
          .map((ch) => (ch === "ی" ? "[یيى]" : ch === "ک" ? "[کك]" : ch === "ا" ? "[اآأإ]" : ch === " " ? "[\\s\\u200c]" : ch))
          .join("\\u200c?"));
      if (parts.length) {
        const re = new RegExp(`(${parts.join("|")})`, "gi");
        html = html.replace(re, "<mark>$1</mark>");
      }
    }
    return toFa(html);
  }

  function debounce(fn, ms) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  }

  function toast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add("show");
    clearTimeout(toast.t);
    toast.t = setTimeout(() => el.toast.classList.remove("show"), 2200);
  }

  // ---------- State ----------
  const state = {
    q: "", province: "", city: "", types: new Set(), ins: "",
    online: false, phone: false, sort: "relevance",
  };
  let items = [];
  let filtered = [];
  let rendered = 0;
  let tokens = [];

  function readUrl() {
    const p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    state.province = p.get("p") || "";
    state.city = p.get("c") || "";
    state.types = new Set((p.get("t") || "").split("|").filter(Boolean));
    state.ins = p.get("i") || "";
    state.online = p.get("o") === "1";
    state.phone = p.get("ph") === "1";
    state.sort = p.get("s") || "relevance";
    if (![...p.keys()].length) {
      try { state.province = localStorage.getItem("darmanet.province") || ""; } catch (e) { /* storage unavailable */ }
    }
  }

  function writeUrl() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.province) p.set("p", state.province);
    if (state.city) p.set("c", state.city);
    if (state.types.size) p.set("t", [...state.types].join("|"));
    if (state.ins) p.set("i", state.ins);
    if (state.online) p.set("o", "1");
    if (state.phone) p.set("ph", "1");
    if (state.sort !== "relevance") p.set("s", state.sort);
    const qs = p.toString();
    history.replaceState(null, "", qs ? `?${qs}` : location.pathname);
    try { localStorage.setItem("darmanet.province", state.province); } catch (e) { /* storage unavailable */ }
  }

  // ---------- Data ----------
  function prepare(db) {
    items = db.centers.map((c) => {
      const phoneSearch = c.phones.map((n) => `${n} ${n.slice(1)} ${n.slice(3)}`).join(" ");
      return Object.assign(c, {
        _name: normalize(c.name),
        _s: normalize([c.name, c.type, c.province, c.city, c.address, c.postalCode, c.note, c.phoneText].join(" ")) + " " + phoneSearch,
        _ins: new Set(c.insurance || []),
      });
    });
    const d = new Date(db.meta.updated);
    el.updated.textContent = isNaN(d) ? db.meta.updated
      : new Intl.DateTimeFormat("fa-IR", { dateStyle: "long" }).format(d);
  }

  async function load() {
    if (window.DARMANET_DB) return window.DARMANET_DB;
    const res = await fetch("data/centers.json");
    if (!res.ok) throw new Error(res.status);
    return res.json();
  }

  // ---------- Filtering ----------
  function apply() {
    tokens = normalize(state.q).split(" ").filter(Boolean);
    const counts = {
      province: new Map(), city: new Map(), type: new Map(),
      ins: new Map(), insAll: 0, online: 0, phone: 0,
    };
    const out = [];

    for (const it of items) {
      let score = 0;
      let fq = true;
      for (const t of tokens) {
        if (!it._s.includes(t)) { fq = false; break; }
        const i = it._name.indexOf(t);
        score += i === 0 ? 6 : i > 0 ? (it._name[i - 1] === " " ? 4 : 3) : 1;
      }
      if (!fq) continue;
      it._score = score;

      const fp = !state.province || it.province === state.province;
      const fc = !state.city || it.city === state.city;
      const ft = !state.types.size || state.types.has(it.type);
      const fi = !state.ins || it._ins.has(state.ins);
      const fo = !state.online || it.onlineReferral === true;
      const fph = !state.phone || it.phones.length > 0;
      const rest = fi && fo && fph;

      if (ft && rest) {
        counts.province.set(it.province, (counts.province.get(it.province) || 0) + 1);
        if (fp) counts.city.set(it.city, (counts.city.get(it.city) || 0) + 1);
      }
      if (fp && fc) {
        if (rest) counts.type.set(it.type, (counts.type.get(it.type) || 0) + 1);
        if (ft && fo && fph) {
          counts.insAll++;
          for (const k of it._ins) counts.ins.set(k, (counts.ins.get(k) || 0) + 1);
        }
        if (ft && fi && fph && it.onlineReferral === true) counts.online++;
        if (ft && fi && fo && it.phones.length) counts.phone++;
        if (ft && rest) out.push(it);
      }
    }

    sortItems(out);
    filtered = out;
    renderFacets(counts);
    renderActive();
    renderCount();
    resetCards();
    writeUrl();
  }

  function sortItems(arr) {
    const s = state.sort;
    if (s === "name") arr.sort((a, b) => collator.compare(a.name, b.name));
    else if (s === "city") arr.sort((a, b) => collator.compare(a.province, b.province) || collator.compare(a.city, b.city) || collator.compare(a.name, b.name));
    else if (tokens.length) arr.sort((a, b) => b._score - a._score || collator.compare(a.name, b.name));
  }

  // ---------- Facets ----------
  function renderFacets(c) {
    const all = [...new Set(items.map((i) => i.province))].sort(collator.compare);
    const total = [...c.province.values()].reduce((a, b) => a + b, 0);
    el.province.innerHTML = `<option value="">همه استان‌ها (${faNum(total)})</option>` +
      all.map((p) => `<option value="${escapeHtml(p)}"${p === state.province ? " selected" : ""}>${escapeHtml(p)} (${faNum(c.province.get(p) || 0)})</option>`).join("");

    if (state.province) {
      const cities = [...new Set(items.filter((i) => i.province === state.province).map((i) => i.city))].sort(collator.compare);
      el.city.disabled = false;
      el.city.innerHTML = `<option value="">همه شهرها</option>` +
        cities.map((x) => `<option value="${escapeHtml(x)}"${x === state.city ? " selected" : ""}>${escapeHtml(x)} (${faNum(c.city.get(x) || 0)})</option>`).join("");
    } else {
      el.city.disabled = true;
      el.city.innerHTML = `<option value="">ابتدا استان را انتخاب کنید</option>`;
    }

    // Type chips, ordered by overall popularity so positions stay stable.
    if (!renderFacets.typeOrder) {
      const m = new Map();
      items.forEach((i) => m.set(i.type, (m.get(i.type) || 0) + 1));
      renderFacets.typeOrder = [...m.entries()].sort((a, b) => b[1] - a[1]).map((e) => e[0]);
    }
    const typeTotal = [...c.type.values()].reduce((a, b) => a + b, 0);
    el.typeChips.innerHTML =
      `<button type="button" class="chip" data-type="" aria-pressed="${!state.types.size}">${icon("grid")}همه <span class="n">${faNum(typeTotal)}</span></button>` +
      renderFacets.typeOrder.map((t) => {
        const [ic, color] = TYPE_STYLE[t] || ["clinic", "#0f766e"];
        const n = c.type.get(t) || 0;
        const on = state.types.has(t);
        return `<button type="button" class="chip" style="--chip-c:${color}" data-type="${escapeHtml(t)}" aria-pressed="${on}"${!n && !on ? ' data-zero=""' : ""}>${icon(ic)}${escapeHtml(t)} <span class="n">${faNum(n)}</span></button>`;
      }).join("");

    el.typeList.innerHTML = renderFacets.typeOrder.map((t) => {
      const [ic, color] = TYPE_STYLE[t] || ["clinic", "#0f766e"];
      const n = c.type.get(t) || 0;
      const on = state.types.has(t);
      return `<label class="opt${!n && !on ? " disabled" : ""}" style="--chip-c:${color}">
          <input type="checkbox" value="${escapeHtml(t)}"${on ? " checked" : ""}>
          ${icon(ic, "icon type-mini")}<span class="lbl">${escapeHtml(t)}</span><span class="count">${faNum(n)}</span>
        </label>`;
    }).join("");

    el.insuranceList.innerHTML =
      [{ key: "", label: "همه (بدون فیلتر بیمه)", n: c.insAll }]
        .concat(INSURERS.map((i) => ({ ...i, label: i.label || i.key, n: c.ins.get(i.key) || 0 })))
        .map((o) => `<label class="opt${!o.n && o.key !== state.ins ? " disabled" : ""}">
            <input type="radio" name="ins" value="${escapeHtml(o.key)}"${o.key === state.ins ? " checked" : ""}>
            ${o.color ? `<span class="dot" style="background:${o.color}"></span>` : ""}
            <span class="lbl">${escapeHtml(o.label)}</span><span class="count">${faNum(o.n)}</span>
          </label>`).join("");

    el.onlineOnly.checked = state.online;
    el.phoneOnly.checked = state.phone;
    el.onlineCount.textContent = `(${faNum(c.online)})`;
    el.phoneCount.textContent = `(${faNum(c.phone)})`;
    el.sort.value = state.sort;
  }

  function renderActive() {
    const pills = [];
    const add = (label, fn) => pills.push({ label, fn });
    if (state.q) add(`«${state.q}»`, () => { state.q = ""; el.q.value = ""; syncClear(); });
    if (state.province) add(state.province, () => { state.province = ""; state.city = ""; });
    if (state.city) add(state.city, () => { state.city = ""; });
    state.types.forEach((t) => add(t, () => state.types.delete(t)));
    if (state.ins) add(`بیمه ${state.ins}`, () => { state.ins = ""; });
    if (state.online) add("معرفی‌نامه آنلاین", () => { state.online = false; });
    if (state.phone) add("دارای تلفن", () => { state.phone = false; });
    renderActive.fns = pills.map((p) => p.fn);
    el.activeFilters.innerHTML = pills.map((p, i) =>
      `<button type="button" class="pill" data-i="${i}" aria-label="حذف فیلتر ${escapeHtml(p.label)}">${escapeHtml(p.label)}${icon("x", "")}</button>`).join("");

    const extra = state.types.size + (state.ins ? 1 : 0) + (state.online ? 1 : 0) + (state.phone ? 1 : 0);
    el.filterBadge.hidden = !extra;
    el.filterBadge.textContent = toFa(extra);
  }

  function renderCount() {
    const n = filtered.length;
    el.resultCount.innerHTML = n ? `<b>${faNum(n)}</b> مرکز درمانی یافت شد` : "نتیجه‌ای یافت نشد";
    el.applyFilters.textContent = n ? `نمایش ${faNum(n)} نتیجه` : "نتیجه‌ای یافت نشد";
    el.empty.hidden = n > 0;
    el.exportCsv.disabled = !n;
  }

  // ---------- Cards ----------
  function card(it) {
    const [ic, color] = TYPE_STYLE[it.type] || ["clinic", "#0f766e"];
    const loc = it.city && it.city !== it.province ? `${it.province}، ${it.city}` : it.province;

    const tags = [];
    if (it.insurance === null) tags.push(`<span class="tag">بیمه پایه: نامشخص</span>`);
    else if (!it.insurance.length) tags.push(`<span class="tag warn">بدون قرارداد بیمه پایه</span>`);
    else INSURERS.forEach((i) => { if (it._ins.has(i.key)) tags.push(`<span class="tag ${i.cls}">${i.key}</span>`); });
    if (it.onlineReferral) tags.push(`<span class="tag ok">✓ معرفی‌نامه آنلاین</span>`);

    const calls = it.phones.map((n) =>
      `<a class="btn call" href="tel:${n}">${icon("phone")}<span class="num">${toFa(formatPhone(n))}</span></a>`).join("");
    const rawPhone = !it.phones.length && it.phoneText && !/E\+/i.test(it.phoneText)
      ? `<span class="phone-raw">${toFa(escapeHtml(it.phoneText))}</span>` : "";
    const googleQ = encodeURIComponent(`${it.type} ${it.name} ${it.city}`);

    return `<article class="card" style="--chip-c:${color}">
      <div class="card-top">
        <span class="type-icon">${icon(ic)}</span>
        <div class="card-title">
          <h3>${highlight(it.name, tokens)}</h3>
          <div class="card-sub"><span class="type-name">${escapeHtml(it.type)}</span><span class="sep">•</span><span>${escapeHtml(loc)}</span></div>
        </div>
      </div>
      ${it.address ? `<p class="address">${icon("pin")}<span>${highlight(it.address, tokens)}${it.postalCode ? ` <span class="postal">· کد پستی ${toFa(it.postalCode)}</span>` : ""}</span></p>` : ""}
      ${tags.length ? `<div class="tags">${tags.join("")}</div>` : ""}
      ${it.note ? `<p class="note">${highlight(it.note, tokens)}</p>` : ""}
      <div class="actions">
        ${calls}${rawPhone}
        <a class="btn ghost" href="https://www.google.com/search?q=${googleQ}" target="_blank" rel="noopener" title="جستجوی این مرکز در گوگل (نقشه، نظرات، ساعت کاری)">${icon("search")}جستجو در گوگل</a>
        ${it.address ? `<button type="button" class="btn ghost" data-copy="${escapeHtml(it.address)}" title="کپی آدرس">${icon("copy")}کپی آدرس</button>` : ""}
      </div>
    </article>`;
  }

  function resetCards() {
    rendered = 0;
    el.cards.innerHTML = "";
    renderMore();
  }

  function renderMore() {
    if (rendered >= filtered.length) return;
    const next = filtered.slice(rendered, rendered + PAGE);
    el.cards.insertAdjacentHTML("beforeend", next.map(card).join(""));
    rendered += next.length;
  }

  // ---------- Export ----------
  function exportCsv() {
    const cols = ["نوع مرکز", "نام مرکز", "استان", "شهرستان", "تلفن", "آدرس", "کد پستی", "معرفی‌نامه آنلاین", "بیمه پایه", "توضیحات"];
    const q = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const rows = filtered.map((it) => [
      it.type, it.name, it.province, it.city,
      it.phones.length ? it.phones.join(" / ") : it.phoneText,
      it.address, it.postalCode,
      it.onlineReferral == null ? "" : it.onlineReferral ? "دارد" : "ندارد",
      it.insurance == null ? "" : it.insurance.length ? it.insurance.join("، ") : "ندارد",
      it.note,
    ].map(q).join(","));
    const blob = new Blob(["﻿" + [cols.map(q).join(","), ...rows].join("\r\n")], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `darmanet-${state.province || "iran"}${state.city ? "-" + state.city : ""}.csv`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast(`${faNum(filtered.length)} مرکز در فایل ذخیره شد`);
  }

  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (e) {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }
    toast("آدرس کپی شد");
  }

  // ---------- Mobile filter sheet ----------
  const mobile = window.matchMedia("(max-width: 900px)");
  function openSheet() {
    el.filters.classList.add("open");
    el.backdrop.hidden = false;
    document.body.style.overflow = "hidden";
    el.openFilters.setAttribute("aria-expanded", "true");
    el.closeFilters.focus();
  }
  function closeSheet() {
    if (!el.filters.classList.contains("open")) return;
    el.filters.classList.remove("open");
    el.backdrop.hidden = true;
    document.body.style.overflow = "";
    el.openFilters.setAttribute("aria-expanded", "false");
    el.openFilters.focus();
  }

  // ---------- Events ----------
  function change(fn, scroll = true) {
    fn();
    apply();
    if (scroll) {
      const top = el.results.getBoundingClientRect().top + window.scrollY - 70;
      if (window.scrollY > top) window.scrollTo({ top, behavior: "smooth" });
    }
  }

  const syncClear = () => { el.clearQ.hidden = !el.q.value; };
  const onSearch = debounce(() => change(() => { state.q = el.q.value.trim(); }, false), 180);
  el.q.addEventListener("input", () => { syncClear(); onSearch(); });
  el.q.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { el.q.blur(); el.results.focus({ preventScroll: true }); }
  });
  el.clearQ.addEventListener("click", () => { el.q.value = ""; syncClear(); el.q.focus(); change(() => { state.q = ""; }, false); });

  el.province.addEventListener("change", () => change(() => { state.province = el.province.value; state.city = ""; }));
  el.city.addEventListener("change", () => change(() => { state.city = el.city.value; }));
  el.sort.addEventListener("change", () => change(() => { state.sort = el.sort.value; }));
  el.onlineOnly.addEventListener("change", () => change(() => { state.online = el.onlineOnly.checked; }, !mobile.matches));
  el.phoneOnly.addEventListener("change", () => change(() => { state.phone = el.phoneOnly.checked; }, !mobile.matches));
  el.insuranceList.addEventListener("change", (e) => change(() => { state.ins = e.target.value; }, !mobile.matches));

  el.typeList.addEventListener("change", (e) => change(() => {
    if (e.target.checked) state.types.add(e.target.value);
    else state.types.delete(e.target.value);
  }, false));

  el.typeChips.addEventListener("click", (e) => {
    const b = e.target.closest(".chip");
    if (!b) return;
    const t = b.dataset.type;
    const x = el.typeChips.scrollLeft;
    change(() => {
      if (!t) state.types.clear();
      else if (state.types.has(t)) state.types.delete(t);
      else state.types.add(t);
    });
    el.typeChips.scrollLeft = x;
  });

  el.activeFilters.addEventListener("click", (e) => {
    const b = e.target.closest(".pill");
    if (b) change(renderActive.fns[+b.dataset.i]);
  });

  const resetAll = () => change(() => {
    Object.assign(state, { q: "", province: "", city: "", ins: "", online: false, phone: false });
    state.types.clear();
    el.q.value = "";
    syncClear();
  });
  el.resetAll.addEventListener("click", resetAll);
  el.emptyReset.addEventListener("click", resetAll);

  el.cards.addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy]");
    if (b) copy(b.dataset.copy);
  });
  el.exportCsv.addEventListener("click", exportCsv);

  el.openFilters.addEventListener("click", openSheet);
  el.closeFilters.addEventListener("click", closeSheet);
  el.applyFilters.addEventListener("click", () => { closeSheet(); change(() => {}); });
  el.backdrop.addEventListener("click", closeSheet);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeSheet();
    if (e.key === "/" && document.activeElement !== el.q && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)) {
      e.preventDefault();
      el.q.focus();
    }
  });
  mobile.addEventListener("change", () => { if (!mobile.matches) closeSheet(); });

  new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) renderMore();
  }, { rootMargin: "800px" }).observe(el.sentinel);

  const bar = document.querySelector(".types-bar");
  const onScroll = () => bar.classList.toggle("stuck", bar.getBoundingClientRect().top <= 0 && window.scrollY > 0);
  window.addEventListener("scroll", onScroll, { passive: true });

  window.addEventListener("popstate", () => { readUrl(); el.q.value = state.q; syncClear(); apply(); });

  // ---------- Init ----------
  el.cards.innerHTML = '<div class="skeleton"></div>'.repeat(4);
  load().then((db) => {
    prepare(db);
    readUrl();
    el.q.value = state.q;
    syncClear();
    apply();
  }).catch((err) => {
    console.error(err);
    el.cards.innerHTML = "";
    el.resultCount.textContent = "خطا در بارگذاری اطلاعات. فایل data/centers.js را با اجرای اسکریپت به‌روزرسانی بسازید.";
  });
})();
