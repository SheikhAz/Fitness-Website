# AuthFit/context_processors.py

import hmac
import hashlib
import json
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings


def _user_hash(uid: int) -> str:
    """
    HMAC-SHA256 of the user's PK.
    - Stable per user across sessions
    - Never exposes the raw DB primary key to the browser
    - Used by the SW to namespace its cache flags per user
      so flags don't bleed when one user logs out and another logs in
    """
    key = getattr(settings, 'SECRET_KEY', 'fallback').encode()
    # FIX 1: was hmac.new() — correct Python API is hmac.new()
    return hmac.new(key, str(uid).encode(), hashlib.sha256).hexdigest()[:16]


def gym_config(request):
    """
    Injects window.GYM_CONFIG into every template via GYM_CONFIG_JSON.

    SECURITY RULES:
    - NEVER include GYM_LATITUDE, GYM_LONGITUDE, GYM_RADIUS_METERS
    - NEVER include user.id or any database primary key
    - Only boolean flags + userHash the frontend legitimately needs
    """
    is_enrolled    = False
    already_marked = False
    user_hash      = ''

    if request.user.is_authenticated:
        try:
            uid   = request.user.id
            today = timezone.localdate()

            user_hash = _user_hash(uid)

            # ── Enrollment check (cached 5 min) ───────────────────
            # FIX 2: key was f"enroll_geo_{uid}" but views.py deletes
            # f"enrolled_{uid}" — they never matched, so cache was always
            # stale. Now both use the same key: f"enrolled_{uid}"
            enroll_key  = f"enrolled_{uid}"
            enroll_data = cache.get(enroll_key)

            if enroll_data is None:
                from AuthFit.models import Enrollment
                try:
                    enrollment  = Enrollment.objects.get(user=request.user)
                    enroll_data = {
                        'exists':  True,
                        'expired': enrollment.is_expired,
                    }
                except Enrollment.DoesNotExist:
                    enroll_data = {'exists': False, 'expired': False}
                cache.set(enroll_key, enroll_data, timeout=300)

            is_enrolled = enroll_data.get('exists') and not enroll_data.get('expired')

            # ── Attendance check (cached, same key as geo_views.py) ──
            if is_enrolled:
                att_key        = f"att_marked_{uid}_{today}"
                already_marked = cache.get(att_key)

                if already_marked is None:
                    from AuthFit.models import Attendence
                    already_marked = Attendence.objects.filter(
                        user=request.user,
                        date=today,
                    ).exists()

                    if already_marked:
                        cache.set(att_key, True, timeout=86400)
                    else:
                        cache.set(att_key, False, timeout=60)

        except Exception:
            # Never let a context processor crash the entire page render.
            # Fail safe: unauthenticated defaults above are already set.
            import logging
            logging.getLogger(__name__).exception(
                "gym_config context processor failed for user %s",
                getattr(request.user, 'id', '?')
            )

    # ── Build the config object ────────────────────────────────
    config = {
        'isAuthenticated': request.user.is_authenticated,
        'isEnrolled':      bool(is_enrolled),
        'alreadyMarked':   bool(already_marked),
        'userHash':        user_hash,
    }

    return {
        'GYM_CONFIG_JSON': json.dumps(config),
        'is_enrolled':     bool(is_enrolled),
        'already_marked':  bool(already_marked),
    }