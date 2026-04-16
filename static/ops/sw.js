// SUMO Ops Service Worker
const SW_VERSION = 'sumo-ops-v1';
const STATIC_CACHE = 'sumo-ops-static-v1';
const RUNTIME_CACHE = 'sumo-ops-runtime-v1';
const OFFLINE_URL = '/ops/offline';

const PRECACHE_URLS = [
  OFFLINE_URL,
  '/static/css/ops.css',
  '/static/ops/manifest.json',
  '/static/ops/icons/icon-192.png',
  '/static/ops/icons/icon-512.png',
  '/static/ops/icons/apple-touch-icon.png',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return Promise.all(
        PRECACHE_URLS.map((url) =>
          cache.add(url).catch((err) => console.warn('SW precache fail', url, err))
        )
      );
    })
    // Do NOT call skipWaiting() here — wait for explicit SKIP_WAITING message
    // from the client so the user controls when the new version takes over.
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((n) => n !== STATIC_CACHE && n !== RUNTIME_CACHE)
          .map((n) => caches.delete(n))
      )
    ).then(() => self.clients.claim())
  );
});

function isStaticAsset(url) {
  return (
    url.pathname.startsWith('/static/') ||
    url.hostname === 'cdnjs.cloudflare.com' ||
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com'
  );
}

function isApiOrStream(url) {
  return (
    url.pathname.startsWith('/ops/api/') ||
    url.pathname.includes('/stream') ||
    url.pathname.includes('/poll')
  );
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Skip non-http(s)
  if (!url.protocol.startsWith('http')) return;

  // Skip API/stream/poll — go straight to network
  if (isApiOrStream(url)) return;

  // Static assets: cache-first
  if (isStaticAsset(url)) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((resp) => {
          if (resp && resp.status === 200) {
            const respClone = resp.clone();
            caches.open(STATIC_CACHE).then((c) => c.put(req, respClone));
          }
          return resp;
        }).catch(() => cached);
      })
    );
    return;
  }

  // Navigations: network-first with offline fallback
  if (req.mode === 'navigate' && url.pathname.startsWith('/ops')) {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          if (resp && resp.status === 200) {
            const respClone = resp.clone();
            caches.open(RUNTIME_CACHE).then((c) => c.put(req, respClone));
          }
          return resp;
        })
        .catch(() =>
          caches.match(req).then((cached) => cached || caches.match(OFFLINE_URL))
        )
    );
    return;
  }

  // Other GETs under /ops/: network with cache fallback
  if (url.pathname.startsWith('/ops/')) {
    event.respondWith(
      fetch(req).catch(() => caches.match(req))
    );
  }
});

// --- Push notifications ---
self.addEventListener('push', (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = { title: 'SUMO Ops', body: event.data ? event.data.text() : '' };
  }
  const title = data.title || 'הזמנה חדשה';
  const options = {
    body: data.body || '',
    icon: data.icon || '/static/ops/icons/icon-192.png',
    badge: data.badge || '/static/ops/icons/icon-192.png',
    tag: data.tag || 'sumo-ops-order',
    renotify: true,
    requireInteraction: data.requireInteraction || false,
    vibrate: [200, 100, 200],
    data: {
      url: data.url || '/ops/orders',
      orderId: data.orderId || null,
    },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || '/ops/orders';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes('/ops') && 'focus' in client) {
          client.navigate(targetUrl).catch(() => {});
          return client.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(targetUrl);
    })
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
