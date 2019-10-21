import gvision.core as gvision
import pytest

RAW_CONFIDENCE = 0.9225577712059021


def test_format_confidence():
    assert gvision.format_confidence(RAW_CONFIDENCE) == 92.3
