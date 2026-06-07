// ============================================================
//  EnterGYM Service Worker — Background Geo Attendance
//  Rewritten: single message handler, immediate first check
// ============================================================

const SW_VERSION = 'v2';

// ── Install & Activate ──────────────────────────────────────
self.addEventListener('install',  () => self.skipWaiting());
self.addEventListener('activate', e  => e.waitUntil(self.clients.claim()));

// ── State ───────────────────────────────────────────────────
let gymCfg     = null;   // { gymLat, gymLng, radius, userId }
let watchId    = null;   // setInterval id
let markedToday = null;  // "YYYY-MM-DD" — prevents double-mark
let cachedLoc  = null;   // last known { lat, lng }

// ── SINGLE top-level message handler ────────────────────────
// Chrome requires ALL addEventListener calls at top-level
// evaluation time — never inside a callback or function.
self.addEventListener('message', async (event) => {
  const msg = event.data || {};

  switch (msg.type) {

    // Page sends gym config and asks SW to start polling
    case 'START_GEO':
      gymCfg = msg.config;  // { gymLat, gymLng, radius, userId }
      if (watchId === null) {
        startPolling();
      }
      break;

    // Page sends a fresh location reading (response to REQUEST_LOC)
    case 'REPORT_LOC':
      cachedLoc = { lat: msg.lat, lng: msg.lng };
      await evaluateLocation(msg.lat, msg.lng);
      break;

    // Page caches location at login time
    case 'CACHE_LOC':
      cachedLoc = { lat: msg.lat, lng: msg.lng };
      // Evaluate immediately — user might already be at gym
      if (gymCfg) {
        await evaluateLocation(msg.lat, msg.lng);
      }
      break;

    // Stop watching (e.g. user logged out)
    case 'STOP_GEO':
      if (watchId !== null) {
        clearInterval(watchId);
        watchId = null;
      }
      break;
  }
});

// ── Start polling loop ───────────────────────────────────────
// Asks all open pages for their current position every 30s.
// The page's geo_attendance.js responds with REPORT_LOC.
function startPolling() {
  // Ask immediately on start — don't wait 30s for first check
  requestLocationFromClients();

  // Then poll every 30 seconds
  watchId = setInterval(requestLocationFromClients, 30_000);
}

async function requestLocationFromClients() {
  const clients = await self.clients.matchAll({ type: 'window' });
  clients.forEach(c => c.postMessage({ type: 'REQUEST_LOC' }));
}

// ── Evaluate distance and auto-mark if close enough ─────────
async function evaluateLocation(lat, lng) {
  if (!gymCfg) return;

  const { gymLat, gymLng, radius = 100, userId } = gymCfg;
  const dist = haversine(lat, lng, gymLat, gymLng);
  const today = todayStr();

  // Already marked today → skip
  if (markedToday === today) return;

  if (dist <= radius) {
    const ok = await autoMarkAttendance(userId);
    if (ok) {
      markedToday = today;
      showNotification(dist);

      // Tell all open pages to refresh
      const clients = await self.clients.matchAll({ type: 'window' });
      clients.forEach(c => c.postMessage({ type: 'ATTENDANCE_MARKED' }));
    }
  }
}

// ── POST to Django to mark attendance ───────────────────────
async function autoMarkAttendance(userId) {
  try {
    const res = await fetch('/api/geo-mark-attendance/', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    return data.status === 'success';
  } catch {
    return false;
  }
}

// ── Push notification ────────────────────────────────────────
function showNotification(dist) {
  const distStr = dist < 1000
    ? `${Math.round(dist)} m`
    : `${(dist / 1000).toFixed(1)} km`;

  self.registration.showNotification('✅ EnterGYM — Attendance Marked!', {
    body:     `You're at the gym (${distStr} away). Today's attendance logged automatically.`,
    icon:     '/static/images/Logo.png',
    badge:    '/static/images/Logo.png',
    tag:      'gym-attendance',
    renotify: false,
    data:     { url: '/attendence/' },
  });
}

// ── Notification click ───────────────────────────────────────
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then(clients => {
      for (const c of clients) {
        if (c.url.includes('/attendence/')) { c.focus(); return; }
      }
      self.clients.openWindow('/attendence/');
    })
  );
});

// ── Helpers ──────────────────────────────────────────────────
function todayStr() {
  return new Date().toLocaleDateString('en-CA'); // "YYYY-MM-DD"
}

function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const r = d => d * Math.PI / 180;
  const dLat = r(lat2 - lat1);
  const dLng = r(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(r(lat1)) * Math.cos(r(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}