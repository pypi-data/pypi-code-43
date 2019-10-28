from skimage.feature import greycomatrix, greycoprops
import numpy as np

@staticmethod
def texture_features(distances, angles, properties, image):
    """
    @brief Calc the texture properties of a greyscale image

    Calculate the property passed as parameter of the function.
    ref: http://scikit-image.org/docs/0.7.0/api/skimage.feature.texture.html

    :param distances: List of pixel pair distance offsets
    :param angles: List of pixel pair angles in radians.
    :param properties: Array of Strings. The feature that you want to calculate. 'contrast', 'dissimilarity'
    'homogeneity', 'ASM', 'energy', 'correlation'.
    :param image: Greyscale image in uint8
    :return:
    """
    glcm = greycomatrix(image, distances=distances, angles=angles, symmetric=True, normed=True)

    return np.hstack([greycoprops(glcm, prop).ravel() for prop in properties])

