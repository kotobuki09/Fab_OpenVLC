class ValueDoc:

    def __init__(self):
        self.text = text
        pass

    def __repr__(self):
        return self.text


class Attribute(ValueDoc):
    def __init__(self, key, type, isReadOnly):
        self.key = key
        self.type = type
        self.isReadOnly = isReadOnly
        self.text = "Attribute(key={}, type={}, isReadonly={})".format(str(self.key), str(self.type), self.isReadOnly)


class Measurement(ValueDoc):
    def __init__(self, key, type):
        self.key = key
        self.type = type
        self.text = "Measurement(key={}, type={})".format(str(self.key), str(self.type))


class Event(ValueDoc):
    def __init__(self, key, type):
        self.key = key
        self.type = type
        self.text = "Event(key={}, type={})".format(str(self.key), str(self.type))


class Action(ValueDoc):
    def __init__(self, key, args_types, return_type):
        self.key = key
        self.args_types = args_types
        self.return_type = return_type
        self.text = "Action(key={}, args_types={}, return_type={})".format(str(self.key), str(self.args_types), self.return_type)
