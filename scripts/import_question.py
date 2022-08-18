import json
from csv import DictReader

from mosql.query import insert

from pybot.database import cursor


def load_view_questions(csv_path, dry_run=True):
    q_list = []
    with open(csv_path) as ff:
        reader = DictReader(ff, delimiter='\t')
        for idx, data in enumerate(reader):
            data['qid'] = f'view_q{idx+1}'
            q_list.append(data)

    # Data for question meta
    tw_metas = []
    en_metas = []
    for qd in q_list:
        en_option = json.dumps({
            chr(ord('A')+idx): qd[f'en_opt{idx+1}']
            for idx in range(4)
        }).replace(' ', '')
        tw_option = json.dumps({
            chr(ord('A')+idx): qd[f'opt{idx+1}']
            for idx in range(4)
        }).replace(' ', '')

        en_metas.append((qd['qid'], 'EN', en_option))
        tw_metas.append((qd['qid'], 'zh_TW', tw_option))

    questions = []
    for qd in q_list:
        ans = int(qd['ans'])
        ans = chr(ord('A') + ans - 1)
        questions.append((qd['qid'], 'zh_TW', qd['tw_description'], ans))
        questions.append((qd['qid'], 'EN', qd['en_description'], ans))

    metas = []
    for idx, qd in enumerate(q_list):
        metas.append((qd['qid'], chr(ord('👊')+idx), qd['coins'], qd['stars'], 'option_only'))

    if not dry_run:
        with cursor() as cur:
            print(#cur.execute(
                insert(
                    table='question_options',
                    columns=('qid', 'lang', 'options'),
                    values=tw_metas + en_metas,
                )
            )
            print(#cur.execute(
                insert(
                    table='question',
                    columns=('qid', 'lang', 'description', 'answer'),
                    values=questions,
                )
            ).replace('"', '')
            print(
                insert(
                    table='question_meta',
                    columns=('qid', 'emoji', 'coin', 'star', 'q_type'),
                    values=metas,
                ).replace('"', '')
            )

    return q_list, questions, tw_metas + en_metas


def load_travel_questions(csv_path, dry_run=True):
    with open(csv_path) as ff:
        reader = DictReader(ff, delimiter='\t')
        q_list = []
        for idx, data in enumerate(reader):
            data['qid'] = f'travel_q{idx+1}'
            q_list.append(data)

    options = []
    questions = []
    metas = []
    for idx, qd in enumerate(q_list):
        # questions
        ans = int(qd['ans'])
        ans = chr(ord('A') + ans - 1)
        questions.append((qd['qid'], 'zh_TW', qd['tw_description'], ans))
        questions.append((qd['qid'], 'EN', qd['en_description'], ans))

        # options
        tw_options = json.dumps({
            chr(ord('A') + idx): qd[f'opt{idx + 1}']
            for idx in range(4)
        }).replace(' ', '')
        en_options = json.dumps({
            chr(ord('A') + idx): qd[f'en_opt{idx + 1}']
            for idx in range(4)
        }).replace(' ', '')
        options.append((qd['qid'], 'zh_TW', tw_options))
        options.append((qd['qid'], 'EN', en_options))

        # metas
        metas.append((qd['qid'], qd['emoji'], qd['coins'], qd['stars'], 'option_only'))

    print(
        insert(
            table='question',
            columns=('qid', 'lang', 'description', 'answer'),
            values=questions,
        ).replace('"', ''),
        '\n'
    )
    print(#cur.execute(
        insert(
            table='question_options',
            columns=('qid', 'lang', 'options'),
            values=options,
        ),
        '\n'
    )
    print(
        insert(
            table='question_meta',
            columns=('qid', 'emoji', 'coin', 'star', 'q_type'),
            values=metas,
        ).replace('"', '')
    )



if __name__ == '__main__':
    #out = load_view_questions('./question_csvs/view.csv', dry_run=False)
    out = load_travel_questions('./question_csvs/travel.csv', dry_run=True)

