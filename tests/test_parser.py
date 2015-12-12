from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import time

import pytz

from nics import parse


def test_can_parse_simple_lines():
    assert ['first', 'second'] == list(parse.text_into_lines('first\r\nsecond'))


def test_can_parse_folded_lines_with_space():
    assert ['first second'] == list(parse.text_into_lines('first\r\n  second'))


def test_can_parse_folded_lines_with_tab():
    assert ['first second'] == list(parse.text_into_lines('first\r\n\t second'))


def test_can_parse_multiple_folded_lines():
    assert ['first second third'] == list(parse.text_into_lines('first\r\n  second\r\n  third'))


def test_replace_single_quoted():
    assert 'A{1}C', ['B'] == parse.replace_quoted('A"B"C')


def test_replace_multiple_quoted():
    assert 'A{1}C{2}', ['B', 'D'] == parse.replace_quoted('A"B"C"D"')


def test_can_use_replaced_quotes():
    text, quoted = parse.replace_quoted('A"B"C"D"')
    assert 'CD' == 'C{1}'.format(*quoted)


def test_can_parse_simple_content():
    assert [('NAME', {}, 'VALUE')] == list(parse.lines_into_content(['NAME:VALUE']))


def test_can_parse_content_with_single_param():
    assert [('NAME', {'FOO': ['BAR']}, 'VALUE')] == list(parse.lines_into_content(['NAME;FOO=BAR:VALUE']))


def test_can_parse_content_with_single_param_multiple_values():
    assert [('NAME', {'FOO': ['BAR', 'BAR2']}, 'VALUE')] == list(parse.lines_into_content(['NAME;FOO=BAR,BAR2:VALUE']))


def test_can_parse_content_with_multiple_params():
    assert [('NAME', {'FOO': ['BAR'], 'FOO2': ['BAR2']}, 'VALUE')] == list(parse.lines_into_content(['NAME;FOO=BAR;FOO2=BAR2:VALUE']))


def test_can_parse_content_with_quoted_param():
    assert [('NAME', {'FOO': ['BAR;FOO2=BAR2']}, 'VALUE')] == list(parse.lines_into_content(['NAME;FOO="BAR;FOO2=BAR2":VALUE']))


def test_parse_boolean_values():
    assert [('NAME', {'VALUE': ['BOOLEAN']}, [True])] == list(parse.lines_into_content(['NAME;VALUE=BOOLEAN:TRUE']))
    assert [('NAME', {'VALUE': ['BOOLEAN']}, [False])] == list(parse.lines_into_content(['NAME;VALUE=BOOLEAN:FALSE']))
    assert [('NAME', {'VALUE': ['BOOLEAN']}, [True])] == list(parse.lines_into_content(['NAME;VALUE=BOOLEAN:true']))
    assert [('NAME', {'VALUE': ['BOOLEAN']}, [False])] == list(parse.lines_into_content(['NAME;VALUE=BOOLEAN:false']))


def test_parse_date_values():
    assert [('NAME', {'VALUE': ['DATE']}, [date(2015, 1, 1)])] == list(parse.lines_into_content(['NAME;VALUE=DATE:20150101']))
    assert [('NAME', {'VALUE': ['DATE']}, [date(2015, 1, 1), date(2015, 1, 2)])] == list(parse.lines_into_content(['NAME;VALUE=DATE:20150101,20150102']))


def test_parse_datetime_values():
    assert [('NAME', {'VALUE': ['DATE-TIME']}, [datetime(2015, 1, 1, 10, 0, 0)])] == list(parse.lines_into_content(['NAME;VALUE=DATE-TIME:20150101T100000']))
    assert [('NAME', {'VALUE': ['DATE-TIME']}, [datetime(2015, 1, 1, 10, 0, 0), datetime(2015, 1, 2, 10, 0, 0)])] == list(parse.lines_into_content(['NAME;VALUE=DATE-TIME:20150101T100000,20150102T100000']))


def test_parse_datetime_value_in_utc():
    assert [('NAME', {'VALUE': ['DATE-TIME']}, [datetime(2015, 1, 1, 10, 0, 0, tzinfo=pytz.utc)])] == list(parse.lines_into_content(['NAME;VALUE=DATE-TIME:20150101T100000Z']))


def test_parse_duration_values():
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(days=1)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:P1D']))
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(days=1), timedelta(days=2)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:P1D,P2D']))


def test_parse_duration_negative():
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(days=-1)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:-P1D']))


def test_parse_duration_positive():
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(days=1)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:+P1D']))


def test_parse_duration_day_and_time():
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(days=1, hours=2, minutes=3, seconds=4)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:P1DT2H3M4S']))


def test_parse_duration_time():
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(hours=2, minutes=3, seconds=4)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:PT2H3M4S']))


def test_parse_duration_weeks():
    assert [('NAME', {'VALUE': ['DURATION']}, [timedelta(days=14)])] == list(parse.lines_into_content(['NAME;VALUE=DURATION:P2W']))


def test_parse_float_values():
    assert [('NAME', {'VALUE': ['FLOAT']}, [0.1])] == list(parse.lines_into_content(['NAME;VALUE=FLOAT:0.1']))
    assert [('NAME', {'VALUE': ['FLOAT']}, [0.1])] == list(parse.lines_into_content(['NAME;VALUE=FLOAT:+0.1']))
    assert [('NAME', {'VALUE': ['FLOAT']}, [-0.1])] == list(parse.lines_into_content(['NAME;VALUE=FLOAT:-0.1']))
    assert [('NAME', {'VALUE': ['FLOAT']}, [1.0])] == list(parse.lines_into_content(['NAME;VALUE=FLOAT:1']))
    assert [('NAME', {'VALUE': ['FLOAT']}, [0.1, 0.2])] == list(parse.lines_into_content(['NAME;VALUE=FLOAT:0.1,0.2']))


def test_parse_integer_values():
    assert [('NAME', {'VALUE': ['INTEGER']}, [1])] == list(parse.lines_into_content(['NAME;VALUE=INTEGER:1']))
    assert [('NAME', {'VALUE': ['INTEGER']}, [1])] == list(parse.lines_into_content(['NAME;VALUE=INTEGER:+1']))
    assert [('NAME', {'VALUE': ['INTEGER']}, [-1])] == list(parse.lines_into_content(['NAME;VALUE=INTEGER:-1']))
    assert [('NAME', {'VALUE': ['INTEGER']}, [1, 2])] == list(parse.lines_into_content(['NAME;VALUE=INTEGER:1,2']))


def test_parse_text_values():
    assert [('NAME', {'VALUE': ['TEXT']}, ['foo'])] == list(parse.lines_into_content(['NAME;VALUE=TEXT:foo']))
    assert [('NAME', {'VALUE': ['TEXT']}, ['foo', 'bar'])] == list(parse.lines_into_content(['NAME;VALUE=TEXT:foo,bar']))


def test_parse_text_with_newlines():
    assert [('NAME', {'VALUE': ['TEXT']}, ['foo\nbar'])] == list(parse.lines_into_content(['NAME;VALUE=TEXT:foo\\nbar']))


def test_parse_text_with_commas():
    assert [('NAME', {'VALUE': ['TEXT']}, ['foo, bar'])] == list(parse.lines_into_content(['NAME;VALUE=TEXT:foo\\, bar']))


def test_parse_text_with_backslashes():
    assert [('NAME', {'VALUE': ['TEXT']}, ['foo\\bar'])] == list(parse.lines_into_content(['NAME;VALUE=TEXT:foo\\\\bar']))


def test_parse_text_with_semi_colons():
    assert [('NAME', {'VALUE': ['TEXT']}, ['foo;bar'])] == list(parse.lines_into_content(['NAME;VALUE=TEXT:foo\\;bar']))


def test_parse_time_values():
    assert [('NAME', {'VALUE': ['TIME']}, [time(10, 0, 0)])] == list(parse.lines_into_content(['NAME;VALUE=TIME:100000']))
    assert [('NAME', {'VALUE': ['TIME']}, [time(10, 0, 0), time(10, 0, 0)])] == list(parse.lines_into_content(['NAME;VALUE=TIME:100000,100000']))


def test_parse_time_value_in_utc():
    assert [('NAME', {'VALUE': ['TIME']}, [time(10, 0, 0, tzinfo=pytz.utc)])] == list(parse.lines_into_content(['NAME;VALUE=TIME:100000Z']))


def test_parse_utc_offset():
    assert [('NAME', {'VALUE': ['UTC-OFFSET']}, [pytz.FixedOffset(60)])] == list(parse.lines_into_content(['NAME;VALUE=UTC-OFFSET:0100']))
    assert [('NAME', {'VALUE': ['UTC-OFFSET']}, [pytz.FixedOffset(60)])] == list(parse.lines_into_content(['NAME;VALUE=UTC-OFFSET:+0100']))
    assert [('NAME', {'VALUE': ['UTC-OFFSET']}, [pytz.FixedOffset(-60)])] == list(parse.lines_into_content(['NAME;VALUE=UTC-OFFSET:-0100']))
    assert [('NAME', {'VALUE': ['UTC-OFFSET']}, [pytz.FixedOffset(90)])] == list(parse.lines_into_content(['NAME;VALUE=UTC-OFFSET:0130']))
