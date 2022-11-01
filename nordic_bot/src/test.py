from _datetime import datetime, timedelta
from time import time
TR_FILENAME = "../data/timeroles.json"
import cProfile


def foo():
    i = 0
    while i< 100000:
        print(i)
        i = i + 1


cProfile.run('foo()')