from sys import argv
import time
from db_connection import db
from emails_collector import EmailsCollector

reset = False
db = db()
conn = None

# Restart connection attempt permanently
while True:
    try:
        conn, error = next(db) if not reset else db.send('restart')

        if not conn:
            raise Exception(error)

        break
    except Exception as error:
        # print("ERROR: Database connection failed")
        print("ERROR", error)

        reset = True

        print("")
        time.sleep(5)

# print(conn)
# # print(next(cnx))
# cursor = conn.cursor(dictionary=True)
# query = ("SELECT NOW() as time_now")
# cursor.execute(query)
# print(cursor.fetchone())
# # print(cnx)


if __name__ == '__main__':
    # print('arguments: ', argv)

    commands = ('--help', 'collect', 'filter', 'send')

    command = None if (len(argv) < 2) else (argv[1] if argv[1] in commands else None)

    if not command:
        print('\nPlease provide proper command or type --help')

    elif command == '--help':
        print('collect     : Collect unique emails into one table')
        print('filter      : Filter collected emails if valid')
        print('send        : Send emails')

    elif command == 'collect':
        print('collecting unique emails..')
        EmailsCollector(conn).handle()

    elif command == 'filter':
        print('filtering emails..')

    elif command == 'send':
        print('sending emails..')

# close connection
# next(db, None)
next(db)
# db.send('close')
