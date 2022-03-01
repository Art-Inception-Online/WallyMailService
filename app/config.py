import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv('.env')

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

mail = {
    'mailer': os.getenv('MAIL_MAILER'),
    'host': os.getenv('MAIL_HOST'),
    'port': os.getenv('MAIL_PORT'),
    'username': os.getenv('MAIL_USERNAME'),
    'password': os.getenv('MAIL_PASSWORD'),
    'encryption': os.getenv('MAIL_ENCRYPTION'),
    'from_address': os.getenv('MAIL_FROM_ADDRESS'),
    'from_name': os.getenv('MAIL_FROM_NAME'),
    'fake_recipient': os.getenv('MAIL_FAKE_RECIPIENT'),
}


class EmailStatus(Enum):
    DOMAIN_HANDLED = 'domain_handled'
    EMAIL_HANDLING = 'email_handling'
    EMAIL_HANDLED = 'email_handled'

