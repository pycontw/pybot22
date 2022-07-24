import os
import contextlib

import MySQLdb
from MySQLdb.cursors import DictCursor

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
            VALUES 
                (%(event_id)s, %(uid)s, %(user_name)s, %(command)s)
        ''', data)


async def record_answer_event(qid: str, uid: str, answer: str, is_correct: bool):
    data = {
        'event_id': gen_id(),
        'uid': uid,
        'question_id': qid,
        'received_answer': answer,
        'is_correct': is_correct,
    }
    with cursor() as cur:
        cur.execute('''
            INSERT INTO
                answer_event
                (`event_id`, `uid`, `question_id`, `received_answer`, `is_correct`)
            VALUES
                (%(event_id)s, %(uid)s, %(question_id)s, %(received_answer)s, %(is_correct)s)
        ''', data)


async def check_client_has_lang(uid: str) -> str:
    with cursor() as cur:
        cur.execute('SELECT lang FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()['lang'] if cur.rowcount > 0 else None


async def update_client_lang(uid: str, lang: str):
    params = {'lang': lang, 'uid': uid}
    with cursor() as cur:
        cur.execute('UPDATE profile SET lang=%(lang)s WHERE uid=%(uid)s', params)


def sync_update_client_lang(uid: str, lang: str):
    params = {'lang': lang, 'uid': uid}
    with cursor() as cur:
        cur.execute('UPDATE profile SET lang=%(lang)s WHERE uid=%(uid)s', params)


async def query_question(qid: str, lang: str) -> dict:
    params = {'lang': lang, 'qid': qid}
    with cursor() as cur:
        cur.execute('SELECT * FROM question WHERE qid=%(qid)s AND lang=%(lang)s', params)
        return cur.fetchone()


async def check_user_already_answered_qid(qid: str, uid: str) -> bool:
    params = {'qid': qid, 'uid': uid, 'is_correct': True}
    with cursor() as cur:
        cur.execute('''
            SELECT
                count(*) as cnt
            FROM
                answer_event
            WHERE
                uid=%(uid)s
                AND question_id=%(qid)s
                AND is_correct=%(is_correct)s
        ''', params)
        return cur.fetchone()['cnt'] > 0


async def update_user_rewards(uid: str, add_coin: int, add_star: int) -> bool:
    params = {
        'add_coin': add_coin,
        'add_star': add_star,
        'uid': uid,
    }
    with cursor() as cur:
        cur.execute('''
            UPDATE
                profile as tar
            LEFT JOIN
                profile as ori USING(uid)
            SET
                tar.coin=ori.coin+%(add_coin)s,
                tar.star=ori.star+%(add_star)s
            WHERE
                tar.uid=%(uid)s
        ''', params)
        return cur.rowcount == 1
