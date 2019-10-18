from collections import namedtuple

from copy import deepcopy
import cairocffi as cairo
import pangocffi as pango
import pangocairocffi as pc

from string import Template

__author__ = 'Jamie Hardt'
__license__ = 'MIT'
__version__ = '0.1'

class FormattedText:
    def __init__(self, template_s, font_family, font_size, alignment='l'):
        """
        Define a formatted text content object.

        :param template_s: A format string.
        :param font_family: The font family name to draw this content with.
        :param font_size: The font size in points.
        :param alignment: A string, one of 'l','c','r'
        """
        self.template = Template(template_s)
        self.font_family = font_family
        self.font_size = font_size
        self.alignment = alignment
        self.update({})

    def update(self, data):
        self.text = self.template.safe_substitute(data)

    def text_height(self, width, pango_context):
        fontn = pango.FontDescription()
        fontn.set_family(self.font_family)
        fontn.set_size(pango.units_from_double(self.font_size))
        pango_context.set_font_description(fontn)
        layout = pango.layout.Layout(pango_context)
        layout.set_width(pango.units_from_double(width))
        layout.set_text(self.text)
        _, raw_height = layout.get_size()
        return pango.units_to_double(raw_height)


class Box:
    def __init__(self, color, line_width):
        self.color = color
        self.line_width = line_width

    def update(self, data):
        pass


class Element:
    def __init__(self, x, y, width, height, content, can_shrink=False):
        """
        Define an element to draw in a part.

        :param x: The x-origin of this element, in the coordinate system of the enclosing Part
        :param y: The y-origin of this element, in the coordinate system of the enclosing Part
        :param width: The width of this Element
        :param height: The default height of this Element
        :param content: The content of this Element
        :param can_shrink: If `True`, this element will have its height reduced to the minimum required
            when its content is updated.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.can_shrink = can_shrink


class Part:
    def __init__(self, elements,
                 minimum_height=0.,
                 bottom_spacing=0.,
                 background_color=None,
                 top_border=None,
                 bottom_border=None):
        """
        Define the layout and drawing paramaters of a part of the document.

        :param elements: a list of elements to place in this part
        :param minimum_height: The miminium height of the part. The part by default is large enough to hold every
            element, provide a minimum height if you'd like this part to be larger than required to place every element.
        :param bottom_spacing: Extra space to add beneath the bottom-most element, to add space between this part and
            the one beneath it.
        :param background_color: The background color, as a tuple (red, green, bluw)
        :param top_border: A top border as a `BorderStyle`
        :param bottom_border: A bottom border as a `BorderStyle`
        """
        self.elements = elements
        self.minimum_height = minimum_height
        self.bottom_spacing = bottom_spacing
        self.background_color = background_color
        self.top_border = top_border
        self.bottom_border = bottom_border

    def update_elements(self, data, pango_context):
        for element in self.elements:
            element.content.update(data)
            if element.can_shrink:
                text_height = element.content.text_height(width=element.width, pango_context=pango_context)
                if text_height < element.height:
                    element.height = text_height

    @property
    def height(self):
        reach = 0.
        for element in self.elements:
            this_reach = element.y + element.height
            reach = max(this_reach, reach)

        return max(self.minimum_height, reach + self.bottom_spacing)


SummaryDescriptor = namedtuple('SummaryDescriptor', 'key, leading_header, trailing_header')


class BorderStyle:
    def __init__(self, width, color=None, dash=None):
        """

        :param width: Width in Cairo units.
        :param color: Color as a tuple (r,g,b).
        :param dash: Dash pattern as a tuple `(list, phase)` where `list` is a list of Cairo lengths between stroked
            and unstroked dashes. Default is `((),0)`, meaning a solid line.
        """
        self.width = width
        self.color = color
        self.dash = dash or ((), 0)


Document = namedtuple('Document', 'content_part, summary_descriptors, page_header, page_footer')

Margins = namedtuple('Margins', 'left, right, top, bottom')


class Renderer:
    def __init__(self, document, media_width, media_height, page_margins, max_content_parts_per_page = None):
        self.margins = page_margins
        self.media_width = media_width
        self.media_height = media_height
        self.max_content_parts_per_page = max_content_parts_per_page or 20
        self.document = document
        self.show_guides = False

        self.pango_context = None
        self.cairo_context = None

    @property
    def page_width(self):
        return self.media_width - (self.margins.left + self.margins.right)

    @property
    def page_height(self):
        return self.media_height - (self.margins.top + self.margins.bottom)

    def layout_bands_for_page(self, content, page_number=None):
        layout = []
        if self.document.page_header is not None:
            header_band = deepcopy(self.document.page_header)
            header_band.update_elements(data={'page_number': page_number}, pango_context=self.pango_context)
            layout.append(header_band)

        for summary_desc in self.document.summary_descriptors:
            new_v = content[0].get(summary_desc.key, None)
            if summary_desc.leading_header is not None:
                hband = deepcopy(summary_desc.leading_header)
                hband.update_elements(data={'new_value': new_v}, pango_context=self.pango_context)
                layout.append(hband)

        for item, next_item in zip(content, content[1:]):

            item_band = deepcopy(self.document.content_part)
            item_band.update_elements(data=item, pango_context=self.pango_context)
            layout.append(item_band)

            for summary_desc in self.document.summary_descriptors:
                k = summary_desc.key
                old_v = item.get(k, None)
                new_v = next_item.get(k, None)

                if old_v != new_v:
                    if summary_desc.trailing_header is not None:
                        tband = deepcopy(summary_desc.trailing_header)
                        tband.update_elements(data={'old_value': old_v}, pango_context=self.pango_context)
                        layout.append(tband)
                    if summary_desc.leading_header is not None:
                        hband = deepcopy(summary_desc.leading_header)
                        hband.update_elements(data={'new_value': new_v}, pango_context=self.pango_context)
                        layout.append(hband)

        # last item
        item_band = deepcopy(self.document.content_part)
        item_band.update_elements(data=content[-1], pango_context=self.pango_context)
        layout.append(item_band)

        if self.document.page_footer is not None:
            footer_band = deepcopy(self.document.page_footer)
            footer_band.update_elements(data={'page_number': page_number}, pango_context=self.pango_context)
            layout.append(footer_band)

        return layout

    def height_of_layout_bands(self, layout):
        height = 0
        for band in layout:
            height += band.height

        return height

    def render_text(self, content: FormattedText, width):
        fontn = pango.FontDescription()
        fontn.set_family(content.font_family)
        fontn.set_size(pango.units_from_double(content.font_size))
        self.pango_context.set_font_description(fontn)
        layout = pango.layout.Layout(self.pango_context)
        layout.set_text(content.text)
        if content.alignment == 'l':
            layout.set_alignment(pango.Alignment.LEFT)
        elif content.alignment == 'c':
            layout.set_alignment(pango.Alignment.CENTER)
        elif content.alignment == 'r':
            layout.set_alignment(pango.Alignment.RIGHT)
        layout.set_width(pango.units_from_double(width))
        pc.update_layout(self.cairo_context, layout)
        pc.show_layout(self.cairo_context, layout)

    def render_line(self, width, height, color, line_width):
        self.cairo_context.save()
        self.cairo_context.set_source_rgb(*color)
        self.cairo_context.rectangle(x=0.0, y=0.0, width=width, height=height)
        self.cairo_context.set_line_width(line_width)
        self.cairo_context.stroke()
        self.cairo_context.restore()

    def render_element(self, element):
        self.cairo_context.save()
        self.cairo_context.translate(element.x, element.y)
        self.cairo_context.set_source_rgb(0.0, 0.0, 0.0)
        self.cairo_context.rectangle(x=0, y=0, width=element.width, height=element.height)
        self.cairo_context.clip()
        if self.show_guides:
            self.cairo_context.save()
            self.cairo_context.set_source_rgb(0.2, 1.0, 2.2)
            self.cairo_context.rectangle(x=0, y=0, width=element.width, height=element.height)
            self.cairo_context.stroke()
            self.cairo_context.restore()
        if isinstance(element.content, FormattedText):
            self.render_text(element.content, element.width)
        elif isinstance(element.content, Box):
            self.render_line(color=element.content.color,
                             width=element.width,
                             height=element.height,
                             line_width=element.content.line_width)

        self.cairo_context.restore()

    def render_band(self, part: Part, y):

        self.cairo_context.save()
        self.cairo_context.translate(self.margins.left, y)

        if part.background_color is not None:
            self.cairo_context.save()
            self.cairo_context.rectangle(0., 0., width=self.page_width, height=part.height)
            self.cairo_context.clip()
            self.cairo_context.set_source_rgb(*part.background_color)
            self.cairo_context.paint()
            self.cairo_context.restore()

        if part.top_border is not None:
            self.cairo_context.save()
            self.cairo_context.set_line_width(part.top_border.width)
            self.cairo_context.set_source_rgb(*part.top_border.color)
            self.cairo_context.set_dash(*part.top_border.dash)
            self.cairo_context.move_to(x=0., y=0.)
            self.cairo_context.line_to(x=self.page_width, y=0.)
            self.cairo_context.stroke()
            self.cairo_context.restore()

        if part.bottom_border is not None:
            self.cairo_context.save()
            self.cairo_context.set_line_width(part.bottom_border.width)
            self.cairo_context.set_source_rgb(*part.bottom_border.color)
            self.cairo_context.set_dash(*part.bottom_border.dash)
            self.cairo_context.move_to(x=0., y=part.height)
            self.cairo_context.line_to(x=self.page_width, y=part.height)
            self.cairo_context.stroke()
            self.cairo_context.restore()

        if self.show_guides:
            self.cairo_context.save()
            self.cairo_context.set_source_rgb(1., .8, .8)
            self.cairo_context.rectangle(0., 0., width=self.page_width, height=part.height)
            self.cairo_context.stroke()
            self.cairo_context.restore()

        self.cairo_context.rectangle(0., 0., width=self.page_width, height=part.height)
        self.cairo_context.clip()

        for element in part.elements:
            self.render_element(element)

        self.cairo_context.restore()

    def render_layout_for_page(self, layout):
        y = self.margins.top

        if self.document.page_footer is not None:
            from_top = layout[:-1]
            from_bottom = [layout[-1]]
        else:
            from_top = layout
            from_bottom = []

        for band in from_top:
            self.render_band(band, y=y)
            height = band.height
            y += height

        y = (self.page_height + self.margins.top) - self.height_of_layout_bands(from_bottom)
        for band in from_bottom:
            self.render_band(band, y=y)
            height = band.height
            y += height

    def render_pages(self, content, page_number=1):
        remainder = self.render_page(content,
                                     page_number=page_number)

        if len(remainder) > 0:
            self.render_pages(content=remainder,
                              page_number=page_number + 1)
        else:
            # FIXME discharge remaining summary footers
            return

    def render_page(self, content, page_number):
        trial_content = content[0:self.max_content_parts_per_page]
        remainder = content[self.max_content_parts_per_page:]

        while True:
            layout = self.layout_bands_for_page(trial_content,
                                                page_number=page_number)
            test_height = self.height_of_layout_bands(layout)

            if test_height > self.page_height:
                remainder = [trial_content[-1]] + remainder
                trial_content = trial_content[:-1]
                continue
            else:
                self.render_layout_for_page(layout)
                self.cairo_context.show_page()
                return remainder

    def render(self, content, out_filename):
        pdf_surface = cairo.PDFSurface(target=out_filename,
                                       width_in_points=self.media_width,
                                       height_in_points=self.media_height)

        self.cairo_context = cairo.Context(target=pdf_surface)
        self.pango_context = pc.PangoCairoFontMap().create_context()
        self.render_pages(content)
        self.cairo_context = None
        self.cairo_context = None
