from sys import argv
import time
from pprint import pprint

from helpers.init import db
from mail.collector import EmailsCollector
from mail.filter import EmailsFilter
from mail.sender import EmailsSender

start_time = time.time()

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
        pprint(EmailsCollector().handle())

    elif command == 'filter':
        print('filtering emails..')
        pprint(EmailsFilter(threads=100).handle(True))

    elif command == 'send':
        print('sending emails..')
        pprint(EmailsSender(campaign_id=1, threads=10, total_send_emails=1).handle())

# close connection
# next(db, None)
next(db)
# db.send('close')

# https://stackoverflow.com/a/1557584/1565790
print("--- %s seconds ---" % (int((time.time() - start_time) * 10) / 10))
