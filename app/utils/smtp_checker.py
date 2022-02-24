import logging
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
    __max_iteration = 0

    def __init__(self, ports: List = (587, 465, 25), debug=0, timeout=3, max_iteration=0):
        """
        :param ports:
        :param debug: [0 = void, 1 = info, 2 = debug]
        :param timeout:
        """
        self.__debug = debug
        self.__ports = ports
        self.__timout = timeout
        self.__max_iteration = max_iteration

        if self.__debug == 1:
            # log.setLevel(logging.DEBUG)
            # logging.basicConfig(level=logging.DEBUG)
            logging.basicConfig(level=logging.INFO, format='%(message)s')

        if self.__debug == 2:
            logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    def validate(self, email):
        # get MX records
        domain = get_domain(email)

        if not domain:
            return False

        mx_records = get_mx_records(domain)

        if not mx_records:
            return False

        log.debug(f'email: {email}')
        log.debug(f'domain: {domain}')
        log.debug(f'MX: {mx_records}')

        i = 0

        for host in mx_records:
            for port in self.__ports:
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
            log.debug(f'port: {port}')

            context = ssl.create_default_context()
            server = SMTP(timeout=self.__timout)

            server.set_debuglevel(2 if self.__debug == 2 else 0)
            server.connect(host, port)
            server.ehlo_or_helo_if_needed()
            # server.starttls(context=context)
            # server.ehlo()

            code, message = server.mail(sender='noreply@drive.ge')
            log.info(f'code: {code}, message: {message.decode()}')

            code, message = server.rcpt(recip=email)
            log.info(f'code: {code}, message: {message.decode()}')

            # if get a message like:
            # code: 550
            # message: b'No such recipient here'
            if re.search('no.*recipient', message.decode(), re.IGNORECASE):
                return False

            # else, mail address might be valid!
            return True
        except Exception as error:
            log.debug(f'error >: {error}')
        # finally:
        #     server.quit()

# https://www.tutorialspoint.com/send-mail-from-your-gmail-account-using-python
# https://cppsecrets.com/users/1102811497104117108109111104116975048484864103109971051084699111109/Check-validity-of-Email-address-using-SMTP-and-dnspython-library.php
