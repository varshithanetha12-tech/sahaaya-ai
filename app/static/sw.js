// Sahaaya AI Service Worker — PWA & Offline Support
const CACHE_NAME = 'sahaaya-ai-v2.4.0';

const PRECACHE_ASSETS = [
    '/',
    '/static/css/custom.css',
    '/static/js/app.js',
    '/static/js/charts.js',
    '/static/js/audio_sim.js',
    '/static/js/i18n.js',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/icons/icon.svg'
];

// Install: Cache app shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-caching offline app shell');
            return cache.addAll(PRECACHE_ASSETS).catch((err) => {
                console.warn('[ServiceWorker] Some assets failed to precache:', err);
            });
        }).then(() => self.skipWaiting())
    );
});

// Activate: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[ServiceWorker] Removing old cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch: Network-first for API, Stale-while-revalidate for static shell
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Bypass non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // For API requests: network-first with graceful offline fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response(
                    JSON.stringify({
                        offline: true,
                        error: 'Network connection unavailable. Sahaaya AI offline mode active.'
                    }),
                    {
                        headers: { 'Content-Type': 'application/json' },
                        status: 503
                    }
                );
            })
        );
        return;
    }

    // For app shell and static resources: Stale-while-revalidate
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
                    const responseToCache = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseToCache);
                    });
                }
                return networkResponse;
            }).catch(() => cachedResponse);

            return cachedResponse || fetchPromise;
        })
    );
});
