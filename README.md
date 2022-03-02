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

**Gather data from different sources**
```python
python app/main.py --collect
```

**Filter valid emails by domain and/or email existence (using SMTP connection)**<br>
*uses threads*
```python
python app/main.py --filter
```

**Send emails via SMTP**<br>
*uses threads*
```python
python app/main.py --send

# define campaign template
python app/main.py --send 1

# define campaign template & total emails should be sent
python app/main.py --send 1 100

# define campaign template & total emails should be sent & total threads should be used
python app/main.py --send 1 100 25
```
