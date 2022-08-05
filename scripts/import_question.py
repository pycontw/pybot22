from pybot.database import cursor
from csv import DictReader
from mosql.query import insert


if __name__ == '__main__':
    with open('/home/kohara/Downloads/questions.csv') as ff:
        reader = DictReader(ff)
        keys = reader.fieldnames
        data = []
        for qd in reader:
            data.append(tuple(v for v in qd.values()))

    values = ', '.join(str(d) for d in data)
    with cursor() as cur:
        # cur.execute(f'''
        #     INSERT INTO "question" ("qid", "lang", "description", "answer", "coin", "star", "q_type") VALUES {values}
        # ''')
        print(
            insert(
                'question',
                columns=("qid", "lang", "description", "answer", "coin", "star", "q_type"),
                values=data,
            )
        )

