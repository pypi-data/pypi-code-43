from optimeed.core.tools import text_format
import copy


class Options:
    def __init__(self):
        self.options = dict()

    def get_name(self, idOption):
        return self.options[idOption][0]

    def get_value(self, idOption):
        return self.options[idOption][1]

    def add_option(self, idOption, name, value):
        self.options[idOption] = (name, value)

    def set_option(self, idOption, value):
        self.options[idOption] = (self.get_name(idOption), value)

    def copy(self):
        return copy.deepcopy(self)

    def set_self(self, the_options):
        for idOption in the_options.options:
            self.set_option(idOption, the_options.get_value(idOption))

    def __str__(self):
        theStr = ''
        if len(self.options):
            theStr += text_format.BLUE + 'Options'
            for key in self.options:
                theStr += '\n◦ {:<15}'.format(self.get_name(key)) + '\t-\t' + str(self.get_value(key))
            theStr += text_format.END
        return theStr


class Option_class:
    def __init__(self):
        self.Options = Options()

    def get_optionValue(self, optionId):
        return self.Options.get_value(optionId)

    def set_optionValue(self, optionId, value):
        self.Options.set_option(optionId, value)

    def get_all_options(self):
        return self.Options

    def set_all_options(self, options):
        self.Options = options

    def add_option(self, idOption, name, value):
        self.Options.add_option(idOption, name, value)
