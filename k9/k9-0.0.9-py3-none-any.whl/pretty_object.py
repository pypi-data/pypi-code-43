
class PrettyObject:
    """
    Prints in an easily readable, simplified, JSON format.  It allows customization of how big dictionaries,
    lists, sets and tuples can be before they are dropped to the next line.

    Note that this is a very relaxed JSON format, and is syntactly incorrect.  You'll want to 
    use **pprint** if you need strict JSON formatted output.
    """

    # Establishes size that list structures would extend
    # to line by line display

    dictLimit  = 1   #: max number of dictionary entries on a single line, default is 1
    listLimit  = 1   #: max number of list items on a single line, default is 1
    setLimit   = 1   #: max number of items in a set on a single line, default is 1
    tupleLimit = 1   #: max number of items in a tuple on a single line, default is 1

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
        """
        Prints an object in a simplified JSON format for easy viewing.  Note that if you need
        syntactically correct JSON, you should use **pprint** instead.

        :param obj: The object to print, can be either list or dictionary.

        Example::

            po = PrettyObject()

            obj = [
                {"Name": "default-vpc", "VpcId": "vpc-2eb67c54", "CidrBlock": "172.31.0.0/16", "IsDefault": True, "State": "available"},
                {"Name": "dvl-vpc", "VpcId": "vpc-422314113412", "CidrBlock": "10.0.0.0/16", "IsDefault": False, "State": "pending"}
            ]
            po.print(obj)

        Output::

            [
                {
                    Name: "default-vpc"
                    VpcId: "vpc-2eb67c54"
                    CidrBlock: "172.31.0.0/16"
                    IsDefault: True
                    State: "available"
                }
                {
                    Name: "dvl-vpc"
                    VpcId: "vpc-422314113412"
                    CidrBlock: "10.0.0.0/16"
                    IsDefault: False
                    State: "pending"
                }
            ]

        """
        print(self.string(obj))

    def print_table(self, obj):
        """
        Prints a list of dictionary objects in a table format.

        :param obj: A list of dictionary objects.

        Example::

            po = PrettyObject()

            obj = [
                {"Name": "default-vpc", "VpcId": "vpc-2eb67c54", "CidrBlock": "172.31.0.0/16", "IsDefault": True, "State": "available"},
                {"Name": "dvl-vpc", "VpcId": "vpc-422314113412", "CidrBlock": "10.0.0.0/16", "IsDefault": False, "State": "pending"}
            ]
            po.print_table(obj)

        Output::

            Name         VpcId             CidrBlock      IsDefault  State
            -----------  ----------------  -------------  ---------  ---------
            default-vpc  vpc-2eb67c54      172.31.0.0/16  True       available
            dvl-vpc      vpc-422314113412  10.0.0.0/16    False      pending
        """
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
    if value:
        return 'True'
    else:
        return ''

