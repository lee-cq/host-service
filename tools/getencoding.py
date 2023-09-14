import locale
import sys


def getencoding():
    """当python版本小于3.10时使用"""
    if sys.version_info.major == 3 and sys.version_info.minor <= 10:
        return locale.getdefaultlocale()[1]
    else:
        return locale.getencoding()
