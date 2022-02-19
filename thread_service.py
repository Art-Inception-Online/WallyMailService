from threading import Thread
from typing import Optional


def run(threads_count: int, callback, args=list(), kwargs={}):
    threads = []

    for i in range(threads_count):
        t = Thread(target=callback, args=args, kwargs={**kwargs, 'thread': i})
        threads.append(t)

    for i in range(threads_count):
        threads[i].start()

    for i in range(threads_count):
        threads[i].join()
