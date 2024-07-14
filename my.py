from __future__ import annotations
from collections.abc import KeysView  # before 3.10: from collections import KeysView
from datetime import datetime
from itertools import islice
from types import GeneratorType
import csv
import io
import json
import os
import subprocess
import sys
import traceback


def printed(var) -> str:
    output = io.StringIO()
    print(var, file=output, flush=True)
    contents = output.getvalue()
    output.close()
    return contents.replace("\\n", "\n")


class Encoder(json.JSONEncoder):
    def default(self, o):
        def merge_dicts(a: dict, b: dict) -> dict:
            return a | b if sys.version_info >= (3, 9) else {**a, **b}

        if isinstance(o, datetime):
            # return merge_dicts({'class': 'datetime'}, {prop: int(o.strftime(fmt)) for prop, fmt in {
            #     'year':   '%Y',
            #     'month':  '%m',
            #     'day':    '%d',
            #     'hour':   '%H',
            #     'minute': '%M',
            #     'second': '%S',
            # }.items()})
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, (GeneratorType, KeysView)):
            # return [self.default(v) for v in o]
            return list(o)
        if isinstance(o, Exception):
            return traceback.format_exc()
        # if hasattr(o, '__str__') and callable(getattr(o, '__str__')):
        #     return o.__str__()
        if hasattr(o, '__dict__'):  # doesn't work for class with declared properties
            return merge_dicts({"class": type(o).__name__}, o.__dict__)
        # if isinstance(o, np.ndarray):
        #     return "\n" + printed(o)
        return printed(o)
        # return merge_dicts({"class": type(o).__name__}, Encoder.__encode_dir(o))

    @staticmethod
    def __encode_dir(o: object) -> dict:
        dic = {}
        attributes = dir(o)
        for attribute in attributes:
            if not callable(o.__getattribute__(attribute)):
                dic[attribute] = o.__getattribute__(attribute)
        return dic


def json_encode_obj(var):
    return json.dumps(var, cls=Encoder, ensure_ascii=False)


def json_encode(var) -> str:
    return str(json_encode_obj(var)).replace("\\n", "\n")


def json_decode_obj(o):
    if isinstance(o, dict):
        if 'class' in o:
            class_ = o['class']
            del o['class']
            return globals()[class_](**o)
    return o


def json_decode(string: str):
    return json.loads(string, object_hook=json_decode_obj)


def dumped_at(skip: int, *var):
    frame = traceback.extract_stack()[-1 - skip]
    filename = frame.filename
    dirname = os.path.dirname(filename)
    while not any([os.path.exists(f"{dirname}/{path}") for path in [".git", ".idea", ".venv"]]):
        if dirname in ("", "/"):
            dirname = None
            break
        else:
            dirname = os.path.dirname(dirname)
    if dirname is not None:
        dirname += "/"
        if filename[:len(dirname)] == dirname:
            filename = filename[len(dirname):]
    prefix = f"{filename}:{frame.lineno}"
    out = prefix
    for v in var:
        out += " " + json_encode(v)
    lines = out.split("\n")
    if lines[-1] == "\"":
        lines[-2] += "\""
        lines = lines[:-1]
    for i in range(1, len(lines)):
        lines[i] = " " * (len(prefix) + 2) + lines[i]
    return "\n".join(lines)


def dump(*var):
    print(dumped_at(2, *var))
    # print(*var)


def log(*var) -> None:
    with open("log.txt", "a") as file:
        file.write(dumped_at(2, *var))


def err(*var):  # duplicated from `dump`
    print(dumped_at(2, *var), file=sys.stderr)


def call(command: str) -> list:
    lines = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True).stdout.readlines()
    return [line.decode("utf-8").rstrip() for line in lines]


def chunks_dict(data: dict, size: int) -> dict:
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}


def chunks_list(lst: list, size: int) -> list:
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


#


def csv_read_to_list(filename: str) -> list[list[str]]:
    with open(filename) as file:
        return [row for row in csv.reader(file)]


def csv_read_to_dict(filename: str) -> list[dict[str, str]]:
    rows = []
    header = None
    with open(filename) as file:
        for row in csv.reader(file):
            if header is None:
                header = row
            else:
                assert len(header) == len(row)
                rows.append({header[i]: row[i] for i in range(len(row))})
    return rows


def csv_write(filename: str, table: list[list[str]]) -> None:
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(table)


def sort_table(table: list, key_column: int = 0, reverse: bool = False) -> list:
    def get_value(row: list):
        return row[key_column]
    table2 = table.copy()
    table2.sort(key=get_value, reverse=reverse)
    return table2


def summarise(dic: dict) -> dict:
    counts = {}
    for key, value in dic.items():
        if value not in counts:
            counts[value] = 0
        counts[value] += 1
    return counts


class AbstractMethodException(Exception):
    def __init__(self) -> None:
        super().__init__("abstract method")
