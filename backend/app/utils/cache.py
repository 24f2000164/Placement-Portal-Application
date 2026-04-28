import json
import app.extensions as _ext

DEFAULT_EXPIRY   = 300
DASHBOARD_EXPIRY = 120
SEARCH_EXPIRY    = 60
LIST_EXPIRY      = 180


def _r():
    """Return the live redis_client, or None if Redis is unavailable."""
    return _ext.redis_client


def cache_get(key):
    r = _r()
    if r is None:
        return None
    try:
        value = r.get(key)
        if value:
            print('Cache HIT: ' + key)
            return json.loads(value)
        print('Cache MISS: ' + key)
        return None
    except Exception as e:
        print('Cache get error: ' + str(e))
        return None


def cache_set(key, value, expiry=DEFAULT_EXPIRY):
    r = _r()
    if r is None:
        return False
    try:
        r.setex(key, expiry, json.dumps(value, default=str))
        print('Cache SET: ' + key + ' expires in ' + str(expiry) + 's')
        return True
    except Exception as e:
        print('Cache set error: ' + str(e))
        return False


def cache_delete(key):
    r = _r()
    if r is None:
        return False
    try:
        r.delete(key)
        print('Cache DELETE: ' + key)
        return True
    except Exception as e:
        print('Cache delete error: ' + str(e))
        return False


def cache_clear_prefix(prefix):
    r = _r()
    if r is None:
        return False
    try:
        keys = r.keys(prefix + '*')
        if keys:
            r.delete(*keys)
            print('Cache CLEAR prefix: ' + prefix + ' (' + str(len(keys)) + ' keys)')
        return True
    except Exception as e:
        print('Cache clear error: ' + str(e))
        return False


def cache_exists(key):
    r = _r()
    if r is None:
        return False
    try:
        return r.exists(key) > 0
    except Exception as e:
        print('Cache exists error: ' + str(e))
        return False


def cache_ttl(key):
    r = _r()
    if r is None:
        return -1
    try:
        return r.ttl(key)
    except Exception as e:
        return -1