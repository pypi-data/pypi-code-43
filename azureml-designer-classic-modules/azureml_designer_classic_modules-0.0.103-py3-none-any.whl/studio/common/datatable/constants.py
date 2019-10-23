class ColumnTypeName:
    NUMERIC = "Numeric"
    STRING = "String"
    BINARY = "Binary"
    OBJECT = "Object"
    CATEGORICAL = "Categorical"
    DATETIME = 'DateTime'
    TIMESPAN = 'TimeSpan'
    NAN = "NAN"


class ElementTypeName:
    INT = 'int64'
    FLOAT = 'float64'
    STRING = 'str'
    BOOL = 'bool'
    OBJECT = 'object'
    CATEGORY = 'category'
    DATETIME = 'datetime64'
    TIMESPAN = 'timedelta64'
    NAN = 'NAN'
    UNCATEGORY = 'uncategory'
    CONVERTABLE_LIST = [INT, FLOAT, STRING, BOOL, OBJECT, CATEGORY]
    NUMERIC_LIST = [INT, FLOAT, BOOL]
