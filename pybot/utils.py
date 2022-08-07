import functools
from datetime import datetime, timedelta
from ulid import ULID
from datetime import datetime


def gen_id(dt: datetime = None):
    if dt is not None:
        return str(ULID.from_datetime(dt))
    return str(ULID())


def timed_cache(**timedelta_kwargs):
    def _wrapper(f):                                                              
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        # Apply @lru_cache to f with no cache size limit
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)
        return _wrapped
    return _wrapper
