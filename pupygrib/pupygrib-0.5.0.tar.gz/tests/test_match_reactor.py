"""Regression tests for reading match_reactor.grib."""

from numpy.testing import assert_allclose
from pytest import approx


gribfile = "data/match_reactor.grib"


class TestIndicatorSection:

    section_number = 0
    fieldnames = {"identifier", "editionNumber", "totalLength"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_identifier(self, section):
        assert section.identifier == b"GRIB"

    def test_totalLength(self, section):
        assert section.totalLength == 2834

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
        "generatingProcess",
        "sort",
        "timeRepres",
        "landType",
        "suplScale",
        "molarMass",
        "logTransform",
        "threshold",
        "totalSizeClasses",
        "sizeClassNumber",
        "integerScaleFactor",
        "lowerRange",
        "upperRange",
        "meanSize",
        "STDV",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section1Length(self, section):
        assert section.section1Length == 80

    def test_table2Version(self, section):
        assert section.table2Version == 139

    def test_centre(self, section):
        assert section.centre == 82

    def test_generatingProcessIdentifier(self, section):
        assert section.generatingProcessIdentifier == 1

    def test_gridDefinition(self, section):
        assert section.gridDefinition == 255

    def test_section1Flags(self, section):
        assert section.section1Flags == 192

    def test_indicatorOfParameter(self, section):
        assert section.indicatorOfParameter == 250

    def test_indicatorOfTypeOfLevel(self, section):
        assert section.indicatorOfTypeOfLevel == 109

    def test_level(self, section):
        assert section.level == 1

    def test_yearOfCentury(self, section):
        assert section.yearOfCentury == 16

    def test_month(self, section):
        assert section.month == 10

    def test_day(self, section):
        assert section.day == 17

    def test_hour(self, section):
        assert section.hour == 0

    def test_minute(self, section):
        assert section.minute == 0

    def test_unitOfTimeRange(self, section):
        assert section.unitOfTimeRange == 1

    def test_P1(self, section):
        assert section.P1 == 0

    def test_P2(self, section):
        assert section.P2 == 3

    def test_timeRangeIndicator(self, section):
        assert section.timeRangeIndicator == 4

    def test_numberIncludedInAverage(self, section):
        assert section.numberIncludedInAverage == 1

    def test_numberMissingFromAveragesOrAccumulations(self, section):
        assert section.numberMissingFromAveragesOrAccumulations == 0

    def test_centuryOfReferenceTimeOfData(self, section):
        assert section.centuryOfReferenceTimeOfData == 21

    def test_subCentre(self, section):
        assert section.subCentre == 0

    def test_decimalScaleFactor(self, section):
        assert section.decimalScaleFactor == 0

    def test_localDefinitionNumber(self, section):
        assert section.localDefinitionNumber == 2

    def test_generatingProcess(self, section):
        assert section.generatingProcess == 0

    def test_sort(self, section):
        assert section.sort == 3

    def test_timeRepres(self, section):
        assert section.timeRepres == 0

    def test_landType(self, section):
        assert section.landType == 0

    def test_suplScale(self, section):
        assert section.suplScale == 0

    def test_molarMass(self, section):
        assert section.molarMass == 13700

    def test_logTransform(self, section):
        assert section.logTransform == 1

    def test_threshold(self, section):
        assert section.threshold == -999

    def test_totalSizeClasses(self, section):
        assert section.totalSizeClasses == 0

    def test_sizeClassNumber(self, section):
        assert section.sizeClassNumber == 0

    def test_integerScaleFactor(self, section):
        assert section.integerScaleFactor == 0

    def test_lowerRange(self, section):
        assert section.lowerRange == 0

    def test_upperRange(self, section):
        assert section.upperRange == 0

    def test_meanSize(self, section):
        assert section.meanSize == 0

    def test_STDV(self, section):
        assert section.STDV == 0


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
        assert section.section2Length == 1130

    def test_numberOfVerticalCoordinateValues(self, section):
        assert section.numberOfVerticalCoordinateValues == 5

    def test_pvlLocation(self, section):
        assert section.pvlLocation == 35

    def test_dataRepresentationType(self, section):
        assert section.dataRepresentationType == 0

    def test_Ni(self, section):
        assert section.Ni == 117

    def test_Nj(self, section):
        assert section.Nj == 103

    def test_latitudeOfFirstGridPoint(self, section):
        assert section.latitudeOfFirstGridPoint == 17250

    def test_longitudeOfFirstGridPoint(self, section):
        assert section.longitudeOfFirstGridPoint == 30250

    def test_resolutionAndComponentFlags(self, section):
        assert section.resolutionAndComponentFlags == 128

    def test_latitudeOfLastGridPoint(self, section):
        assert section.latitudeOfLastGridPoint == 42750

    def test_longitudeOfLastGridPoint(self, section):
        assert section.longitudeOfLastGridPoint == 59250

    def test_iDirectionIncrement(self, section):
        assert section.iDirectionIncrement == 250

    def test_jDirectionIncrement(self, section):
        assert section.jDirectionIncrement == 250

    def test_scanningMode(self, section):
        assert section.scanningMode == 64


class TestBitMapSection:

    section_number = 3
    fieldnames = {
        "section3Length",
        "numberOfUnusedBitsAtEndOfSection3",
        "tableReference",
        "bitmap",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section3Length(self, section):
        assert section.section3Length == 1513

    def test_numberOfUnusedBitsAtEndOfSection3(self, section):
        assert section.numberOfUnusedBitsAtEndOfSection3 == 5

    def test_tableReference(self, section):
        assert section.tableReference == 0

    def test_bitmap(self, section):
        bitmap = section.bitmap
        assert len(bitmap) == 1507 * 8 - 5
        assert bitmap.sum() == 44


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
        assert section.section4Length == 99

    def test_dataFlag(self, section):
        assert section.dataFlag == 0

    def test_binaryScaleFactor(self, section):
        assert section.binaryScaleFactor == -9

    def test_referenceValue(self, section):
        assert section.referenceValue == approx(-84.7472)

    def test_bitsPerValue(self, section):
        assert section.bitsPerValue == 16

    def test_values(self, section):
        assert len(section.values) == 44


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
        assert_allclose(values.filled(0), target_values)
