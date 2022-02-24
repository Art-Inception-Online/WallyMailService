import time
from threading import Thread


def run(threads_count: int, callback, args=list(), kwargs={}, wait=0):
    """
    Run callback in multiple threads
    Each callback receives kwarg with key: thread - thread number

    :param threads_count:
    :param callback:
    :param args:
    :param kwargs:
    :param wait:
    :return:
    """
    threads = []

    for i in range(threads_count):
        t = Thread(target=callback, args=args, kwargs={**kwargs, 'thread': i})
        threads.append(t)

    for i in range(threads_count):
        time.sleep(wait)
        threads[i].start()

    for i in range(threads_count):
        threads[i].join()
