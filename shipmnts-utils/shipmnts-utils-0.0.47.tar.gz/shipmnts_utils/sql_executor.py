from django.db import connection


def execute_select_query(query, output_format='tuple', fetch=None):
    tuple_data, json_data = None, None
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        if fetch and fetch == "one":
            tuple_data = cursor.fetchone()
        else:
            tuple_data = cursor.fetchall()
    finally:
        cursor.close()
        if output_format=='json':
            if tuple_data:
                if fetch=="one":
                    tuple_data = [tuple_data]
                json_data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in
                            tuple_data]
            return json_data
        return tuple_data

def execute_update_query(query):
   c = connection.cursor()
   data = None
   try:
       c.execute(query)
       connection.commit()
       data = c.fetchone()
   except:
        connection.rollback()
   finally:
       c.close()
       return data

