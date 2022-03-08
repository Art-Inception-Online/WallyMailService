import argparse
from sys import argv
import time
from pprint import pprint

from config import EmailFilterType
import config
from helpers.init import db
from mail.collector import EmailsCollector
from mail.filter import EmailsFilter
from mail.sender import EmailsSender
from utils.safe_getter import get

start_time = time.time()

if __name__ == '__main__':
    mail_config = config.mail
    # commands = ('--help', '--collect', '--filter', '--send')

    parser = argparse.ArgumentParser(description='How to use instructions',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--channel', metavar='relay', choices=list(config.smtp_channels),
                        help=f'switch smtp channel \npossible values: {list(config.smtp_channels)}\n ')
    parser.add_argument('--collect', action='store_true', help='collect data\n ')
    parser.add_argument('--filter', metavar='', nargs='*',
                        help=f'filter (validate) email entries by several options \n'
                             f'type possible values: {list(EmailFilterType.list())}\n'
                             f'params: type, threads\n ')
    parser.add_argument('--send', metavar='', nargs='*',
                        help=f'send email(s) \nparams: campaign template id, total emails, threads\n'
                             f'default: campaign_id=1, total_emails=1, threads_count=1\n ')

    args = parser.parse_args()

    if args.channel:
        mail_config = config.get_mail_configuration(args.channel)

    if args.collect:
        print('collecting unique emails..')

        pprint(EmailsCollector().handle())

    elif args.filter is not None:
        print('Start filtering emails..')

        first_arg = get(args.filter, 0, EmailFilterType.list()[0])
        filter_type = EmailFilterType(first_arg) if (EmailFilterType.has_value(first_arg)) \
            else EmailFilterType.DOMAIN
        threads_count = int(get(args.filter, 1, 1))

        print(f'filter_type: {filter_type.value}')
        print(f'threads_count: {threads_count}')

        pprint(EmailsFilter(threads=threads_count).handle(filter_by=filter_type))

    elif args.send is not None:
        print('sending emails..')

        campaign_id = int(get(args.send, 0, 1))
        total_send_emails = int(get(args.send, 1, 1))
        threads_count = int(get(args.send, 2, 1))

        print(f'campaign_id: {campaign_id}')
        print(f'total_send_emails: {total_send_emails}')
        print(f'threads_count: {threads_count}')

        EmailsSender(config=mail_config, campaign_id=campaign_id, total_send_emails=total_send_emails,
                     threads=threads_count).handle()

# close connection
# next(db, None)
next(db)
# db.send('close')

# https://stackoverflow.com/a/1557584/1565790
print("--- %s seconds ---" % (int((time.time() - start_time) * 10) / 10))
