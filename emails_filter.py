import os
import inspect
from config import EmailStatus as Status
from email import Email
from pprint import pprint
from net_helper import get_host_by_name, get_mx_records


class EmailsFilter(Email):
    def __init__(self):
        super().__init__()
        pass

    def handle(self):
        try:
            # Step1: filter emails by domains
            self.filter_by_domains()

            stats = {
                'Total valid emails': (self._db.get_record(f'SELECT COUNT(*) FROM {self._TABLE_EMAILS} '
                                                           f'WHERE valid <> "0"', dict=False)[0]),
                'Total valid domains': (self._db.get_record(f'SELECT COUNT(DISTINCT domain) FROM {self._TABLE_EMAILS} '
                                                            f'valid <> "0"', dict=False)[0]),
            }

            return stats
        except Exception as error:
            fn = __name__
            fn = os.path.basename(inspect.getframeinfo(inspect.currentframe()).filename)
            ln = inspect.getframeinfo(inspect.currentframe()).lineno
            print(f'ERROR ({fn}:{ln})', error)

    def filter_by_domains(self):
        """
        Filter emails by valid (existing) domain
        by detecting Host IP or MX Record(s)
        """
        domains = self._db.get_records(f'SELECT domain FROM {self._TABLE_EMAILS} WHERE status IS NULL '
                                       f'GROUP BY domain ORDER BY count(*) DESC '
                                       f'-- LIMIT 0', dict=False)

        for domain, in domains:
            print(f'{domain}'.ljust(25), end='')

            # get domain ip or mx records
            ip = get_host_by_name(domain)

            valid = None

            if not ip:
                print('!get_host_by_name'.ljust(20), end='')
                if not get_mx_records(domain):
                    print('!get_mx_records'.ljust(20), end='')

                    valid = '0'
            else:
                print(f'{ip}', end='')

            # Update related emails with proper `valid` & `status` field values
            query = f'UPDATE {self._TABLE_EMAILS} SET valid = %s, status = %s WHERE domain = %s'
            self._db.execute(query, (valid, Status.DOMAIN_HANDLED.value, domain), commit=True)

            print()

    def filter_by_email_existence(self):
        pass
