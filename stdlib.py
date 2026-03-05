# stdlib.py — Стандартная библиотека языка ПОВЕЛЕВАЮ
import random as _random


def randint(a, b):
    return _random.randint(int(a), int(b))


def length(collection):
    return len(collection)


def to_int(value):
    return int(value)


def to_float(value):
    return float(value)


def to_str(value):
    return str(value)
