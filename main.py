import argparse
import json
import os.path
import sys
from tabulate import tabulate
from datetime import date, datetime

REPORTS_DIR = 'reports'

parser = argparse.ArgumentParser()
parser.add_argument('--file', help='path to .log file', default='example.log', nargs='+')
parser.add_argument('--report', help='path to report file')
parser.add_argument('--date', help='filter log by given date')
args = parser.parse_args()

table = {}
counter = 0
filter_date = args.date
if filter_date:
    filter_date = datetime.strptime(filter_date, '%Y-%d-%m').date()

for file_name in args.file:
    if not os.path.exists(file_name):
        print('file not found:', file_name)
        continue
    with open(file_name) as file:
        for line in file:
            row = json.loads(line)
            if filter_date:
                if date.fromisoformat(row['@timestamp'][:row['@timestamp'].index('T')]) != filter_date:
                    continue
            handler = row['url']
            if handler not in table.keys():
                table[handler] = {'': counter, 'handler': handler, 'total': 0, 'time': 0}
                counter += 1
            table[handler]['total'] += 1
            table[handler]['time'] += row['response_time']

table = table.values()
for row in table:
    row['avg_response_time'] = round(row['time']/row['total'], 3)
    del row['time']

out = tabulate(table, headers='keys')
if args.report and out:
    with open(os.path.join(REPORTS_DIR, args.report), 'w') as file:
        file.write(out)
print(out)
