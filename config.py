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


class EmailStatus(Enum):
    DOMAIN_HANDLED = 'domain_handled'
    EMAIL_HANDLING = 'email_handling'
    EMAIL_HANDLED = 'email_handled'

