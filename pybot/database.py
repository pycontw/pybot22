import os
import contextlib

#import MySQLdb
#from MySQLdb.cursors import DictCursor

from pybot.utils import gen_id


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


async def record_command_event(uid: str, user_name: str, command: str):
    data = {
        'event_id': gen_id(),
        'uid': uid,
        'user_name': user_name,
        'command': command,
    }
    with cursor() as cur:
        cur.execute('''
            INSERT INTO
                command_event
                (`event_id`, `uid`, `name`, `command`)
            VALUES (
                (%(event_id)s, %(uid)s, %(user_name)s, %(command)s)
            )
        ''', data)


async def record_answer_event(qid: str, uid: str, answer: str):
    data = {
        'event_id': gen_id(),
        'uid': uid,
        'question_id': qid,
        'received_answer': answer,
    }
    with cursor() as cur:
        cur.execute('''
            INSERT INTO
                answer_event
                (`event_id`, `uid`, `question_id`, `received_answer`)
            VALUES (
                (%(event_id)s, %(uid)s, %(question_id)s, %(received_answer)s)
            )
        ''', data)


async def check_client_has_lang(uid: str):
    with cursor() as cur:
        cur.execute('SELECT lang FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()['lang'] if cur.rowcount > 0 else None


async def update_client_lang(uid: str, lang: str):
    params = {'lang': lang, 'uid': uid}
    with cursor() as cur:
        cur.execute('UPDATE profile SET lang=%(lang)s WHERE uid=%(uid)s', params)
