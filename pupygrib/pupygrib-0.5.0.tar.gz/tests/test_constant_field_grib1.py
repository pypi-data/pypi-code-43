"""Regression tests for reading constant_field.grib1."""

import numpy
from numpy.testing import assert_allclose
import pytest
from pytest import approx


gribfile = "data/constant_field.grib1"


class TestIndicatorSection:

    section_number = 0
    fieldnames = {"identifier", "editionNumber", "totalLength"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_identifier(self, section):
        assert section.identifier == b"GRIB"

    def test_totalLength(self, section):
        assert section.totalLength == 102

    def test_editionNumber(self, section):
        assert section.editionNumber == 1


class TestProductDefinitionSection:

    section_number = 1
    fieldnames = {
        "section1Length",
        "table2Version",
        "centre",
        "generatingProcessIdentifier",
        "gridDefinition",
        "section1Flags",
        "indicatorOfParameter",
        "indicatorOfTypeOfLevel",
        "level",
        "yearOfCentury",
        "month",
        "day",
        "hour",
        "minute",
        "unitOfTimeRange",
        "P1",
        "P2",
        "timeRangeIndicator",
        "numberIncludedInAverage",
        "numberMissingFromAveragesOrAccumulations",
        "centuryOfReferenceTimeOfData",
        "subCentre",
        "decimalScaleFactor",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section1Length(self, section):
        assert section.section1Length == 28

    def test_table2Version(self, section):
        assert section.table2Version == 1

    def test_centre(self, section):
        assert section.centre == 96

    def test_generatingProcessIdentifier(self, section):
        assert section.generatingProcessIdentifier == 1

    def test_gridDefinition(self, section):
        assert section.gridDefinition == 255

    def test_section1Flags(self, section):
        assert section.section1Flags == 128

    def test_indicatorOfParameter(self, section):
        assert section.indicatorOfParameter == 51

    def test_indicatorOfTypeOfLevel(self, section):
        assert section.indicatorOfTypeOfLevel == 109

    def test_level(self, section):
        assert section.level == 1

    def test_yearOfCentury(self, section):
        assert section.yearOfCentury == 6

    def test_month(self, section):
        assert section.month == 12

    def test_day(self, section):
        assert section.day == 5

    def test_hour(self, section):
        assert section.hour == 12

    def test_minute(self, section):
        assert section.minute == 0

    def test_unitOfTimeRange(self, section):
        assert section.unitOfTimeRange == 1

    def test_P1(self, section):
        assert section.P1 == 6

    def test_P2(self, section):
        assert section.P2 == 0

    def test_timeRangeIndicator(self, section):
        assert section.timeRangeIndicator == 0

    def test_numberIncludedInAverage(self, section):
        assert section.numberIncludedInAverage == 0

    def test_numberMissingFromAveragesOrAccumulations(self, section):
        assert section.numberMissingFromAveragesOrAccumulations == 0

    def test_centuryOfReferenceTimeOfData(self, section):
        assert section.centuryOfReferenceTimeOfData == 21

    def test_subCentre(self, section):
        assert section.subCentre == 0

    def test_decimalScaleFactor(self, section):
        assert section.decimalScaleFactor == 0


class TestGridDescriptionSection:

    section_number = 2
    fieldnames = {
        "section2Length",
        "numberOfVerticalCoordinateValues",
        "pvlLocation",
        "dataRepresentationType",
        "Ni",
        "Nj",
        "latitudeOfFirstGridPoint",
        "longitudeOfFirstGridPoint",
        "resolutionAndComponentFlags",
        "latitudeOfLastGridPoint",
        "longitudeOfLastGridPoint",
        "iDirectionIncrement",
        "jDirectionIncrement",
        "scanningMode",
        "latitudeOfSouthernPole",
        "longitudeOfSouthernPole",
        "angleOfRotationInDegrees",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section2Length(self, section):
        assert section.section2Length == 50

    def test_numberOfVerticalCoordinateValues(self, section):
        assert section.numberOfVerticalCoordinateValues == 2

    def test_pvlLocation(self, section):
        assert section.pvlLocation == 43

    def test_dataRepresentationType(self, section):
        assert section.dataRepresentationType == 10

    def test_Ni(self, section):
        assert section.Ni == 248

    def test_Nj(self, section):
        assert section.Nj == 400

    def test_latitudeOfFirstGridPoint(self, section):
        assert section.latitudeOfFirstGridPoint == -13250

    def test_longitudeOfFirstGridPoint(self, section):
        assert section.longitudeOfFirstGridPoint == 5750

    def test_resolutionAndComponentFlags(self, section):
        assert section.resolutionAndComponentFlags == 136

    def test_latitudeOfLastGridPoint(self, section):
        assert section.latitudeOfLastGridPoint == 26650

    def test_longitudeOfLastGridPoint(self, section):
        assert section.longitudeOfLastGridPoint == 30450

    def test_iDirectionIncrement(self, section):
        assert section.iDirectionIncrement == 100

    def test_jDirectionIncrement(self, section):
        assert section.jDirectionIncrement == 100

    def test_scanningMode(self, section):
        assert section.scanningMode == 64

    def test_latitudeOfSouthernPole(self, section):
        assert section.latitudeOfSouthernPole == -22000

    def test_longitudeOfSouthernPole(self, section):
        assert section.longitudeOfSouthernPole == -40000

    def test_angleOfRotationInDegrees(self, section):
        assert section.angleOfRotationInDegrees == 0


class TestBinaryDataSection:

    section_number = 4
    fieldnames = {
        "section4Length",
        "dataFlag",
        "binaryScaleFactor",
        "referenceValue",
        "bitsPerValue",
        "values",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section4Length(self, section):
        assert section.section4Length == 12

    def test_dataFlag(self, section):
        assert section.dataFlag == 8

    def test_binaryScaleFactor(self, section):
        assert section.binaryScaleFactor == -17

    def test_referenceValue(self, section):
        assert section.referenceValue == approx(1.8499522e-06)

    def test_bitsPerValue(self, section):
        assert section.bitsPerValue == 0

    def test_values(self, section):
        assert section.values is None


class TestEndSection:

    section_number = 5
    fieldnames = {"endOfMessage"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_endOfMessage(self, section):
        assert section.endOfMessage == b"7777"


@pytest.fixture(scope="module")
def target_longitudes():
    return numpy.tile(numpy.linspace(5.75, 30.45, 248), (400, 1))


@pytest.fixture(scope="module")
def target_latitudes():
    lats = numpy.linspace(26.65, -13.25, 400)
    return numpy.tile(lats.reshape((400, 1)), (1, 248))


@pytest.fixture(scope="module")
def target_values():
    return numpy.full((400, 248), 1.8499522e-06)


class TestMessage:
    def test_longitudes(self, message, target_longitudes):
        longitudes, _ = message.get_coordinates()
        assert_allclose(longitudes, target_longitudes)

    def test_latitudes(self, message, target_latitudes):
        _, latitudes = message.get_coordinates()
        assert_allclose(latitudes, target_latitudes)

    def test_values(self, message, target_values):
        values = message.get_values()
        assert_allclose(values, target_values)
