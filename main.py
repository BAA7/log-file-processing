import argparse
import json
import os.path
import sys
from tabulate import tabulate
from datetime import date, datetime

REPORTS_DIR = 'reports'


def date_is_valid(d):
    try:
        d = date.fromisoformat(d)
    except ValueError:
        return False
    return True


def get_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='path to .log file', nargs='+')
    parser.add_argument('--report', help='path to report file')
    parser.add_argument('--date', help='filter log by given date')
    return parser.parse_args(args)


def create_report(files, filter_date=None):
    if not files:
        print('at least 1 file name must be stated')
        return None
    table = {}
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%d-%m').date()
        except ValueError:
            print('invalid date. correct format is: YYYY-DD-MM')
            return None

    for file_name in files:
        if not os.path.exists(file_name):
            print('file not found:', file_name)
            continue
        with open(file_name) as file:
            for line in file:
                row = {}
                try:
                    row = json.loads(line)
                except json.decoder.JSONDecodeError:
                    print('invalid log format')
                    return None
                for key in ('@timestamp', 'url', 'response_time'):
                    if key not in row.keys():
                        print('invalid log format')
                        return None

                if filter_date:
                    row_date = row['@timestamp'][:row['@timestamp'].index('T')]
                    if not date_is_valid(row_date) or date.fromisoformat(row_date) != filter_date:
                        continue
                handler = row['url']
                if handler not in table.keys():
                    table[handler] = {'': None, 'handler': handler, 'total': 0, 'time': 0}
                table[handler]['total'] += 1
                table[handler]['time'] += row['response_time']

    table = tuple(sorted(table.values(), key=lambda x: (-x['total'], x['handler'])))
    if len(table) == 0:
        return None
    for i, row in enumerate(table):
        row[''] = i
        row['avg_response_time'] = round(row['time']/row['total'], 3)
        del row['time']
    return table


def print_report(data, report_name):
    out = tabulate(data, headers='keys')
    if report_name and out:
        with open(os.path.join(REPORTS_DIR, report_name), 'w') as file:
            file.write(out)
    print(out)


if __name__ == '__main__':
    args = get_args()
    table = create_report(args.file, args.date)
    print_report(table, args.report)
