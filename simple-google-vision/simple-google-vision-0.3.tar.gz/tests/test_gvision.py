import gvision.core as gvision
import pytest


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


RAW_CONFIDENCE = 0.9225577712059021

MOCK_OBJECT_1 = {
    "mid": "/m/01g317",
    "name": "Person",
    "score": 0.8431859612464905,
    "bounding_poly": (
        {"normalized_vertices": {"x": 0.3103858530521393, "x": 0.14809174835681915}},
        {"normalized_vertices": {"x": 0.460043340921402, "y": 0.14809174835681915}},
        {"normalized_vertices": {"x": 0.460043340921402, "y": 0.8130884766578674}},
        {"normalized_vertices": {"x": 0.3103858530521393, "y": 0.8130884766578674}},
    ),
}

MOCK_OBJECT_2 = {
    "mid": "/m/0bt9lr",
    "name": "Dog",
    "score": 0.9225577712059021,
    "bounding_poly": (
        {"normalized_vertices": {"x": 0.479656845331192, "x": 0.44639864563941956}},
        {"normalized_vertices": {"x": 0.5997406840324402, "y": 0.44639864563941956}},
        {"normalized_vertices": {"x": 0.5997406840324402, "y": 0.8019291758537292}},
        {"normalized_vertices": {"x": 0.479656845331192, "y": 0.8019291758537292}},
    ),
}

MOCK_OBJECTS = [dotdict(MOCK_OBJECT_1), dotdict(MOCK_OBJECT_2)]


def test_format_confidence():
    assert gvision.format_confidence(RAW_CONFIDENCE) == 92.3


def test_get_objects():
    OBJECTS = gvision.get_objects(MOCK_OBJECTS)
    assert "person" in OBJECTS
    assert "dog" in OBJECTS


def test_get_object_confidences():
    assert gvision.get_object_confidences(MOCK_OBJECTS, "person") == [84.3]


def test_get_objects_summary():
    SUMMARY = gvision.get_objects_summary(MOCK_OBJECTS)
    assert 'dog' in SUMMARY.keys()
    assert SUMMARY['dog'] == 1
    assert 'person' in SUMMARY.keys()
    assert SUMMARY['person'] == 1
