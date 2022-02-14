import mysql.connector
import config

cnx, error = None, None


def db():
    global cnx
    global error

    def init():
        """NOTE:
        Exception must be handled locally,
        otherwise .send(..) will not work!!!
        """

        global cnx
        global error

        try:
            # print('DB connecting..')
            cnx = mysql.connector.connect(**config.db)
            # print('DB connected.')

            # set auto commit false
            # print(f'autocommit is: {cnx.autocommit}')

            # cnx.cursor().execute('SET AUTOCOMMIT = 0;')

        except Exception as e:
            cnx = None
            error = e
            pass

        return cnx, error

    def close():
        # yield cnx.close()
        cnx.close()
        # print('DB Connection closed.')

    i = init()

    while True:
        val = (yield i)

        if val == 'restart':
            i = init()
        elif val == 'close' or val == None:
            i = close()
            pass
