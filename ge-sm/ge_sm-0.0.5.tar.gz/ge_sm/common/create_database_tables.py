from ge_sm.common.database_connection import RedshiftDBConnection
from sqlalchemy import Table, Column, Date, String, BIGINT, Float
import csv


def upload_with_pandas(df, tblname):
    con = RedshiftDBConnection()
    df.to_sql(name = tblname, con = con.engine, index = False, schema = 'chaajaa', if_exists = 'append')

def create_table_from_csv(tblname, fielddefs):
    con = RedshiftDBConnection()
    con.schema = 'chaajaa'
    meta = con.metadata
    tb = Table(tblname, meta)
    # open csv file of field names
    with open('./common/' + fielddefs) as csv_file:
        dtmap = [r for r in csv.reader(csv_file)]
    csv_file.close()
    # conversion dictionary for data dtypes
    typedict = {'date': Date, 'double precision': Float, 'bigint': BIGINT, 'varchar(256)': String,
                'varchar(1000)': String}
    for d in dtmap:
        print(d[0], d[3])
        tb.append_column(Column(d[0], typedict[d[3]]))
    meta.create_all(con.engine)

def delete_all_data(tblname):
    # just get rid of current data in given table
    con = RedshiftDBConnection()
    con.schema = 'chaajaa'
    meta = con.metadata
    tb = Table(tblname, meta)
    con.engine.execute(tb.delete())


if __name__ == '__main__':
    # historic_load(create_table=False, tblname='fb_page_metrics_monthly')
    con = RedshiftDBConnection()
