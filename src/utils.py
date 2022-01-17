class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class StringUtils(object):

    @staticmethod
    def init_caps(s):
        return s[0].upper() + s[1:]

    @staticmethod
    def clean(s):
        if not s:
            return ""
        return str(s).replace("-", " ").strip().lower()