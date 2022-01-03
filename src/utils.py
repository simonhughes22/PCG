class Singleton(object):
    __instance = None
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args)
        return cls.__instance

class StringUtils(object):

    @staticmethod
    def init_caps(s):
        return s[0].upper() + s[1:]

    @staticmethod
    def clean(s):
        if not s:
            return ""
        return str(s).replace("-", " ").strip().lower()