import logging
import socket
from smtplib import SMTP
from typing import List
import ssl
import re

from utils.net import get_domain, get_mx_records

log = logging.getLogger(name=__name__)


class SMTPChecker:
    __debug = 0
    __timout = 3
    __ports = (587, 465, 25, 2525)
    __max_iteration = 10
    __sender = 'noreply@test.com'

    def __init__(self, ports: List = (587, 465, 25), debug=0, timeout=3, max_iteration=10, sender='noreply@test.com'):
        """
        :param ports:
        :param debug: [0 = void, 1 = info, 2 = debug]
        :param timeout:
        """
        self.__debug = debug
        self.__ports = ports
        self.__timout = timeout
        self.__max_iteration = max_iteration
        self.__stop_iteration = False
        self.__sender = sender

        if self.__debug == 1:
            # log.setLevel(logging.DEBUG)
            # logging.basicConfig(level=logging.DEBUG)
            logging.basicConfig(level=logging.INFO, format='%(message)s')

        if self.__debug == 2:
            logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    def validate(self, email):
        """
        Validate email trying to connect via smtp
            False ~ means invalid
            True  ~ means POSSIBLY valid
            None  ~ means unknown

        :param email:
        :return:
        """
        # get MX records
        domain = get_domain(email)

        if not domain:
            return False

        mx_records = get_mx_records(domain)

        if not mx_records:
            # raise ConnectionError('MX records not available')
            return False

        # append addition additional host
        # like: smtp.google.com
        # like: smtp.yandex.ru

        first_mx_entry_domain = '.'.join(mx_records[0].strip('.').split('.')[-2:])
        mx_records.insert(0, f'smtp.{first_mx_entry_domain}')
        # mx_records.append(f'smtp.{first_mx_entry_domain}')

        # append additional host
        mx_records.insert(0, f'smtp.{domain}')

        if not mx_records:
            return False

        log.debug(f'email: {email}')
        log.debug(f'domain: {domain}')
        log.debug(f'MX: {mx_records}')

        i = 0

        for host in mx_records:
            if self.__stop_iteration:
                break

            # remove trailing dots
            host = host.strip('.')

            for port in self.__ports:
                if self.__stop_iteration:
                    break

                # break iteration
                if self.__max_iteration and self.__max_iteration == i:
                    return

                try:
                    if not self.__debug:
                        print('.', end='')

                    log.info(f'PAIR: {i}, {email}, {domain}, {host}, {port}')
                    is_valid = self.__validate(email, domain, host, port)

                    if is_valid in (True, False):
                        return is_valid
                except Exception as error:
                    print(f'error: {error}')
                    pass

                i += 1

    def __validate(self, email, domain, host, port):
        try:
            log.debug(f'conn: {host}:{port}')

            context = ssl.create_default_context()

            # There seems to a bug in python, as `starttls()` causes an error:
            # `server_hostname cannot be an empty string or start with a leading dot.`
            # so, to avoid it - use the host in initialize as well
            # https://stackoverflow.com/a/53385409/1565790
            # https://bugs.python.org/issue36094
            server = SMTP(host=host, port=port, timeout=self.__timout)

            server.set_debuglevel(2 if self.__debug == 2 else 0)
            conn_code, *conn_others = server.connect(host, port)

            log.debug(f'CONN CODE >> : {conn_code}')

            # if approached to this line, then it means - connection successful
            # and no need farther iteration for another port(s)
            self.__stop_iteration = True

            # ehlo_host = socket.gethostname()
            ehlo_host = self.__sender.split('@')[1]
            server.ehlo(ehlo_host)

            # server.ehlo_or_helo_if_needed()
            # server.starttls(context=context)
            server.starttls()
            server.ehlo()
            # server.ehlo_or_helo_if_needed()

            # server.login(email, 'somepassword')

            sender_code, sender_message = server.mail(sender=self.__sender)
            log.info(f'SENDER >> : code: {sender_code}, message: {sender_message.decode()}')

            # Server Permanent Error Codes
            # 530 - means: Authentication Required
            # CLOSED RELAY!
            if re.search('auth', sender_message.decode(), re.IGNORECASE):
                return

            code, message = server.rcpt(recip=email)
            log.info(f'RCPT >>: code: {code}, message: {message.decode()}')

            # if get a message like:
            # e.g.: b'550 No such recipient here'
            if re.search('no.*recipient', message.decode(), re.IGNORECASE):
                return False

            # e.g.: b'550 relay not permitted, authentication required'
            #  in this case, rcpt seams to be existed!
            if re.search('relay.*not.*permitted', message.decode(), re.IGNORECASE):
                return True

            # e.g.: b'503 5.5.4 Bad sequence of commands. 1646307466-pgMeEi1NG7-bkKWu68k\r\n'
            if re.search('Bad.*sequence', message.decode(), re.IGNORECASE):
                return

            # 250 Accepted
            if code < 400:
                return True
        except Exception as error:
            log.debug(f'SMTP ERROR: {error}')
        # finally:
        #     server.quit()

# https://www.tutorialspoint.com/send-mail-from-your-gmail-account-using-python
# https://cppsecrets.com/users/1102811497104117108109111104116975048484864103109971051084699111109/Check-validity-of-Email-address-using-SMTP-and-dnspython-library.php
