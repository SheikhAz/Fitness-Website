from django.core.cache import cache


def check_login_attempt(ip, phone):
    # Use phone as primary key — reliable across proxies
    key = f"login:{phone}"   # ← remove IP dependency

    try:
        attempts = cache.get(key, 0)
    except Exception:
        return True

    if attempts >= 3:
        return False

    try:
        if attempts == 0:
            cache.set(key, 1, timeout=60)
        else:
            cache.incr(key)
    except Exception:
        pass

    return True


def reset_attempt(ip, phone):
    key = f"login:{ip}:{phone}"
    try:
        cache.delete(key)
    except Exception:
        pass
