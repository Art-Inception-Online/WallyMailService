import json
import os
import re
import uuid
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import utils
import smtplib
from typing import Dict

from app.config import mail as config

# html might contain src attr on a new line
image_source_pattern = r'(<img.*\n*.*src=")([^(http?s:)][^\'"]*)'
image_source_placeholder = '{cid}'


def send(to, subject, body_html, body_text_plain='', user_variables: Dict = {}, debug_level=0):
    to = to if not config['fake_recipient'] else config['fake_recipient']

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = utils.formataddr((config['from_name'], config['from_address']))
    msg['To'] = to
    msg['Date'] = utils.formatdate(localtime=1)
    msg['Message-ID'] = utils.make_msgid()

    user_variables['message-id'] = utils.make_msgid().strip('<>')
    msg.add_header('X-Mailgun-Variables', json.dumps(user_variables))

    body_html = __prepare_message(msg, body_html)
    body = MIMEText(body_html, "html", _charset="utf-8")
    msg.attach(body)

    if body_text_plain:
        msg.attach(MIMEText(body_text_plain, "txt", _charset="utf-8"))

    # return msg

    with smtplib.SMTP(host=config['host'], port=config['port']) as smtp:
        smtp.set_debuglevel(debug_level)

        ehlo_host = config['from_address'].split("@")[1]
        smtp.ehlo(ehlo_host)

        # smtp.ehlo()

        if config['encryption'] == 'tls':
            try:
                smtp.starttls()
            except:
                pass

        if config['username']:
            try:
                smtp.login(config['username'], config['password'])
            except:
                pass

        # smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        smtp.send_message(msg)
        # smtp.quit()

    return msg


def __prepare_message(msg: MIMEMultipart, message):
    # prepare inline images
    image_sources = get_image_sources(message)

    message = __replace_image_sources_with_placeholder(message)

    for image_source in image_sources:
        # image path should be relative to the project root!!!
        image_id, image_attachment = get_image_attachment(f'../{image_source}')

        msg.attach(image_attachment)

        message = re.sub(image_source_placeholder, image_id, message, 1)

    return message


def __replace_image_sources_with_placeholder(message):
    """replace all of them with: cid:{cid}"""
    return re.sub(image_source_pattern, rf'\1cid:{image_source_placeholder}', message)


def get_image_sources(message):
    """find all inline image sources"""
    return [x[1] for x in re.findall(image_source_pattern, message, flags=re.IGNORECASE | re.MULTILINE)]


def get_image_attachment(path):
    try:
        with open(path, 'rb') as file:
            _uuid = uuid.uuid4()
            msg_image = MIMEImage(file.read(), name=os.path.basename(path))
            msg_image.add_header('Content-ID', '<{}>'.format(_uuid))
            return str(_uuid), msg_image
    except FileNotFoundError as error:
        # print(type(error))
        print(f'ERROR (get_image_attachment): {error}')
