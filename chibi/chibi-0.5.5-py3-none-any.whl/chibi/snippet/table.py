def string_table_to_dict( s, row_separator='/n', column_separator=' ' ):
    rows = s.split( row_separator )
    headers = rows.pop(0)
    headers = headers.split( column_separator )
    headers = _clean_empty_strings( headers )


def _clean_empty_strings( l ):
    return [ i for i in l if i ]
