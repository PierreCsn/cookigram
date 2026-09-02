const CACHE = 'cookigram-__VERSION__';
const PRECACHE = __PRECACHE__;


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
  if (event.request.mode === 'navigate') {
    event.respondWith(networkFirst(event.request));
    return;
  }
  event.respondWith(cacheFirst(event.request));
});

const cacheSuccessful = async (cache, request, response) => {
  if (response?.status === 200 && response.type === 'basic') {
    await cache.put(request, response.clone());
  }
  return response;
};

const networkFirst = async request => {
  const cache = await caches.open(CACHE);
  try {
    return await cacheSuccessful(cache, request, await fetch(request));
  } catch (_) {
    return (await cache.match(request, { ignoreSearch: true })) || cache.match('./');
  }
};

const cacheFirst = async request => {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  return cacheSuccessful(cache, request, await fetch(request));
};
