from builtins import bytes


def compat_bytes(item, encoding=None):
    if hasattr(item, '__bytes__'):
        return item.__bytes__()
    else:
        if encoding:
            return bytes(item, encoding)
        else:
            return bytes(item)
