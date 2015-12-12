import datetime
import re

import pytz

QUOTED_RE = re.compile('"([^"]*)"')


def text_into_lines(text):
    _buffer = None
    for line in text.split('\r\n'):
        if line.startswith(' ') or line.startswith('\t'):
            _buffer.append(line[1:])
        else:
            if _buffer is not None:
                yield ''.join(_buffer)
            _buffer = [line]
    if _buffer is not None:
        yield ''.join(_buffer)


def replace_quoted(text):
    matches = QUOTED_RE.findall(text)
    for i, match in enumerate(matches):
        text = text.replace('"%s"' % match, '{%d}' % i)
    return text, matches


def separate_line(line):
    name_params, value = line.split(':', 1)
    name, params = name_params, {}
    try:
        name, all_params = name.split(';', 1)
        all_params, quotes = replace_quoted(all_params)
        for param in all_params.split(';'):
            param_key, param_value = param.split('=')
            params[param_key.upper()] = [v.format(*quotes) for v in param_value.split(',')]
    except ValueError:
        pass
    return name, params, value


def convert_to_booleans(value):
    values = []
    for v in value.split(','):
        values.append(True if value.upper() == 'TRUE' else False)
    return values


def convert_to_dates(value):
    values = []
    for v in value.split(','):
        year, month, day = v[0:4], v[4:6], v[6:]
        values.append(datetime.date(int(year), int(month), int(day)))
    return values


def convert_to_datetimes(value):
    values = []
    for v in value.split(','):
        date, time = v.split('T')
        date = convert_to_dates(date)
        time = convert_to_times(time)
        values.append(datetime.datetime.combine(date[0], time[0]))
    return values


def convert_to_floats(value):
    values = []
    for v in value.split(','):
        values.append(float(v))
    return values


def convert_to_integers(value):
    values = []
    for v in value.split(','):
        values.append(int(v))
    return values


def convert_to_texts(value):
    values = []
    for v in value.split(','):
        v = v.replace()
        if values and values[-1][-1] == '\\':
            values[-1] = '%s%s' % (values[-1][:-1], v)
        else:
            values.append(v)
    return values


def convert_to_times(value):
    values = []
    for v in value.split(','):
        hour, minute, second = v[0:2], v[2:4], v[4:6]
        is_utc = v[-1] == 'Z'
        tz = None
        if is_utc:
            tz = pytz.utc
        values.append(datetime.time(int(hour), int(minute), int(second), tzinfo=tz))
    return values


def convert_to_utc_offsets(value):
    values = []
    for v in value.split(','):
        hours, minutes = int(v[:-2]), int(v[-2:])
        minutes += 60 * abs(hours)
        if hours < 0:
            minutes *= -1
        values.append(pytz.FixedOffset(minutes))
    return values


def convert_to_type(value, params):
    if 'VALUE' in params:
        _type = params['VALUE'][0].upper()
        if _type == 'BOOLEAN':
            value = convert_to_booleans(value)
        elif _type == 'DATE':
            value = convert_to_dates(value)
        elif _type == 'DATE-TIME':
            value = convert_to_datetimes(value)
        elif _type == 'FLOAT':
            value = convert_to_floats(value)
        elif _type == 'INTEGER':
            value = convert_to_integers(value)
        elif _type == 'TEXT':
            value = convert_to_texts(value)
        elif _type == 'TIME':
            value = convert_to_times(value)
        elif _type == 'UTC-OFFSET':
            value = convert_to_utc_offsets(value)
    return value


def lines_into_content(lines):
    for line in lines:
        name, params, value = separate_line(line)
        value = convert_to_type(value, params)
        yield name, params, value
