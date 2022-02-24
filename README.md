# WallyMailService
Wally Mail Service (Gather, Filter, Send emails)

**Gather emails from different table sources**
```python
python main.py collect
```

**Filter valid emails by domain and/or email existence (using SMTP conn)**<br>
*using threads*
```python
python main.py filter
```

**Send emails via SMTP**<br>
*using threads*
```python
python main.py send
```
