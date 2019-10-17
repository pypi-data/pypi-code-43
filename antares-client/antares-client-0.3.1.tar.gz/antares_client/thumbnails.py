import os
import requests


THUMBNAIL_TYPES = ["template", "science", "difference"]
THUMBNAIL_URL = "http://antares.noao.edu/alerts/data/{alert_id}/thumbnails/{img_type}"


def get_thumbnails(alert_id, output_dir=None):
    """
    Download thumbnail images for a given ANTARES `alert_id`.

    If `output_dir` is given, save the files to that location.

    Returns a dict containing the three thumbnails, of structure:
    
    .. code:: json

       {
           'template': {
               'file_name': '...fits.gz',
               'file_bytes': '...'
           },
           'science': {
               'file_name': '...fits.gz',
               'file_bytes': '...'
           },
           'difference': {
               'file_name': '...fits.gz',
               'file_bytes': '...'
           }
       }

    Parameters
    ----------
    alert_id: int
        ANTARES Alert ID
    output_dir: str
        Output directory (optional, default None)

    Returns
    ----------
    dict

    Raises
    ----------
    requests.HTTPError
        If the server responds with a 4XX or 5XX status code

    """
    # Download image data
    results = {}
    for img_type in THUMBNAIL_TYPES:
        url = THUMBNAIL_URL.format(alert_id=alert_id, img_type=img_type)
        res = requests.get(url)
        res.raise_for_status()
        file_name = res.headers["Content-Disposition"].partition("=")[2]
        file_bytes = res.content
        results[img_type] = {"file_name": file_name, "file_bytes": file_bytes}

        # Output to file
        if output_dir:
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_bytes)

    return results
