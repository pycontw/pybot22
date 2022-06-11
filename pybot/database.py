import os
import contextlib

import MySQLdb
from MySQLdb.cursors import DictCursor


@contextlib.contextmanager
def db_conn():
    conn = MySQLdb.connect(
        use_unicode=True,
        host='localhost',
        user='root',
        passwd=os.getenv('DB_PASSWORD'),
        db='pycon22',
        cursorclass=DictCursor,
    )
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def cursor():
    with db_conn() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
