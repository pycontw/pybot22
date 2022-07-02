from ulid import ULID
from datetime import datetime


def gen_id(dt: datetime = None):
    if dt is not None:
        return str(ULID.from_datetime(dt))
    return str(ULID())
