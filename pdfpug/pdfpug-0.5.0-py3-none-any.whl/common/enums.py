#  MIT License
#
#  Copyright (C) 2019 Nekhelesh Ramananthan
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#  AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from enum import Enum, unique


@unique
class HeaderTier(Enum):
    """
    Enum Weights to set the hierarchy of a header

    The weights are compatible with Markdown levels such as h1, h2, h3 etc.

    >>> from pdfpug.modules import Header
    >>> from pdfpug.common import HeaderTier
    >>> h1_header = Header('h1 Header', tier=HeaderTier.h1)
    >>> h2_header = Header('h2 Header', tier=HeaderTier.h2)
    >>> h3_header = Header('h3 Header', tier=HeaderTier.h3)

    .. figure:: ../_images/header_tiers.png
        :height: 150
    """

    #: Page level header. Equivalent to a markdown h1 header.
    h1 = "h1"

    #: Section level header. Equivalent to a markdown h2 header.
    h2 = "h2"

    #: Paragraph level header. Equivalent to a markdown h3 header.
    h3 = "h3"

    #: Paragraph level header. Equivalent to a markdown h4 header.
    h4 = "h4"

    #: Paragraph level header. Equivalent to a markdown h5 header.
    h5 = "h5"


@unique
class HeaderStyle(Enum):
    """
    Enum header styles

    >>> from pdfpug.modules import Header
    >>> from pdfpug.common import HeaderStyle
    >>> block_header = Header('Block Header', style=HeaderStyle.block)
    """

    block = "block"
    """
    The header is formatted to appear inside a content block

    .. figure:: ../_images/block_header.png
        :height: 50
    """

    dividing = "dividing"
    """
    The header is formatted to divide itself from the content below it using a
    horizontal line

    .. figure:: ../_images/dividing_header.png
        :height: 35
    """


@unique
class Alignment(Enum):
    """
    Enum Alignment options
    """

    #: Right align content
    right = "right aligned"

    #: Left align content
    left = "left aligned"

    #: Justify content across the line
    justified = "justified"

    #: Center align content
    center = "center aligned"


@unique
class TableSpacing(Enum):
    """
    Enum Table row spacing
    """

    #: Tight spacing of row content
    tight = "very compact"

    #: Compact spacing of row content
    compact = "compact"

    #: Good spacing of row content
    comfortable = "padded"

    #: Spacious padding of row content
    spacious = "very padded"


@unique
class TableRowStyle(Enum):
    """
    Table row style
    """

    #: Set if alternate rows should be colored differently
    striped = "striped"


@unique
class TableRowType(Enum):
    """
    Table row type
    """

    #: Header row
    header = "th"

    #: Body row
    body = "td"


@unique
class State(Enum):
    """
    Enum content state options
    """

    #: Positive content
    positive = "positive"

    #: Negative content
    negative = "negative"

    #: Error content
    error = "error"

    #: Warning content
    warning = "warning"

    #: Active content
    active = "active"

    #: Disabled content
    disabled = "disabled"


class MessageState(Enum):
    """
    Enum Message box style options
    """

    #: Positive message
    positive = "positive"

    #: Negative Message
    negative = "negative"

    #: Error message
    error = "error"

    #: Success message
    success = "success"

    #: Warning message
    warning = "warning"

    #: Info message
    info = "info"


@unique
class TableType(Enum):
    """
    Enum Table types
    """

    celled = "celled"
    """
    Default table style with each cell clearly visible due to separators

    .. figure:: ../_images/celled_table_style.png
        :height: 100
    """

    #: Bare minimum row separating lines with table border
    simple = "basic"
    """
    Bare minimum row separating lines with table border

    .. figure:: ../_images/simple_table_style.png
        :height: 100
    """

    bare = "very basic"
    """
    Bare minimum row separating lines and no table border

    .. figure:: ../_images/bare_table_style.png
        :height: 100
    """


@unique
class TableColumnWidth(Enum):
    """
    Enum Table column width rules
    """

    fixed = "fixed"
    """
    Equal widths for all columns

    .. figure:: ../_images/celled_table_style.png
        :height: 100
    """

    minimum = "collapsing"
    """
    Minimum width for each column based on their content

    .. figure:: ../_images/minimum_table_column_width.png
        :height: 100
    """


@unique
class ParagraphAlignment(Enum):
    """
    Enum Alignment options
    """

    #: Left align content
    left = "left"

    #: Right align content
    right = "right"

    #: Center align content
    center = "center"


@unique
class Size(Enum):
    """
    Enum Size options
    """

    #: Mini
    mini = "mini"

    #: Tiny
    tiny = "tiny"

    #: Small
    small = "small"

    #: Medium
    medium = "medium"

    #: Large
    large = "large"

    #: Big
    big = "big"

    #: Huge
    huge = "huge"

    #: Massive
    massive = "massive"


@unique
class ListType(Enum):
    ordered = "ordered"
    bulleted = "bulleted"


@unique
class Orientation(Enum):
    """
    Enum Orientation options
    """

    #: Layout elements horizontally
    horizontal = "horizontal"

    #: Layout elements vertically
    vertical = "vertical"


@unique
class Color(Enum):
    """
    Enum Colors
    """

    #: Red
    red = "red"

    #: Orange
    orange = "orange"

    #: Yellow
    yellow = "yellow"

    #: Olive
    olive = "olive"

    #: Green
    green = "green"

    #: Teal
    teal = "teal"

    #: Blue
    blue = "blue"

    #: Purple
    purple = "purple"

    #: Violet
    violet = "violet"

    #: Pink
    pink = "pink"

    #: Brown
    brown = "brown"

    #: Grey
    grey = "grey"


@unique
class ImageStyle(Enum):
    """
    Enum Image Style
    """

    #: Appear inline as an avatar (circular image)
    avatar = "avatar"
    """
    Image which appears inline as an avatar (circular image)

    .. figure:: ../_images/avatar_image.png
        :height: 25
    """

    rounded = "rounded"
    """
    Image with rounded edges

    .. figure:: ../_images/rounded_image.png
        :height: 150
    """

    circular = "circular"
    """
    Crop image into a circular shape. The input image should have the same width
    and height for this style to work.

    .. figure:: ../_images/circular_image.png
        :height: 150
    """


@unique
class ImageLayout(Enum):
    """
    Enum Image Layouts
    """

    #: Float to the left of neighbouring content
    left_float = "left float"

    #: Float to the right of neighbouring content
    right_float = "right float"

    #: Horizontally center the image
    centered = "centered"


@unique
class LabelType(Enum):
    """
    Enum Label types
    """

    #: Label looks like a shopping tag
    tag = "tag"

    #: Minimalistic label with just an outline
    basic = "basic"

    #: Circular shaped label
    circular = "circular"


@unique
class SegmentType(Enum):
    """
    Enum Segment Type
    """

    #: Basic segment type with no special formatting
    basic = "basic"

    stacked = "stacked"
    """
    Segment that appears to contain multiple pages which are stacked cleanly

    .. figure:: ../_images/stacked_segment.png
        :height: 100
    """

    piled = "piled"
    """
    Segment that appears to look like a pile of papers

    .. figure:: ../_images/piled_segment.png
        :height: 90
    """

    vertical = "vertical"
    """
    Segment type that formats the content to be aligned as part of a vertical group

    .. figure:: ../_images/vertical_segment.png
        :height: 110
    """

    circular = "circular"
    """
    Circular segment type. For a circle, ensure content has equal width and height

    .. figure:: ../_images/circular_segment.png
        :height: 100
    """


@unique
class SegmentEmphasis(Enum):
    """
    Enum Segment Emphasis
    """

    secondary = "secondary"
    """
    Lesser emphasis than the normal standard

    .. figure:: ../_images/secondary_segment.png
        :height: 45
    """

    tertiary = "tertiary"
    """
    Lesser emphasis than secondary elements

    .. figure:: ../_images/tertiary_segment.png
        :height: 45
    """


@unique
class SegmentSpacing(Enum):
    """
    Enum Segment Spacing
    """

    compact = "compact"
    """
    Segment will take up only as much space as is necessary

    .. figure:: ../_images/compact_segment.png
        :height: 50
    """

    padded = "padded"
    """
    Segment will add good amount of padding on all sides making it look more spacious

    .. figure:: ../_images/padded_segment.png
        :height: 60
    """


@unique
class Theme(Enum):
    """
    Predefined theme collection
    """

    mood_swing = "moodswing"
    """
    Mood Swing Theme

    .. figure:: ../_images/moodswing.png
        :width: 500
    """


class PageSize(Enum):
    """
    Predefined Page sizes
    """

    #: ISO Dimensions 297mm x 420mm
    a3 = "A3"

    #: ISO Dimensions 210mm x 297mm (most frequently used for printing)
    a4 = "A4"

    #: ISO Dimensions 148mm x 210mm
    a5 = "A5"

    #: ISO Dimensions 176mm x 250mm
    b5 = "B5"

    #: ISO Dimensions 250mm x 353mm
    b4 = "B4"

    #: Equivalent to the dimensions of letter papers in North America 8.5in x 11in
    letter = "letter"

    #: Equivalent to the dimensions of legal papers in North America 8.5in x 14in
    legal = "legal"

    #: Equivalent to the dimensions of ledger papers in North America 11in x 17in
    ledger = "ledger"


class PageOrientation(Enum):
    """
    Orientation of Report
    """

    #: Page is displayed in portrait mode where the longest edge of the page is
    #: vertical
    portrait = "portrait"

    #: Page is displayed in landscape mode where the longest edge of the page is
    #: horizontal
    landscape = "landscape"
