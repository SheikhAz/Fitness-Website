from django.core.cache import cache

MAX_ATTEMPTS = 3
LOCKOUT_SECONDS = 60


def check_login_attempt(ip: str, phone: str) -> bool:
    key = f"login:{phone}"
    try:
        attempts = cache.get(key, 0)
    except Exception:
        return True  # Fail open on cache error

    if attempts >= MAX_ATTEMPTS:
        return False

    try:
        if attempts == 0:
            cache.set(key, 1, timeout=LOCKOUT_SECONDS)
        else:
            cache.incr(key)
    except Exception:
        pass

    return True


def reset_attempt(ip: str, phone: str) -> None:
    key = f"login:{phone}"  # ← must match check_login_attempt
    try:
        cache.delete(key)
    except Exception:
        pass
