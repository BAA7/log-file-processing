import argparse
import os.path
import pytest
import main
from tabulate import tabulate

keys = ('', 'handler', 'total', 'avg_response_time')
rows = {
    'first': (
        (0, '/api/homeworks/...', 3, 0.064),
        (1, '/api/context/...', 2, 0.038),
        (2, '/api/specializations/...', 2, 0.036),
        (3, '/api/challenges/...', 1, 0.124),
        (4, '/api/users/...', 1, 0.072),
    ),
    'second': (
        (0, '/api/context/...', 2, 0.048),
        (1, '/api/homeworks/...', 2, 0.07),
        (2, '/api/challenges/...', 1, 0.128),
        (3, '/api/specializations/...', 1, 0.044),
    ),
    'both': (
        (0, '/api/homeworks/...', 5, 0.066),
        (1, '/api/context/...', 4, 0.043),
        (2, '/api/specializations/...', 3, 0.039),
        (3, '/api/challenges/...', 2, 0.126),
        (4, '/api/users/...', 1, 0.072),
    ),
    'with_date': (
        (0, '/api/context/...', 3, 0.043),
        (1, '/api/specializations/...', 3, 0.039),
        (2, '/api/homeworks/...', 2, 0.082),
        (3, '/api/challenges/...', 1, 0.124),
        (4, '/api/users/...', 1, 0.072),
    )
}
data = {key: tuple([dict(zip(keys, row)) for row in rows[key]]) for key in rows.keys()}


@pytest.mark.parametrize(
    "file, report, date",
    [
        (None, None, None),
    ]
)
def test_get_args(file, report, date):
    args = []
    if file:
        args.extend(['--file', file])
    if report:
        args.extend(['--report', report])
    if date:
        args.extend(['--date', date])
    assert main.get_args(args) == argparse.Namespace(file=file, report=report, date=date)


@pytest.mark.parametrize(
    "files, date, output, printed",
    [
        (['log_example/my_example1.log'], None, data['first'], None),
        (['log_example/my_example2.log'], None, data['second'], None),
        (['log_example/my_example1.log', 'log_example/my_example2.log'], None, data['both'], None),
        (['log_example/my_example1.log', 'log_example/my_example2.log'], None, data['both'], None),
        (['log_example/my_example1.log', 'log_example/my_example2.log'], '2025-22-06', data['with_date'], None),
        (['log_example/my_example1.log', 'log_example/my_example2.log'], '2025-06-22', None, 'invalid date. correct format is: YYYY-DD-MM\n'),
        (None, None, None, 'at least 1 file name must be stated\n'),
        (['log_example/my_example1.log', 'non_existent.log'], None, data['first'], 'file not found: non_existent.log\n'),
        (['non_existent.log'], None, None, 'file not found: non_existent.log\n'),
        (['log_example/bad_example.log'], None, None, 'invalid log format\n'),
        (['log_example/bad_example.log'], '2025-22-06', None, 'invalid log format\n'),
        (['log_example/not_a_log.log'], None, None, 'invalid log format\n'),
    ]
)
def test_create_report(files, date, output, printed, capsys):
    assert main.create_report(files, date) == output
    if printed:
        assert capsys.readouterr().out == printed


@pytest.mark.parametrize(
    "table",
    [
        (data['first'],),
        (data['second'],),
        (data['both'],),
        (data['with_date'],),
    ]
)
def test_print_report(table, capsys):
    out = tabulate(table, headers='keys')
    report_name = 'test_report'
    main.print_report(table, report_name)
    assert capsys.readouterr().out == out + '\n'
    assert os.path.exists(os.path.join(main.REPORTS_DIR, report_name))
    with open(os.path.join(main.REPORTS_DIR, report_name)) as report_file:
        assert report_file.read() == out
