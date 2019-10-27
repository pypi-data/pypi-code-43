"""
Gvision core.
"""
from typing import Union, List, Set, Dict

from google.cloud import vision
from google.cloud.vision import types
from google.oauth2 import service_account


def format_confidence(confidence: Union[str, float]) -> float:
    """Takes a confidence from the API like 
       0.55623 and returns 55.6 (%).
    """
    return round(float(confidence) * 100, 1)


def get_box(normalized_vertices: List):
    """
    Return the relative bounxing box coordinates
    defined by the tuple (y_min, x_min, y_max, x_max)
    where the coordinates are floats in the range [0.0, 1.0] and
    relative to the width and height of the image.
    """
    y = []
    x = []
    for box in normalized_vertices:
        y.append(box.y)
        x.append(box.x)

    box = [min(set(y)), min(set(x)), max(set(y)), max(set(x))]

    rounding_decimals = 5
    box = [round(coord, rounding_decimals) for coord in box]
    return box


def get_objects(objects: List[types.LocalizedObjectAnnotation]) -> List[str]:
    """
    Get a list of the unique objects predicted.
    """
    labels = [obj.name.lower() for obj in objects]
    return list(set(labels))


def get_object_confidences(objects: List[types.LocalizedObjectAnnotation], target: str):
    """
    Return the list of confidences of instances of target label.
    """
    confidences = [
        format_confidence(obj.score) for obj in objects if obj.name.lower() == target
    ]
    return confidences


def get_objects_summary(objects: List[types.LocalizedObjectAnnotation]):
    """
    Get a summary of the objects detected.
    """
    objects_labels = get_objects(objects)
    return {
        target: len(get_object_confidences(objects, target))
        for target in objects_labels
    }


class Vision(object):
    """Interact with Google Vision."""

    def __init__(self, api_key_file):
        credentials = service_account.Credentials.from_service_account_file(
            api_key_file
        )
        scoped_credentials = credentials.with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"]
        )
        self._client = vision.ImageAnnotatorClient(credentials=scoped_credentials)

    def object_localization(self, image_bytes):
        """Return the list of objects in an image from the imge bytes."""
        return self._client.object_localization(image=types.Image(content=image_bytes))
