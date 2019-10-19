# Basic imports
import io
import numpy as np
from urllib.request import urlopen
from PIL import Image

# 3-rd party imports
from PyQt5.QtCore import QFile, QIODevice
import rasterio

def loadImg(path):
    """
    ----------
    Parameters
    ----------
    path : str
           path to the image file 

    -------
    Returns
    -------
    npImg : 3-d ndarray encoded in UINT8

    """

    rasObj = rasterio.open(path)
    nCh = rasObj.count
    if nCh < 3:
        npImg = np.zeros((rasObj.height, rasObj.width, 3), dtype="uint8")
        for i in range(3):
            npImg[:, :, i] = rasObj.read(1)
    else:
        npImg = np.zeros((rasObj.height, rasObj.width, nCh), dtype="uint8")
        for i in range(nCh):
            npImg[:, :, i] = rasObj.read(i + 1)

    return npImg


def loadImgWeb(URL):
    """
    ----------
    Parameters
    ----------
    URL : str
          URL to the UINT8-encoded image file 

    -------
    Returns
    -------
    npImg : 3-d ndarray encoded in UINT8

    """

    with urlopen(URL)as url:
        file = io.BytesIO(url.read())
        npImg = np.array(Image.open(file), dtype="uint8")

    return npImg


def loadMap(path):
    """
    ----------
    Parameters
    ----------
    path : str
           path to the csv file 

    -------
    Returns
    -------
    pdMap : Pandas dataframe or None if path is empty

    """

    try:
        pdMap = pd.read_csv(path, header=None)
    except:
        pdMap = None

    return pdMap


def saveQImg(qimg, path):
    """
    ----------
    Parameters
    ----------
    qimg : qimage
            
    path : str
           path to the destination
    -------
    Returns
    -------
    None

    """
    
    qfile = QFile(path + ".jpg")
    qfile.open(QIODevice.WriteOnly)
    qimg.save(qfile, "JPG")
    qfile.close()
