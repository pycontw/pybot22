
from pybot.database import cursor


async def check_client_has_lang(uid: str):
    with cursor() as cur:
        cur.execute('SELECT lang FROM profile WHERE uid=%(uid)s', {'uid': uid})
        return cur.fetchone()['lang'] if cur.rowcount > 0 else None


async def update_client_lang(uid: str, lang: str):
    params = {'lang': lang, 'uid': uid}
    with cursor() as cur:
        cur.execute('UPDATE profile SET lang=%(lang)s WHERE uid=%(uid)s', params)
