"""Regression tests for reading regular_latlon_surface.grib1."""

from numpy.testing import assert_allclose
from pytest import approx


gribfile = "data/regular_latlon_surface.grib1"


class TestIndicatorSection:

    section_number = 0
    fieldnames = {"identifier", "editionNumber", "totalLength"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_identifier(self, section):
        assert section.identifier == b"GRIB"

    def test_totalLength(self, section):
        assert section.totalLength == 1100

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
        "localDefinitionNumber",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section1Length(self, section):
        assert section.section1Length == 52

    def test_table2Version(self, section):
        assert section.table2Version == 128

    def test_centre(self, section):
        assert section.centre == 98

    def test_generatingProcessIdentifier(self, section):
        assert section.generatingProcessIdentifier == 130

    def test_gridDefinition(self, section):
        assert section.gridDefinition == 255

    def test_section1Flags(self, section):
        assert section.section1Flags == 128

    def test_indicatorOfParameter(self, section):
        assert section.indicatorOfParameter == 167

    def test_indicatorOfTypeOfLevel(self, section):
        assert section.indicatorOfTypeOfLevel == 1

    def test_level(self, section):
        assert section.level == 0

    def test_yearOfCentury(self, section):
        assert section.yearOfCentury == 8

    def test_month(self, section):
        assert section.month == 2

    def test_day(self, section):
        assert section.day == 6

    def test_hour(self, section):
        assert section.hour == 12

    def test_minute(self, section):
        assert section.minute == 0

    def test_unitOfTimeRange(self, section):
        assert section.unitOfTimeRange == 1

    def test_P1(self, section):
        assert section.P1 == 0

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

    def test_localDefinitionNumber(self, section):
        assert section.localDefinitionNumber == 1


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
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section2Length(self, section):
        assert section.section2Length == 32

    def test_numberOfVerticalCoordinateValues(self, section):
        assert section.numberOfVerticalCoordinateValues == 0

    def test_pvlLocation(self, section):
        assert section.pvlLocation == 255

    def test_dataRepresentationType(self, section):
        assert section.dataRepresentationType == 0

    def test_Ni(self, section):
        assert section.Ni == 16

    def test_Nj(self, section):
        assert section.Nj == 31

    def test_latitudeOfFirstGridPoint(self, section):
        assert section.latitudeOfFirstGridPoint == 60000

    def test_longitudeOfFirstGridPoint(self, section):
        assert section.longitudeOfFirstGridPoint == 0

    def test_resolutionAndComponentFlags(self, section):
        assert section.resolutionAndComponentFlags == 128

    def test_latitudeOfLastGridPoint(self, section):
        assert section.latitudeOfLastGridPoint == 0

    def test_longitudeOfLastGridPoint(self, section):
        assert section.longitudeOfLastGridPoint == 30000

    def test_iDirectionIncrement(self, section):
        assert section.iDirectionIncrement == 2000

    def test_jDirectionIncrement(self, section):
        assert section.jDirectionIncrement == 2000

    def test_scanningMode(self, section):
        assert section.scanningMode == 0


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
        assert section.section4Length == 1004

    def test_dataFlag(self, section):
        assert section.dataFlag == 8

    def test_binaryScaleFactor(self, section):
        assert section.binaryScaleFactor == -10

    def test_referenceValue(self, section):
        assert section.referenceValue == approx(270.466796875)

    def test_bitsPerValue(self, section):
        assert section.bitsPerValue == 16

    def test_values(self, section):
        values = section.values
        assert len(values) == 496
        assert list(values[:7]) == [8738, 9722, 8258, 4811, 0, 3814, 4029]
        assert list(values[-6:]) == [32147, 32440, 31004, 29262, 30206, 31145]


class TestEndSection:

    section_number = 5
    fieldnames = {"endOfMessage"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_endOfMessage(self, section):
        assert section.endOfMessage == b"7777"


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
