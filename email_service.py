from db_helper import Database


class Email:
    _TABLE_EMAILS = '_emails'

    def __init__(self):
        self._db = Database()
        pass
