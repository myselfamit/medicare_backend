from datetime import datetime
import multiprocessing
import re

def result_list_to_dict(result):
    return [row._asdict() for row in result]

def apply_multi_processing(func_obj, result):
    with multiprocessing.Pool() as pool:
        data = pool.map(func_obj, result)
        return data

def result_row_to_dict(result_row):
    return result_row._asdict()


def list_to_searchable_dropdown(result, label_key, value_key):
    if type(result) == list:
        data = []
        for row in result:
            data.append({'label': row[label_key], 'value': row[value_key]})
    else:
        data = result

    return data

def to_datetime(s): return datetime.strptime(s, '%Y-%m-%d')


def strip_white_space(value=None):
    if value:
        value = " ".join(value.split())
    return value


def strip_special_chars(value):
    return (re.sub('[^A-Za-z0-9]+', ' ', value)).strip()

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(t, date_format):
    return t.strftime(date_format).replace('{S}', str(t.day) + suffix(t.day))