from helpers.db import Database


class Email:
    _TABLE_EMAILS = '_emails'
    _TABLE_DOMAINS = '_domains'
    _TABLE_SENT = '_sent_emails'
    _TABLE_WEBHOOK_EVENTS = '_sent_email_events'

    def __init__(self):
        self._db = Database()
        pass
