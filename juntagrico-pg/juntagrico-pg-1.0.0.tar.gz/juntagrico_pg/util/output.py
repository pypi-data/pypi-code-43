from texttable import Texttable


def pretty_print(cursor):
    if cursor.description is not None:
        columns = [col[0] for col in cursor.description]
        table = Texttable()
        table.set_cols_align(['l' for x in columns])
        table.set_cols_valign(['m' for x in columns])
        rows = [columns]
        for row in cursor.fetchall():
            parsed_row = [row[x] for x in range(0, len(columns))]
            rows.append(parsed_row)
        table.add_rows(rows)
        return table.draw()
    return ''
