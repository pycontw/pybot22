
from pybot.database import cursor


def export_channel():
    out_path = './sql/data/channel.sql'
    with cursor() as cur:
        cur.execute('SELECT * FROM channel')
        ds = cur.fetchall()

    keys = ['channel_id', 'channel_name', 'welcome_msg']
    with open(out_path, 'w') as out:
        for d in ds:
            line = f"INSERT INTO `pycon22`.`channel` (`channel_id`,`channel_name`,`welcome_msg`) VALUES ("
            out.write(line)
            v_str = ','.join([f"'{d[k]}'" for k in keys])
            out.write(v_str)
            out.write(');\n')


def export_question():
    out_path = './sql/data/question.sql'
    with cursor() as cur:
        cur.execute('SELECT * FROM question')
        ds = cur.fetchall()

    keys = ['qid', 'lang', 'description', 'answer']
    with open(out_path, 'w') as out:
        for d in ds:
            line = f"INSERT INTO `pycon22`.`question` (`qid`,`lang`,`description`,`answer`) VALUES ("
            out.write(line)
            v_list = []
            for k in keys:
                v = d[k].replace("'", "''")
                v_list.append(v)
            v_str = ','.join([f"'{v}'" for v in v_list])
            out.write(v_str)
            out.write(');\n')


def export_question_meta():
    out_path = './sql/data/question_meta.sql'
    with cursor() as cur:
        cur.execute('SELECT * FROM question_meta')
        ds = cur.fetchall()

    keys = ['qid', 'emoji', 'coin', 'star', 'q_type', 'channel_id']
    with open(out_path, 'w') as out:
        for d in ds:
            line = f"INSERT INTO `pycon22`.`question_meta` (`qid`,`emoji`,`coin`,`star`,`q_type`,`channel_id`) VALUES ("
            out.write(line)
            v_str = ','.join([f"'{d[k]}'" for k in keys])
            out.write(v_str)
            out.write(');\n')


def export_question_options():
    out_path = './sql/data/question_options.sql'
    with cursor() as cur:
        cur.execute('SELECT * FROM question_options')
        ds = cur.fetchall()

    keys = ['qid', 'lang', 'options']
    with open(out_path, 'w') as out:
        for d in ds:
            line = f"INSERT INTO `pycon22`.`question_options` (`qid`,`lang`,`options`) VALUES ("
            out.write(line)
            v_list = []
            for k in keys:
                v = d[k].replace("'", "''")
                v_list.append(v)
            v_str = ','.join([f"'{v}'" for v in v_list])
            out.write(v_str)
            out.write(');\n')



if __name__ == '__main__':
    export_channel()
    export_question()
    export_question_meta()
    export_question_options()
