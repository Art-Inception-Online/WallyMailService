import re
import time
from pathlib import Path
from string import Template

from config import EmailStatus
from helpers.db_connection import db
from mail.service import Email
from utils import thread
from utils.send import send


class EmailsSender(Email):
    __already_sent_emails = 0

    def __init__(self, config, campaign_id: int, total_send_emails=10, threads=10,
                 check_email_for_existence=False, wait: float = 0):
        self.__campaign_id = campaign_id
        self.__threads = threads
        self.__total_send_emails = total_send_emails
        # @TODO - needs to be implemented via smtp_checker.py
        self.__check_email_for_existence = check_email_for_existence
        self.__wait = wait
        self.__config = config

        super().__init__()

    def handle(self):
        print(f'Handling:\n Thread  |  Sent №  |  Sleep |        Email        ')
        thread.run(self.__threads, self.__send, kwargs={'db': db})

    def __send(self, *args, **kwargs):
        thread_index = 'n/a' if 'thread' not in kwargs else kwargs.get("thread")

        conn, error = next(kwargs.get("db")())

        while self.__already_sent_emails < self.__total_send_emails:
            self.__already_sent_emails += 1

            try:
                cursor = conn.cursor(dictionary=False, buffered=True)

                # lock
                cursor.execute(f'LOCK TABLES {self._TABLE_EMAILS} AS t1 WRITE, {self._TABLE_EMAILS} WRITE, ' \
                               f'{self._TABLE_SENT} WRITE')

                query = f'SELECT t1.email FROM {self._TABLE_EMAILS} t1 ' \
                        f'WHERE (t1.valid <> 0 OR t1.valid IS NULL) ' \
                        f'AND t1.status NOT IN ("{EmailStatus.EMAIL_HANDLING.value}", ' \
                        f'"{EmailStatus.EMAIL_HANDLED.value}") ' \
                        f'ORDER BY weight DESC ' \
                        f'LIMIT 1'
                cursor.execute(query)
                row = cursor.fetchone()

                if not row:
                    return

                email, *other = row

                # set email as handling, info for other thread(s)
                self.__change_email_handling_status(email, EmailStatus.EMAIL_HANDLING, cursor)
                # conn.commit()

                # THREAD SAFE PRINT
                content = f'{thread_index}'.ljust(6).rjust(9) + '|' \
                          + f'#{self.__already_sent_emails}'.ljust(8).rjust(10) + '|' \
                          + f'{self.__wait}s'.ljust(5).rjust(8) + '|' \
                          + f' {email}'

                # get message
                message_substitution_data = {'name': email.split('@')[0], 'email': email}
                subject, html_message = self.__get_subject_and_message(message_substitution_data)
                alternative_message = self.__get_alternative_message(message_substitution_data)

                msg = send(email, subject, html_message, alternative_message,
                           {'campaign-id': self.__campaign_id}, config=self.__config)

                self.__set_email_as_sent(email, subject, msg['Message-ID'].strip('<>'), cursor)
                conn.commit()

                print("{0}\n".format(content), end='')
                time.sleep(self.__wait)
            except Exception as error:
                print(f'ERROR: {error}')
                pass
            finally:
                # Unlock tables
                cursor.execute(f'UNLOCK TABLES')

    def __get_subject_and_message(self, data: dict = {}):
        """read message from template and substitute data"""
        template = Template(Path(f'app/templates/campaign-{self.__campaign_id}.html').read_text(encoding="UTF-8"))

        # data replacement
        message = template.substitute(data)

        # get subject if applicable
        subject_pattern = r'{% block subject %}([^.]*){% endblock %}'
        subject_match = re.findall(subject_pattern, message, flags=re.S)
        subject = (subject_match[0]).strip() if subject_match else 'No subject'

        # remove subject block
        # message = re.sub(r'{%\s*block.*endblock\s*%}', '', message, flags=re.S)
        message = re.sub(subject_pattern, '', message, flags=re.S)

        return subject, message

    def __get_alternative_message(self, data: dict = {}):
        """alternative message for text/plain"""
        try:
            template = Template(Path(f'app/templates/campaign-{self.__campaign_id}.txt').read_text(encoding="UTF-8"))
            return template.substitute(data)
        except FileNotFoundError:
            return

    def __change_email_handling_status(self, email, status: EmailStatus, cursor):
        """set email as handling|handled"""
        query = f'UPDATE {self._TABLE_EMAILS} SET status = %s WHERE email = %s'
        cursor.execute(query, (status.value, email))

    def __set_email_as_sent(self, email, subject, message_id, cursor):
        self.__change_email_handling_status(email, EmailStatus.EMAIL_HANDLED, cursor)

        query = f'INSERT INTO {self._TABLE_SENT} SET campaign_id = %s, email = %s, subject = %s, message_id = %s, ' \
                f'status = "ok" '
        cursor.execute(query, (self.__campaign_id, email, subject, message_id))
