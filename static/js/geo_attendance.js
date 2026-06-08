// ============================================================
//  geo_attendance.js  v3 — reliable START_GEO on every load
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
    isEnrolled,
    onAttendancePage,
    alreadyMarked,
  } = cfg;

  const LOC_KEY    = 'gym_location';
  const LOC_MAX_MS = 10 * 60 * 1000;

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

  // ── Build gym config object ──────────────────────────────────
  function buildConfig() {
    return { gymLat, gymLng, radius, userId, isEnrolled };
  }

  // ── Send message to SW ───────────────────────────────────────
  function swPost(msg) {
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage(msg);
    }
  }

  // ── Send START_GEO + immediate location to SW ────────────────
  // Called on every page load so gymCfg is never null in SW,
  // even after Chrome restarts the SW process.
  function sendStartGeo() {
    swPost({ type: 'START_GEO', config: buildConfig() });

    // Also send current location immediately so SW can check
    // distance right away without waiting for the 30s poll.
    const loc = loadLoc();
    if (loc) {
      setTimeout(() => {
        swPost({ type: 'REPORT_LOC', lat: loc.lat, lng: loc.lng });
      }, 300);  // small delay so START_GEO is processed first
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
    if (loadLoc()) return;

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
        // Respond instantly with cached location
        const cached = loadLoc();
        if (cached) {
          swPost({ type: 'REPORT_LOC', lat: cached.lat, lng: cached.lng });
        } else {
          // No cache — get live GPS
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
        if (onAttendancePage) {
          setTimeout(() => window.location.reload(), 1500);
        }
      }
    });
  }

  // ── Background watchPosition — keeps localStorage fresh ─────
  let bgWatchId = null;

  function startBackgroundWatch() {
    if (!navigator.geolocation || bgWatchId !== null) return;

    bgWatchId = navigator.geolocation.watchPosition(
      pos => saveLoc(pos.coords.latitude, pos.coords.longitude),
      () => {},
      { enableHighAccuracy: true, maximumAge: 30_000 }
    );
  }

  // ── Attendance page UI ───────────────────────────────────────
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

    listenToSW();
    await requestNotificationPermission();
    startBackgroundWatch();
    silentlyCache();

    // ── KEY FIX: always send START_GEO on every page load ───────
    // SW loses gymCfg when Chrome restarts it. Resending on every
    // page load ensures it always has the config it needs.
    if (navigator.serviceWorker.controller) {
      // SW already controlling — send immediately
      sendStartGeo();
    } else {
      // SW just installed — wait for it to take control
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        sendStartGeo();
      });
    }

    // Belt-and-suspenders: also resend after SW is fully ready
    // This catches the case where controllerchange already fired
    // before our listener was attached.
    navigator.serviceWorker.ready.then(() => {
      setTimeout(sendStartGeo, 1000);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();