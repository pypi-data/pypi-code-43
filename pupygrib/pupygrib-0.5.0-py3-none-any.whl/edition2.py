"""An edition 2 GRIB message."""

from pupygrib import base
from pupygrib import binary
from pupygrib import fields


class IndicatorSection(base.Section):
    """The indicator section (0) of an edition 2 GRIB message."""

    identifier = fields.BytesField(1, 4)
    discipline = fields.Uint8Field(7)
    editionNumber = fields.Uint8Field(8)
    totalLength = fields.Uint64Field(9)


class IdentificationSection(base.Section):
    """The identification section (1) of an edition 2 GRIB message."""

    section1Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    centre = fields.Uint16Field(6)
    subCentre = fields.Uint16Field(8)
    tablesVersion = fields.Uint8Field(10)
    localTablesVersion = fields.Uint8Field(11)
    significanceOfReferenceTime = fields.Uint8Field(12)
    year = fields.Uint16Field(13)
    month = fields.Uint8Field(15)
    day = fields.Uint8Field(16)
    hour = fields.Uint8Field(17)
    minute = fields.Uint8Field(18)
    second = fields.Uint8Field(19)
    productionStatusOfProcessedData = fields.Uint8Field(20)
    typeOfProcessedData = fields.Uint8Field(21)


class LocalUseSection(base.Section):
    """The local use section (2) of an edition 2 GRIB message."""

    section2Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)


class GridDescriptionSection(base.Section):
    """The grid description section (3) of an edition 2 GRIB message."""

    section3Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    sourceOfGridDefinition = fields.Uint8Field(6)
    numberOfDataPoints = fields.Uint32Field(7)
    numberOfOctetsForNumberOfPoints = fields.Uint8Field(11)
    interpretationOfNumberOfPoints = fields.Uint8Field(12)
    gridDefinitionTemplateNumber = fields.Uint16Field(13)


class ProductDefinitionSection(base.Section):
    """The product definition section (4) of an edition 2 GRIB message."""

    section4Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    NV = fields.Uint16Field(6)
    productDefinitionTemplateNumber = fields.Uint16Field(8)


class DataRepresentationSection(base.Section):
    """The data representation section (5) of an edition 2 GRIB message."""

    section5Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    numberOfValues = fields.Uint32Field(6)
    dataRepresentationTemplateNumber = fields.Uint16Field(10)


class BitMapSection(base.Section):
    """The bit-map section (6) of an edition 2 GRIB message."""

    section6Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    bitMapIndicator = fields.Uint8Field(6)


class DataSection(base.Section):
    """The data section (7) of an edition 2 GRIB message."""

    section7Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)


class EndSection(base.Section):
    """The end section (8) of an edition 2 GRIB message."""

    endOfMessage = fields.BytesField(1, 4)


class Message(base.Message):
    """An edition 2 GRIB message."""

    def _get_section0(self):
        return IndicatorSection(self._data, 0, 16)

    def _get_section1(self):
        prevsection = self[0]
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return IdentificationSection(self._data, prevsection.end, length)

    def _get_section2(self):
        prevsection = self[1]
        number = binary.unpack_uint8_from(self._data, prevsection.end + 4)
        if number != 2:
            return None
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return LocalUseSection(self._data, prevsection.end, length)

    def _get_section3(self):
        prevsection = self[2] or self[1]
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return GridDescriptionSection(self._data, prevsection.end, length)

    def _get_section4(self):
        prevsection = self[3]
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return ProductDefinitionSection(self._data, prevsection.end, length)

    def _get_section5(self):
        prevsection = self[4]
        number = binary.unpack_uint8_from(self._data, prevsection.end + 4)
        if number != 5:
            return None
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return DataRepresentationSection(self._data, prevsection.end, length)

    def _get_section6(self):
        prevsection = self[5] or self[4]
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return BitMapSection(self._data, prevsection.end, length)

    def _get_section7(self):
        prevsection = self[6]
        length = binary.unpack_uint32_from(self._data, prevsection.end)
        return DataSection(self._data, prevsection.end, length)

    def _get_section8(self):
        return EndSection(self._data, self[7].end, 4)
