"""Regression tests for reading regular_latlon_surface.grib2."""

gribfile = "data/regular_latlon_surface.grib2"


class TestIndicatorSection:

    section_number = 0
    fieldnames = {"identifier", "discipline", "editionNumber", "totalLength"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_identifier(self, section):
        assert section.identifier == b"GRIB"

    def test_discipline(self, section):
        assert section.discipline == 0

    def test_editionNumber(self, section):
        assert section.editionNumber == 2

    def test_totalLength(self, section):
        assert section.totalLength == 1188


class TestIdentificationSection:

    section_number = 1
    fieldnames = {
        "section1Length",
        "numberOfSection",
        "centre",
        "subCentre",
        "tablesVersion",
        "localTablesVersion",
        "significanceOfReferenceTime",
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
        "productionStatusOfProcessedData",
        "typeOfProcessedData",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section1Length(self, section):
        assert section.section1Length == 21

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 1

    def test_centre(self, section):
        assert section.centre == 98

    def test_subCentre(self, section):
        assert section.subCentre == 0

    def test_tablesVersion(self, section):
        assert section.tablesVersion == 5

    def test_localTablesVersion(self, section):
        assert section.localTablesVersion == 0

    def test_significanceOfReferenceTime(self, section):
        assert section.significanceOfReferenceTime == 1

    def test_year(self, section):
        assert section.year == 2008

    def test_month(self, section):
        assert section.month == 2

    def test_day(self, section):
        assert section.day == 6

    def test_hour(self, section):
        assert section.hour == 12

    def test_minute(self, section):
        assert section.minute == 0

    def test_second(self, section):
        assert section.second == 0

    def test_productionStatusOfProcessedData(self, section):
        assert section.productionStatusOfProcessedData == 0

    def test_typeOfProcessedData(self, section):
        assert section.typeOfProcessedData == 255


class TestLocalUseSection:

    section_number = 2
    fieldnames = {"section2Length", "numberOfSection"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section2Length(self, section):
        assert section.section2Length == 17

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 2


class TestGridDescriptionSection:

    section_number = 3
    fieldnames = {
        "section3Length",
        "numberOfSection",
        "sourceOfGridDefinition",
        "numberOfDataPoints",
        "numberOfOctetsForNumberOfPoints",
        "interpretationOfNumberOfPoints",
        "gridDefinitionTemplateNumber",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section3Length(self, section):
        assert section.section3Length == 72

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 3

    def test_sourceOfGridDefinition(self, section):
        assert section.sourceOfGridDefinition == 0

    def test_numberOfDataPoints(self, section):
        assert section.numberOfDataPoints == 496

    def test_numberOfOctetsForNumberOfPoints(self, section):
        assert section.numberOfOctetsForNumberOfPoints == 0

    def test_interpretationOfNumberOfPoints(self, section):
        assert section.interpretationOfNumberOfPoints == 0

    def test_gridDefinitionTemplateNumber(self, section):
        assert section.gridDefinitionTemplateNumber == 0


class TestProductDefinitionSection:

    section_number = 4
    fieldnames = {
        "section4Length",
        "numberOfSection",
        "NV",
        "productDefinitionTemplateNumber",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section4Length(self, section):
        assert section.section4Length == 34

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 4

    def test_NV(self, section):
        assert section.NV == 0

    def test_productDefinitionTemplateNumber(self, section):
        assert section.productDefinitionTemplateNumber == 0


class TestDataRepresentationSection:

    section_number = 5
    fieldnames = {
        "section5Length",
        "numberOfSection",
        "numberOfValues",
        "dataRepresentationTemplateNumber",
    }

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section5Length(self, section):
        assert section.section5Length == 21

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 5

    def test_numberOfValues(self, section):
        assert section.numberOfValues == 496

    def test_dataRepresentationTemplateNumber(self, section):
        assert section.dataRepresentationTemplateNumber == 0


class TestBitMapSection:

    section_number = 6
    fieldnames = {"section6Length", "numberOfSection", "bitMapIndicator"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section6Length(self, section):
        assert section.section6Length == 6

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 6

    def test_bitMapIndicator(self, section):
        assert section.bitMapIndicator == 255


class TestDataSection:

    section_number = 7
    fieldnames = {"section7Length", "numberOfSection"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_section7Length(self, section):
        assert section.section7Length == 997

    def test_numberOfSection(self, section):
        assert section.numberOfSection == 7


class TestEndSection:

    section_number = 8
    fieldnames = {"endOfMessage"}

    def test_fieldnames(self, section):
        assert section.fieldnames == self.fieldnames

    def test_endOfMessage(self, section):
        assert section.endOfMessage == b"7777"
