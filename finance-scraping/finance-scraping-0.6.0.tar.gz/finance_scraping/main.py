import csv
from datetime import datetime
from io import BytesIO, StringIO
import logging
import os
import time
from zipfile import ZIP_DEFLATED, ZipFile

from finance_scraping import (
    aws,
    config,
    loading,
    parsing_html,
    scraping,
    utils
)

LOG_FILE_NAME = 'finance-scraping.log'
RAW_PAGES_S3_PREFIX = 'raw-page-content'
RAW_PAGES_S3_SUFFIX = 'archive.zip'
SECURITY_REPORT_S3_PREFIX = 'parsed-page-data'
SECURITY_REPORT_S3_SUFFIX = 'security_report.csv'
CSV_HEADER = [
    'company_name',
    'capital',
    'date',
    'time',
    'last_quote',
    'last_close',
    'daily_change_abs',
    'daily_change_rel',
    'bid',
    'offer',
    'low',
    'high',
    'day_volume',
    'p_e',
    'yield_percent',
    'collection_date'
]
CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS {} (
    company_name VARCHAR,
    capital FLOAT,
    date DATE,
    time TIME,
    last_quote FLOAT,
    last_close FLOAT,
    daily_change_abs FLOAT,
    daily_change_rel FLOAT,
    bid FLOAT,
    offer FLOAT,
    low FLOAT,
    high FLOAT,
    day_volume FLOAT,
    p_e FLOAT,
    yield_percent FLOAT,
    collection_date DATE
    );"""


def setup_logging(log_file):
    """
    Setup logging.
    """
    fmt = '%(asctime)s %(levelname)s: %(message)s'
    log_file_path = os.path.join(os.environ['HOME'], log_file)

    logging.basicConfig(
        filename=log_file_path,
        format=fmt,
        filemode='a',
        level=logging.INFO
    )


def extract():
    """
    Perform the extraction steps of webscraping:
        - download raw pages contents
        - zip data
        - upload zipped archive to AWS S3

    This function takes no parameters since all parameters are collected from
    environment variables.
    """
    # collect functions parameters from environment variables
    params = config.get_environment_variables()
    bucket = params['AWS']['data_bucket']
    profile = params['AWS']['profile']

    # get list of urls to scrape
    urls_list = scraping.get_urls(
        bucket,
        params['SCRAPING']['urls_s3_key'],
        profile
    )

    session = scraping.get_session(
        params['REQUESTS']['max_retries'],
        params['REQUESTS']['backoff_factor'],
        params['REQUESTS']['retry_on']
    )

    # open a ZipFile archive to be stored in memory
    zip_file_object = BytesIO()
    zip_archive = ZipFile(zip_file_object, 'a', compression=ZIP_DEFLATED)

    # iterate through URL and download page content
    logging.info('scraping started')

    for url in urls_list:

        results = scraping.download_page_contents(
            session,
            url,
            params['REQUESTS']['user_agent'],
            params['REQUESTS']['timeout'],
            params['REQUESTS']['max_retries']
        )

        # if page scraping was successful
        # zip page contents as a text file in an archive
        if results is not None:
            text_buffer = StringIO(results)
            security_id = scraping.get_security_id(url)
            zip_archive.writestr(f'{security_id}.txt', text_buffer.getvalue())

        time.sleep(0.5)

    zip_archive.close()

    # upload ZIP archive containing raw page contents to S3
    date = datetime.today().strftime('%Y/%m/%d')
    archive_key = aws.get_s3_key(
        RAW_PAGES_S3_PREFIX,
        RAW_PAGES_S3_SUFFIX,
        date
    )
    msg = f"uploading pages contents to s3://{bucket}/{archive_key}"
    logging.info(msg)

    aws.upload_object_to_s3(
        zip_file_object,
        bucket,
        archive_key,
        profile
    )

    logging.info('scraping finished')


def transform(date=None):
    """
    Perform the transform step of the pipeline:
        - download and unzip raw page archive from AWS S3
        - parse page contents to retrieve financial data
        - write data as a CSV file
        - upload CSV to S3

    AWS parameters are collected from environment variables.
    If you want to transform data collected at a date other than today,
    pass the 'date' argument.

    :param str date: date corresponding to the data to process,
                     optional (default None)
    """
    if not date:
        date = datetime.today().strftime('%Y/%m/%d')
    else:
        date = utils.format_date(date)

    # collect functions parameters from environment variables
    params = config.get_environment_variables()
    bucket = params['AWS']['data_bucket']
    profile = params['AWS']['profile']

    # download raw web pages contents
    archive_key = aws.get_s3_key(
        RAW_PAGES_S3_PREFIX,
        RAW_PAGES_S3_SUFFIX,
        date
    )

    logging.info(f'downloading raw pages {archive_key} from bucket {bucket}')

    raw_pages_zip = aws.download_s3_object(
        bucket,
        archive_key,
        profile
    )

    # we will unzip web pages contents in memory
    logging.info('reading raw pages archive')
    zip_data = BytesIO(raw_pages_zip)
    zip_obj = ZipFile(zip_data, 'r')

    # we will write data parsed from the web page to a csv in memory
    # 1 page = 1 row
    csv_obj = StringIO()
    writer = csv.DictWriter(csv_obj, CSV_HEADER, lineterminator='\n')
    writer.writeheader()

    # loop through files in the archive (1 file = 1 web page)
    for file_name in zip_obj.namelist():

        logging.info(f'parsing {file_name}')

        # extract file content, parse HTML code, write to csv
        page_contents = zip_obj.read(file_name).decode()
        parsed = parsing_html.parse_webpage(page_contents, date)
        writer.writerow(parsed)

    csv_key = aws.get_s3_key(
        SECURITY_REPORT_S3_PREFIX,
        SECURITY_REPORT_S3_SUFFIX,
        date
    )

    logging.info(f'uploading file {csv_key} to bucket {bucket}')
    aws.upload_object_to_s3(
        csv_obj,
        bucket,
        csv_key,
        profile
    )

    logging.info('transform finished')


def load(date=None):
    """
    Load the CSV file containing security data into the database.

    :param str date: date of security data collection, optional (default None)
    """
    if not date:
        date = datetime.today().strftime('%Y/%m/%d')
    else:
        date = utils.format_date(date)

    # collect functions parameters from environment variables
    params = config.get_environment_variables()
    bucket = params['AWS']['data_bucket']
    profile = params['AWS']['profile']
    con_params = params['DATABASE']
    database = con_params['database']
    table_name = con_params['table']

    # create table if exists
    logging.info(f"creating table '{table_name}' if not exists")
    con = loading.get_connection(con_params)
    loading.execute_sqls([(CREATE_TABLE_SQL.format(table_name), ())], con)

    # to make the 'load' step idempotent, we check if data for the specified
    # date is already in the database, if it is we either stop or delete and
    # load again
    con = loading.get_connection(con_params)
    loading.check_table_for_loaded_data(table_name, date, con)

    # download CSV file to be loaded and remove header
    csv_key = aws.get_s3_key(
        SECURITY_REPORT_S3_PREFIX,
        SECURITY_REPORT_S3_SUFFIX,
        date
    )
    logging.info(f"downloading '{csv_key}' from S3 bucket '{bucket}'")
    csv_data = aws.download_s3_object(
        bucket,
        csv_key,
        profile
    )
    csv_no_header = utils.remove_header(csv_data.decode())

    # load the whole CSV at once
    logging.info(
        f"loading data into database '{database}' "
        f"in table '{table_name}'"
    )
    con = loading.get_connection(con_params)
    loading.copy_into(
        file_object=StringIO(csv_no_header),
        table_name=table_name,
        connection=con
    )
    logging.info('loading finished')


def main():
    """
    Run the entire ETL pipeline.
    """
    args = utils.parse_cli()

    if args.configure:
        config.configure()

    elif args.build:
        config.terraform_configure()
        config.terraform_build()

    setup_logging(LOG_FILE_NAME)

    if args.extract:
        extract()

    if args.transform:
        transform(args.date)

    if args.load:
        load(date=args.date)

    elif args.nuke:
        answer = input('Are you sure you want to destroy the infrastructure? \
(yes/no): ')
        if answer == 'yes':
            config.terraform_nuke()
        else:
            print('The infrastructure will not be destroyed.')


if __name__ == '__main__':
    main()
