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
    nav: "M3 11 21 3l-8 18-2-8z",
    edit: "M4 20h4L19 9l-4-4L4 16zm10-14 4 4",
    map: "M9 4 3 6v14l6-2 6 2 6-2V4l-6 2zM9 4v14m6-12v14",
    search: "M4 11a7 7 0 1 0 14 0 7 7 0 1 0-14 0m16.5 9.5L16 16",
    x: "M6 6l12 12M18 6 6 18",
    grid: "M4 4h6v6H4zm10 0h6v6h-6zM4 14h6v6H4zm10 0h6v6h-6z",
    bolt: "M13 2 4 14h7l-1 8 9-12h-7z",
    ribbon: "M12 3a3.5 3.5 0 0 0-3.5 3.5c0 2.6 2 5.1 3.5 7.2 1.5-2.1 3.5-4.6 3.5-7.2A3.5 3.5 0 0 0 12 3zm-2.2 13.7L6.5 21m11 0-3.3-4.3",
  };

  // Categories and services, from db.taxonomy (built by categories.py).
  let CATS = [];
  const CAT = new Map();
  const SVC = new Map(); // service key -> { label, cat }
  // Categories where a center without a specific service is worth flagging.
  const FLAG_UNSPECIFIED = new Set(["imaging"]);
  const catStyle = (key) => CAT.get(key) || { icon: "clinic", color: "#0f766e", label: "" };

  const $ = (id) => document.getElementById(id);
  const el = {
    q: $("q"), clearQ: $("clearQ"), province: $("province"), city: $("city"),
    typeChips: $("typeChips"), serviceChips: $("serviceChips"), typeList: $("typeList"),
    insuranceList: $("insuranceList"),
    onlineOnly: $("onlineOnly"), phoneOnly: $("phoneOnly"), allDayOnly: $("allDayOnly"),
    onlineCount: $("onlineCount"), phoneCount: $("phoneCount"), allDayCount: $("allDayCount"),
    resultCount: $("resultCount"), activeFilters: $("activeFilters"),
    cards: $("cards"), sentinel: $("sentinel"), empty: $("empty"),
    sort: $("sort"), filters: $("filters"), backdrop: $("backdrop"),
    openFilters: $("openFilters"), closeFilters: $("closeFilters"),
    applyFilters: $("applyFilters"), resetAll: $("resetAll"), emptyReset: $("emptyReset"),
    filterBadge: $("filterBadge"), exportCsv: $("exportCsv"), updated: $("updated"),
    toast: $("toast"), results: $("results"),
    mapToggle: $("mapToggle"), mapToggleMobile: $("mapToggleMobile"), mapPanel: $("mapPanel"),
    mapEl: $("map"), mapCount: $("mapCount"), searchArea: $("searchArea"), mapPreview: $("mapPreview"),
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

  const IS_ANDROID = /Android/i.test(navigator.userAgent);

  // How far to trust a center's map point: "ok", "approx" (street/area level) or
  // "suspect" (far from the neighborhood named in its address).
  function locQuality(it) {
    const g = it.geocode || {};
    if (g.suspect) return "suspect";
    return g.approx ? "approx" : "ok";
  }

  function suspectText(it) {
    const s = it.geocode.suspect;
    return `آدرس این مرکز در «${s.area}» است، اما نقطه ثبت‌شده روی نقشه حدود ${toFa(Math.round(s.km))} کیلومتر دورتر است.`;
  }

  // Google Maps search for the place itself: its kind and name in its city
  // («تصویربرداری آرینا تهران»), skipping words the name already contains.
  function nameSearchUrl(it) {
    const kind = it.type.includes("(") ? it.type.split("(")[0].replace("بخش", "").trim() : it.type;
    const parts = [it.name.includes(kind) ? "" : kind, it.name, it.name.includes(it.city) ? "" : it.city];
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(parts.filter(Boolean).join(" "))}`;
  }

  const addressSearchUrl = (it) =>
    `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${it.name} ${it.address} ${it.city}`.slice(0, 200))}`;

  function navMenu(it) {
    if (!it.location) return "";
    const { lat, lng } = it.location;
    const ll = `${lat},${lng}`;
    const quality = locQuality(it);
    const approx = quality !== "ok";
    const links = [
      ...(approx ? [["جستجوی آدرس در Google Maps", addressSearchUrl(it)]] : []),
      ["Google Maps", `https://www.google.com/maps/dir/?api=1&destination=${ll}`],
      ["بلد", `https://balad.ir/location?latitude=${lat}&longitude=${lng}&zoom=17`],
      ["Waze", `https://waze.com/ul?ll=${ll}&navigate=yes`],
    ];
    if (IS_ANDROID) links.push(["سایر برنامه‌ها (نشان و …)", `geo:${ll}?q=${ll}(${encodeURIComponent(it.name)})`]);
    return `<details class="nav-menu">
        <summary class="btn nav-btn" title="${approx ? "موقعیت این مرکز دقیق نیست" : "مسیریابی تا این مرکز"}">${icon("nav")}مسیریابی${quality === "suspect" ? " <small>(نامطمئن)</small>" : approx ? " <small>(تقریبی)</small>" : ""}</summary>
        <div class="menu" role="menu">
          ${quality === "suspect" ? `<p class="menu-note">${suspectText(it)} برای اطمینان آدرس را جستجو کنید یا پیش از حرکت تماس بگیرید.</p>`
            : approx ? `<p class="menu-note">موقعیت این مرکز تقریبی است؛ پیش از حرکت تماس بگیرید.</p>` : ""}
          ${links.map(([label, href]) => `<a role="menuitem" href="${href}" target="_blank" rel="noopener">${escapeHtml(label)}</a>`).join("")}
        </div>
      </details>`;
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
    q: "", province: "", city: "", cat: "", svcs: new Set(), ins: "",
    online: false, phone: false, allDay: false, sort: "relevance",
    map: false, bounds: null, near: null,
  };
  let items = [];
  let filtered = [];
  let mapItems = []; // matches every filter except the map area
  let listSig = "";
  const byId = new Map();
  let rendered = 0;
  let tokens = [];
  const globalSvc = new Map();
  // Service names/synonyms as whole phrases -> a marker token stored on tagged centers,
  // so «ام آر آی» means MRI instead of three short words matching everywhere.
  let synonyms = [];

  function readUrl() {
    const p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    state.province = p.get("p") || "";
    state.city = p.get("c") || "";
    state.cat = CAT.has(p.get("cat")) ? p.get("cat") : "";
    state.svcs = new Set((p.get("sv") || "").split("|").filter((k) => SVC.has(k) && SVC.get(k).cat === state.cat));
    state.allDay = p.get("h") === "1";
    state.ins = p.get("i") || "";
    state.online = p.get("o") === "1";
    state.phone = p.get("ph") === "1";
    state.sort = p.get("s") || "relevance";
    if (state.sort === "near" && !state.near) state.sort = "relevance";
    state.map = p.get("m") === "1";
    const mv = (p.get("mv") || "").split(",").map(Number);
    pendingView = mv.length === 3 && mv.every(Number.isFinite) ? mv : null;
    if (![...p.keys()].length) {
      // No filters in the address: restore the visitor's last province and city.
      try {
        state.province = localStorage.getItem("darmanet.province") || "";
        const city = localStorage.getItem("darmanet.city") || "";
        state.city = state.province && items.some((it) => it.province === state.province && it.city === city) ? city : "";
      } catch (e) { /* storage unavailable */ }
    }
  }

  function writeUrl() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.province) p.set("p", state.province);
    if (state.city) p.set("c", state.city);
    if (state.cat) p.set("cat", state.cat);
    if (state.svcs.size) p.set("sv", [...state.svcs].join("|"));
    if (state.allDay) p.set("h", "1");
    if (state.ins) p.set("i", state.ins);
    if (state.online) p.set("o", "1");
    if (state.phone) p.set("ph", "1");
    if (state.sort !== "relevance" && state.sort !== "near") p.set("s", state.sort);
    if (state.map) {
      p.set("m", "1");
      if (mapState.map) {
        const c = mapState.map.getCenter();
        p.set("mv", `${c.lat.toFixed(4)},${c.lng.toFixed(4)},${mapState.map.getZoom()}`);
      }
    }
    const qs = p.toString();
    history.replaceState(null, "", qs ? `?${qs}` : location.pathname);
    try {
      localStorage.setItem("darmanet.province", state.province);
      localStorage.setItem("darmanet.city", state.city);
    } catch (e) { /* storage unavailable */ }
  }

  // ---------- Data ----------
  function prepare(db) {
    CATS = db.taxonomy || [];
    CATS.forEach((c) => {
      CAT.set(c.key, c);
      c.services.forEach((s) => SVC.set(s.key, { ...s, cat: c.key }));
    });
    // Centers no longer listed on the source stay in the database, marked deleted.
    items = db.centers.filter((c) => !c.deleted).map((c) => {
      const phoneSearch = c.phones.map((n) => `${n} ${n.slice(1)} ${n.slice(3)}`).join(" ");
      const cats = c.categories || [];
      const svcs = (c.services || []).filter((k) => SVC.has(k));
      // Category/service names and synonyms make searches like «ام آر آی» or «اکو» work.
      const tagWords = cats.map((k) => catStyle(k).label)
        .concat(svcs.flatMap((k) => [SVC.get(k).label, ...SVC.get(k).syn]))
        .concat(c.allDay ? ["شبانه روزی", "24 ساعته"] : [])
        .concat(svcs.map((k) => `§${k}`));
      return Object.assign(c, {
        _name: normalize(c.name),
        _s: normalize([c.name, c.type, c.province, c.city, c.address, c.postalCode, c.note, c.phoneText, ...tagWords].join(" ")) + " " + phoneSearch,
        _ins: new Set(c.insurance || []),
        _cats: new Set(cats),
        _svcs: new Set(svcs),
      });
    });
    items.forEach((it) => it._svcs.forEach((k) => globalSvc.set(k, (globalSvc.get(k) || 0) + 1)));
    items.forEach((it) => byId.set(it.id, it));
    synonyms = [...SVC.values()]
      .flatMap((sv) => [sv.label, ...sv.syn].map((w) => [normalize(w), `§${sv.key}`]))
      .filter(([w]) => w)
      .sort((a, b) => b[0].length - a[0].length);
    const d = new Date(db.meta.updated);
    el.updated.textContent = isNaN(d) ? db.meta.updated
      : new Intl.DateTimeFormat("fa-IR", { dateStyle: "long" }).format(d);
  }

  const toLatinDigits = (s) => String(s)
    .replace(/[۰-۹]/g, (d) => d.charCodeAt(0) - 0x06f0).replace(/[٠-٩]/g, (d) => d.charCodeAt(0) - 0x0660);

  // Points set by hand in admin mode; published next to the data and applied on load.
  async function loadManual() {
    try {
      const res = await fetch("data/manual_locations.json", { cache: "no-store" });
      if (!res.ok) return {};
      const data = await res.json();
      return Object.fromEntries(Object.entries(data).filter(([k]) => !k.startsWith("_")));
    } catch (e) {
      return {}; // offline or opened from disk: the data file already contains them
    }
  }

  function applyManual(db, manual) {
    for (const c of db.centers) {
      const m = manual[c.id];
      if (m) {
        c.location = { lat: m.lat, lng: m.lng };
        c.geocode = { source: "manual", at: m.at };
      }
    }
  }

  async function load() {
    if (window.DARMANET_DB) return window.DARMANET_DB;
    const res = await fetch("data/centers.json");
    if (!res.ok) throw new Error(res.status);
    return res.json();
  }

  // ---------- Filtering ----------
  function apply() {
    let query = ` ${normalize(state.q)} `;
    for (const [phrase, marker] of synonyms) {
      if (query.includes(` ${phrase} `)) query = query.replace(` ${phrase} `, ` ${marker} `);
    }
    tokens = query.split(" ").filter(Boolean);
    const counts = {
      province: new Map(), city: new Map(), cat: new Map(), svc: new Map(),
      ins: new Map(), insAll: 0, online: 0, phone: 0, allDay: 0, catAll: 0,
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
      it._dist = state.near && it.location ? distanceKm(state.near, it.location) : Infinity;

      const fp = !state.province || it.province === state.province;
      const fc = !state.city || it.city === state.city;
      const fcat = !state.cat || it._cats.has(state.cat);
      let fsv = !state.svcs.size;
      if (!fsv) for (const k of state.svcs) if (it._svcs.has(k)) { fsv = true; break; }
      const ft = fcat && fsv;
      const fi = !state.ins || it._ins.has(state.ins);
      const fo = !state.online || it.onlineReferral === true;
      const fph = !state.phone || it.phones.length > 0;
      const fh = !state.allDay || it.allDay;
      const rest = fi && fo && fph && fh;

      if (ft && rest) {
        counts.province.set(it.province, (counts.province.get(it.province) || 0) + 1);
        if (fp) counts.city.set(it.city, (counts.city.get(it.city) || 0) + 1);
      }
      if (fp && fc) {
        if (rest) {
          counts.catAll++;
          for (const k of it._cats) counts.cat.set(k, (counts.cat.get(k) || 0) + 1);
          if (fcat) for (const k of it._svcs) counts.svc.set(k, (counts.svc.get(k) || 0) + 1);
        }
        if (ft && fo && fph && fh) {
          counts.insAll++;
          for (const k of it._ins) counts.ins.set(k, (counts.ins.get(k) || 0) + 1);
        }
        if (ft && fi && fph && fh && it.onlineReferral === true) counts.online++;
        if (ft && fi && fo && fh && it.phones.length) counts.phone++;
        if (ft && fi && fo && fph && it.allDay) counts.allDay++;
        if (ft && rest) out.push(it);
      }
    }

    sortItems(out);
    mapItems = out;
    filtered = state.bounds ? out.filter((it) => inBounds(it, state.bounds)) : out;
    renderFacets(counts);
    renderActive();
    renderCount();
    // Panning the map often leaves the same results; keep the list (and its scroll) then.
    const sig = filtered.map((it) => it.id).join(",") + "|" + state.sort;
    if (sig !== listSig) {
      listSig = sig;
      resetCards();
    }
    if (state.map && mapState.map) syncMarkers();
    writeUrl();
  }

  function sortItems(arr) {
    const s = state.sort;
    if (s === "name") arr.sort((a, b) => collator.compare(a.name, b.name));
    else if (s === "city") arr.sort((a, b) => collator.compare(a.province, b.province) || collator.compare(a.city, b.city) || collator.compare(a.name, b.name));
    else if (s === "near" && state.near) arr.sort((a, b) => a._dist - b._dist);
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

    // Category chips (pick one), then the chosen category's service chips (pick any).
    const catAll = c.catAll;
    el.typeChips.innerHTML =
      `<button type="button" class="chip" data-cat="" aria-pressed="${!state.cat}">${icon("grid")}همه <span class="n">${faNum(catAll)}</span></button>` +
      CATS.map((cat) => {
        const n = c.cat.get(cat.key) || 0;
        const on = state.cat === cat.key;
        return `<button type="button" class="chip" style="--chip-c:${cat.color}" data-cat="${cat.key}" aria-pressed="${on}"${!n && !on ? ' data-zero=""' : ""}>${icon(cat.icon)}${escapeHtml(cat.label)} <span class="n">${faNum(n)}</span></button>`;
      }).join("");

    const cat = CAT.get(state.cat);
    const svcs = cat ? cat.services.filter((s) => globalSvc.get(s.key)) : [];
    el.serviceChips.hidden = svcs.length < 2;
    el.serviceChips.style.setProperty("--chip-c", cat ? cat.color : "");
    el.serviceChips.innerHTML = svcs.length < 2 ? "" :
      `<span class="sub-label">خدمت:</span>` +
      svcs.map((s) => {
        const n = c.svc.get(s.key) || 0;
        const on = state.svcs.has(s.key);
        return `<button type="button" class="chip" data-svc="${s.key}" aria-pressed="${on}"${!n && !on ? ' data-zero=""' : ""}>${escapeHtml(s.label)} <span class="n">${faNum(n)}</span></button>`;
      }).join("");

    revealActive(el.typeChips);
    revealActive(el.serviceChips);

    el.typeList.innerHTML =
      `<label class="opt"><input type="radio" name="cat" value=""${!state.cat ? " checked" : ""}>${icon("grid", "icon type-mini")}<span class="lbl">همه</span><span class="count">${faNum(catAll)}</span></label>` +
      CATS.map((cat) => {
        const n = c.cat.get(cat.key) || 0;
        const on = state.cat === cat.key;
        return `<label class="opt${!n && !on ? " disabled" : ""}" style="--chip-c:${cat.color}">
          <input type="radio" name="cat" value="${cat.key}"${on ? " checked" : ""}>
          ${icon(cat.icon, "icon type-mini")}<span class="lbl">${escapeHtml(cat.label)}</span><span class="count">${faNum(n)}</span>
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

    el.allDayOnly.checked = state.allDay;
    el.allDayCount.textContent = `(${faNum(c.allDay)})`;
    el.onlineOnly.checked = state.online;
    el.phoneOnly.checked = state.phone;
    el.onlineCount.textContent = `(${faNum(c.online)})`;
    el.phoneCount.textContent = `(${faNum(c.phone)})`;
    el.sort.value = state.sort;
  }

  // On narrow screens the chip rows scroll sideways; keep the selected chip in view.
  function revealActive(row) {
    const chip = row.querySelector('.chip[aria-pressed="true"][data-cat]:not([data-cat=""]), .chip[aria-pressed="true"][data-svc]');
    if (!chip || row.scrollWidth <= row.clientWidth) return;
    const rr = row.getBoundingClientRect();
    const cr = chip.getBoundingClientRect();
    if (cr.left < rr.left || cr.right > rr.right) {
      row.scrollLeft += cr.left - rr.left - (rr.width - cr.width) / 2;
    }
  }

  function renderActive() {
    const pills = [];
    const add = (label, fn) => pills.push({ label, fn });
    if (state.q) add(`«${state.q}»`, () => { state.q = ""; el.q.value = ""; syncClear(); });
    if (state.province) add(state.province, () => { state.province = ""; state.city = ""; });
    if (state.city) add(state.city, () => { state.city = ""; });
    if (state.cat) add(catStyle(state.cat).label, () => { state.cat = ""; state.svcs.clear(); });
    state.svcs.forEach((k) => add(SVC.get(k).label, () => state.svcs.delete(k)));
    if (state.allDay) add("شبانه‌روزی", () => { state.allDay = false; });
    if (state.bounds && mobile.matches) add("محدوده انتخاب‌شده روی نقشه", () => { state.bounds = null; });
    if (state.ins) add(`بیمه ${state.ins}`, () => { state.ins = ""; });
    if (state.online) add("معرفی‌نامه آنلاین", () => { state.online = false; });
    if (state.phone) add("دارای تلفن", () => { state.phone = false; });
    renderActive.fns = pills.map((p) => p.fn);
    el.activeFilters.innerHTML = pills.map((p, i) =>
      `<button type="button" class="pill" data-i="${i}" aria-label="حذف فیلتر ${escapeHtml(p.label)}">${escapeHtml(p.label)}${icon("x", "")}</button>`).join("");

    const extra = (state.cat ? 1 : 0) + state.svcs.size + (state.ins ? 1 : 0) +
      (state.online ? 1 : 0) + (state.phone ? 1 : 0) + (state.allDay ? 1 : 0);
    el.filterBadge.hidden = !extra;
    el.filterBadge.textContent = toFa(extra);
  }

  function renderCount() {
    const n = filtered.length;
    el.resultCount.innerHTML = !n ? "نتیجه‌ای یافت نشد"
      : state.bounds ? `<b>${faNum(n)}</b> مرکز در محدوده نقشه <span class="muted">(از ${faNum(mapItems.length)})</span>`
      : `<b>${faNum(n)}</b> مرکز درمانی یافت شد`;
    el.applyFilters.textContent = n ? `نمایش ${faNum(n)} نتیجه` : "نتیجه‌ای یافت نشد";
    el.empty.hidden = n > 0;
    el.exportCsv.disabled = !n;
  }

  // ---------- Cards ----------
  function card(it) {
    const primary = (it.categories || [])[0];
    const { icon: ic, color } = catStyle(primary);
    const loc = it.city && it.city !== it.province ? `${it.province}، ${it.city}` : it.province;

    const tags = [];
    const svcTags = [...it._svcs].map((k) => SVC.get(k));
    svcTags.forEach((s) => tags.push(`<span class="tag svc" style="--chip-c:${catStyle(s.cat).color}">${escapeHtml(s.label)}</span>`));
    if (FLAG_UNSPECIFIED.has(primary) && !svcTags.some((s) => s.cat === primary)) {
      tags.push(`<span class="tag unknown" title="نوع خدمات این مرکز در منبع ذکر نشده است؛ تماس بگیرید">خدمات مشخص نشده</span>`);
    }
    if (it.allDay) tags.push(`<span class="tag ok">شبانه‌روزی</span>`);
    if (it.location && locQuality(it) === "suspect") {
      tags.unshift(`<span class="tag warn loc-warn" title="${escapeHtml(suspectText(it))}">⚠ موقعیت روی نقشه احتمالاً نادرست</span>`);
    }
    if (it.insurance === null) tags.push(`<span class="tag">بیمه پایه: نامشخص</span>`);
    else if (!it.insurance.length) tags.push(`<span class="tag warn">بدون قرارداد بیمه پایه</span>`);
    else INSURERS.forEach((i) => { if (it._ins.has(i.key)) tags.push(`<span class="tag ${i.cls}">${i.key}</span>`); });
    if (it.onlineReferral) tags.push(`<span class="tag ok">✓ معرفی‌نامه آنلاین</span>`);

    const calls = it.phones.map((n) =>
      `<a class="btn call" href="tel:${n}">${icon("phone")}<span class="num">${toFa(formatPhone(n))}</span></a>`).join("");
    const rawPhone = !it.phones.length && it.phoneText && !/E\+/i.test(it.phoneText)
      ? `<span class="phone-raw">${toFa(escapeHtml(it.phoneText))}</span>` : "";
    const googleQ = encodeURIComponent(`${it.type} ${it.name} ${it.city}`);

    return `<article class="card" data-id="${it.id}" style="--chip-c:${color}">
      <div class="card-top">
        <span class="type-icon">${icon(ic)}</span>
        <div class="card-title">
          <h3>${highlight(it.name, tokens)}</h3>
          <div class="card-sub"><span class="type-name">${escapeHtml(it.type)}</span><span class="sep">•</span><span>${escapeHtml(loc)}</span>${it._dist < Infinity ? `<span class="sep">•</span><span class="dist">${fmtKm(it._dist)}</span>` : ""}</div>
        </div>
      </div>
      ${it.address ? `<p class="address">${icon("pin")}<span>${highlight(it.address, tokens)}${it.postalCode ? ` <span class="postal">· کد پستی ${toFa(it.postalCode)}</span>` : ""}</span></p>` : ""}
      ${tags.length ? `<div class="tags">${tags.join("")}</div>` : ""}
      ${it.note ? `<p class="note">${highlight(it.note, tokens)}</p>` : ""}
      <div class="actions">
        ${calls}${rawPhone}
        ${navMenu(it)}
        ${it.location ? `<button type="button" class="btn ghost" data-locate="${it.id}">${icon("map")}روی نقشه</button>` : ""}
        ${ADMIN ? `<button type="button" class="btn ghost admin-edit" data-edit="${it.id}">${icon("edit")}ویرایش موقعیت</button>` : ""}
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
    const cols = ["نوع مرکز", "دسته‌بندی", "خدمات", "شبانه‌روزی", "نام مرکز", "استان", "شهرستان", "تلفن", "آدرس", "کد پستی", "معرفی‌نامه آنلاین", "بیمه پایه", "توضیحات"];
    const q = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const rows = filtered.map((it) => [
      it.type, [...it._cats].map((k) => catStyle(k).label).join("، "),
      [...it._svcs].map((k) => SVC.get(k).label).join("، "), it.allDay ? "بله" : "",
      it.name, it.province, it.city,
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

  // ---------- Map ----------
  // Leaflet is loaded only when the map is first opened, so the list stays fast.
  const mapState = {
    map: null, cluster: null, markers: new Map(), sig: null,
    programmatic: false, needFit: false, user: null, loading: null, highlighted: null,
  };
  let pendingView = null;

  function loadAsset(tag, attrs) {
    return new Promise((resolve, reject) => {
      const node = Object.assign(document.createElement(tag), attrs);
      node.onload = resolve;
      node.onerror = reject;
      document.head.appendChild(node);
    });
  }

  function loadLeaflet() {
    mapState.loading = mapState.loading || Promise.all([
      loadAsset("link", { rel: "stylesheet", href: "assets/vendor/leaflet.min.css" }),
      loadAsset("link", { rel: "stylesheet", href: "assets/vendor/MarkerCluster.css" }),
      loadAsset("script", { src: "assets/vendor/leaflet.min.js" }),
    ]).then(() => loadAsset("script", { src: "assets/vendor/leaflet.markercluster.js" }));
    return mapState.loading;
  }

  const filterSig = () => [state.q, state.province, state.city, state.cat, [...state.svcs].join(","),
    state.ins, state.online, state.phone, state.allDay].join("|");

  function mapBounds() {
    const b = mapState.map.getBounds();
    return { s: b.getSouth(), w: b.getWest(), n: b.getNorth(), e: b.getEast() };
  }

  const inBounds = (it, b) => it.location && it.location.lat >= b.s && it.location.lat <= b.n &&
    it.location.lng >= b.w && it.location.lng <= b.e;

  // Moves made by the code (fit to results, near me) should not count as the user exploring.
  function moveMap(fn) {
    mapState.programmatic = true;
    fn(mapState.map);
    setTimeout(() => { mapState.programmatic = false; }, 900);
  }

  function initMap() {
    const L = window.L;
    const map = L.map(el.mapEl, { zoomSnap: 0.5 }).setView([32.4, 53.7], 5);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
    }).addTo(map);
    map.attributionControl.setPrefix(false);

    const cluster = L.markerClusterGroup({
      chunkedLoading: true, showCoverageOnHover: false, maxClusterRadius: 50,
      iconCreateFunction: (group) => {
        const n = group.getChildCount();
        const big = n >= 100;
        return L.divIcon({
          className: "pin-wrap", iconSize: big ? [48, 48] : [40, 40],
          html: `<div class="cluster${big ? " lg" : ""}">${faNum(n)}</div>`,
        });
      },
    });
    map.addLayer(cluster);

    const Locate = L.Control.extend({
      options: { position: "topleft" },
      onAdd() {
        const b = L.DomUtil.create("button", "locate-btn leaflet-bar");
        b.type = "button";
        b.title = "نزدیک من";
        b.setAttribute("aria-label", "نزدیک من");
        b.innerHTML = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/></svg>';
        L.DomEvent.disableClickPropagation(b);
        L.DomEvent.on(b, "click", () => locateMe());
        return b;
      },
    });
    map.addControl(new Locate());

    map.on("moveend", onMapMove);
    map.on("click", hidePreview);
    mapState.map = map;
    mapState.cluster = cluster;
  }

  function onMapMove() {
    if (!state.map) return;
    if (!mobile.matches) {
      // Desktop: the list always shows what is inside the map.
      state.bounds = mapBounds();
      apply();
    } else if (!mapState.programmatic) {
      el.searchArea.hidden = false;
    }
    writeUrl();
  }

  function makeMarker(it) {
    const L = window.L;
    const { icon: ic, color } = catStyle((it.categories || [])[0]);
    const quality = locQuality(it);
    const marker = L.marker([it.location.lat, it.location.lng], {
      title: quality === "suspect" ? `${it.name} (موقعیت احتمالاً نادرست)` : it.name,
      icon: L.divIcon({
        className: "pin-wrap", iconSize: [30, 30], iconAnchor: [15, 36], popupAnchor: [0, -34],
        html: `<div class="pin${quality === "ok" ? "" : " approx"}${quality === "suspect" ? " suspect" : ""}" style="--pin:${color}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[ic] || ICONS.clinic}"/></svg></div>`,
      }),
    });
    marker.on("click", () => openCenter(it, marker, true));
    return marker;
  }

  function syncMarkers() {
    const sig = filterSig();
    if (sig !== mapState.sig) {
      mapState.sig = sig;
      mapState.cluster.clearLayers();
      const layers = [];
      for (const it of mapItems) {
        if (!it.location) continue;
        if (!mapState.markers.has(it.id)) mapState.markers.set(it.id, makeMarker(it));
        layers.push(mapState.markers.get(it.id));
      }
      mapState.cluster.addLayers(layers);
    }
    if (mapState.needFit) {
      mapState.needFit = false;
      fitToResults();
    }
    updateMapCount();
  }

  function fitToResults() {
    const pts = mapItems.filter((it) => it.location).map((it) => [it.location.lat, it.location.lng]);
    if (!pts.length) return;
    moveMap((m) => (pts.length === 1 ? m.setView(pts[0], 15) : m.fitBounds(pts, { padding: [40, 40], maxZoom: 15 })));
  }

  function updateMapCount() {
    if (!state.map) return;
    el.mapCount.textContent = state.bounds
      ? `${faNum(filtered.length)} مرکز در این محدوده`
      : `${faNum(mapItems.filter((it) => it.location).length)} مرکز روی نقشه`;
  }

  function popupHtml(it) {
    const ll = `${it.location.lat},${it.location.lng}`;
    const phone = it.phones[0];
    return `<div class="pop">
        <h4>${escapeHtml(it.name)}</h4>
        <div class="muted">${escapeHtml(it.type)} · ${escapeHtml(it.city)}${it._dist < Infinity ? ` · <span class="dist">${fmtKm(it._dist)}</span>` : ""}</div>
        ${locQuality(it) === "suspect" ? `<div class="pop-warn">⚠ ${suspectText(it)}</div>`
          : locQuality(it) === "approx" ? '<div class="muted">موقعیت تقریبی است</div>' : ""}
        <div class="pop-actions">
          ${phone ? `<a class="call" href="tel:${phone}">تماس ${toFa(formatPhone(phone))}</a>` : ""}
          ${locQuality(it) === "ok" ? "" : `<a class="ghost" href="${addressSearchUrl(it)}" target="_blank" rel="noopener">جستجوی آدرس</a>`}
          <a class="ghost" href="https://www.google.com/maps/dir/?api=1&destination=${ll}" target="_blank" rel="noopener">مسیریابی</a>
          ${ADMIN ? `<button type="button" class="ghost admin-edit" data-edit="${it.id}">ویرایش موقعیت</button>` : ""}
        </div>
      </div>`;
  }

  function openCenter(it, marker, fromMap) {
    if (mobile.matches) {
      showPreview(it);
      return;
    }
    marker.unbindPopup();
    marker.bindPopup(popupHtml(it), { maxWidth: 300 }).openPopup();
    // Leaflet keeps clicks inside popups from reaching the page, so bind the admin button here.
    const editBtn = ADMIN && marker.getPopup().getElement().querySelector("[data-edit]");
    if (editBtn) editBtn.addEventListener("click", () => { marker.closePopup(); editLocation(it.id); });
    if (fromMap) {
      // Load more of the list until the clicked center's card exists, then show it.
      const idx = filtered.indexOf(it);
      while (idx >= rendered && rendered < filtered.length) renderMore();
      const cardEl = el.cards.querySelector(`.card[data-id="${it.id}"]`);
      if (cardEl) {
        cardEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
        cardEl.classList.add("flash");
        setTimeout(() => cardEl.classList.remove("flash"), 1600);
      }
    }
  }

  function showPreview(it) {
    el.mapPreview.innerHTML = `<button type="button" class="preview-close" aria-label="بستن">${icon("x")}</button>${card(it)}`;
    el.mapPreview.hidden = false;
  }

  function hidePreview() {
    el.mapPreview.hidden = true;
    el.mapPreview.innerHTML = "";
  }

  async function focusCenter(id) {
    const it = byId.get(id);
    if (!it || !it.location) return;
    if (!state.map) await openMap();
    const marker = mapState.markers.get(id);
    if (!marker || !mapState.cluster.hasLayer(marker)) {
      moveMap((m) => m.setView([it.location.lat, it.location.lng], 16));
      return;
    }
    mapState.cluster.zoomToShowLayer(marker, () => openCenter(it, marker, false));
  }

  function highlightMarker(id) {
    if (mapState.highlighted) mapState.highlighted.classList.remove("hl");
    mapState.highlighted = null;
    const marker = id && mapState.markers.get(id);
    const pin = marker && marker.getElement() && marker.getElement().querySelector(".pin");
    if (pin) {
      pin.classList.add("hl");
      mapState.highlighted = pin;
    }
  }

  async function openMap() {
    state.map = true;
    document.body.classList.add("map-mode");
    el.mapPanel.hidden = false;
    el.mapToggle.setAttribute("aria-pressed", "true");
    try {
      await loadLeaflet();
    } catch (err) {
      toast("بارگذاری نقشه ممکن نشد");
      closeMap();
      return;
    }
    const first = !mapState.map;
    if (first) initMap();
    mapState.map.invalidateSize();
    mapState.sig = null;
    if (first && pendingView) {
      const [lat, lng, z] = pendingView;
      pendingView = null;
      moveMap((m) => m.setView([lat, lng], z));
    } else if (first) {
      mapState.needFit = true;
      if (!mobile.matches) state.bounds = null;
    }
    if (!mobile.matches && !mapState.needFit) state.bounds = mapBounds();
    apply();
  }

  function closeMap() {
    state.map = false;
    // On mobile an area chosen with «جستجو در این محدوده» stays as a filter on the list.
    if (!mobile.matches) state.bounds = null;
    document.body.classList.remove("map-mode");
    el.mapPanel.hidden = true;
    el.mapToggle.setAttribute("aria-pressed", "false");
    el.searchArea.hidden = true;
    hidePreview();
    apply();
  }

  const toggleMap = () => (state.map ? closeMap() : openMap());

  // ---------- Near me ----------
  function distanceKm(a, b) {
    const r = Math.PI / 180;
    const h = Math.sin((b.lat - a.lat) * r / 2) ** 2 +
      Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin((b.lng - a.lng) * r / 2) ** 2;
    return 12742 * Math.asin(Math.sqrt(h));
  }

  function fmtKm(d) {
    if (d < 1) return `${toFa(Math.max(10, Math.round(d * 100) * 10))} متر`;
    return `${toFa(d < 10 ? d.toFixed(1) : Math.round(d)).replace(".", "٫")} کیلومتر`;
  }

  function locateMe() {
    if (!navigator.geolocation) {
      toast("مرورگر شما از موقعیت‌یابی پشتیبانی نمی‌کند");
      return;
    }
    toast("در حال یافتن موقعیت شما…");
    navigator.geolocation.getCurrentPosition((pos) => {
      state.near = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      state.sort = "near";
      if (mapState.map && state.map) {
        const L = window.L;
        if (mapState.user) mapState.user.remove();
        mapState.user = L.marker([state.near.lat, state.near.lng], {
          interactive: false, keyboard: false,
          icon: L.divIcon({ className: "pin-wrap", iconSize: [16, 16], html: '<div class="user-dot"></div>' }),
        }).addTo(mapState.map);
        if (mobile.matches) {
          moveMap((m) => m.setView([state.near.lat, state.near.lng], 14));
        } else {
          mapState.map.setView([state.near.lat, state.near.lng], 14);
        }
      }
      apply();
    }, () => {
      toast("دسترسی به موقعیت شما داده نشد");
      if (!state.near && state.sort === "near") {
        state.sort = "relevance";
        apply();
      }
    }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
  }

  // ---------- Admin mode (hidden) ----------
  // Open the site once with ?admin to turn it on in this browser. Saving needs a GitHub
  // token with write access to the repository; it is kept only in this browser and the
  // change is committed to site/data/manual_locations.json, which GitHub Pages republishes.
  const GH = { owner: "ehsanprs", repo: "darmanet", branch: "main", path: "site/data/manual_locations.json" };
  const ADMIN = (() => {
    const asked = new URLSearchParams(location.search).has("admin");
    try {
      if (asked) localStorage.setItem("darmanet.admin", "1");
      return localStorage.getItem("darmanet.admin") === "1";
    } catch (e) {
      return asked;
    }
  })();
  const adminState = { editing: null, marker: null, panel: null };

  const ghToken = () => { try { return localStorage.getItem("darmanet.ghToken") || ""; } catch (e) { return ""; } };

  const b64encode = (text) => {
    let bin = "";
    new TextEncoder().encode(text).forEach((b) => { bin += String.fromCharCode(b); });
    return btoa(bin);
  };
  const b64decode = (b64) => new TextDecoder().decode(Uint8Array.from(atob(b64.replace(/\n/g, "")), (ch) => ch.charCodeAt(0)));

  async function github(method, body) {
    const url = `https://api.github.com/repos/${GH.owner}/${GH.repo}/contents/${GH.path}`;
    const res = await fetch(method === "GET" ? `${url}?ref=${GH.branch}` : url, {
      method,
      cache: "no-store",
      headers: { Authorization: `Bearer ${ghToken()}`, Accept: "application/vnd.github+json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (res.status === 401) throw new Error("توکن GitHub نامعتبر است یا منقضی شده.");
    if (res.status === 403 || res.status === 404) throw new Error("این توکن اجازه نوشتن در مخزن را ندارد.");
    return res;
  }

  async function saveManual(it, lat, lng) {
    const today = new Date().toISOString().slice(0, 10);
    for (let attempt = 0; attempt < 3; attempt++) {
      const cur = await (await github("GET")).json();
      const data = JSON.parse(b64decode(cur.content));
      data[it.id] = { lat: +lat.toFixed(6), lng: +lng.toFixed(6), at: today, name: it.name };
      const res = await github("PUT", {
        message: `Admin: set location of ${it.name} (${it.city})`,
        content: b64encode(JSON.stringify(data, null, 2) + "\n"),
        sha: cur.sha,
        branch: GH.branch,
      });
      if (res.ok) return;
      if (res.status !== 409 && res.status !== 422) throw new Error(`خطای GitHub (${res.status})`);
      // Someone else saved meanwhile: read the new version and try again.
    }
    throw new Error("ذخیره به دلیل تغییر هم‌زمان انجام نشد؛ دوباره تلاش کنید.");
  }

  function parseCoords(text) {
    const t = toLatinDigits(text || "");
    const m = t.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/) || t.match(/@(-?\d+\.\d+),\s*(-?\d+\.\d+)/) ||
      t.match(/(-?\d{1,2}\.\d+)\s*[,،\s]\s*(-?\d{1,2}\.\d+)/);
    if (!m) return null;
    const lat = +m[1];
    const lng = +m[2];
    return lat > 24 && lat < 41 && lng > 43 && lng < 64.5 ? { lat, lng } : null;
  }

  function adminBar() {
    const bar = document.createElement("div");
    bar.className = "admin-bar";
    bar.innerHTML = `<b>حالت مدیر</b><span id="adminTokenState"></span>
      <button type="button" class="link-btn" id="adminTokenBtn">توکن GitHub</button>
      <button type="button" class="link-btn" id="adminExit">خروج از حالت مدیر</button>`;
    document.body.prepend(bar);
    const refresh = () => {
      $("adminTokenState").textContent = ghToken() ? "· توکن تنظیم شده" : "· برای ذخیره، توکن GitHub را تنظیم کنید";
    };
    refresh();
    $("adminTokenBtn").addEventListener("click", () => {
      const dlg = document.createElement("dialog");
      dlg.className = "admin-dialog";
      dlg.innerHTML = `<form method="dialog">
          <h3>توکن GitHub</h3>
          <p class="hint">یک توکن fine-grained فقط برای مخزن ${GH.owner}/${GH.repo} با دسترسی «Contents: Read and write» بسازید و اینجا وارد کنید. توکن فقط در همین مرورگر ذخیره می‌شود.</p>
          <input type="password" id="adminTokenInput" dir="ltr" autocomplete="off" placeholder="github_pat_…">
          <div class="admin-actions">
            <button value="save" class="btn primary small">ذخیره</button>
            <button value="clear" class="btn ghost small">حذف توکن</button>
            <button value="cancel" class="btn ghost small">انصراف</button>
          </div></form>`;
      document.body.appendChild(dlg);
      dlg.addEventListener("close", async () => {
        const value = dlg.querySelector("#adminTokenInput").value.trim();
        try {
          if (dlg.returnValue === "save" && value) localStorage.setItem("darmanet.ghToken", value);
          if (dlg.returnValue === "clear") localStorage.removeItem("darmanet.ghToken");
        } catch (e) { toast("ذخیره توکن در این مرورگر ممکن نیست"); }
        dlg.remove();
        refresh();
        if (dlg.returnValue === "save" && value) {
          try {
            await (await github("GET")).json();
            toast("توکن کار می‌کند ✓");
          } catch (err) { toast(err.message); }
        }
      });
      dlg.showModal();
    });
    $("adminExit").addEventListener("click", () => {
      try { localStorage.removeItem("darmanet.admin"); } catch (e) { /* ignore */ }
      location.reload();
    });
  }

  function closeEditor() {
    if (adminState.marker) adminState.marker.remove();
    if (adminState.panel) adminState.panel.remove();
    if (mapState.map) mapState.map.off("click", onEditClick);
    Object.assign(adminState, { editing: null, marker: null, panel: null });
  }

  function onEditClick(e) {
    adminState.marker.setLatLng(e.latlng);
    showEditPoint(e.latlng);
  }

  function showEditPoint(ll) {
    const input = adminState.panel && adminState.panel.querySelector(".edit-coords");
    if (input) input.value = `${ll.lat.toFixed(6)}, ${ll.lng.toFixed(6)}`;
  }

  async function editLocation(id) {
    const it = byId.get(id);
    if (!it) return;
    closeEditor();
    hidePreview();
    if (!state.map) await openMap();
    if (!mapState.map) return;
    const L = window.L;
    const start = it.location ? [it.location.lat, it.location.lng] : mapState.map.getCenter();
    adminState.editing = it;
    adminState.marker = L.marker(start, {
      draggable: true, zIndexOffset: 2000, autoPan: true,
      icon: L.divIcon({ className: "pin-wrap", iconSize: [30, 30], iconAnchor: [15, 36],
        html: `<div class="pin edit-pin"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS.edit}"/></svg></div>` }),
    }).addTo(mapState.map);
    adminState.marker.on("dragend", () => showEditPoint(adminState.marker.getLatLng()));
    mapState.map.on("click", onEditClick);
    moveMap((m) => m.setView(start, Math.max(m.getZoom(), 16)));

    const g = it.geocode || {};
    const panel = document.createElement("div");
    panel.className = "edit-panel";
    panel.innerHTML = `
      <h4>${escapeHtml(it.name)}</h4>
      <p class="muted">${escapeHtml(it.type)} · ${escapeHtml(it.city)}<br>${escapeHtml(it.address)}</p>
      <p class="muted">منبع فعلی: ${escapeHtml(g.source || "بدون موقعیت")}${g.approx ? " · تقریبی" : ""}${g.suspect ? " · احتمالاً نادرست" : ""}</p>
      <label class="muted" for="editCoords">مختصات یا لینک Google Maps</label>
      <input class="edit-coords" id="editCoords" dir="ltr" placeholder="35.7575, 51.4100">
      <p class="hint">نشانگر را بکشید، روی نقشه کلیک کنید، یا مختصات را از Google Maps (کلیک راست روی محل) جای‌گذاری کنید.</p>
      <div class="admin-actions">
        <a class="btn ghost small" target="_blank" rel="noopener" href="${nameSearchUrl(it)}">جستجوی نام در Google Maps</a>
        <a class="btn ghost small" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${it.address} ${it.city}`)}">جستجوی آدرس</a>
        <button type="button" class="btn primary small" data-admin="save">ذخیره موقعیت</button>
        ${it.location ? '<button type="button" class="btn ghost small" data-admin="verify">موقعیت فعلی درست است</button>' : ""}
        <button type="button" class="btn ghost small" data-admin="cancel">انصراف</button>
      </div>`;
    el.mapPanel.appendChild(panel);
    adminState.panel = panel;
    showEditPoint(adminState.marker.getLatLng());
    const input = panel.querySelector(".edit-coords");
    input.addEventListener("input", () => {
      const p = parseCoords(input.value);
      if (p) {
        adminState.marker.setLatLng([p.lat, p.lng]);
        moveMap((m) => m.panTo([p.lat, p.lng]));
      }
    });
    panel.addEventListener("click", async (e) => {
      const action = e.target.closest("[data-admin]")?.dataset.admin;
      if (!action) return;
      if (action === "cancel") return closeEditor();
      if (!ghToken()) return toast("ابتدا توکن GitHub را از نوار بالا تنظیم کنید");
      const p = action === "verify" ? it.location : parseCoords(input.value);
      if (!p) return toast("مختصات معتبر داخل ایران وارد کنید");
      e.target.disabled = true;
      try {
        await saveManual(it, p.lat, p.lng);
        it.location = { lat: +p.lat.toFixed(6), lng: +p.lng.toFixed(6) };
        it.geocode = { source: "manual", at: new Date().toISOString().slice(0, 10) };
        const old = mapState.markers.get(it.id);
        if (old) mapState.cluster.removeLayer(old);
        mapState.markers.delete(it.id);
        mapState.sig = null;
        listSig = "";
        closeEditor();
        apply();
        toast("ذخیره شد ✓ حدود یک دقیقه دیگر روی سایت منتشر می‌شود");
      } catch (err) {
        toast(err.message);
        e.target.disabled = false;
      }
    });
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

  // Choosing a place zooms the map to it.
  const refit = () => {
    if (!state.map) return;
    mapState.needFit = true;
    state.bounds = null;
    el.searchArea.hidden = true;
  };
  el.province.addEventListener("change", () => change(() => { state.province = el.province.value; state.city = ""; refit(); }));
  el.city.addEventListener("change", () => change(() => { state.city = el.city.value; refit(); }));
  el.sort.addEventListener("change", () => {
    if (el.sort.value === "near" && !state.near) {
      state.sort = "near";
      locateMe();
      return;
    }
    change(() => { state.sort = el.sort.value; });
  });
  el.onlineOnly.addEventListener("change", () => change(() => { state.online = el.onlineOnly.checked; }, !mobile.matches));
  el.allDayOnly.addEventListener("change", () => change(() => { state.allDay = el.allDayOnly.checked; }, !mobile.matches));
  el.phoneOnly.addEventListener("change", () => change(() => { state.phone = el.phoneOnly.checked; }, !mobile.matches));
  el.insuranceList.addEventListener("change", (e) => change(() => { state.ins = e.target.value; }, !mobile.matches));

  const selectCat = (key) => {
    state.cat = state.cat === key ? "" : key;
    state.svcs.clear();
  };
  el.typeList.addEventListener("change", (e) => change(() => {
    state.cat = e.target.value;
    state.svcs.clear();
  }, false));

  el.typeChips.addEventListener("click", (e) => {
    const b = e.target.closest(".chip");
    if (!b) return;
    const x = el.typeChips.scrollLeft;
    change(() => selectCat(b.dataset.cat));
    el.typeChips.scrollLeft = x;
  });

  el.serviceChips.addEventListener("click", (e) => {
    const b = e.target.closest(".chip");
    if (!b) return;
    const x = el.serviceChips.scrollLeft;
    change(() => {
      const k = b.dataset.svc;
      if (state.svcs.has(k)) state.svcs.delete(k);
      else state.svcs.add(k);
    });
    el.serviceChips.scrollLeft = x;
  });

  el.activeFilters.addEventListener("click", (e) => {
    const b = e.target.closest(".pill");
    if (b) change(renderActive.fns[+b.dataset.i]);
  });

  const resetAll = () => change(() => {
    Object.assign(state, { q: "", province: "", city: "", cat: "", ins: "", online: false, phone: false, allDay: false, bounds: null });
    if (state.map) mapState.needFit = true;
    state.svcs.clear();
    el.q.value = "";
    syncClear();
  });
  el.resetAll.addEventListener("click", resetAll);
  el.emptyReset.addEventListener("click", resetAll);

  // Cards also appear in the map preview, so handle their buttons anywhere on the page.
  document.addEventListener("click", (e) => {
    const copyBtn = e.target.closest("[data-copy]");
    if (copyBtn) copy(copyBtn.dataset.copy);
    const locate = e.target.closest("[data-locate]");
    if (locate) focusCenter(locate.dataset.locate);
    const edit = ADMIN && e.target.closest("[data-edit]");
    if (edit) editLocation(edit.dataset.edit);
    if (e.target.closest(".preview-close")) hidePreview();
  });
  el.cards.addEventListener("mouseover", (e) => {
    if (!state.map || mobile.matches) return;
    const c = e.target.closest(".card");
    highlightMarker(c && c.dataset.id);
  });
  el.cards.addEventListener("mouseleave", () => highlightMarker(null));

  el.mapToggle.addEventListener("click", toggleMap);
  el.mapToggleMobile.addEventListener("click", toggleMap);
  el.searchArea.addEventListener("click", () => {
    state.bounds = mapBounds();
    el.searchArea.hidden = true;
    hidePreview();
    apply();
  });
  el.exportCsv.addEventListener("click", exportCsv);

  // Only one directions menu open at a time; close it on outside click or Escape.
  const closeMenus = (except) => document.querySelectorAll(".nav-menu[open]")
    .forEach((d) => { if (d !== except) d.open = false; });
  document.addEventListener("toggle", (e) => {
    if (!e.target.classList || !e.target.classList.contains("nav-menu") || !e.target.open) return;
    closeMenus(e.target);
    // Open toward whichever side has room, so the menu never leaves the screen.
    const menu = e.target.querySelector(".menu");
    menu.style.left = menu.style.right = "";
    if (menu.getBoundingClientRect().left < 8) { menu.style.right = "auto"; menu.style.left = "0"; }
  }, true);
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".nav-menu")) closeMenus();
    else if (e.target.closest(".menu a")) closeMenus();
  });

  el.openFilters.addEventListener("click", openSheet);
  el.closeFilters.addEventListener("click", closeSheet);
  el.applyFilters.addEventListener("click", () => { closeSheet(); change(() => {}); });
  el.backdrop.addEventListener("click", closeSheet);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { closeMenus(); closeSheet(); hidePreview(); closeEditor(); }
    if (e.key === "/" && document.activeElement !== el.q && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)) {
      e.preventDefault();
      el.q.focus();
    }
  });
  mobile.addEventListener("change", () => {
    if (!mobile.matches) closeSheet();
    if (mapState.map && state.map) {
      mapState.map.invalidateSize();
      el.searchArea.hidden = true;
      hidePreview();
      state.bounds = mobile.matches ? null : mapBounds();
      apply();
    }
  });

  new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) renderMore();
  }, { rootMargin: "800px" }).observe(el.sentinel);

  const bar = document.querySelector(".types-bar");
  const onScroll = () => bar.classList.toggle("stuck", bar.getBoundingClientRect().top <= 0 && window.scrollY > 0);
  window.addEventListener("scroll", onScroll, { passive: true });

  window.addEventListener("popstate", () => {
    const wasMap = state.map;
    readUrl();
    el.q.value = state.q;
    syncClear();
    if (state.map && !wasMap) openMap();
    else if (!state.map && wasMap) closeMap();
    else apply();
  });

  // ---------- Init ----------
  el.cards.innerHTML = '<div class="skeleton"></div>'.repeat(4);
  if (ADMIN) adminBar();
  load().then(async (db) => {
    applyManual(db, await loadManual());
    prepare(db);
    readUrl();
    el.q.value = state.q;
    syncClear();
    apply();
    if (state.map) openMap();
  }).catch((err) => {
    console.error(err);
    el.cards.innerHTML = "";
    el.resultCount.textContent = "خطا در بارگذاری اطلاعات. فایل data/centers.js را با اجرای اسکریپت به‌روزرسانی بسازید.";
  });
})();
