from init import conn


class Database(object):
    __cursor = None

    def execute(self, query, params: tuple = (), fetch_one=False, fetch_all=False, return_dict=True, commit=False):
        print('query: ', query)

        self.__cursor = conn.cursor(dictionary=return_dict)
        self.__cursor.execute(query, params)

        if commit:
            self.commit()

        if fetch_one:
            return self.__cursor.fetchone()

        if fetch_all:
            return self.__cursor.fetchall()

    def get_record(self, query, params: tuple = (), return_dict=True, commit=True):
        return self.execute(query, params, fetch_one=True, return_dict=return_dict, commit=False)

    def get_records(self, query, params: tuple = (), return_dict=True, commit=True):
        return self.execute(query, params, fetch_all=True, return_dict=return_dict, commit=False)

    def commit(self):
        conn.commit()

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
