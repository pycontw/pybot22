import csv
import json

from pybot.database import cursor



def update_sponsor_questions():
    file_path = './question_csvs/sponsor_qs.csv'
    with open(file_path) as ff:
        reader = csv.DictReader(ff, delimiter='\t')
        ds = [d for d in reader]

    with cursor() as cur:
        for d in ds:
            params = {
                'description': d['tw_description'],
                'qid': d['qid'],
                'lang': 'zh_TW',
            }
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['description'] = d['en_description']
            params['lang'] = 'EN'
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            tw_opts = {}
            en_opts = {}
            for i in range(4):
                opt = chr(ord('A') + i)
                tw_opts[opt] = d[f'tw_opt{i+1}']
                en_opts[opt] = d[f'en_opt{i+1}']

            params['option_json'] = json.dumps(en_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['lang'] = 'zh_TW'
            params['option_json'] = json.dumps(tw_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)


def update_travel_questions():
    file_path = './question_csvs/travel.csv'
    with open(file_path) as ff:
        reader = csv.DictReader(ff, delimiter='\t')
        ds = [d for d in reader]

    with cursor() as cur:
        for d in ds:
            params = {
                'description': d['tw_description'],
                'qid': d['qid'],
                'lang': 'zh_TW',
            }
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['description'] = d['en_description']
            params['lang'] = 'EN'
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            tw_opts = {}
            en_opts = {}
            for i in range(4):
                opt = chr(ord('A') + i)
                tw_opts[opt] = d[f'opt{i+1}']
                en_opts[opt] = d[f'en_opt{i+1}']

            params['option_json'] = json.dumps(en_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['lang'] = 'zh_TW'
            params['option_json'] = json.dumps(tw_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)


def update_view_questions():
    file_path = './question_csvs/view.csv'
    with open(file_path) as ff:
        reader = csv.DictReader(ff, delimiter='\t')
        ds = [d for d in reader]

    with cursor() as cur:
        for d in ds:
            params = {
                'description': d['tw_description'],
                'qid': d['qid'],
                'lang': 'zh_TW',
            }
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['description'] = d['en_description']
            params['lang'] = 'EN'
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            tw_opts = {}
            en_opts = {}
            for i in range(4):
                opt = chr(ord('A') + i)
                tw_opts[opt] = d[f'opt{i+1}']
                en_opts[opt] = d[f'en_opt{i+1}']

            params['option_json'] = json.dumps(en_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['lang'] = 'zh_TW'
            params['option_json'] = json.dumps(tw_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)


def update_open_questions():
    file_path = './question_csvs/open_question.csv'
    with open(file_path) as ff:
        reader = csv.DictReader(ff, delimiter='\t')
        ds = [d for d in reader]

    with cursor() as cur:
        for d in ds:
            params = {
                'description': d['tw_description'],
                'qid': d['qid'],
                'lang': 'zh_TW',
            }
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['description'] = d['en_description']
            params['lang'] = 'EN'
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)


def update_python_questions():
    file_path = './question_csvs/python_challenge.csv'
    with open(file_path) as ff:
        reader = csv.DictReader(ff, delimiter='\t')
        ds = [d for d in reader]

    with cursor() as cur:
        for d in ds:
            params = {
                'description': d['tw_description'],
                'qid': d['qid'],
                'lang': 'zh_TW',
            }
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['description'] = d['en_description']
            params['lang'] = 'EN'
            cur.execute('''
                UPDATE
                    question
                SET
                    description=%(description)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            tw_opts = {}
            en_opts = {}
            for i in range(4):
                opt = chr(ord('A') + i)
                tw_opts[opt] = d[f'tw_opt{i+1}']
                en_opts[opt] = d[f'en_opt{i+1}']

            params['option_json'] = json.dumps(en_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['lang'] = 'zh_TW'
            params['option_json'] = json.dumps(tw_opts).replace(' ', '')
            cur.execute('''
                UPDATE
                    question_options
                SET
                    options=%(option_json)s
                WHERE
                    qid=%(qid)s
                    AND lang=%(lang)s
            ''', params)

            params['emoji'] = d['emoji'].replace(':', '')
            cur.execute('''
                UPDATE
                    question_meta
                SET
                    emoji=%(emoji)s
                WHERE
                    qid=%(qid)s
            ''', params)


def update_channel_msg():
    with open('./question_csvs/channel_msg.csv') as ff:
        rows = list(csv.DictReader(ff, delimiter='\t'))

    with cursor() as cur:
        for row in rows:
            cur.execute('''
                UPDATE
                    channel
                SET
                    channel_name=%(channel_name)s,
                    welcome_msg=%(welcome_msg)s
                WHERE
                    channel_id=%(channel_id)s
            ''', row)


def update_game_channel_msg():
    with open('./question_csvs/game_channel.csv') as ff:
        rows = list(csv.DictReader(ff, delimiter='\t'))

    with cursor() as cur:
        for row in rows:
            print(row['channel'])
            cur.execute('''
                UPDATE
                    channel
                SET
                    welcome_msg=%(welcome_msg)s
                WHERE
                    channel_id=%(channel_id)s
            ''', row)


if __name__ == '__main__':
    # update_sponsor_questions()
    # update_travel_questions()
    # update_view_questions()
    # update_open_questions()
    # update_python_questions()
    # update_channel_msg()
    update_game_channel_msg()
