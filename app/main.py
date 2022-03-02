from sys import argv
import time
from pprint import pprint

from config import EmailFilterType
from helpers.init import db
from mail.collector import EmailsCollector
from mail.filter import EmailsFilter
from mail.sender import EmailsSender
from utils.safe_getter import get

start_time = time.time()

if __name__ == '__main__':
    commands = ('--help', '--collect', '--filter', '--send')

    command = None if (len(argv) < 2) else (argv[1] if argv[1] in commands else None)

    if not command:
        print('\nPlease provide proper command or type --help')

    elif command == '--help':
        print('collect     : Collect unique emails into one table')
        print('filter      : Filter collected emails if valid')
        print('send        : Send emails')

    elif command == '--collect':
        print('collecting unique emails..')
        pprint(EmailsCollector().handle())

    elif command == '--filter':
        print('Start filtering emails..')

        filter_type = EmailFilterType(get(argv, 2)) if (EmailFilterType.has_value(get(argv, 2))) \
            else EmailFilterType.DOMAIN
        threads_count = int(get(argv, 3, 1))

        print(f'filter_type: {filter_type.value}')
        print(f'threads_count: {threads_count}')

        pprint(EmailsFilter(threads=threads_count).handle(filter_by=filter_type))

    elif command == '--send':
        campaign_id = int(get(argv, 2, 1))
        total_send_emails = int(get(argv, 3, 1))
        threads_count = int(get(argv, 4, 1))

        print('sending emails..')
        print(f'campaign_id: {campaign_id}')
        print(f'total_send_emails: {total_send_emails}')
        print(f'threads_count: {threads_count}')

        EmailsSender(campaign_id=campaign_id, total_send_emails=total_send_emails, threads=threads_count).handle()

# close connection
# next(db, None)
next(db)
# db.send('close')

# https://stackoverflow.com/a/1557584/1565790
print("--- %s seconds ---" % (int((time.time() - start_time) * 10) / 10))
