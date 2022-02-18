import os
import inspect
from config import EmailStatus as Status
from email_service import Email
from net_helper import *
from smtp_checker import SMTPChecker
from pprint import pprint


class EmailsFilter(Email):
    def __init__(self):
        super().__init__()
        pass

    def handle(self, filter_by_email_existence=False):
        try:
            # Step1: filter emails by domains
            self.filter_by_domains()

            # Step 2: check each email for existence
            if filter_by_email_existence:
                self.filter_by_email_existence()

            return self.stats()
        except Exception as error:
            fn = __name__
            fn = os.path.basename(inspect.getframeinfo(inspect.currentframe()).filename)
            ln = inspect.getframeinfo(inspect.currentframe()).lineno
            print(f'ERROR ({fn}:{ln})', error)

    def filter_by_domains(self):
        """
        Filter email by valid (existing) domain
        by detecting Host IP or MX Record(s)
        """
        domains = self._db.get_records(f'SELECT domain FROM {self._TABLE_EMAILS} WHERE status IS NULL '
                                       f'GROUP BY domain ORDER BY count(*) DESC '
                                       f'-- LIMIT 0', dict=False)

        for domain, in domains:
            valid = validate_domain(domain)

            # Update related emails with proper `valid` & `status` field values
            query = f'UPDATE {self._TABLE_EMAILS} SET valid = %s, status = %s WHERE domain = %s'
            self._db.execute(query, (None if valid else '0', Status.DOMAIN_HANDLED.value, domain), commit=True)

    def filter_by_email_existence(self):
        """
        Filter emails for existence on mail server
        """

        raise Exception('Not implemented')

        emails = self._db.get_records(f'SELECT email FROM {self._TABLE_EMAILS} WHERE valid IS NULL '
                                      f'ORDER BY weight DESC, email DESC '
                                      f' LIMIT 1', dict=False)

        for email, in emails:
            is_valid = SMTPChecker(debug=0, timeout=1, max_iteration=5).validate(email)
            print(f'{email} is valid: {is_valid}')

    def stats(self):
        return {
            'Total valid emails':
                (self._db.get_record(f'SELECT COUNT(*) FROM {self._TABLE_EMAILS} '
                                     f'WHERE valid <> 0 OR valid IS NULL', dict=False)[0]),
            'Total valid domains':
                (self._db.get_record(f'SELECT COUNT(DISTINCT domain) FROM {self._TABLE_EMAILS} '
                                     f'WHERE valid <> 0 OR valid IS NULL', dict=False)[0]),
        }
