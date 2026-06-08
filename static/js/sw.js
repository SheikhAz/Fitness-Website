// ============================================================
//  EnterGYM Service Worker v4
//  Only marks attendance for enrolled members
// ============================================================

self.addEventListener('install',  () => self.skipWaiting());
self.addEventListener('activate', e  => e.waitUntil(self.clients.claim()));

let gymCfg  = null;
let watchId = null;

self.addEventListener('message', async (event) => {
  const msg = event.data || {};

  switch (msg.type) {
    case 'START_GEO':
      gymCfg = msg.config;  // { gymLat, gymLng, radius, userId, isEnrolled }
      if (watchId === null) {
        requestLocationFromClients();
        watchId = setInterval(requestLocationFromClients, 30_000);
      }
      break;

    case 'REPORT_LOC':
    case 'CACHE_LOC':
      if (gymCfg) await evaluateLocation(msg.lat, msg.lng);
      break;

    case 'STOP_GEO':
      clearInterval(watchId);
      watchId = null;
      break;
  }
});

async function requestLocationFromClients() {
  const clients = await self.clients.matchAll({ type: 'window' });
  clients.forEach(c => c.postMessage({ type: 'REQUEST_LOC' }));
}

async function evaluateLocation(lat, lng) {
  const { gymLat, gymLng, radius = 100, userId, isEnrolled } = gymCfg;

  // ── Not enrolled → skip entirely ────────────────────────────
  if (!isEnrolled) return;

  const dist = haversine(lat, lng, gymLat, gymLng);
  if (dist > radius) return;

  // Within range — verify with server (source of truth)
  const statusRes = await checkAttendanceStatus();
  if (!statusRes.enrolled) return;   // server confirms not enrolled
  if (statusRes.marked)   return;   // already marked today

  // Mark attendance
  const ok = await autoMarkAttendance(userId);
  if (ok) {
    showNotification(dist);
    const clients = await self.clients.matchAll({ type: 'window' });
    clients.forEach(c => c.postMessage({ type: 'ATTENDANCE_MARKED' }));
  }
}

async function checkAttendanceStatus() {
  try {
    const res  = await fetch('/api/attendance-status/', { credentials: 'include' });
    const data = await res.json();
    return { marked: data.marked === true, enrolled: data.enrolled !== false };
  } catch {
    return { marked: false, enrolled: true };  // on error, try to mark
  }
}

async function autoMarkAttendance(userId) {
  try {
    const res  = await fetch('/api/geo-mark-attendance/', {
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

function showNotification(dist) {
  const distStr = dist < 1000
    ? `${Math.round(dist)} m`
    : `${(dist / 1000).toFixed(1)} km`;

  self.registration.showNotification('✅ EnterGYM — Attendance Marked!', {
    body:     `You're at the gym (${distStr} away). Attendance logged automatically.`,
    icon:     '/static/images/Logo.png',
    badge:    '/static/images/Logo.png',
    tag:      'gym-attendance',
    renotify: false,
    data:     { url: '/attendence/' },
  });
}

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

function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const r = d => d * Math.PI / 180;
  const dLat = r(lat2 - lat1);
  const dLng = r(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(r(lat1)) * Math.cos(r(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}