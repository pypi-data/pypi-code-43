
class PrettyObject:

    # Establishes size that list structures would extend
    # to line by line display
    dictLimit  = 1
    listLimit  = 1
    setLimit   = 1
    tupleLimit = 1

    INDENT = "    "

    def pretty_dict(self, obj: dict, indent=""):
        if len(obj) < self.dictLimit:
            return self.pretty_dict_line(obj, indent)

        result = "{\n"
        for key in obj:
            result += indent + self.INDENT + key + ": ";
            result += self.string(obj[key], indent + self.INDENT) + "\n"

        result += indent + "}"
        return result

    def pretty_dict_line(self, obj: dict, indent=""):
        if len(obj) == 0:
            return "{}"

        first = True
        result = "{"
        for key in obj:
            if not first:
                result += ", "
            first = False
            result += key + ": ";
            result += self.string(obj[key], indent)

        result += "}"
        return result

    def pretty_list(self, obj, indent=""):
        if len(obj) < self.listLimit:
            return self.pretty_list_line(obj, indent)

        result = "[\n"
        for item in obj:
            result += indent + self.INDENT + self.string(item, indent + self.INDENT) + "\n"

        result += indent + "]"
        return result

    def pretty_list_line(self, obj, indent=""):
        if len(obj) == 0:
            return "[]"

        first = True;
        result = "["
        for item in obj:
            if not first:
                result += ", "
            first = False
            result += self.string(item, indent)

        result += "]"

        return result

    def pretty_tuple(self, obj, indent=""):
        if len(obj) < self.listLimit:
            return self.pretty_tuple_line(obj, indent)

        result = "(\n"
        for item in obj:
            result += indent + self.INDENT + self.string(item, indent + self.INDENT) + "\n"

        result += indent + ")"
        return result

    def pretty_tuple_line(self, obj, indent=""):
        if len(obj) == 0:
            return "()"

        first = True;
        result = "("
        for item in obj:
            if not first:
                result += ", "
            first = False
            result += self.string(item, indent)

        result += ")"

        return result

    def string(self, obj, indent=""):
        if isinstance(obj, dict):
            return self.pretty_dict(obj, indent)

        if isinstance(obj, list):
            return self.pretty_list(obj, indent)

        if isinstance(obj, tuple):
            return self.pretty_tuple(obj, indent)

        if isinstance(obj, str):
            return '"' + obj + '"'

        else:
            return str(obj)

    def print(self, obj):
        print(self.string(obj))

    def print_table(self, obj):
        if not isinstance(obj, list):
             print("Object is not a table:")
             self.print(obj)
             return

        # Capture stats on the table
        lengths = {}
        order = []
        for record in obj:
            for key in record:
                value  = str(record[key])
                length = len(value)

                if not key in lengths:
                    keylen = len(key)
                    if keylen > length:
                        length = keylen

                    lengths.update({key: length})
                    order.append(key)
                    continue

                if lengths[key] < length:
                    lengths.update({key: length})

        # Print the header
        line = ""
        for key in order:
            line += key.ljust(lengths[key])
            line += "  "
        print(line)

         # Print underline
        line = ""
        for key in order:
            line += "".ljust(lengths[key], '-')
            line += "  "
        print(line)

        # Print table content
        for record in obj:
            line = ""
            for key in order:
                if key in record:
                    value = str(record[key])
                else:
                    value = ""
                line += value.ljust(lengths[key]+2)

            print(line)


def get_tags(tag):
    result = {}
    for vpair in tag:
        result.update({vpair.get('Key'): vpair.get('Value')})

    return result


def get_tag(tags, key):
    for vpair in tags:
        if vpair['Key'] == key:
            return vpair['Value']
    return ""

def get_name(tags):
    if tags is None:
        return ''
    for vpair in tags:
        if vpair['Key'] == 'Name':
            return vpair['Value']
    return ''

def get_true(value):
    '''For easy viewing, only display True'''

    if value:
        return 'True'
    else:
        return ''

