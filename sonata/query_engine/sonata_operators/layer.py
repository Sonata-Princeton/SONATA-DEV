class Proto(object):
    __slot__ = ["name", "fields"]

    def __int__(self, name, fields):
        self.name = name
        self.fields = fields


class IP(Proto)