import os
import inspect
from .service import Email


class EmailsCollector(Email):
    def __init__(self):
        # # super(EmailsCollector, self).__init__(conn)
        # super().__init__(conn)
        super().__init__()
        pass

    def handle(self):
        try:
            # debug sample
            # print(self._db.get_records('SELECT * FROM some_emails WHERE id BETWEEN %s AND %s', [100, 100]))
            # return

            # empty table
            self._db.execute(f'TRUNCATE {self._TABLE_EMAILS}', commit=True)

            self._db.execute(f'TRUNCATE {self._TABLE_DOMAINS}', commit=True)

            # insert all emails into one
            self.collect(self.get_tables())

            # update `domain` field
            self.set_domain_value(self._TABLE_EMAILS)

            # delete entries without domain
            self._db.execute(f'DELETE FROM {self._TABLE_EMAILS} WHERE domain = "" OR domain IS NULL', commit=True)

            stats = {
                'Total emails': (self._db.get_record(f'SELECT COUNT(*) FROM {self._TABLE_EMAILS}', dict=False)[0]),
                'Total domains': (self._db.get_record(f'SELECT COUNT(DISTINCT domain) FROM {self._TABLE_EMAILS}', dict=False)[0]),
            }

            return stats
        except Exception as error:
            fn = __name__
            fn = os.path.basename(inspect.getframeinfo(inspect.currentframe()).filename)
            ln = inspect.getframeinfo(inspect.currentframe()).lineno
            print(f'ERROR ({fn}:{ln})', error)

    def get_tables(self):
        tables = self._db.get_records('SHOW TABLE STATUS WHERE Name NOT LIKE "\_%"')
        return [list(row.values())[0] for row in tables]

    def collect(self, tables):
        t1 = self._TABLE_EMAILS

        for table in tables:
            query = f'INSERT INTO {t1} (email, weight) SELECT email, weight FROM `{table}` ' \
                    f'WHERE `{table}`.email IS NOT NULL ' \
                    f'ON DUPLICATE KEY UPDATE `{t1}`.times = `{t1}`.times + 1'
            self._db.execute(query, commit=True)

    def set_domain_value(self, table):
        query = f'UPDATE {table} SET domain = ' \
                f'RIGHT(REGEXP_SUBSTR(email, "@.*$"), LENGTH(REGEXP_SUBSTR(email, "@.*$")) - 1);'
        self._db.execute(query, commit=True)

    def get_stats(self):
        query = f'SELECT COUNT(*) FROM {self._TABLE_EMAILS}'
