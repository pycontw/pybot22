from pybot.database import import_questions
import csv
import sys
from csv import DictReader


if __name__ == '__main__':
    args = sys.argv[1:]
    # args is a list of the command line args
    if len(args) < 1:
        print("Usage: import channel_id")
        exit()

    channel_id = args[0]
    with open('./quesionary_2022.csv') as ff:
        reader = DictReader(ff, quotechar='\'',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        keys = reader.fieldnames
        q_table = []
        for _q in reader:
            _q['channel_id'] = channel_id
            q_table.append(_q)
        print (q_table)
        import_questions(q_table)    
