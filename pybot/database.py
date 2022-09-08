import os
import json
import contextlib
from typing import Dict, List

import MySQLdb
from MySQLdb.cursors import DictCursor

from pybot.utils import gen_id, timed_cache


sql_server_host = os.getenv('SQL_SERVER_HOST') 
g_sql_server = sql_server_host if sql_server_host else 'localhost'


@contextlib.contextmanager
def db_conn():
    conn = MySQLdb.connect(
        use_unicode=True,
        host='localhost',
        #port=3307,
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


async def record_reaction_event(
    qid: str,
    uid: str,
    channel_id: str,
    channel_name: str,
):
    params = {
        'event_id': gen_id(),
        'qid': qid,
        'uid': uid,
        'channel_id': channel_id,
        'channel_name': channel_name,
    }
    with cursor() as cur:
        cur.execute('''
            INSERT INTO
                reaction_event
                (`event_id`, `qid`, `uid`, `channel_id`, `channel_name`)
            VALUES
                (%(event_id)s, %(qid)s, %(uid)s, %(channel_id)s, %(channel_name)s)
        ''', params)


async def check_client_has_lang(uid: str) -> str:
    with cursor() as cur:
        cur.execute('SELECT lang FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()['lang'] if cur.rowcount > 0 else None


async def update_client_email(uid: str, email: str):
    with cursor() as cur:
        params = {'uid': uid, 'email': email}
        cur.execute('UPDATE profile SET email=%(email)s WHERE uid=%(uid)s', params)


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
        cur.execute('''
        SELECT
            q.qid,
            q.lang,
            q.description,
            q.answer,
            qm.coin,
            qm.star,
            qm.emoji,
            qm.q_type,
            qm.channel_id,
            qo.options
        FROM
            question as q
        JOIN
            question_meta as qm
            ON qm.qid=q.qid
        LEFT JOIN
            question_options as qo
            ON qo.qid=q.qid AND qo.lang=q.lang
        WHERE
            q.qid=%(qid)s
            AND q.lang=%(lang)s
        ''', params)
        result = cur.fetchone()
    if result and result['options']:
        result['options'] = json.loads(result['options'])
    return result


async def query_next_questionnaire(uid: str, lang: str) -> dict:
    params = {'lang': lang, 'uid': uid}
    with cursor() as cur:
        cur.execute('''
            SELECT
                q.qid,
                q.lang,
                q.description,
                q.answer,
                qm.coin,
                qm.star,
                qm.emoji,
                qm.q_type,
                qm.channel_id,
                qo.options
            FROM
                question as q
            JOIN
                question_meta as qm
                ON qm.qid=q.qid
            LEFT JOIN
                question_options as qo
                ON qo.qid=q.qid AND qo.lang=q.lang
            WHERE
                q.qid LIKE "u_qa_%%"
                AND q.lang=%(lang)s
                AND q.qid not in (
                    SELECT qid
                    FROM question as q
                    LEFT JOIN
                        answer_event as ans
                        ON ans.question_id=q.qid
                    WHERE
                        ans.uid=%(uid)s
                        AND q.qid LIKE "u_qa_%%"
                )
            ORDER BY
                q.qid
            LIMIT 1
        ''', params)
        result = cur.fetchone()

    if not result:
        # Already finished answering all questionnaires.
        return None

    result['options'] = json.loads(result['options'])
    return result


@timed_cache(seconds=10)
def sync_query_init_messages() -> Dict[int, dict]:
    with cursor() as cur:
        cur.execute('''
            SELECT
                qm.qid,
                qm.emoji,
                ch.channel_id,
                ch.welcome_msg
            FROM
                channel as ch
            LEFT JOIN
                question_meta as qm
                ON qm.channel_id=ch.channel_id
            ORDER BY
                qm.qid
        ''')
        data = cur.fetchall()

    results = {}
    for d in data:
        channel_id = int(d['channel_id'])
        if channel_id not in results:
            results[channel_id] = {
                'welcome_msg': d['welcome_msg'],
                'emoji_to_qid': {},
            }

        results[channel_id]['emoji_to_qid'][d['emoji']] = d['qid']
    return results


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


def sync_check_user_is_staff(uid: str) -> bool:
    with cursor() as cur:
        cur.execute('SELECT is_staff FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()['is_staff']


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


async def query_user_rewards(uid: str):
    with cursor() as cur:
        cur.execute('SELECT coin, star FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()


async def query_user_name(uid: str) -> str:
    with cursor() as cur:
        cur.execute('SELECT name FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()['name'] if cur.rowcount > 0 else None


# this is called by rank_init() function that should be sync
def query_all_users_profile() -> dict:
    with cursor() as cur:
        cur.execute('SELECT uid, name, coin FROM profile')
        return cur.fetchall() if cur.rowcount > 0 else None


async def query_user_rank_by_coin(limit=10) -> List[dict]:
    with cursor() as cur:
        cur.execute('''
            SELECT
                uid,
                name,
                coin
            FROM
                profile
            WHERE
                is_staff = 0
            ORDER BY
                coin DESC
            LIMIT
                %(limit)s
        ''', {'limit': limit})
        return cur.fetchall()


async def query_user_has_stars(limit=200, low_bound=5) -> List[dict]:
    with cursor() as cur:
        cur.execute('''
            SELECT
                uid,
                name,
                star
            FROM
                profile
            WHERE
                star >= %(low_bound)s
                AND reward IS NULL
            LIMIT
                %(limit)s
        ''', {'limit': limit, 'low_bound': low_bound})
        return cur.fetchall()


async def update_user_lotto_reward(uid: str, reward_name: str):
    params = {'uid': uid, 'reward': reward_name}
    with cursor() as cur:
        cur.execute('UPDATE profile SET reward=%(reward)s WHERE uid=%(uid)s', params)


async def update_channel_id(channel_name: str, new_id: int):
    params = {
        'channel_name': channel_name,
        'new_id': new_id,
    }
    with cursor() as cur:
        cur.execute('''
            UPDATE
                channel as c
            LEFT JOIN
                question_meta as q
                ON c.channel_id = q.channel_id
            SET
                c.channel_id = %(new_id)s,
                q.channel_id = %(new_id)s
            WHERE
                c.channel_name = %(channel_name)s
        ''', params)
