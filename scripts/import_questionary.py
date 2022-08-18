import csv
import sys

from pybot.database import cursor


def import_questions(q_table: list):

    for _q in q_table:
        with cursor() as cur:
            cur.execute('''
                REPLACE INTO question (qid, lang, description, answer)
                VALUES (%(qid)s, %(lang)s, %(description)s, %(answer)s)
            ''', {'qid': _q['qid'], 'lang': _q['lang'], 'description': _q['description'], 'answer': _q['answer']})

            cur.execute('''
                REPLACE INTO question_meta (qid, emoji, coin, star, q_type, channel_id)
                VALUES (%(qid)s, %(emoji)s, %(coin)s, %(star)s, %(q_type)s, %(channel_id)s)
            ''', {'qid': _q['qid'], 'emoji': _q['emoji'], 'coin': _q['coin'], 'star': _q['star'], 'q_type': _q['q_type'], 'channel_id': _q['channel_id']})    
    
            cur.execute('''
                REPLACE INTO question_options (qid, lang, options)
                VALUES (%(qid)s, %(lang)s, %(options)s)
            ''', {'qid': _q['qid'], 'lang': _q['lang'], 'options': _q['options']})  

    return


if __name__ == '__main__':
    args = sys.argv[1:]
    # args is a list of the command line args
    if len(args) < 1:
        print("Usage: import channel_id")
        exit()

    channel_id = args[0]
    with open('./quesionary_2022.csv') as ff:
        reader = csv.DictReader(ff, quotechar='\'',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        keys = reader.fieldnames
        q_table = []
        for _q in reader:
            _q['channel_id'] = channel_id
            q_table.append(_q)
        print (q_table)
        import_questions(q_table)    
