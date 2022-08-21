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



if __name__ == '__main__':
    #update_sponsor_questions()
    # update_travel_questions()
    update_view_questions()
