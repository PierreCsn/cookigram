const CACHE = 'cookigram-__VERSION__';
const PRECACHE = [
  './',
  './assets/app.css?__VERSION__',
  './assets/scaling.css?__VERSION__',
  './assets/images.css?__VERSION__',
  './assets/app.js?__VERSION__',
  './manifest.webmanifest',
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PRECACHE)));
});
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.open(CACHE).then(cache =>
      cache.match(event.request).then(hit => hit || fetch(event.request).then(response => {
        if (response && response.status === 200 && response.type === 'basic') {
          cache.put(event.request, response.clone());
        }
        return response;
      }))
    )
  );
});