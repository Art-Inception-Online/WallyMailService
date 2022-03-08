import inspect
import json
import os
import re
import time
from pprint import pprint

import requests
import config
from config import EmailFilterType, EmailStatus
from helpers.db_connection import db
from mail.service import Email
from utils import thread
from utils.net import *
from utils.smtp_checker import SMTPChecker



def mailgun_verify_email(email):
    # # DEBUG
    # return {'address': email, 'is_disposable_address': False, 'is_role_address': False,
    #         'reason': [], 'result': 'deliverable', 'risk': 'low'}

    response = requests.get(
        "https://api.mailgun.net/v4/address/validate",
        auth=("api", config.mailgun_api_key),
        params={"address": email})

    return response.json()


class EmailsFilter(Email):
    def __init__(self, threads=10):
        self.__threads = threads
        super().__init__()

    def handle(self, filter_by: EmailFilterType = EmailFilterType.DOMAIN):
        try:
            if filter_by == EmailFilterType.DOMAIN:
                print('Filtering by domain:')
                print(f'Handling:\n Thread  |         Domain         |   VALID   |        IP        |       MX       ')

                # each thread should receive new db instance
                thread.run(self.__threads, self.__filter_by_domains, kwargs={'db': db})

            elif filter_by == EmailFilterType.EVENTS:
                print('Filtering by WEBHOOK EVENTS..')
                self.__filter_by_webhook_events()
                print('DONE.')

            elif filter_by == EmailFilterType.SMTP:
                print('Filtering by SMTP..')
                print(f'Handling:\n Thread  |          Email          |   VALID')
                thread.run(self.__threads, self.__filter_by_smtp, kwargs={'db': db})

            elif filter_by == EmailFilterType.API:
                print('Filtering by MAILGUN API..')
                print(f'Handling:\n Thread  |          Email          |   VALID')
                thread.run(self.__threads, self.__filter_by_api, kwargs={'db': db})

            return self.stats()
        except Exception as error:
            fn = __name__
            fn = os.path.basename(inspect.getframeinfo(inspect.currentframe()).filename)
            ln = inspect.getframeinfo(inspect.currentframe()).lineno
            print(f'ERROR ({fn}:{ln})', error)

    def __filter_by_domains(self, *args, **kwargs):
        """
        Filter mail by valid (existing) domain
        by detecting Host IP or MX Record(s)
        """
        thread_i = 'n/a' if 'thread' not in kwargs else kwargs.get("thread")

        conn, error = next(kwargs.get("db")())

        while True:
            try:
                cursor = conn.cursor(dictionary=False, buffered=True)

                # lock tables
                # to prevent duplicate entry handling
                cursor.execute(f'LOCK TABLES {self._TABLE_EMAILS} WRITE, {self._TABLE_EMAILS} AS t1 WRITE, '
                               f'{self._TABLE_DOMAINS} WRITE, {self._TABLE_DOMAINS} AS t2 WRITE')

                query = f'SELECT t1.domain FROM {self._TABLE_EMAILS} t1 ' \
                        f'LEFT JOIN {self._TABLE_DOMAINS} t2 ON t2.domain = t1.domain ' \
                        f'WHERE t1.status IS NULL AND t2.id IS NULL ' \
                        f'GROUP BY t1.domain ORDER BY count(*) DESC ' \
                        f'LIMIT 1'
                cursor.execute(query)
                row = cursor.fetchone()

                if not row:
                    return

                domain, = row

                # insert into domains, as validating it
                query = f'INSERT INTO {self._TABLE_DOMAINS} SET domain = %s ON DUPLICATE KEY UPDATE id=id'
                cursor.execute(query, (domain,))
                # conn.commit()

                data = validate_domain(domain)

                # THREAD SAFE PRINT
                content = f'{thread_i}'.ljust(6).rjust(9) + '|' \
                          + f'{domain}'.ljust(23).rjust(24) + '|' \
                          + f'{data["valid"]}'.ljust(8).rjust(11) + '|' \
                          + f'{data["ip"]}'.ljust(17).rjust(18) + '|' \
                          + f'{data["mx"]}'.ljust(15).rjust(16)

                print("{0}\n".format(content), end='')

                query = f'UPDATE {self._TABLE_DOMAINS} SET valid = %s, ip = %s, mx = %s WHERE domain = %s'
                cursor.execute(query, ('1' if data['valid'] else '0', data["ip"],
                                       None if not data["mx"] else json.dumps(data["mx"]), domain))

                # Update related emails with proper `valid` & `status` field values
                query = f'UPDATE {self._TABLE_EMAILS} SET valid = %s, status = %s WHERE domain = %s'
                cursor.execute(query, (None if data['valid'] else '0', EmailStatus.DOMAIN_HANDLED.value, domain))

                conn.commit()
            finally:
                # Unlock tables
                cursor.execute(f'UNLOCK TABLES')

    def __filter_by_webhook_events(self, **kwargs):
        """
        Filter emails based on webhook events,
        where event is a negative value: {
            # Mailgun for (https://documentation.mailgun.com/en/latest/api-events.html#event-types)
            "rejected", "failed", "unsubscribed", "complained",

            # Sendgrid for (https://docs.sendgrid.com/for-developers/tracking-events/event)
            "dropped", "bounce", "blocked"
        }
        """

        # @FIX: escape event string more accurately
        # conn, error = next(db())
        # conn.escape_string() - not exists
        # print(conn.prepare_for_mysql(("d\"foo", "bar")))

        query_addon = ''
        if config.webhook_events_determining_emails_as_invalid:
            __events = config.webhook_events_determining_emails_as_invalid
            # query_addon = f'AND t2.event IN ("' + '", "'.join(__events) + '") '
            query_addon = f'AND t2.event IN ("' + '", "'.join([e.replace('"', '\\"') for e in __events]) + '") '

        query = f'UPDATE {self._TABLE_EMAILS} t1 ' \
                f'INNER JOIN ( ' \
                f'SELECT email, GROUP_CONCAT(DISTINCT event) AS events FROM {self._TABLE_WEBHOOK_EVENTS} t2 ' \
                f'WHERE 1=1 {query_addon} ' \
                f'GROUP BY t2.email ' \
                f') t3 ON t3.email = t1.email ' \
                f'SET t1.valid = 0, t1.notes = t3.events'

        self._db.execute(query, commit=True)

    def __filter_by_smtp(self, *args, **kwargs):
        """Filter emails for existence on mail server"""
        thread_i = 'n/a' if 'thread' not in kwargs else kwargs.get("thread")

        conn, error = next(kwargs.get("db")())

        while True:
            try:
                cursor = conn.cursor(dictionary=False, buffered=True)

                # lock tables
                # to prevent duplicate entry handling
                cursor.execute(f'LOCK TABLES {self._TABLE_EMAILS} WRITE, {self._TABLE_EMAILS} AS t1 WRITE')

                # closed relay!
                # as they require authentication
                exclude_domains = (
                    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'yahoo.co.uk', 'ymail.com', 'yahoo.de',
                    'live.com', 'yandex.ru', 'mail.ru', 'rambler.ru', 'bk.ru', 'inbox.ru', 'list.ru',
                )

                query = f'SELECT email FROM {self._TABLE_EMAILS} ' \
                        f'WHERE valid IS NULL AND status NOT IN (%s) ' \
                        f'AND domain NOT IN ("' + '", "'.join(exclude_domains) + '") ' \
                        f'AND smtp_checked = 0 ' \
                        f'ORDER BY weight DESC ' \
                        f'LIMIT 1'
                cursor.execute(query, (EmailStatus.EMAIL_HANDLED.value,))
                email, = cursor.fetchone()

                print(f'handling.. {email}')

                # Possible values: True, False, None
                is_valid = SMTPChecker(debug=0, timeout=3, max_iteration=10, sender="me@test.com").validate(email)
                valid = 1 if is_valid else (0 if is_valid is False else None)

                # THREAD SAFE PRINT
                content = f'{thread_i}'.ljust(6).rjust(9) + '|' \
                          + f'{email}'.ljust(23).rjust(25) + '|' \
                          + f'{is_valid}'.ljust(8).rjust(11)
                print("\n{0}\n".format(content), end='')

                # Update related emails with proper `valid` & `status` field values
                query = f'UPDATE {self._TABLE_EMAILS} SET smtp_checked = 1, valid = %s, status = %s WHERE email = %s'
                cursor.execute(query, (valid, EmailStatus.DOMAIN_HANDLED.value, email))
                conn.commit()
            finally:
                # Unlock tables
                cursor.execute(f'UNLOCK TABLES')

    def __filter_by_api(self, *args, **kwargs):
        """Filter emails for existence via MAILGUN API"""
        thread_i = 'n/a' if 'thread' not in kwargs else kwargs.get("thread")

        conn, error = next(kwargs.get("db")())

        while True:
            try:
                cursor = conn.cursor(dictionary=False, buffered=True)

                # lock tables
                # to prevent duplicate entry handling
                cursor.execute(f'LOCK TABLES {self._TABLE_EMAILS} WRITE, {self._TABLE_EMAILS} AS t1 WRITE, '
                               f'{self._TABLE_VERIFICATION_LOG} WRITE')

                query = f'SELECT email FROM {self._TABLE_EMAILS} WHERE ' \
                        f'valid IS NULL AND status NOT IN (%s) AND api_checked = 0 ' \
                        f'AND (smtp_checked = 0 OR (smtp_checked = 1 AND valid IS NULL)) ' \
                        f'ORDER BY weight DESC ' \
                        f'LIMIT 1'
                cursor.execute(query, (EmailStatus.EMAIL_HANDLED.value,))
                email, = cursor.fetchone()

                print(f'handling.. {email}')

                # simulate result
                response = mailgun_verify_email(email)
                print(f'response: {response}')

                # save response
                query = f'INSERT INTO {self._TABLE_VERIFICATION_LOG} ' \
                        f'SET email = %s, transport = %s, status = %s, risk = %s, payload = %s'
                cursor.execute(query, (email, 'mailgun', response['result'], response['risk'], json.dumps(response)))

                # determine valid or not
                is_valid = None

                # [Field Explanation]
                # https://documentation.mailgun.com/en/latest/api-email-validation.html#field-explanation
                if response['risk'] in ('high',) or response['result'] in ('undeliverable', 'do_not_send'):
                    # despite even if 'status' could be 'deliverable'
                    is_valid = False
                elif response['result'] in ('deliverable',):
                    is_valid = True

                valid = 1 if is_valid else (0 if is_valid is False else None)

                # THREAD SAFE PRINT
                content = f'{thread_i}'.ljust(6).rjust(9) + '|' \
                          + f'{email}'.ljust(23).rjust(25) + '|' \
                          + f'{is_valid}'.ljust(8).rjust(11)
                print("\n{0}\n".format(content), end='')

                # Update related emails with proper `valid` & `status` field values
                query = f'UPDATE {self._TABLE_EMAILS} SET api_checked = 1, valid = %s WHERE email = %s'
                cursor.execute(query, (valid, email))
                conn.commit()
            finally:
                # Unlock tables
                cursor.execute(f'UNLOCK TABLES')

    def stats(self):
        return {
            'Total valid emails':
                (self._db.get_record(f'SELECT COUNT(*) FROM {self._TABLE_EMAILS} '
                                     f'WHERE valid <> 0 OR valid IS NULL', dict=False)[0]),
            'Total valid domains':
                (self._db.get_record(f'SELECT COUNT(DISTINCT domain) FROM {self._TABLE_EMAILS} '
                                     f'WHERE valid <> 0 OR valid IS NULL', dict=False)[0]),
        }
