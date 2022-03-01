from app.helpers.db import Database


class Email:
    _TABLE_EMAILS = '_emails'
    _TABLE_DOMAINS = '_domains'
    _TABLE_SENT = '_sent_emails'

    def __init__(self):
        self._db = Database()
        pass
