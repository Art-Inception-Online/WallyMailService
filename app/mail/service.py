from helpers.db import Database


class Email:
    _TABLE_EMAILS = '_emails'
    _TABLE_DOMAINS = '_domains'

    def __init__(self):
        self._db = Database()
        pass
