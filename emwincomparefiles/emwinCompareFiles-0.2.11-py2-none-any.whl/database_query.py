#!/usr/bin/python
#
# This script will query the edpdb database and save the 
# output to a file. 
#
import datetime
import psycopg2
from psycopg2 import Error
from psycopg2 import sql

print("Running database_query.py\n")

def check_date(userInput):
    try:
        date = datetime.datetime.strptime(userInput, '%m-%d-%Y').strftime('%m-%d-%Y')
    except ValueError:
        raise ValueError("Date format should be MM-DD-YYYY")
    return date

#Ask user for input
date1 = check_date(raw_input("Enter query Start date as MM-DD-YYYY (Should be the day Legacy data was collected): "))
date2 = check_date(raw_input("Enter query End date as MM-DD-YYYY (Two days after Legacy data was collected): "))

#userInput1 = raw_input("Enter query Start date as MM-DD-YYYY (Should be the day Legacy data was collected): ")
#userInput2 = raw_input("Enter query End date as MM-DD-YYYY (Two days after Legacy data was collected): ")
#
#try:
#    date1 = datetime.datetime.strptime(userInput1, '%m-%d-%Y').strftime('%m-%d-%Y')
#    date2 = datetime.datetime.strptime(userInput2, '%m-%d-%Y').strftime('%m-%d-%Y')
#except ValueError:
#    raise ValueError("Date format should be MM-DD-YYYY")

# Connect to the database 

try:
    # ------ DEV ------
    #connection = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-dev.cprk.ncep.noaa.gov' password='JaQy2p5z'")
    #connection = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-dev.bldr.ncep.noaa.gov' password='JaQy2p5z'")
    # ------- QA -------
    #connection = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-qa.cprk.ncep.noaa.gov' password='abcvedf2w'")
    #connection = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-qa.bldr.ncep.noaa.gov' password='abcvedf2w'")
    # ------ OPS ------
    connection = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-op.cprk.ncep.noaa.gov' password='abcvedf2w'")
    print "Successfully connected to the database "
except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while connecting to database: ", error)

print(date1)
print(date2)

# Define a cursor to work with
# Points to a specific row within the query result
# A read-only attribute describing the result of a query; a sequence of column instances
cur = connection.cursor()

                #WHERE (event.eventtype_id = 9) and (event.endtime > {dtStart} AND event.endtime < {dtEnd})                     -- eventtype_id = 9 means product has been ingested
# Query excludes image products
print "Running query..."
queryStmt = """COPY (WITH event_reduced AS (                                                                                   -- copy output to file
                SELECT event.nwwproduct_uuid                                                                                   -- WITH creates auxillary table to use later
                FROM edp.event                                                                                                 -- queries "event" table
                WHERE (event.eventtype_id = 9) and (event.endtime > {dtStart} AND event.endtime <= {dtEnd})                     -- eventtype_id = 9 means product has been ingested
                ), product_reduced AS ( 
                SELECT nwwproduct_uuid, nwwproduct.checksum , nwwproduct.esb_timestamp, nwwproduct.datatype_ttaaii,            -- datatypes make up WMO header
                       nwwproduct.datatype_cccc, nwwproduct.datatype_nnn, nwwproduct.datatype_yygggg, nwwproduct.received_via, 
                       CAST((regexp_replace(nwwproduct.message_content, '[\n]+', ' ', 'g' )) AS VARCHAR(34))                   -- message_content becomes a 34 character length variable (for output)
                FROM edp.nwwproduct                                                                                            -- queries "nwwproduct" table 
                WHERE (nwwproduct.received_via != 'WEBIMG') and (nwwproduct.esb_timestamp > {dtStart} AND nwwproduct.esb_timestamp <= {dtEnd}) -- exlcuding WEBIMG products for now
                ) 
            SELECT DISTINCT ON (checksum) product_reduced.esb_timestamp, product_reduced.datatype_ttaaii,                      -- exclude duplicates by checking file checksum 
                 product_reduced.datatype_cccc, product_reduced.datatype_nnn, product_reduced.datatype_yygggg, 
		 product_reduced.received_via, product_reduced.regexp_replace, product_reduced.checksum
            FROM product_reduced, event_reduced 
            WHERE event_reduced.nwwproduct_uuid = product_reduced.nwwproduct_uuid                                              -- verify products match by comparing uuid
            ) TO STDOUT WITH CSV HEADER                                                                                        -- copy to CSV file
            """                                                                                     

query = sql.SQL(queryStmt).format(dtStart=sql.Literal(date1), dtEnd=sql.Literal(date2))

with open('Database_Query.csv', 'w') as file1:
    cur.copy_expert(query, file1)
print "CSV file created.\n"
