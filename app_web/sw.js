// sw.js - Service Worker para funcionalidad offline
const CACHE_NAME = 'natillera-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/dashboard.html',
  '/aportes.html',
  '/prestamos.html',
  '/actividades.html',
  '/perfil.html',
  '/style.css'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});