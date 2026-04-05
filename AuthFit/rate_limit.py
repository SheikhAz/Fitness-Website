from django.core.cache import cache


def check_login_attempt(ip, phone):
    key = f"login:{ip}:{phone}"

    try:
        attempts = cache.get(key, 0)
    except Exception:
        return True  # allow login if Redis fails

    if attempts >= 3:
        return False

    try:
        cache.set(key, attempts + 1, timeout=60)
    except Exception:
        pass

    return True


def reset_attempt(ip, phone):
    key = f"login:{ip}:{phone}"
    try:
        cache.delete(key)
    except Exception:
        pass
