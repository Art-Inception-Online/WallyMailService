# WallyMailService
Wally Mail Service (Gather, Filter, Send emails)

**Gather emails from different table sources**

### Usage

**Prepare virtual environment**
```shell
python -m venv .venv
```

**Activate virtual environment**
```shell
# *nix
source ./.venv/bin/activate
# win
.\.venv\scripts\activate.bat
```

**Install requirements**
```shell
pip install -r requirements.txt
```

### Commands

**Help**
```shell
$ python app/main.py --help
```

The output might look like:
```shell
usage: main.py [-h] [--channel relay] [--collect] [--filter [...]] [--send [...]]

How to use instructions

optional arguments:
  -h, --help       show this help message and exit
  --channel relay  switch smtp channel
                   possible values: ['mailgun', 'sendgrid', 'sendinblue', 'mandrillapp', 'mailjet']

  --collect        collect data

  --filter [ ...]  filter (validate) email entries by several options
                   type possible values: ['domain', 'smtp', 'api', 'events']
                   params: type, threads

  --send [ ...]    send email(s)
```

**Gather data from different source collection**
```python
python app/main.py --collect
```

**Filter (verify) valid emails by domain and/or email existence (using SMTP connection)**<br>
*uses threads*
```python
# filter emails by valid domain (checking for existing MX record
python app/main.py --filter domain

# filter emails by webhook responses (sendgrid, mailgun)
python app/main.py --filter events

# filter emails using smtp communication response
python app/main.py --filter smtp

# using 10 threads
python app/main.py --filter smtp 10
```

**Filter (verify) emails via Mailgun API**<br>
*uses threads*
```python
python app/main.py --filter api

# using thread
python app/main.py --filter api 10
```

**Send emails via SMTP**<br>
*uses threads*
```python
# send first campaign template message to one single email
python app/main.py --send

# send by switching smtp relay via additional option
python app/main.py --send --channel mailgun
python app/main.py --send 1 --channel sendgrid

# define campaign template
python app/main.py --send 1

# define campaign template & total emails should be sent
python app/main.py --send 1 100

# define campaign template & total emails should be sent & total threads should be used
python app/main.py --send 1 100 25
```
