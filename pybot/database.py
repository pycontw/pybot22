import os
import json
import contextlib
from typing import Dict, List
from functools import lru_cache

import MySQLdb
from MySQLdb.cursors import DictCursor

from pybot.utils import gen_id, timed_cache


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
            ORDER BY
                coin DESC
            LIMIT
                %(limit)s
        ''', {'limit': limit})
        return cur.fetchall()


async def query_user_has_starts(limit=200, low_bound=5) -> List[dict]:
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
            LIMIT
                %(limit)s
        ''', {'limit': limit, 'low_bound': low_bound})
        return cur.fetchall()


async def get_channel_questionare_table(channel_id: str, q_type: str) -> List[dict]:
    with cursor() as cur:
        cur.execute('''
            SELECT
               qid,
               channel_id,
               q_type
            FROM
                question_meta
            WHERE
                channel_id=%(channel_id)s
                AND q_type=%(q_type)s
        ''', {'channel_id': channel_id, 'q_type': q_type})
        return cur.fetchall()


async def get_next_user_questionare_qid(uid: str, channel_id: str, q_type) -> dict:

    q_table = await get_channel_questionare_table(channel_id, q_type)
    # print(f'{uid},{channel_id},{q_type}')
    # print(q_table)
    for _q in q_table:
        ans = await check_user_already_answered_qid(_q['qid'], uid)
        if ans != True:
            break
    if ans == True:
        _q['qid'] = 'u_qa_finished'
    return _q  
