def build_sql_where_clause(baseUrl, Params):
    #Build WhereClause
    if len(Params) is not 0:
        baseUrl = baseUrl + ' WHERE '
    i = 0
    for param in Params:
        i = i + 1
        p_1 = str(param[0])
        p_2 = str(param[1])
        p_2 = sql_typeChecking(p_2, str(param[2]))
        p_ = p_1 + p_2
        baseUrl = baseUrl + p_
        if i == len(Params) :
            baseUrl = baseUrl + ';'
            return baseUrl
        else:
            baseUrl = baseUrl + ' AND '
    next
    return baseUrl + ' LIMIT 1000;'


def remove_Params(Params):
    i=0
    while i < len(Params):
        #for param in Params:
        if Params[i][1] == 'null' or None:
            del Params[i]
        else:
            i = i + 1
    return Params


def sql_typeChecking(fieldValue, type):
    #
    if type == 'str':
        fieldValue = '"' + fieldValue + '"'
    if type == 'int':
        fieldValue = fieldValue
    return fieldValue

