import requests
import pandas as pd
import os


def login(username, password):
    """
    Returns a token that can be used to download controlled data. The token can also directly be copied from the iCGC
    web page.
    :param username: The ICGC username to log in
    :param password: The ICGC password to log in
    :return: Token token needed for the download of some specific data.
    """
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{"username":"' + username + '","password":"' + password + '"}'

    token = requests.post('https://dcc.icgc.org/api/v1/auth/login', headers=headers, data=data).json()['token']

    return token


def download_file_by_primary_site(filetype, primary_site, keep_file=False):
    """
    Returns a pandas DataFrame of the given file type for the given primary_site.
    :param filetype: File type the user wants to download. E.g. "ssm" or "cnsm".
    :param primary_site: Primary Site the user wants to filter for. E.g. "Blood" or "Liver".
    :param keep_file: True if the file should be saved in the directory. False if not.
    :return: Pandas DataFrame of the downloaded file.
    """
    filename = str(filetype) + "_" + primary_site + ".tsv.gz"
    params = (
        ('filters', '{"donor":{"primarySite":{"is":["' + primary_site + '"]}}}'),
        ('info', '[{"key":"' + filetype + '","value":"TSV"}]'),
    )
    download_id = requests.get('https://dcc.icgc.org/api/v1/download/submit', params=params).json()["downloadId"]
    response = requests.get('https://dcc.icgc.org/api/v1/download/' + download_id)
    open(filename, 'wb').write(response.content)
    df = pd.read_csv(filename, sep="\t", compression="gzip", low_memory=False)
    if not keep_file:
        os.remove(filename)

    return df


def download_data_release(params, cookies, filename, keep_file=False):
    """
    Helper function for some of the other methods. Downloads the data of a speciic data release.
    :param params: params to filter for
    :param cookies: cookies
    :param filename: the filename the user wants to download
    :param keep_file: True if the file should be saved in the directory. False if not.
    :return: Pandas DataFrame of the downloaded file.
    """
    response = requests.get('https://dcc.icgc.org/api/v1/download', params=params, cookies=cookies)
    open(filename, 'wb').write(response.content)
    df = pd.read_csv(filename, sep="\t", compression="gzip", low_memory=False)
    if not keep_file:
        os.remove(filename)
    return df


def download_file_by_project(token, release, project_code, filetype, status="controlled", keep_file=False):
    """
    Returns a pandas DataFrame of the given project and filetype.
    :param token: The ICGC access token of the ICGC user page or got by the login method.
    :param release: The release version the data should be downloaded from.
    :param project_code: The project code of the project. E.g. "ALL-US"
    :param filetype: The filetype the user wants to download. E.g. "simple_somatic_mutation" or
    "copy_number_somatic_mutation"
    :param status: The status of the data. Either "controlled" or "open"
    :param keep_file: True if the file should be saved in the directory. False if not.
    :return: Pandas DataFrame of the downloaded file.
    """
    filename = filetype + "_" + str(release) + "_" + project_code + "_" + status + ".tsv.gz"

    cookies = {
        'dcc_portal_token': str(token),
    }

    params = (
        ('fn', '/release_' + str(release) +
         '/Projects/' + str(project_code) +
         '/' + filetype + '.' + status + '.' +
         str(project_code) + '.tsv.gz'),
    )

    try:
        df = download_data_release(params, cookies, filename, keep_file)
    except:
        try:
            params = (
                ('fn', '/release_' + str(release) +
                 '/Projects/' + str(project_code) +
                 '/' + filetype + '.' + "open" + '.' +
                 str(project_code) + '.tsv.gz'),
            )
            df = download_data_release(params, cookies, filename, keep_file)
        except:
            params = (
                ('fn', '/release_' + str(release) +
                 '/Projects/' + str(project_code) +
                 '/' + filetype + '.' +
                 str(project_code) + '.tsv.gz'),
            )
            df = download_data_release(params, cookies, filename, keep_file)

    return df


def download_donor_summary(token, release, keep_file=False):
    """
    Returns a pandas DataFrame of the given donor summary file.
    :param token: The ICGC access token of the ICGC user page or got by the login method.
    :param filetype: The filetype the user wants to download. E.g. "simple_somatic_mutation" or
    "copy_number_somatic_mutation"
    :param release: The release version the data should be downloaded from.
    :param keep_file: True if the file should be saved in the directory. False if not.
    :return: Pandas DataFrame of the given donor summary file.
    """
    filename = "donor.all_projects.tsv.gz"

    cookies = {
        'dcc_portal_token': str(token),
    }

    params = (
        ('fn', '/release_' + str(release) +
         '/Summary/' + filename),
    )

    return download_data_release(params, cookies, filename, keep_file)
