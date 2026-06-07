// ============================================================
//  geo_attendance.js  v2 — fixed REQUEST_LOC response timing
// ============================================================

(function () {
  'use strict';

  const cfg = window.GYM_CONFIG || {};
  const {
    gymLat,
    gymLng,
    radius        = 100,
    userId,
    isAuthenticated,
    onAttendancePage,
    alreadyMarked,
  } = cfg;

  const LOC_KEY    = 'gym_location';
  const LOC_MAX_MS = 10 * 60 * 1000;   // 10 minutes

  // ── Haversine ────────────────────────────────────────────────
  function haversine(lat1, lng1, lat2, lng2) {
    const R = 6371000;
    const r = d => d * Math.PI / 180;
    const dLat = r(lat2 - lat1);
    const dLng = r(lng2 - lng1);
    const a = Math.sin(dLat/2)**2 +
              Math.cos(r(lat1)) * Math.cos(r(lat2)) * Math.sin(dLng/2)**2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  }

  // ── localStorage helpers ─────────────────────────────────────
  function saveLoc(lat, lng) {
    try {
      localStorage.setItem(LOC_KEY, JSON.stringify({ lat, lng, ts: Date.now() }));
    } catch {}
  }

  function loadLoc() {
    try {
      const raw = localStorage.getItem(LOC_KEY);
      if (!raw) return null;
      const loc = JSON.parse(raw);
      if (Date.now() - loc.ts > LOC_MAX_MS) return null;
      return loc;
    } catch { return null; }
  }

  // ── Send message to SW ───────────────────────────────────────
  function swPost(msg) {
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage(msg);
    }
  }

  // ── SW registration ──────────────────────────────────────────
  async function registerSW() {
    if (!('serviceWorker' in navigator)) return null;
    try {
      const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      return reg;
    } catch (e) {
      console.warn('[GEO] SW registration failed:', e);
      return null;
    }
  }

  // ── Silent cache on login ────────────────────────────────────
  function silentlyCache() {
    if (!navigator.geolocation) return;
    if (loadLoc()) return;   // already fresh

    navigator.geolocation.getCurrentPosition(
      pos => {
        saveLoc(pos.coords.latitude, pos.coords.longitude);
        swPost({ type: 'CACHE_LOC', lat: pos.coords.latitude, lng: pos.coords.longitude });
      },
      () => {},
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 60_000 }
    );
  }

  // ── Listen for SW messages ───────────────────────────────────
  function listenToSW() {
    navigator.serviceWorker.addEventListener('message', event => {
      const { type } = event.data || {};

      if (type === 'REQUEST_LOC') {
        // ✅ KEY FIX: respond IMMEDIATELY with cached location
        // Don't call getCurrentPosition() here — that takes 5-10s
        // and by then the SW has already moved on.
        const cached = loadLoc();
        if (cached) {
          // Respond instantly with cached coords
          swPost({ type: 'REPORT_LOC', lat: cached.lat, lng: cached.lng });
        } else {
          // No cache — get live GPS (slower but necessary)
          navigator.geolocation.getCurrentPosition(
            pos => {
              saveLoc(pos.coords.latitude, pos.coords.longitude);
              swPost({ type: 'REPORT_LOC', lat: pos.coords.latitude, lng: pos.coords.longitude });
            },
            () => {},
            { enableHighAccuracy: true, timeout: 8000, maximumAge: 30_000 }
          );
        }
      }

      if (type === 'ATTENDANCE_MARKED') {
        console.log('[GEO] Auto-attendance marked by SW!');
        if (onAttendancePage) {
          setTimeout(() => window.location.reload(), 1500);
        }
      }
    });
  }

  // ── Background watchPosition — keeps localStorage fresh ─────
  // This means REQUEST_LOC always finds a fresh cached location.
  let bgWatchId = null;

  function startBackgroundWatch() {
    if (!navigator.geolocation || bgWatchId !== null) return;

    bgWatchId = navigator.geolocation.watchPosition(
      pos => {
        // Every time GPS updates, refresh the cache
        saveLoc(pos.coords.latitude, pos.coords.longitude);
      },
      () => {},
      { enableHighAccuracy: true, maximumAge: 30_000 }
    );
  }

  // ── Attendance page UI helpers ───────────────────────────────
  function showGeoError(msg) {
    const el = document.getElementById('geo-error');
    if (!el) return;
    document.getElementById('geo-error-text').textContent = msg;
    el.style.display = 'block';
  }

  function hideGeoError() {
    const el = document.getElementById('geo-error');
    if (el) el.style.display = 'none';
  }

  function setButtonState(state) {
    const btn   = document.getElementById('btn-attend');
    const label = document.getElementById('btn-label');
    if (!btn || !label) return;

    if (state === 'loading') {
      btn.disabled = true;
      label.innerHTML = '<span style="letter-spacing:3px">LOCATING…</span>';
    } else if (state === 'marked') {
      btn.disabled = true;
      btn.classList.add('marked');
      label.innerHTML = '<span class="check-icon">✓</span> ATTENDANCE LOGGED';
    } else {
      btn.disabled = false;
      label.innerHTML = '<span class="pulse-ring"></span>◈ MARK ATTENDANCE';
    }
  }

  function evaluateLocation(lat, lng) {
    const dist = haversine(lat, lng, gymLat, gymLng);
    if (dist <= radius) {
      document.getElementById('attendance-form')?.submit();
    } else {
      const distStr = dist < 1000
        ? `${Math.round(dist)} m`
        : `${(dist / 1000).toFixed(1)} km`;
      setButtonState('idle');
      showGeoError(`⊘ YOU ARE ${distStr} FROM GYM — MUST BE WITHIN 100 M`);
    }
  }

  // ── Button click handler ─────────────────────────────────────
  window.checkLocationAndSubmit = function () {
    hideGeoError();

    if (!navigator.geolocation) {
      showGeoError('⊘ GEOLOCATION NOT SUPPORTED BY THIS BROWSER');
      return;
    }

    const cached = loadLoc();
    if (cached) {
      evaluateLocation(cached.lat, cached.lng);
      // Refresh cache silently in background
      navigator.geolocation.getCurrentPosition(
        pos => saveLoc(pos.coords.latitude, pos.coords.longitude),
        () => {},
        { enableHighAccuracy: true, timeout: 8000, maximumAge: 60_000 }
      );
      return;
    }

    setButtonState('loading');
    navigator.geolocation.getCurrentPosition(
      pos => {
        setButtonState('idle');
        saveLoc(pos.coords.latitude, pos.coords.longitude);
        evaluateLocation(pos.coords.latitude, pos.coords.longitude);
      },
      error => {
        setButtonState('idle');
        const msgs = {
          1: '⊘ LOCATION BLOCKED — Click 🔒 in address bar → Allow Location → Refresh',
          2: '⊘ LOCATION UNAVAILABLE — Check GPS / Network',
          3: '⊘ LOCATION TIMED OUT — Try again',
        };
        showGeoError(msgs[error.code] || '⊘ LOCATION ERROR — TRY AGAIN');
      },
      { enableHighAccuracy: true, timeout: 10_000, maximumAge: 0 }
    );
  };

  // ── Notification permission ──────────────────────────────────
  async function requestNotificationPermission() {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  }

  // ── Main init ────────────────────────────────────────────────
  async function init() {
    if (!isAuthenticated) return;

    const reg = await registerSW();
    if (!reg) return;

    // Attach SW message listener BEFORE sending START_GEO
    listenToSW();

    await requestNotificationPermission();

    // Keep localStorage fresh via watchPosition
    startBackgroundWatch();

    // Silently grab location if not cached yet
    silentlyCache();

    // Wait for SW to be controlling this page, then send START_GEO
    if (navigator.serviceWorker.controller) {
      swPost({ type: 'START_GEO', config: { gymLat, gymLng, radius, userId } });
    } else {
      // SW just installed for the first time — wait for it to activate
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        swPost({ type: 'START_GEO', config: { gymLat, gymLng, radius, userId } });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();