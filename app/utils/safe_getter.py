def get(entries, key_index, default_value=None):
    """get value safely from list (and/or dict)"""
    try:
        return entries[key_index]
    except:
        return default_value
