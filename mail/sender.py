from utils import thread
from mail.service import Email
import time


class EmailsSender(Email):
    __already_sent_emails = 0

    def __init__(self, threads=10, total_send_emails=10, check_email_for_existence=False, wait: float = 0):
        self.__threads = threads
        self.__total_send_emails = total_send_emails
        self.__check_email_for_existence = check_email_for_existence
        self.__wait = wait

        super().__init__()

    def handle(self):
        print(f'Handling:\n Thread  |  Sent  |  Sleep')
        thread.run(self.__threads, self.__send)

    def __send(self, *args, **kwargs):
        thread = 'n/a' if not 'thread' in kwargs else kwargs.get("thread")

        while self.__already_sent_emails < self.__total_send_emails:
            self.__already_sent_emails += 1

            # THREAD SAFE PRINT
            content = f'{thread}'.ljust(6).rjust(9) + '|' \
                      + f'#{self.__already_sent_emails}'.ljust(6).rjust(8) + '|' \
                      + f'{self.__wait}s'.ljust(5).rjust(7)

            self.send('test@admin.ge')

            print("{0}\n".format(content), end='')
            time.sleep(self.__wait)

    def send(self, email):
        # get not sent mail
        pass
