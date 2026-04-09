from django.core.cache import cache


def check_login_attempt(ip, phone):
    key = f"login:{ip}:{phone}"

    try:
        attempts = cache.get(key, 0)
    except Exception:
        return True

    if attempts >= 3:
        return False  # blocked — don't touch the cache, let timeout expire naturally

    try:
        if attempts == 0:
            cache.set(key, 1, timeout=60)  # start fresh 60s window
        else:
            cache.incr(key)  # atomic increment, preserves original timeout
    except Exception:
        pass

    return True


def reset_attempt(ip, phone):
    key = f"login:{ip}:{phone}"
    try:
        cache.delete(key)
    except Exception:
        pass
