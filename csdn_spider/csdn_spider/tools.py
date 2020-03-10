import time
from prettytable import PrettyTable


class Printer:
    start_time = 0
    last_time = 0
    last_values = []
    table = PrettyTable()

    def __init__(self):
        self.start()

    def start(self):
        self.start_time = time.time()
        self.last_time = time.time()

    def print(self, tags: [], values: [], interval: float = 1):
        if len(self.last_values) != len(values):
            self.last_values = values
        if len(self.table.field_names) == 0:
            self.table.field_names = ["Tags", "Count", " Add ", "Speed"]
        curr = time.time()
        if curr - self.last_time < interval:
            return

        self.table.clear_rows()
        for i in range(len(tags)):
            add = values[i] - self.last_values[i]
            speed = values[i] / (curr - self.start_time)
            self.table.add_row([tags[i], f'{values[i]}', f'{add}', f'{speed:.1f}'])

        print(self.table)
        self.last_time = curr - (curr - self.last_time) % interval
        self.last_values = values


def between(_str, start, end):
    b = _str.find(start) + len(start)
    e = _str.find(end, b)
    return _str[b:e]


def rbetween(_str, start, end):
    e = _str.rfind(end)
    b = _str.rfind(start, 0, e) + len(start)
    return _str[b:e]


def tail(_str, start):
    return _str[_str.rfind(start) + len(start):]


def head(_str, end):
    return _str[0:_str.find(end)]


def list0(ls, default=''):
    if len(ls) > 0:
        return ls[0]
    return default