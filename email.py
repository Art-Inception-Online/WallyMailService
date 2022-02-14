class Email:
    _TABLE_EMAILS = '_emails'

    def __init__(self, conn):
        self._conn = conn

    def execute_query(self, query):
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute(query)

        # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html
        self._conn.commit()

        # https: // dev.mysql.com / doc / connector - python / en / connector - python - api - mysqlconnection -
        # rollback.html
        # self.__conn.rollback()

        cursor.close()

    pass
