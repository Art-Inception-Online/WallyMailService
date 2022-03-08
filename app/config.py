import os
import pprint

from dotenv import load_dotenv
from enum import Enum

from utils.enum_extended import EnumExtended

load_dotenv('app/.env')

# https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
db = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE'),
    'raise_on_warnings': os.getenv('DB_RAISE_ON_WARNINGS').lower() in ('true', '1', 't'),
    'get_warnings': os.getenv('DB_GET_WARNINGS').lower() in ('true', '1', 't'),
    'raw': os.getenv('DB_RAW').lower() in ('true', '1', 't'),
    'autocommit': os.getenv('DB_AUTOCOMMIT').lower() in ('true', '1', 't'),
}

# load all smtp configurations
smtp_channels = {}

for i in range(1, 4):
    __mailer = os.getenv(f'MAIL_{i}_MAILER')

    smtp_channels[__mailer] = {
        'mailer': __mailer,
        'host': os.getenv(f'MAIL_{i}_HOST'),
        'port': os.getenv(f'MAIL_{i}_PORT'),
        'username': os.getenv(f'MAIL_{i}_USERNAME'),
        'password': os.getenv(f'MAIL_{i}_PASSWORD'),
        'encryption': os.getenv(f'MAIL_{i}_ENCRYPTION'),
        'from_address': os.getenv(f'MAIL_{i}_FROM_ADDRESS'),
        'from_name': os.getenv(f'MAIL_{i}_FROM_NAME'),
    }

default_smtp_channel = os.getenv('DEFAULT_MAILER') if os.getenv('DEFAULT_MAILER') else list(smtp_channels)[0]


def get_mail_configuration(channel):
    return {
        **smtp_channels[channel],
        'fake_recipient': os.getenv('MAIL_FAKE_RECIPIENT'),
    }


mail = get_mail_configuration(default_smtp_channel)

mailgun_api_key = os.getenv('MAILGUN_API_KEY')


class EmailStatus(Enum):
    DOMAIN_HANDLED = 'domain_handled'
    EMAIL_HANDLING = 'email_handling'
    EMAIL_HANDLED = 'email_handled'


class EmailFilterType(EnumExtended):
    DOMAIN = 'domain'
    SMTP = 'smtp'
    API = 'api'
    EVENTS = 'events'
