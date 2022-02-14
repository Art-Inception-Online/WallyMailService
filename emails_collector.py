import os
import inspect
from email import Email


class EmailsCollector(Email):
    def __init__(self, conn):
        # super(EmailsCollector, self).__init__(conn)
        super().__init__(conn)
        pass

    def handle(self):
        try:
            # empty table
            self.execute_query(f'TRUNCATE {self._TABLE_EMAILS}')

            # insert all emails into one
            self.collect(self.get_tables())

            # update `domain` field
            self.set_domain_value(self._TABLE_EMAILS)

            # return stats

        except Exception as error:
            fn = __name__
            fn = os.path.basename(inspect.getframeinfo(inspect.currentframe()).filename)
            ln = inspect.getframeinfo(inspect.currentframe()).lineno
            print(f'ERROR ({fn}:{ln})', error)

    def get_tables(self):
        # WORKING Query (displays correctly):
        #   SHOW TABLES LIKE '\_%'

        # INVALID Query:
        #   SHOW TABLES NOT LIKE '\_%'

        # NOT working MySQL query properly:
        #   SHOW TABLES WHERE 'Tables_in_<table-name>' LIKE '\_%'

        # INVALID Query:
        #   SHOW TABLES WHERE 'Tables_in_<table-name>' LIKE '\_%' ESCAPE '\'

        # WORKING QUERY
        #    SHOW TABLE STATUS WHERE Name NOT LIKE "\_%";

        # cursor = self.__conn.cursor(dictionary=True)
        cursor = self._conn.cursor()
        # query = 'SHOW TABLES'
        # DEBUG VERSION
        query = 'SHOW TABLE STATUS WHERE Name NOT LIKE "\_%" AND Name LIKE "mbox_emails"'
        # query = "SHOW TABLE STATUS WHERE Name NOT LIKE '\_%'"
        cursor.execute(query)
        # print(cursor.fetchone())

        # for row in cursor:
        #     print(row)

        tables = list()

        for table, *others in cursor:
            if table[0] == '_':
                continue

            tables.append(table)

        return tables

    def collect(self, tables):
        t1 = self._TABLE_EMAILS

        for table in tables:
            query = f'INSERT INTO {t1} (email, weight) SELECT email, weight FROM {table} ' \
                    f'ON DUPLICATE KEY UPDATE `{t1}`.times = `{t1}`.times + 1'
            self.execute_query(query)

    def set_domain_value(self, table):
        query = f'UPDATE {table} SET domain = ' \
                f'RIGHT(REGEXP_SUBSTR(email, "@.*$"), LENGTH(REGEXP_SUBSTR(email, "@.*$")) - 1);'
        self.execute_query(query)

    def get_stats(self):
        query = f'SELECT COUNT(*) FROM {self._TABLE_EMAILS}'
