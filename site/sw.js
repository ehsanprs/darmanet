// Service worker: makes the installed app open offline.
// Pages and data come from the network when possible (so updates show up), with the
// saved copy as fallback; fonts, icons and map code are served from the saved copy.
// Requests to other sites (map tiles, Google, GitHub) are not touched.
const CACHE = "darmanet-v1";
const CORE = [
  "./", "index.html", "manifest.json",
  "assets/styles.css", "assets/app.js", "assets/logo.svg",
  "assets/fonts/Vazirmatn-wght.woff2", "assets/icons/icon-192.png",
  "data/centers.js", "data/manual_locations.json",
];
const STATIC = /\/assets\/(fonts|icons|vendor)\/|logo\.svg$/;

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) =>
    Promise.all(CORE.map((url) => cache.add(url).catch(() => null)))));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;

  if (STATIC.test(new URL(req.url).pathname)) {
    event.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) caches.open(CACHE).then((c) => c.put(req, res.clone()));
      return res;
    })));
    return;
  }

  event.respondWith(fetch(req).then((res) => {
    if (res.ok) {
      const copy = res.clone();
      // Store pages without their ?filters so any link to the site works offline.
      caches.open(CACHE).then((c) => c.put(req.mode === "navigate" ? "index.html" : req, copy));
    }
    return res;
  }).catch(() => caches.match(req, { ignoreSearch: true })
    .then((hit) => hit || (req.mode === "navigate" ? caches.match("index.html") : undefined))
    .then((hit) => hit || Response.error())));
});
