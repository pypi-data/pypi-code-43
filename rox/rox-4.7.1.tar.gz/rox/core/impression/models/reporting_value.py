class ReportingValue(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return '%s - %s %s' % (super(ReportingValue, self).__str__(), self.name, self.value)
