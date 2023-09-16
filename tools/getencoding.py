import locale


def getencoding():
    """当python版本小于3.10时使用"""
    if hasattr(locale, "getencoding"):
        return locale.getencoding()

    return locale.getdefaultlocale()[1]
