import os
from os.path import dirname, join
import subprocess


def get_environment_variables():
    """
    Read the configuration from the environment variables.

    :return dict[dict]: configuration
    """
    configuration = {}

    configuration['AWS'] = {
        'data_bucket': os.getenv('FINANCE_SCRAPING_S3_BUCKET'),
        'profile': os.getenv('FINANCE_SCRAPING_AWS_PROFILE')
    }
    # set AWS profile to None if user typed 'None'
    if configuration['AWS']['profile'] == 'None':
        configuration['AWS']['profile'] = None

    configuration['REQUESTS'] = {
        'user_agent': os.getenv('FINANCE_SCRAPING_USER_AGENT'),
        'max_retries': int(os.getenv('FINANCE_SCRAPING_MAX_RETRIES')),
        'backoff_factor': float(os.getenv('FINANCE_SCRAPING_BACKOFF_FACTOR')),
        'retry_on': tuple(
            map(int, os.getenv('FINANCE_SCRAPING_RETRY_ON').split(','))),
        'timeout': int(os.getenv('FINANCE_SCRAPING_TIMEOUT'))
    }

    configuration['SCRAPING'] = {
        'urls_s3_key': os.getenv('FINANCE_SCRAPING_URLS_S3_KEY')}

    configuration['DATABASE'] = {
        'database': os.getenv('FINANCE_SCRAPING_DB_NAME'),
        'table': os.getenv('FINANCE_SCRAPING_DB_TABLE'),
        'db_user': os.getenv('FINANCE_SCRAPING_DB_USERNAME'),
        'password': os.getenv('FINANCE_SCRAPING_DB_PASSWORD'),
        'host': os.getenv('FINANCE_SCRAPING_HOST'),
        'port': os.getenv('FINANCE_SCRAPING_PORT'),
    }

    return configuration


def configure():
    """
    Run BASH configuration script.
    """
    config_file_path = join(
        dirname(__file__),
        join('scripts', 'configure.sh'))
    try:
        subprocess.run(['bash', config_file_path])
    # ProcessLookupError happens if you hit ctrl+c
    except (KeyboardInterrupt, ProcessLookupError):
        msg = (
            "\nConfiguration may be incomplete, "
            "run 'finance-scraping -c' again.")
        print(msg)


def terraform_configure():
    """
    Run BASH configuration script to store Terraform environment variables.
    """
    config_file_path = join(
        dirname(__file__),
        join('scripts', 'terraform_configure.sh'))
    try:
        subprocess.run(['bash', config_file_path])
    except (KeyboardInterrupt, ProcessLookupError):
        msg = (
            "\nConfiguration may be incomplete, "
            "run 'finance-scraping --build' again.")
        print(msg)


def terraform_build():
    """
    Builds the infrastructure for the scraper ETL in AWS with Terraform.
    """
    build_file_path = join(
        dirname(__file__),
        join('scripts', 'terraform_build.sh'))
    env = os.environ
    env['BASH_ENV'] = os.path.join(env['HOME'], '.bash_non_interactive')
    try:
        subprocess.run(['bash', build_file_path], env=env)
    except (KeyboardInterrupt, ProcessLookupError):
        msg = (
            "\nConfiguration may be incomplete, "
            "run 'finance-scraping --build' again.")
        print(msg)


def terraform_nuke():
    """
    Destroy the infrastructure for the scraper ETL in AWS with Terraform.
    """
    nuke_file_path = join(
        dirname(__file__),
        join('scripts', 'terraform_nuke.sh'))
    env = os.environ
    env['BASH_ENV'] = os.path.join(env['HOME'], '.bash_non_interactive')
    try:
        subprocess.run(['bash', nuke_file_path])
    except (KeyboardInterrupt, ProcessLookupError):
        msg = (
            "\nDestruction may be incomplete, "
            "run 'finance-scraping --nuke' again.")
        print(msg)
