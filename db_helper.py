from init import conn


class Database(object):
    def __init__(self, dictionary=True):
        self.__cursor = conn.cursor(dictionary=dictionary)

    def execute(self, query, params: tuple = (), fetch_one=False, fetch_all=False):
        self.__cursor.execute(query, params)

        if fetch_one:
            return self.__cursor.fetchone()

        if fetch_all:
            return self.__cursor.fetchall()

    def get_record(self, query, params: tuple = ()):
        return self.execute(query, params, fetch_one=True)

    def get_records(self, query, params: tuple = ()):
        print('query: ', query)
        return self.execute(query, params, fetch_all=True)

    def __del__(self):
        self.__cursor.close()


# def execute_query(query, params: tuple = (), single_record=True):
#     print(query)
#
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute(query)
#
#     # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html
#     conn.commit()
#
#     # https: // dev.mysql.com / doc / connector - python / en / connector - python - api - mysqlconnection -
#     # rollback.html
#     # conn.rollback()
#
#     cursor.close()


# SAMPLE
# def get_records(self, query, params: tuple = ()):
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute(query, params)
#     return cursor.fetchall()
