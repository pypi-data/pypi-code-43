import logging
import os
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

import finance_scraping.aws as aws


def validate_urls(urls):
    """
    Make sure each URL in a list starts with 'http://' and is not empty,
    which can happen when reading URLs from a file.

    :param list(str) urls: list of URLs
    :return list(str): list of validated URLs
    """
    validated = []

    for u in urls:
        if u.startswith('http://'):
            validated.append(u)

        elif u.startswith('www.'):
            validated.append(f'http://{u}')

        else:
            continue

    return validated


def get_urls(bucket, urls_key, aws_profile=None):
    """
    Get the list of URLs to scrape from a text file stored in S3.

    :param str bucket: AWS S3 bucket where the file containing URLS is stored
    :param str urls_key: AWS S3 key to the file containing URLs
    :param str aws_profile: AWS profile to use (default None)
    :return list(str): list of URLs
    """
    data = aws.download_s3_object(
        bucket,
        urls_key,
        aws_profile
    )

    text = data.decode()
    urls = text.split(os.linesep)
    validated = validate_urls(urls)
    return validated


def get_session(max_retries, backoff_factor, retry_on):
    """
    Get session object for HTTP requests.

    To have granular control on request retries, we define a 'Retry' object
    from urllib3 and use it as a parameter for the HTTP adapter mounted on the
    Session object.

    :param int max_retries: maximum number of retries on HTTP request failure
    :param float backoff_factor: delay backoff factor for HTTP request retries
    :param list(int) retry_on: HTTP status codes allowing HTTP request retry
    :return requests.Session: session object
    """
    session = requests.Session()

    retry = Retry(
        total=max_retries,
        read=max_retries,
        connect=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=retry_on
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def download_page_contents(
        session,
        url,
        user_agent,
        timeout,
        max_retries
):
    """
    Download the contents of a web page.

    If the server's response was 200 return the text part of the response.
    If the response is not 200 and not one of the status codes the Session
    object is programmed to retry on (typically 500, 502 and 504), send the
    status code.
    We catch other unexpected errors and retry a maximum of 10 times.

    :param requests.Session: Session object
    :param str url: page URL
    :param str user_agent: custome user-agent to put in request headers
    :param int timeout: allowed period for the server to respond (seconds)
    :param int max_retries: maximum number of retries on HTTP request failure
    :return str: web page content
    """
    headers = {'User-Agent': user_agent}

    while max_retries > 0:

        try:
            response = session.get(url, timeout=timeout, headers=headers)
            if response.ok:
                logging.info(f'scraped {url}')
                return response.text

            else:
                msg = f'scraping failed: {response.status_code} for {url}'
                logging.error(msg)
                return

        except Exception as e:
            msg = f'scraping failed: {e} for {url}'
            logging.error(msg)
            max_retries -= 1
            time.sleep(10)


def get_security_id(url):
    """
    Get security ID from the URL where financial information about this
    security is displayed, using a regular expression.

    :param str url: url of the company's page
    :return str: ID of the security
    """
    result = re.search('(?<=&id=).{10}', url)
    return result.group(0)
