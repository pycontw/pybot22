import re
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


@timed_cache(seconds=1800)
def _get_custom_emoji_name_id_map(emojis):
    return {
        emoji.name: emoji.id
        for emoji in emojis
    }


EMOJI_STR_MATCHER = re.compile(r'<:(\S*):(\d*)>')


def replace_emoji_str(msg: str, emojis) -> str:
    matched_strs = set(EMOJI_STR_MATCHER.findall(msg))
    custom_emoji_name_id_map = _get_custom_emoji_name_id_map(emojis)
    for emoji_name, ori_id in matched_strs:
        new_id = custom_emoji_name_id_map[emoji_name]
        ori_str = f'<:{emoji_name}:{ori_id}>'
        new_str = f'<:{emoji_name}:{new_id}>'
        msg = msg.replace(ori_str, new_str)
    return msg
