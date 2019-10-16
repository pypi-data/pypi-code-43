import psycopg2, time, os, json
from pandas import DataFrame
from foqus.configuration import *
from ip2geotools.databases.noncommercial import DbIpCity
import logging
import coloredlogs

if LOCAL is False:

    from azure_storage_logging.handlers import TableStorageHandler

    # configure the handler and add it to the logger
    logger = logging.getLogger(__name__)
    handler = TableStorageHandler(account_name=LOG_AZURE_ACCOUNT_NAME,
                                  account_key=LOG_AZURE_ACCOUNT_KEY,
                                  extra_properties=('%(hostname)s',
                                                    '%(levelname)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
else:

    logger = logging.getLogger(__name__)
    coloredlogs.install()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_PATH + 'trynfit_debug.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s', '%d/%b/%Y %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

table_name = DATABASE_USERS_MANAGEMENT_TABLE_NAME

def get_client_code_country(adress):
    if adress == "":
        code_country = ""
    elif adress == "127.0.0.1" or "192.168.100" in adress:
        code_country = "fr"
    else:
        response = DbIpCity.get(adress, api_key='free')
        code_country = response.country
        code_country =code_country.lower()
        logger.info(" The code country is %s" %code_country)
    return code_country


class PostgreSQL:
    if USE_DATABASE_AZURE:

        def __init__(self, host=DATABASE_ADDRESS_AZURE,
                     user=DATABASE_USER_AZURE,
                     dbname=DATABASE_NAME_AZURE,
                     password=DATABASE_PASSWORD_AZURE,
                     sslmode="require"):
            # Connect to an existing database
            try:
                # Construct connection string
                conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname,
                                                                                             password, sslmode)
                self.connector = psycopg2.connect(conn_string)
                logger.info("Connection  established  to database in azure ")
                logger.info("Database name: " + dbname)
                logger.info("Database host: " + host)
                logger.info("Database user: " + user)

                self.cursor = self.connector.cursor()
            except Exception as e:
                logger.error("Unable to connect to the database in azure ! Please verify your parameters." + str(e))
    else:

        def __init__(self, dbname=DATABASE_NAME, host=DATABASE_ADDRESS, user=DATABASE_USER, password=DATABASE_PASSWORD):
            # Connect to an existing database
            try:
                self.connector = psycopg2.connect(
                    "dbname='" + dbname + "' user='" + user + "' host='" + host + "' password='" + password + "'")
                logger.info("Connected to PostgreSQL database successfully..")
                logger.info("Database name: " + dbname)
                logger.info("Database host: " + host)
                logger.info("Database user: " + user)
                # Open a cursor to perform database operations
                self.cursor = self.connector.cursor()
            except:
                logger.error("Unable to connect to the database! Please verify your parameters.")

    # Users management table methods
    def create_users_management_table(self):

        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "customer VARCHAR(1000),"
                                "customerPassword VARCHAR(1000),"
                                "customerEmail VARCHAR(1000),"
                                "customerJob VARCHAR(1000),"
                                "customerPhone VARCHAR(1000),"
                                "aboutUs VARCHAR(1000),"
                                "subjectHelp VARCHAR(1000),"
                                "domaine VARCHAR(1000),"
                                "firstName VARCHAR(512),"
                                "lastName VARCHAR(512),"
                                "stafNumber VARCHAR(512),"
                                "token VARCHAR(1000),"
                                "apikey VARCHAR(512),"
                                "expire BIGINT,"
                                "is_active INT,"
                                "conx_time VARCHAR(99999),"
                                "ip VARCHAR(99999),"
                                "conx_counter VARCHAR(99999),"
                                "device VARCHAR(99999),"
                                "country VARCHAR(99999),"
                                "type VARCHAR(1000)"
                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            self.connector.rollback()

    def add_customer(self, customer, customerPassword="", customerEmail="", is_active=0, customerJob="",
                     customerPhone="", token="", aboutUs="", subjectHelp="",
                     domaine="", firstName="", lastName="", stafNumber="", apikey="", expiration_duration_in_hours=72,
                     type=""):

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)

        self.cursor.execute("SELECT apikey FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
        if self.cursor.fetchone() is None:
            try:
                query_insert_new_client = "INSERT INTO " + table_name + " (customer , customerPassword, customerEmail, " \
                                                                        "is_active, customerJob, customerPhone, token, aboutUs, subjectHelp, domaine, " \
                                                                        "firstName, lastName, stafNumber, apikey, expire, conx_time, ip, conx_counter, device, country, type) VALUES ('" + customer + "','" + customerPassword + "','" + customerEmail + "','" + str(
                    0) + "','" + customerJob + "','" + customerPhone + "','" + token + "','" + aboutUs + "','" + subjectHelp + "','" + domaine + "','" + firstName + "','" + lastName + "','" + stafNumber + "', '" + apikey + "','" + str(
                    int(
                        time.time()) + expiration_duration_in_hours * 3600) + "', ' ', ' ', '0', ' ', ' ', '" + type + "')"
                self.cursor.execute(query_insert_new_client)
                logger.info("Inserting values into table '" + table_name + "' successfully")
                return True
            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.", e)
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

        else:
            logger.error("email utilise")
            return False

    def update_customer(self, customer="", apikey="", expiration_duration_in_hours=72):
        table_name = DATABASE_USERS_MANAGEMENT_TABLE_NAME
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        self.cursor.execute("SELECT apikey FROM " + table_name + " WHERE customer = %s", (customer,))

        if self.cursor.fetchone() is not None:
            try:
                self.cursor.execute("UPDATE " + table_name + " SET apikey = '" + apikey + "' , expire = '" + str(int(
                    time.time() + expiration_duration_in_hours * 3600)) + "' WHERE customer = '" + customer + "';")
                logger.info("Updating values into table '" + table_name + "' successfully")
            except:
                logger.warning("Updating table '" + table_name + "' failed.")
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

    def complete_add_customer(self, customer, customerEmail, firstName="", lastName="", customerJob="",
                              customerPhone="", stafNumber="", domaine=""):

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        res = self.cursor.execute("SELECT apikey FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
        if self.cursor.fetchone() is None:
            logger.warning("user is not registred '")
        else:
            try:
                self.cursor.execute(
                    "UPDATE " + table_name + " SET firstName = '" + firstName + "' ,lastName = '" + lastName + "' ,customer = '" + customer + "',customerJob = '" + customerJob + "',customerPhone = '" + customerPhone + "',stafNumber = '" + stafNumber + "',domaine = '" + domaine + "' WHERE  customerEmail = '" + customerEmail + "';")

            except:
                logger.warning("Inserting into table '" + table_name + "' failed.")
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

    def get_customer_from_apikey(self, apikey=""):

        try:
            self.cursor.execute("SELECT customer FROM " + table_name + " WHERE apikey = %s", (apikey,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get customer from apikey")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_apikey_from_customer_email(self, customerEmail=""):

        try:
            self.cursor.execute("SELECT apikey FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
        except Exception as e:
            logger.error("Table " + table_name + " doesn't exist or problem during get apikey from customerEmail")

            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_customer_name_from_customer_email(self, customerEmail=""):

        try:
            self.cursor.execute("SELECT customer FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get apikey from customer")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_customer_type_from_customer_email(self, customerEmail=""):

        try:
            self.cursor.execute("SELECT domaine FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get apikey from customer")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_apikey_from_customer(self, customer=""):

        try:
            self.cursor.execute("SELECT apikey FROM " + table_name + " WHERE customer = %s", (customer,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get apikey from customer")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_profile_from_token(self, token=""):

        try:
            self.cursor.execute("SELECT apikey FROM " + table_name + " WHERE token = %s", (token,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get apikey from customer")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def activate_profile(self, token=""):

        try:
            self.cursor.execute("UPDATE " + table_name + " SET is_active = 1 WHERE token = '" + token + "';")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")

        except:

            logger.warning("Updating table '" + table_name + "' failed.")
            self.connector.rollback()

    def login(self, customerEmail="", customerPassword="", type_user=""):
        try:
            if type_user == "customer":
                self.cursor.execute(
                    "SELECT type FROM " + table_name + " WHERE customerEmail = '" + customerEmail + "' AND  customerPassword = '" + customerPassword + "' AND  type = '" + type_user + "';")
                if self.cursor.fetchone() is None:
                    return "False" + "#$#None"
                else:
                    return "True" + "#$#" + type_user

            elif type_user == "admin":
                self.cursor.execute(
                    "SELECT type FROM " + table_name + " WHERE customerEmail = '" + customerEmail + "' AND  customerPassword = '" + customerPassword + "';")
                res = self.cursor.fetchone()[0]

                if res is None:
                    return "False" + "#$#None"
                else:
                    return "True" + "#$#" + res
        except:
            self.connector.rollback()
            return "False" + "#$#None"


    def get_profile(self, table_name="objects", customerEmail=""):
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
            return self.cursor.fetchone()
        except:
            self.connector.rollback()
            return

    def get_full_profile_from_token(self, token=""):

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE token = %s", (token,))
        try:
            return self.cursor.fetchone()
        except:
            self.connector.rollback()

    def get_email_from_customer(self, customer="", customer_type=""):
        table_name = DATABASE_USERS_MANAGEMENT_TABLE_NAME

        self.cursor.execute("SELECT customerEmail FROM " + table_name + " WHERE customer = '" + customer +
                            "' AND domaine= '" + customer_type + "';")
        try:
            return self.cursor.fetchone()[0]
        except:
            self.connector.rollback()

    def get_customer_info_from_customer_name(self, customer_name=""):

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer = %s", (customer_name,))
        try:
            return self.cursor.fetchall()

        except:
            self.connector.rollback()

    def get_if_user_is_active(self, customerEmail=""):

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        try:
            self.cursor.execute("SELECT is_active FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
            return self.cursor.fetchone()
        except:
            self.connector.rollback()

    def set_profile(self, table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME, firstName="",lastName="",customerJob="", customerPhone="",customerEmail="",customer="", id=""):
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET firstName = '" + firstName + "' ,lastName = '" + lastName + "' ,customerJob = '" + customerJob + "' ,customerPhone = '" + customerPhone + "' ,customerEmail = '" + customerEmail + "' ,customer = '" + customer + "' WHERE id = " + id + ";")
        except Exception as e:
            logger.warning("exception in updating profile %s" %e)
            self.connector.rollback()

    def set_password(self, table_name="objects", customerPasswordN="", customerEmail=""):
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        try:
            ch = "UPDATE " + table_name + " SET customerPassword = '" + customerPasswordN + "' WHERE customerEmail = '" + customerEmail + "';"
            self.cursor.execute(ch)
        except:
            self.connector.rollback()

    def get_first_name_from_customer(self, customerEmail=""):

        try:
            self.cursor.execute("SELECT firstName  FROM " + table_name + " WHERE customerEmail = %s", (customerEmail,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get apikey from customer")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_expiration_from_customer(self, customer=""):

        try:
            self.cursor.execute("SELECT expire FROM " + table_name + " WHERE customer = %s", (customer,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get expire from customer")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_expiration_from_apikey(self, apikey=""):

        try:
            self.cursor.execute("SELECT expire FROM " + table_name + " WHERE apikey = %s", (apikey,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get expire from apikey")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    # Hash table methods
    def create_urls_hash_table(self):
        table_name = DATABASE_HASH_TABLE_NAME
        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "url VARCHAR(1000),"
                                "hash VARCHAR(512)"
                                ");")
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            self.connector.rollback()

    def add_or_update_url_hash(self, url="", hash=""):
        table_name = DATABASE_HASH_TABLE_NAME
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        self.cursor.execute("SELECT hash FROM " + table_name + " WHERE url = %s", (url,))
        if self.cursor.fetchone() is None:
            try:
                self.cursor.execute("INSERT INTO " + table_name + " (url, hash) VALUES ('" + url +
                                    "', '" + hash + "')")
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
            except:
                logger.warning("Inserting into table '" + table_name + "' failed.")
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()
        else:
            try:
                self.cursor.execute("UPDATE " + table_name + " SET hash = '" + hash + "' WHERE url = '" + url + "';")
                logger.info("Updating values into table '" + table_name + "' successfully")
                self.commit_db_changes()
            except:
                logger.warning("Updating table '" + table_name + "' failed.")
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

    def get_hash_from_url(self, url=""):
        table_name = DATABASE_HASH_TABLE_NAME
        try:
            self.cursor.execute("SELECT hash FROM " + table_name + " WHERE url = %s", (url,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get hash from url")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def get_url_from_hash(self, hash=""):
        table_name = DATABASE_HASH_TABLE_NAME
        try:
            self.cursor.execute("SELECT url FROM " + table_name + " WHERE hash = %s", (hash,))
        except:
            logger.error("Table " + table_name + " doesn't exist or problem during get url from hash")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def create_history_table(self, table_name="objects"):
        # Execute a command: this creates a new
        table_name = table_name + "_history"
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "hash VARCHAR(1000),"
                                "reference VARCHAR(1000),"
                                "similars VARCHAR(99999)"
                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            self.connector.rollback()

    def get_similars(self, table_name="objects", reference=""):
        try:
            self.cursor.execute("SELECT similars FROM " + table_name + " WHERE reference = %s", (reference,))
        except Exception as e:
            logger.error("Table " + table_name + " doesn't exist or problem during get similarity %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def delete_hash(self, hash=""):
        try:
            url_getted = self.get_url_from_hash(hash=hash)
            logger.info("Delete hash for url " + url_getted[0])
            self.cursor.execute("DELETE FROM " + DATABASE_HASH_TABLE_NAME + " WHERE url = %s",
                                (url_getted[0],))

            self.commit_db_changes()
            logger.info("Delete hash from " + DATABASE_HASH_TABLE_NAME + " successful")
        except Exception as e:
            logger.error(
                "Delete hash from " + DATABASE_HASH_TABLE_NAME + " Failed error (" + str(e) + ")")
            self.connector.rollback()
            return None

    def delete_smilitaries(self, table_name, url=""):
        try:
            self.cursor.execute("DELETE FROM " + table_name + " WHERE reference = %s", (url,))
            self.commit_db_changes()
            logger.info("Deleting similarities from  " + table_name + " succuessfully ended...")
            logger.info("Start deleting similars ...")
            self.delete_from_smilitaries(table_name=table_name, url=url)
            self.commit_db_changes()
        except Exception as e:
            logger.error("Error  " + str(e) + " ...")
            logger.error("Deleting similarities from  " + table_name + " failed...")
            self.connector.rollback()
            return None

    def get_url_from_similars(self, table_name, similars=""):
        try:
            self.cursor.execute("SELECT reference FROM " + table_name + " WHERE similars = %s", (similars,))
        except:
            logger.warning("Erreur getting reference from table" + table_name + "...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def delete_from_smilitaries(self, table_name, url=""):
        try:
            self.cursor.execute("SELECT similars FROM " + table_name + " WHERE similars LIKE '%" + url[0] + "%'")
            similars = self.cursor.fetchone()
            for similar in similars:
                url_to_update = self.get_url_from_similars(table_name, similar)
                # new_similars = similar.replace(url[0] + '\n', '')
                # self.add_or_update_similars(table_name, url_to_update[0], new_similars)
                logger.info(
                    "Updating similars into table '" + table_name + "' successfully for url " + url_to_update[0])

        except Exception as e:
            logger.error("Updating similars into table " + table_name + " Failed (" + str(e) + ")")
            self.connector.rollback()
            return None

    def create_prediction_table(self, table_name):
        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "id_product VARCHAR(1000),"
                                "short_description VARCHAR(30000),"
                                "caracteristic VARCHAR(30000),"
                                "url_image VARCHAR(10000),"
                                "principal_categorie VARCHAR(1000),"
                                "text_categorie VARCHAR(1000),"
                                "image_categorie VARCHAR(1000)"
                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            self.connector.rollback()

    def get_prediction_table(self, table_name):
        try:
            self.cursor.execute("SELECT * FROM " + table_name + ";")
        except Exception as e:
            logger.error("Error in getting prediction table %s" % e)
        return self.cursor.fetchall()

    def add_prediction_table(self, table_name, row_values, principal_categorie):
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        # self.cursor.execute("SELECT id_product FROM " + table_name + ";")
        # if self.cursor.fetchone() is None:
        try:
            self.cursor.execute("INSERT INTO " + table_name + " (id_product, short_description, caracteristic,"
                                                              "url_image, principal_categorie,"
                                                              " text_categorie, image_categorie ) "
                                                              "VALUES ('" + str(row_values[0]) +
                                "', '" + str(row_values[1]).replace("'", " ") + "', '"
                                + str(row_values[2]).replace("'", " ") + "', '" + str(row_values[5]) +
                                "', '" + principal_categorie + "', '" + str(row_values[14]) +
                                "', '" + str(row_values[15]) + "')")
            logger.info("Inserting values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Inserting into table '" + table_name + "' failed.")
            self.connector.rollback()
        self.commit_db_changes()
        # Query the database and obtain data as Python objects
        self.cursor.execute("SELECT * FROM " + table_name + ";")
        self.cursor.fetchone()

    def update_prediction_table(self, table_name, id_product, new_principal_categorie):
        try:
            self.cursor.execute(

                "UPDATE " + table_name + " SET text_categorie = '" + new_principal_categorie + "' WHERE id_product = '" + id_product + "';")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except:
            logger.warning("Updating table '" + table_name + "' failed.")
            self.connector.rollback()
        # Query the database and obtain data as Python objects
        self.cursor.execute("SELECT * FROM " + table_name + ";")
        self.cursor.fetchone()

    def delete_predict_table(self, table_name):
        try:
            self.cursor.execute("DELETE FROM " + table_name + " ;")
            self.commit_db_changes()
            logger.info("Deleting latest values from  " + table_name + " succuessfully ended...")

        except Exception as e:
            logger.error("Error  " + str(e) + " ...")
            logger.error("Deleting similarities from  " + table_name + " failed...")
            self.connector.rollback()

    def create_or_update_history(self, table_name, url):
        hash = self.get_hash_from_url(url)
        similars = self.get_similars(table_name, url)
        table_name = table_name + "_history"
        self.cursor.execute("SELECT hash FROM " + table_name + " WHERE reference = %s", (url,))
        if self.cursor.fetchone() is None:
            try:
                self.cursor.execute("INSERT INTO " + table_name + " (hash, reference, similars) VALUES ('" + hash[0] +
                                    "', '" + url[0] + "', '" + similars[0] + "')")
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed. erreur (" + e + ")")
                self.connector.rollback()
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()
        else:
            try:
                self.cursor.execute(
                    "UPDATE " + table_name + " SET similars = '" + similars + "' WHERE reference = '" + url + "';")
                self.commit_db_changes()
                logger.info("Updating values into table '" + table_name + "' successfully")
            except:
                logger.warning("Updating table '" + table_name + "' failed.")
                self.connector.rollback()
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

    def get_data(self, table_name):
        try:
            self.cursor.execute("SELECT 1 FROM " + table_name)
            if self.cursor.fetchone():
                return True
            else:
                return False
        except:
            self.connector.rollback()
            return False

    def get_all_users(self):
        try:
            self.cursor.execute("SELECT * FROM " + DATABASE_USERS_MANAGEMENT_TABLE_NAME + ";")
        except Exception as e:
            logger.error("Error in getting users management %s" % e)
        return self.cursor.fetchall()

    def create_status_projects_table(self, table_name):
        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "customer_name VARCHAR(1000),"
                                "customer_type VARCHAR(30000),"
                                "project VARCHAR(30000),"
                                "api VARCHAR(10000),"
                                "status INT,"
                                "name VARCHAR(1000),"
                                "training_details TEXT,"
                                "counter INT"

                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            self.connector.rollback()

    # new_function
    def get_training_detalis(self, table_name, customer, customer_type, project, api):
        try:
            self.cursor.execute(
                "SELECT training_details,counter,status FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api + "' AND  project = '" + project + "';")
        except Exception as e:
            logger.error("Error in getting projects %s" % e)
        return self.cursor.fetchone()

    def insert_or_update_status_projects_table(self, table_name, customer, customer_type, project_to_delete, api,
                                                   status, name, training_details=None, counter=None):
            ch = "SELECT * FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api + "' AND name = '" + name + "' AND  project = '" + project_to_delete + "';"
            try:
                self.cursor.execute(ch)
            except Exception as e:
                logger.error(e)

            if self.cursor.fetchone() is None:
                try:
                    if counter and training_details:
                        self.cursor.execute(
                            "INSERT INTO " + table_name + " (customer_name, customer_type, project, api, status, name,training_details,counter ) VALUES ('" + customer +
                            "', '" + customer_type + "', '" + project_to_delete + "', '" + api + "', " + str(
                                status) + " , '" + name + "', '" + training_details + "','" + str(counter) + "')")
                    else:
                        self.cursor.execute(
                            "INSERT INTO " + table_name + " (customer_name, customer_type, project, api, status, name,training_details,counter ) VALUES ('" + customer +
                            "', '" + customer_type + "', '" + project_to_delete + "', '" + api + "', " + str(
                                status) + " , '" + name + "', '" + str({}) + "','" + str(0) + "')")

                    self.commit_db_changes()
                    logger.info("Inserting values into table '" + table_name + "' successfully")
                except Exception as e:
                    logger.warning("Inserting into table '" + table_name + "' failed...Exception " + str(e))
                    self.connector.rollback()

                # Query the database and obtain data as Python objects
                self.cursor.execute("SELECT * FROM " + table_name + ";")
                self.cursor.fetchone()
            else:
                try:
                    if counter and training_details:
                        cccc = "UPDATE " + table_name + " SET status = '" + str(
                            status) + "' ,training_details = '" + training_details + "' ,counter = '" + str(
                            counter) + "' WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api + "' AND  project = '" + project_to_delete + "' AND  name = '" + name + "';"
                        self.cursor.execute(cccc)
                    else:
                        cccc = "UPDATE " + table_name + " SET status = " + str(
                            status) + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api + "' AND  project = '" + project_to_delete + "' AND  name = '" + name + "';"
                        self.cursor.execute(cccc)
                    self.commit_db_changes()
                    logger.info("Updating values into table '" + table_name + "' successfully")
                except Exception as e:
                    logger.warning("Updating table '" + table_name + "' failed..." + str(e))
                    self.connector.rollback()

                # Query the database and obtain data as Python objects
                self.cursor.execute("SELECT * FROM " + table_name + ";")
                self.cursor.fetchone()

        # Insert value into history client
    def insert_or_update_into_table_history(self, table_name, date, customer_name, customer_type, project_name, url,
                                             api, result_search,
                                             result_classification, ip_adress, domain_url, type_reference):

        code_country = get_client_code_country(ip_adress)

        self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_name = '" + customer_name +
                            "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api +
                            "' AND url = '" + url + "' AND  ip_adress = '" + ip_adress + "' AND  project_name = '" + project_name + "';")
        sql_requete = self.cursor.fetchone()
        # self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_email = %s", (customer_email,))
        if sql_requete is not None:
            try:
                count = sql_requete
                counter = int(count[9]) + 1
                update_requete = "UPDATE " + table_name + " SET result_search = '" + json.dumps(
                    result_search) + "', result_classification = '" + \
                                 json.dumps(result_classification) + "' , date = '" + date + "' , counter = '" + str(
                    counter) + "' , ip_adress = '" + ip_adress + "', code_country = '" + code_country + "',domain_url = '" + domain_url + "',type_reference = '" + type_reference + "' WHERE customer_name = '" + \
                                 customer_name + "' AND  customer_type = '" + customer_type + "'" + \
                                 " AND  api = '" + api + "' AND  project_name = '" + project_name + "' AND  ip_adress = '" + ip_adress + "' AND  url = '" + url + "';"
                self.cursor.execute(update_requete)
                self.commit_db_changes()
                logger.info("Updating values into table '" + table_name + "' successfully")
            except Exception as e:
                logger.warning("Updating table '" + table_name + "' failed..." + str(e))
                self.connector.rollback()
        else:
            try:
                self.cursor.execute(
                    "INSERT INTO " + table_name + " (date, customer_name , customer_type, project_name, url, api,"
                                                  " result_search, result_classification,ip_adress,code_country, counter,domain_url,type_reference) VALUES ('" + date + "','"
                    + customer_name + "','" + customer_type + "','" + project_name + "','" + url + "','" + api
                    + "','" + json.dumps(result_search) + "','" + json.dumps(
                        result_classification) + "','" + ip_adress + "','" + code_country + "','" + "1" + "','" + domain_url + "','" + type_reference + "')")
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
            except Exception as e:
                logger.error("Error in inserting into table %s" % e)


    def update_type_reference_classification(self, type_reference, customer_name, customer_type, date, project_name,
                                             url):
        table_name = 'client_history_table'

        try:
            self.cursor.execute(
                            "UPDATE " + table_name + " SET  type_reference = '" + type_reference + "' WHERE customer_name = '" + customer_name +
                            "' AND  customer_type = '" + customer_type + "' AND date ='" + date + "' AND project_name = '" + project_name + "' AND url ='" + url + "';")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def get_from_status_projects(self, table_name, customer, customer_type, api):
        try:
            self.cursor.execute(
                "SELECT project , name FROM " + table_name + " WHERE customer_name = '" + customer + "' AND customer_type  = '" + customer_type + "'" + " AND  api = '" + api + "' AND  status > 0 " + ";")
        except:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def get_from_status_projects_only_2(self, table_name, customer, customer_type):
        try:
            self.cursor.execute(
                "SELECT project , name FROM " + table_name + " WHERE customer_name = '" + customer + "' AND customer_type = '" + customer_type + "' AND api='similars' AND status = 2 " + ";")
        except:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table")
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def get_status_project(self, table_name, customer, customer_type, api, project):
        try:
            self.cursor.execute(
                "SELECT status FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api + "'" + " AND  project = '" + project + "'" + ";")
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get status from status_projects table, exception ...: %s " % e)
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    def select_status_project_similars(self, table_name, customer, customer_type):
        api = "similars"
        try:
            self.cursor.execute(
                "SELECT name , status FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'" + " AND  api = '" + api + "'" + ";")
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get status from status_projects table, exception ...: %s " % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def create_social_media_table(self, table_name):
        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "customer_email VARCHAR(1000),"
                                "media_type VARCHAR(1000),"
                                "instagram_username VARCHAR(1000),"
                                "access_token VARCHAR(10000)"
                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            self.connector.rollback()

    def insert_social_media_table(self, table_name, customer_email, media_type, instagram_username,
                                  access_token):

        self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_email = %s", (customer_email,))
        if self.cursor.fetchone() is None:
            try:
                self.cursor.execute(
                    "INSERT INTO " + table_name + " (customer_email , media_type, instagram_username, access_token ) VALUES ('" + customer_email + "','" + media_type +
                    "','" + instagram_username + "','" + access_token + "')")
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
            except Exception as e:
                logger.warning("Error in inserting into table %s, The exception is: %s " % (table_name, e))
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

        else:
            logger.error("customer_email not found ")

    def get_from_social_media_table(self, table_name, customer_email):
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_email = %s", (customer_email,))
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            logger.warning("Trying to create table...")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()

    # History recherche client
    def create_client_history_table(self, table_name="objects"):
        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "date DATE NOT NULL DEFAULT CURRENT_DATE,"
                                "customer_name VARCHAR(99999),"
                                "customer_type VARCHAR(99999),"
                                "project_name VARCHAR(99999),"
                                "url VARCHAR(99999),"
                                "api VARCHAR(99999),"
                                "result_search VARCHAR(99999),"
                                "result_classification VARCHAR(99999),"
                                "counter INT,"
                                "ip_adress VARCHAR(99999),"
                                "code_country VARCHAR(99999) "
                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")
        except:
            logger.warning("Table '" + table_name + "' already exists.")
            self.connector.rollback()

    def select_similars_classification_result(self, table_name, customer_name, customer_type):
        api = "search_similars"
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_name = '" + customer_name +
                                "' AND  customer_type = '" + customer_type + "' AND  api = '" + api + "';")
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def select_list_all_clients_with_projects(self, table_name):

        try:
            query = "SELECT customer_name, customer_type, project, api, status, name FROM " + table_name + " ;"
            self.cursor.execute(query)
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return DataFrame(self.cursor.fetchall(),
                         columns=['customer_name', 'customer_type', 'project', 'api', 'status', 'name'])

    def select_number_post_per_clients(self, table_name):
        try:
            query = "SELECT SUM(counter), customer_name, customer_type FROM " + table_name + " GROUP BY customer_name, customer_type;"
            self.cursor.execute(query)

        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def get_sum_of_counter_from_country_code(self, table_name, customer_name, customer_type):
        api = "search_similars"
        try:
            query = "SELECT SUM(counter), code_country FROM " + table_name + " WHERE customer_name ='" + customer_name + "' AND customer_type = '" + customer_type + "' AND api = '" + api + "' GROUP BY code_country;"
            self.cursor.execute(query)
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get counter or code_country from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def get_date_counter(self, table_name, customer_name, customer_type, month):
        api = "search_similars"
        try:
            query = "SELECT SUM(counter), date FROM " + table_name + " WHERE customer_name = '" + customer_name + "' AND  customer_type = '" + customer_type + "' AND  to_char(date , 'MM') = '" + month + "' AND  api = '" + api + "' GROUP BY date;"
            self.cursor.execute(query)
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get counter or code_country from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def get_date_and_counter_from_historic_table(self, table_name, customer_name, customer_type, month):
        api = "search_similars"
        try:
            query = "SELECT SUM(counter), DATE(date) FROM " + table_name + " WHERE customer_name = '" + customer_name + "' AND  customer_type = '" + customer_type + "' AND  to_char(date , 'MM') = '" + month + "' AND  api = '" + api + "' GROUP BY DATE(date) ORDER BY DATE(date);"
            self.cursor.execute(query)
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get counter or code_country from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def update_type_reference_similars(self,type_reference, customer_name, customer_type,date, project_name, url,ip_adress):
        table_name = 'client_history_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  type_reference = '" + type_reference + "' WHERE customer_name = '" + customer_name +
                "' AND  customer_type = '" + customer_type + "' AND date ='" + date + "' AND project_name = '" + project_name +"' AND url ='" + url + "' AND ip_adress ='" + ip_adress +"';")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def select_historic_project(self, table_name, customer_name, customer_type, project_name):
        api = "search_similars"
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_name = '" + customer_name +
                                "' AND  customer_type = '" + customer_type + "' AND  project_name = '" + project_name + "' AND  api = '" + api + "';")
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def select_utilistation_par_mois(self, table_name, customer_name, customer_type, month):
        api = "search_similars"

        try:
            query = "SELECT SUM(counter) FROM " + table_name + " WHERE customer_name = '" + customer_name + "' AND  customer_type = '" + customer_type + "' AND  to_char(date , 'MM') = '" + month + "' AND  api = '" + api + "';"
            self.cursor.execute(query)
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()[0][0]

    def select_all_utilistation_par_mois(self, table_name, customer_name, customer_type, month):
        api = "search_similars"
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_name = '" + customer_name +
                                "' AND  customer_type = '" + customer_type + "' AND  to_char(date , 'MM') = '" + month + "' AND  api = '" + api + "';")
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    # client_products_ table
    def create_client_products_table(self, table_name="objects"):
        # Execute a command: this creates a new table
        try:
            self.cursor.execute("CREATE TABLE " + table_name +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "reference VARCHAR(1000),"
                                "urlProduit VARCHAR(99999)"
                                ");")
            self.commit_db_changes()
            logger.info("Creating table '" + table_name + "' successfully")

        except:
            self.connector.rollback()

    def add_or_update_products(self, table_name="objects", reference="", urlProduit="", count=0, rest_photos=0, itr=0, nb_iteration=0):
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        self.cursor.execute("SELECT urlProduit FROM " + table_name + " WHERE reference = %s", (reference,))
        counter_request = count + 1
        if self.cursor.fetchone() is None:
            try:
                self.cursor.execute("INSERT INTO " + table_name + " (reference, urlProduit) VALUES ('" + reference +
                                    "', '" + urlProduit + "')")

                logger.info("Inserting values into table '" + table_name + "' successfully")

            except:
                logger.warning("Inserting into table '" + table_name + "' failed.")
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()
        else:
            try:
                self.cursor.execute(
                    "UPDATE " + table_name + " SET urlProduit = '" + urlProduit + "' WHERE reference = '" + reference + "';")

                logger.info("Updating values into table '" + table_name + "' successfully")
            except:
                logger.error("Updating table '" + table_name + "' failed.")
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()
        if counter_request == 100 :
            self.commit_db_changes()
            logger.info( "Data commited into %s successfully" %table_name)
        elif counter_request == rest_photos and itr == nb_iteration + 1:
            self.commit_db_changes()
            logger.info("Rest of data  commited into table '" + table_name + "' successfully")


    def get_url_product_from_url_reference(self, table_name, url_reference):
        try:
            self.cursor.execute("SELECT urlproduit FROM " + table_name + " WHERE reference = %s", (url_reference,))
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return ['']
        return self.cursor.fetchone()

    # CMS table with the access token for client
    def create_cms_table(self):
        try:
            self.cursor.execute("CREATE TABLE cms_client_table" +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "customer_name VARCHAR(1000),"
                                "customer_type VARCHAR(30000),"
                                "project_name VARCHAR(30000),"
                                "cms VARCHAR(30000),"
                                "url_shop VARCHAR(30000),"
                                "access_token VARCHAR(1000)"
                                ");")
            logger.info("Creating table cms_client_table successfully")
        except Exception as e:
            logger.warning("Table cms_client_table exist or problem during creating table , exception is : %s" % e)
            self.connector.rollback()

    # Add or update cms_client_table
    def add_or_update_cms_table(self, table_name="cms_client_table", customer_name="", customer_type="",
                                project_name="", cms="", url_shop="", token=""):
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE customer_name = '" + customer_name +
                            "' AND  customer_type = '" + customer_type + "' AND  project_name = '" + project_name +
                            "' AND  cms = '" + cms + "' AND  url_shop = '" + url_shop + "';")
        test = self.cursor.fetchone()
        if test is None:
            try:
                self.cursor.execute("INSERT INTO " + table_name + " (customer_name, customer_type, project_name, cms,"
                                                                  " url_shop, access_token) VALUES ('" + customer_name +
                                    "', '" + customer_type + "', '" + project_name + "', '" + cms + "', '"
                                    + url_shop + "', '" + token + "')")
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")

            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.")
                self.connector.rollback()

            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()
        else:
            try:
                self.cursor.execute(
                    "UPDATE " + table_name + " SET access_token = '" + token + "' WHERE customer_name = '" +
                    customer_name + "' AND  customer_type = '" + customer_type + "' AND  project_name = '" +
                    project_name + "' AND  cms = '" + cms + "';")
                self.commit_db_changes()
                logger.info("Updating values into table '" + table_name + "' successfully")
            except Exception as e:
                logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
                self.connector.rollback()

            # Query the database and obtain data as Python objects
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            self.cursor.fetchone()

    def update_cms_data_client(self, customer_name, customer_type, url_shop, cms):

        table_name = "cms_client_table"
        try:
            query = "UPDATE " + table_name + " SET customer_name = '" + customer_name + "', customer_type = '" + customer_type + "' WHERE url_shop = '" + url_shop + "' AND  cms = '" + cms + "';"
            self.cursor.execute(query)
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def get_token_for_client(self, table_name, customer_name, customer_type, cms, url_shop, project_name):
        try:
            self.cursor.execute("SELECT access_token FROM " + table_name + " WHERE customer_name = '" + customer_name
                                + "' AND  customer_type = '" + customer_type + "' AND  project_name = '" + project_name
                                + "' AND  cms = '" + cms + "' AND  url_shop = '" + url_shop + "';")
        except Exception as e:
            logger.error("Table " + table_name + "doesn't exist or problem during get"
                                                 " project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return ()
        return self.cursor.fetchone()

    def get_url_for_client(self, table_name, customer_name, customer_type):
        try:
            self.cursor.execute("SELECT url_shop, cms FROM " + table_name + " WHERE customer_name = '" + customer_name
                                + "' AND  customer_type = '" + customer_type + "';")
        except Exception as e:
            logger.error("Table " + table_name + "doesn't exist or problem during get"
                                                 " project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()

    def get_similars_request_period(self, table_name, customer_name, customer_type, first_day, current_day):
        try:
            query = "SELECT SUM(counter) FROM " + table_name + " WHERE customer_name = '" + customer_name + "' AND  customer_type = '" + customer_type + "' AND  date BETWEEN  '" + first_day + "'  AND '" + current_day + "'  ;"
            self.cursor.execute(query)
        except Exception as e:
            logger.error(
                "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return None
        return self.cursor.fetchall()[0][0]

    def get_ip_address(self, table_name, customer_name="", customer_type=""):
        try:
            self.cursor.execute(
                "SELECT ip_adress FROM " + table_name + " WHERE customer_name = '" + customer_name + "' AND  customer_type = '" + customer_type + "';")
        except:
            self.connector.rollback()

        return self.cursor.fetchall()

    # Payment table
    def create_payment_table(self):
        try:
            self.cursor.execute("CREATE TABLE payment_table" +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "customer_name VARCHAR(1000),"
                                "customer_type VARCHAR(30000),"
                                "date DATE NOT NULL DEFAULT CURRENT_DATE,"
                                "payment_method VARCHAR(30000),"
                                "choosed_plan VARCHAR(30000),"
                                "transction_id VARCHAR(30000),"
                                "currency VARCHAR(30000),"
                                "status INT,"
                                "total NUMERIC(10, 5),"
                                "stripe_customer_id VARCHAR(30000)"

                                ");")
            self.commit_db_changes()
            logger.info("Creating table cms_client_table successfully")
        except Exception as e:
            logger.warning("Table cms_client_table exist or problem during creating table , exception is : %s" % e)
            self.connector.rollback()

    def create_plans_table(self):
        try:
            self.cursor.execute("CREATE TABLE Plan" +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "plan_name VARCHAR(1000),"
                                "payment_period INT,"
                                "total NUMERIC,"
                                "max_image_training BIGINT"
                                ");")
            logger.info("Creating table cms_client_table successfully")
            self.commit_db_changes()
        except Exception as e:
            logger.warning("Table cms_client_table exist or problem during creating table , exception is : %s" % e)
            self.connector.rollback()

    def add_new_plan(self, plan_name, max_image_training, total, payment_period):
        table_name = 'Plan'
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE plan_name = '" + plan_name +
                            "' AND payment_period = '" + str(payment_period) + "' AND total= '" + str(total) +
                            "' AND max_image_training = '" + str(max_image_training) + "';")
        if self.cursor.fetchone() is None:
            try:
                self.cursor.execute(
                    "INSERT INTO " + table_name + " (plan_name, payment_period, total, max_image_training) VALUES ('"
                    + plan_name + "','" + str(payment_period) + "','" + str(total) + "','" + str(
                        max_image_training) + "');")
                logger.info("Inserting values into table '" + table_name + "' successfully")
                self.commit_db_changes()
                return True
            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.", e)
                self.connector.rollback()

    def get_plan_form_name(self, name):
        table_name = 'Plan'
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE plan_name='" + name + "';")

            return self.cursor.fetchone()
        except Exception as e:
            logger.warning("No payment for client %s and domaine %s" % (name))
            self.connector.rollback()
            return ()

    def create_payment_client(self, customer, customer_type, date, currency, total):
        table_name = 'payment_table'
        transction_id = stripe_customer_id = ""
        self.cursor.execute(
            "SELECT * FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "'  ;")
        if self.cursor.fetchone() is None:
            try:
                query = "INSERT INTO " + table_name + "(customer_name, customer_type, date, payment_method, " \
                                                      "choosed_plan, currency, status, total) VALUES ('" \
                        + customer + "', '" + customer_type + "', '" + date + "', 'stripe', 'FREE', '" + currency + "', '" + \
                        str(0) + "', '" + str(total) + "' );"
                self.cursor.execute(query)
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
                return True
            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.", e)
                self.connector.rollback()
        else:
            try:
                self.cursor.execute(
                    "UPDATE " + table_name + " SET status = 0 WHERE customer_name= '" + customer + "' AND customer_type = '" + customer_type + "';")
                self.commit_db_changes()

                logger.info("Updating values into table '" + table_name + "' successfully")

            except Exception as e:
                self.connector.rollback()
                logger.info("Updating values into table '" + table_name + "' failed %s" % e)

    def update_stripe_customer_id(self, customer_name, customer_type, stripe_customer_id, plan):
        table_name = 'payment_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  stripe_customer_id = '" + stripe_customer_id + "' WHERE customer_name = '" + \
                customer_name + "' AND  customer_type = '" + customer_type + "' AND choosed_plan = '" + plan + "' AND  payment_method = 'stripe' ;")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def update_transction_id(self, customer_name, customer_type, transction_id, plan, date, methode):
        table_name = 'payment_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  transction_id = '" + transction_id + "' WHERE customer_name = '" + customer_name +
                "' AND  customer_type = '" + customer_type + "' AND payment_time ='" + date + "' AND choosed_plan = '" + plan + "' AND  payment_method = '"+ methode + "' ;")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def update_historic_users_management(self, conx_time, ip, device, country, email):
        table_name = DATABASE_USERS_MANAGEMENT_TABLE_NAME

        self.cursor.execute(
            "SELECT conx_counter, conx_time, ip, device, country FROM " + table_name + " WHERE customeremail = '" + email + "';")
        sql_requete = self.cursor.fetchone()
        if sql_requete[0] == None:
            conx_counter = 1
        else:
            conx_counter = int(sql_requete[0]) + 1

        if sql_requete[1] == None:
            conx_time_all = conx_time
        else:
            conx_time_all = sql_requete[1] + "+++" + conx_time

        if sql_requete[2] == None:
            ip_all = ip
        else:
            ip_all = sql_requete[2] + "+++" + ip

        if sql_requete[3] == None:
            device_all = device
        else:
            device_all = sql_requete[3] + "+++" + device

        if sql_requete[4] == None:
            country_all = country
        else:
            country_all = sql_requete[4] + "+++" + country
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET conx_time = '" + conx_time_all + "', ip = '" + ip_all + "' , conx_counter = '" + str(
                    conx_counter) + "' , device = '" + device_all + "' , country = '" + country_all + "' WHERE customeremail = '" + email + "' ;")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def get__historic_users_management(self):
        table_name = DATABASE_USERS_MANAGEMENT_TABLE_NAME
        try:
            self.cursor.execute(
                "SELECT customeremail, conx_counter, conx_time, ip, device, country, customer, domaine, expire FROM " + table_name + " WHERE type = 'customer';")
            return self.cursor.fetchall()
        except Exception as e:
            logger.warning("No historic data for clients %s " % e)
            self.connector.rollback()
            return ()

    def create_roles_table(self):
        try:
            self.cursor.execute("CREATE TABLE Roles" +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "type_user VARCHAR(1000),"
                                "permission JSON"
                                ");")
            logger.info("Creating table Role successfully")
            self.commit_db_changes()
        except Exception as e:
            logger.warning("Table Role exist or problem during creating table , exception is : %s" % e)
            self.connector.rollback()

    def get_permission(self, type_user):
        table_name = 'roles'
        try:
            self.cursor.execute("SELECT type_user, permission FROM " + table_name + " WHERE type_user = %s",
                                (type_user,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.warning("No historic data for clients ")
            self.connector.rollback()
            return ()

    def verif_permission(self, customerEmail="", type_user=""):
        try:
            if type_user == "admin":
                self.cursor.execute(
                    "SELECT type FROM " + table_name + " WHERE customerEmail = '" + customerEmail + "';")
                res = self.cursor.fetchone()[0]
                if res is None:
                    return "Email not found"
                else:
                    return res
            else:
                return "Error"

        except:
            self.connector.rollback()
            return "Email not found"

    def delete_user(self, table_name, email=""):
        try:
            self.cursor.execute("DELETE FROM " + table_name + " WHERE customeremail = %s", (email,))
            self.commit_db_changes()
            logger.info("Deleting user from  " + table_name + " succuessfully ended...")
            return True
        except Exception as e:
            logger.error("Error  " + str(e) + " ...")
            logger.error("Deleting user from  " + table_name + " failed...")
            self.connector.rollback()
            return False

    def get_type_user(self, customerEmail=""):
        try:
            self.cursor.execute(
                "SELECT type FROM " + table_name + " WHERE customerEmail = '" + customerEmail + "';")
            res = self.cursor.fetchone()[0]
            if res is None:
                return "Email not found"
            else:
                return res

        except:
            self.connector.rollback()
            return "Email not found"

    def get_info_user(self, customerEmail=""):
        try:
            self.cursor.execute(
                "SELECT type, customer, domaine FROM " + table_name + " WHERE customerEmail = '" + customerEmail + "';")
            res = self.cursor.fetchone()
            if res is None:
                return ["Email not found", "", ""]
            else:
                return res

        except:
            self.connector.rollback()
            return "Email not found"

    def get_users_for_admin(self, table_name):
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE type IN ('SN1', 'SN2', 'SN3', 'admin');")
            res = self.cursor.fetchall()
            return res

        except:
            self.connector.rollback()
            return "Error"

    def get_customers(self, table_name):
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE type = 'customer';")
            res = self.cursor.fetchall()
            return res

        except:
            self.connector.rollback()
            return "Error"

    def delete_project(self, table_name, customer_name, customer_type, project_name):
        self.cursor.execute(
            "SELECT * FROM " + table_name + " WHERE customer_name= '" + customer_name + "' AND customer_type = '" + customer_type + "' AND name = '" + project_name + "' AND status > 0;")
        if self.cursor.fetchone() is not None:
            try:
                self.cursor.execute(
                    "UPDATE " + table_name + " SET status = 0 WHERE customer_name= '" + customer_name + "' AND customer_type = '" + customer_type + "' AND name = '" + project_name + "';")
                self.commit_db_changes()
                return True
            except Exception as e:
                self.connector.rollback()
                return False
        else:
            return False

    def add_entreprise_package(self, table_name, plan_name, total, max_images_training):
        self.cursor.execute(
            "SELECT * FROM " + table_name + " WHERE plan_name = '" + plan_name + "'  ;")
        if self.cursor.fetchone() is None:
            try:
                query = "INSERT INTO " + table_name + "(plan_name, total, max_image_training, payment_period) VALUES ('" + plan_name + "', '" + str(total) + "', '" + str(max_images_training) + "', '365" + "' );"
                self.cursor.execute(query)
                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
                return True
            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.", e)
                self.connector.rollback()
                return None
        else:
            return False
    def create_tva_table(self):
        try:
            self.cursor.execute("CREATE TABLE country_tva" +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "country VARCHAR(1000),"
                                "tva FLOAT"
                                ");")
            logger.info("Creating table cms_client_table successfully")
            self.commit_db_changes()
        except Exception as e:
            logger.warning("Table cms_client_table exist or problem during creating table , exception is : %s" % e)
            self.connector.rollback()

    def add_new_tva_amount(self, country, tva):
        table_name = 'country_tva'
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE country = '" + country +
                            "' AND tva = '" + str(tva) + "';")
        if self.cursor.fetchone() is None:
            try:
                self.cursor.execute(
                    "INSERT INTO " + table_name + " (country, tva) VALUES ('"
                    + country + "','" + str(tva) + "');")
                logger.info("Inserting values into table '" + table_name + "' successfully")
                self.commit_db_changes()
                return True
            except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.", e)
                self.connector.rollback()

    def update_client_payement(self, customer_name, customer_type, date, choosed_plan, status, payement_method, total):
        table_name = 'payment_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET payment_time = '" + date + "', choosed_plan= '" + choosed_plan +
                "' , status = '" + str(status) + "', payment_method = '" + payement_method + "', total= '" + str(
                    total) + "' WHERE customer_name = '" + \
                customer_name + "' AND  customer_type = '" + customer_type + "';")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def get_country_tva(self, country):
        table_name = 'country_tva'
        try:
            self.cursor.execute(
                "SELECT tva FROM " + table_name + " WHERE country='" + country + "';")

            return self.cursor.fetchone()
        except Exception as e:
            logger.warning("No tva for country %s" % country)
            self.connector.rollback()
            return ()

    def get_client_payment(self, customer, customer_type):
        table_name = 'payment_table'
        try:
            self.cursor.execute(
                "SELECT * FROM " + table_name + " WHERE customer_name='" + customer + "' AND customer_type='" + customer_type + "';")

            return self.cursor.fetchone()
        except Exception as e:
            logger.warning("No payment for client %s and domaine %s" % (customer, customer_type))
            self.connector.rollback()
            return ()

    def get_details_trainings(self, customer, customer_type):
        table_name = 'status_projects'
        try:
            self.cursor.execute(
                "SELECT training_details FROM " + table_name + " WHERE customer_name = '" + customer +
                "' AND  customer_type = '" + customer_type + "';")
        except Exception as e:
            logger.error("Error in getting counter %s" % e)
        return self.cursor.fetchall()

    def get_counter_post(self, customer, customer_type, date_start, date_fin):
        table_name = 'client_history_table'
        try:
            self.cursor.execute(
                "SELECT SUM(counter) FROM " + table_name + " WHERE customer_name = '" + customer
                + "' AND  customer_type = '" + customer_type + "' AND date BETWEEN '" + date_start + "' AND '" + date_fin +"';")
        except Exception as e:
            logger.error("Error in getting counter post %s" % e)
        return self.cursor.fetchone()

    def max_training_image(self, plan):
        table_name = 'plan'
        try:
            self.cursor.execute(
                "SELECT max_image_training FROM " + table_name + " WHERE plan_name = '" + plan + "';")
        except Exception as e:
            logger.error("Error in getting counter post %s" % e)
        return self.cursor.fetchone()

    def get_all_plans_payement(self, table_name):
        try:
            self.cursor.execute("SELECT * FROM " + table_name + ";")
            res = self.cursor.fetchall()
            return res

        except:
            self.connector.rollback()
            return None

    def update_status_name_deleted_project(self, project, status, customer_name, customer_type, project_to_delete, api):
        table_name = 'status_projects'

        try:

            self.cursor.execute("UPDATE " + table_name + " SET  status = '" + str(
                status) + "' , project = '" + project + "' WHERE customer_name = '" + customer_name +
                                "' AND  customer_type = '" + customer_type + "' AND name ='" + project_to_delete + "' AND api = '" + api + "';")
            self.commit_db_changes()
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is .......%s" % e)
            self.connector.rollback()

    def update_customer_name_payment_table(self, new_customer_name, customer_name, customer_type):
        table_name = 'payment_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  customer_name = '" + new_customer_name + "' WHERE customer_name = '" + \
                customer_name + "' AND customer_type = '" + customer_type + "' ;")
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def update_customer_name_history_table(self, new_customer_name, customer_name, customer_type):
        table_name = 'client_history_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  customer_name = '" + new_customer_name + "' WHERE customer_name = '" + \
                customer_name + "' AND customer_type = '" + customer_type + "' ;")
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def update_customer_name_cms_table(self,new_customer_name, customer_name, customer_type):
        table_name = 'cms_client_table'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  customer_name = '" + new_customer_name + "' WHERE customer_name = '" + \
                customer_name + "' AND customer_type = '" + customer_type + "' ;")
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def update_customer_name_projects_table(self,new_customer_name, customer_name, customer_type):
        table_name = 'status_projects'
        try:
            self.cursor.execute(
                "UPDATE " + table_name + " SET  customer_name = '" + new_customer_name + "' WHERE customer_name = '" + \
                customer_name + "' AND customer_type = '" + customer_type + "' ;")
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def rename_table_client(self, existing_name, new_name):
        try:
            self.cursor.execute(
                "ALTER TABLE " + existing_name + " RENAME TO " + new_name + " ;")
            logger.info("Updating values into table '" + table_name + "' successfully")
        except Exception as e:
            logger.warning("Updating table '" + table_name + "' failed. the exception is %s" % e)
            self.connector.rollback()

    def save_client_reviews(self, customer_name, customer_type, project_name, review, url_image):
        table_name = 'client_review'

        try:
                self.cursor.execute(
                    "INSERT INTO " + table_name + " (customer_name, customer_type, project_name, review, url_image) VALUES ('"
                    + customer_name + "','" + str(customer_type) + "','" + str(project_name) + "','" + str(review) + "','" + str(
                        url_image) + "');")
                logger.info("Inserting values into table '" + table_name + "' successfully")
                self.commit_db_changes()
                return True
        except Exception as e:
                logger.warning("Inserting into table '" + table_name + "' failed.", e)
                self.connector.rollback()
                return False

    def get_reviews(self, customer_name, customer_type):
            table_name = "client_review"
            try:
                self.cursor.execute("SELECT review, COUNT(review) FROM " + table_name + " WHERE customer_name = '" + customer_name +
                                    "' AND  customer_type = '" + customer_type + "' GROUP BY review;")
            except Exception as e:
                logger.error(
                    "Table " + table_name + " doesn't exist or problem during get project from status_projects table , exception is : %s" % e)
                self.connector.rollback()
                return None
            return self.cursor.fetchall()


    def create_payement_info(self):
        try:
            self.cursor.execute("CREATE TABLE payment_info" +
                                "("
                                "id BIGSERIAL PRIMARY KEY NOT NULL,"
                                "customer_name VARCHAR(1000),"
                                "customer_type VARCHAR(1000),"
                                "full_name VARCHAR(1000),"
                                "address VARCHAR(1000),"
                                "zip_code VARCHAR(1000),"
                                "country VARCHAR(1000),"
                                "city VARCHAR(1000)"
                                ");")
            logger.info("Creating table payment info successfully")
            self.commit_db_changes()
        except Exception as e:
            logger.warning("Table cms_client_table exist or problem during creating table , exception is : %s" % e)
            self.connector.rollback()

    def insert_or_update_payment_info(self, table_name, customer, customer_type, full_name, adress,zip_code, country, city):
            ch = "SELECT * FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "';"
            try:
                self.cursor.execute(ch)
            except Exception as e:
                logger.error(e)

            if self.cursor.fetchone() is None:
                self.cursor.execute(
                            "INSERT INTO " + table_name + " (customer_name, customer_type, full_name, address, "
                                                          "zip_code, country, city) VALUES ('" + customer +
                            "', '" + customer_type + "', '" + full_name + "', '" + adress + "', " + zip_code +
                            " , '" + country + "', '" + city + "')")

                self.commit_db_changes()
                logger.info("Inserting values into table '" + table_name + "' successfully")
            else:
                cccc = "UPDATE " + table_name + " SET address = '" + adress + "' ,full_name= '" + full_name +\
                       "' ,country= '" + country + "' ,city= '" + city + "' ,zip_code= '" + zip_code\
                       + "' WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "';"
                self.cursor.execute(cccc)
                self.commit_db_changes()
                logger.info("Updating values into table '" + table_name + "' successfully")

    def get_client_adress(self, table_name, customer, customer_type):
        query = "SELECT * FROM " + table_name + " WHERE customer_name = '" + customer + "' AND  customer_type = '" + customer_type + "';"

        try:
            self.cursor.execute(query)
        except:
            logger.error("Error getting client address")
            self.connector.rollback()
            return None
        return self.cursor.fetchone()
        # Insert value into history client

    def get_client_from_shop(self, table_name, shop):
        try:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE url_shop = '" + shop + "';")
            if self.cursor.fetchone() is None:
                return False
            else:
                return True

        except Exception as e:
            logger.error("Table " + table_name + "doesn't exist or problem during get"
                                                 " project from status_projects table , exception is : %s" % e)
            self.connector.rollback()
            return False

    def commit_db_changes(self):
        # Make the changes to the database persistent
        self.connector.commit()

    def close_connection(self):
        # Close communication with the database
        self.cursor.close()
        self.connector.close()
