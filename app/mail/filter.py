import inspect
import json
import os
from pprint import pprint

from config import EmailStatus as Status
from helpers.db_connection import db
from mail.service import Email
from utils import thread
from utils.net import *
from utils.smtp_checker import SMTPChecker

from config import EmailFilterType


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
                print('Filtering by SMTP: NOT IMPLEMENTED YET!')
                thread.run(self.__threads, self.__filter_by_smtp(), kwargs={'db': db})
                pass

            elif filter_by == EmailFilterType.API:
                print('Filtering by API: NOT IMPLEMENTED YET!')

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
        thread_i = 'n/a' if not 'thread' in kwargs else kwargs.get("thread")

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
                cursor.execute(query, (None if data['valid'] else '0', Status.DOMAIN_HANDLED.value, domain))

                conn.commit()
            finally:
                # Unlock tables
                cursor.execute(f'UNLOCK TABLES')

    def __filter_by_smtp(self, *args, **kwargs):
        """Filter emails for existence on mail server"""
        thread_i = 'n/a' if not 'thread' in kwargs else kwargs.get("thread")

        conn, error = next(kwargs.get("db")())

        while True:
            try:
                cursor = conn.cursor(dictionary=False, buffered=True)

                # lock tables
                # to prevent duplicate entry handling
                cursor.execute(f'LOCK TABLES {self._TABLE_EMAILS} WRITE, {self._TABLE_EMAILS} AS t1 WRITE')

                query = f'SELECT email FROM {self._TABLE_EMAILS} t1 ' \
                        f'LEFT JOIN {self._TABLE_DOMAINS} t2 ON t2.domain = t1.domain ' \
                        f'WHERE t1.status IS NULL AND t2.id IS NULL ' \
                        f'GROUP BY t1.domain ORDER BY count(*) DESC ' \
                        f'LIMIT 1'
                cursor.execute(query)
                row = cursor.fetchone()
            finally:
                # Unlock tables
                cursor.execute(f'UNLOCK TABLES')

        raise Exception('Not implemented')

        emails = self._db.get_records(f'SELECT mail FROM {self._TABLE_EMAILS} WHERE valid IS NULL '
                                      f'ORDER BY weight DESC, mail DESC '
                                      f' LIMIT 1', dict=False)

        for email, in emails:
            is_valid = SMTPChecker(debug=0, timeout=1, max_iteration=5).validate(email)
            print(f'{email} is valid: {is_valid}')

    def __filter_by_webhook_events(self):
        """
        Filter emails based on webhook events,
        where event is a negative value: {"complained", "unsubscribed", "failed"}
        """
        query = f'UPDATE {self._TABLE_EMAILS} t1 ' \
                f'INNER JOIN ( ' \
                    f'SELECT email, GROUP_CONCAT(DISTINCT event) AS events FROM {self._TABLE_WEBHOOK_EVENTS} t2 ' \
                    f'WHERE t2.event IN ("complained", "unsubscribed", "failed") ' \
                    f'GROUP BY t2.email ' \
                f') t3 ON t3.email = t1.email ' \
                f'SET t1.valid = 0, t1.notes = t3.events'
        self._db.execute(query, commit=True)

    def stats(self):
        return {
            'Total valid emails':
                (self._db.get_record(f'SELECT COUNT(*) FROM {self._TABLE_EMAILS} '
                                     f'WHERE valid <> 0 OR valid IS NULL', dict=False)[0]),
            'Total valid domains':
                (self._db.get_record(f'SELECT COUNT(DISTINCT domain) FROM {self._TABLE_EMAILS} '
                                     f'WHERE valid <> 0 OR valid IS NULL', dict=False)[0]),
        }
