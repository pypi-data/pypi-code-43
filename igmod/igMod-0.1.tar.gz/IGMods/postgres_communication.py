import psycopg2
from postgres_quaries import *

#conn = psycopg2.connect("dbname=insta user=postgres password=CQlR+nein1_p")
#cur = conn.cursor()
def posgres_leave():
    conn.commit()
    cur.close()
    conn.close()

SELECT_FROM_PROFILE_WHERE_NAME = "SELECT * FROM profiles WHERE name = :name"
INSERT_INTO_PROFILE = "INSERT INTO profiles (name) VALUES (?)"



def sqlexecuter(BEFEHL):
    cur.execute(BEFEHL)
#sqlexecuter(SQL_CREATE_PROFILE_TABLE)
#sqlexecuter(SQL_CREATE_DETAILED_ACCOUNT)
#posgres_leave()