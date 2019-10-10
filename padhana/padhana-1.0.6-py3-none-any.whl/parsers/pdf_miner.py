import base64
import imghdr
import io
import json
import re

from pdfminer.converter import PDFConverter
from pdfminer.layout import LTChar
from pdfminer.layout import LTCurve
from pdfminer.layout import LTFigure
from pdfminer.layout import LTImage
from pdfminer.layout import LTLine
from pdfminer.layout import LTPage
from pdfminer.layout import LTRect
from pdfminer.layout import LTText
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextBoxVertical
from pdfminer.layout import LTTextGroup
from pdfminer.layout import LTTextLine
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

from padhana.core import Document, DocumentMetadata, ContentNode


class ContentNodeConverter(PDFConverter):
    CONTROL = re.compile(u'[\x00-\x08\x0b-\x0c\x0e-\x1f]')

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1,
                 laparams=None, imagewriter=None, stripcontrol=False):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno, laparams=laparams)
        self.imagewriter = imagewriter
        self.stripcontrol = stripcontrol
        self.root = ContentNode(type="pages")
        return

    def receive_layout(self, ltpage):

        def show_group(item, parent_node):
            if isinstance(item, LTTextBox):
                node = ContentNode(type="textBox", bbox=item.bbox, id=item.index)
                parent_node.children.append(node)
            elif isinstance(item, LTTextGroup):
                node = ContentNode(type="textGroup", bbox=item.bbox)
                parent_node.children.append(node)
                for child in item:
                    show_group(child, node)
            return

        def render(item, parent_node):
            if isinstance(item, LTPage):
                node = ContentNode(type="page", bbox=item.bbox, rotate=item.rotate)
                parent_node.children.append(node)
                for child in item:
                    render(child, node)
                if item.groups is not None:
                    layout = ContentNode(type="layout")
                    node.children.append(layout)
                    for group in item.groups:
                        show_group(group, layout)
            elif isinstance(item, LTLine):
                node = ContentNode(type="line", bbox=item.bbox, linewidth=item.linewidth)
                parent_node.children.append(node)
            elif isinstance(item, LTRect):
                # If LTRect is found, create the 4 lines (this is needed in extracting tables from the PDf
                node = ContentNode(type="rect", bbox=item.bbox, linewidth=item.linewidth)
                parent_node.children.append(node)
            elif isinstance(item, LTCurve):
                node = ContentNode(type="curve", bbox=item.bbox, pts=item.get_pts())
                parent_node.children.append(node)
            elif isinstance(item, LTFigure):
                node = ContentNode(type="figure", bbox=item.bbox, name=item.name)
                parent_node.children.append(node)
                for child in item:
                    render(child, node)
            elif isinstance(item, LTTextLine):
                node = ContentNode(type="textLine", bbox=item.bbox)
                parent_node.children.append(node)
                for child in item:
                    render(child, node)
            elif isinstance(item, LTTextBox):
                wmode = 'horizontal'
                if isinstance(item, LTTextBoxVertical):
                    wmode = 'vertical'
                node = ContentNode(type="textBox", bbox=item.bbox, id=item.index, wmode=wmode)
                parent_node.children.append(node)
                for child in item:
                    render(child, node)
            elif isinstance(item, LTChar):
                node = ContentNode(type="text", bbox=item.bbox, color_space=item.ncs.name,
                                   ncolor=item.graphicstate.ncolor, size=item.size, value=item.get_text())
                parent_node.children.append(node)
            elif isinstance(item, LTText):
                node = ContentNode(type="text", value=item.get_text())
                parent_node.children.append(node)
            elif isinstance(item, LTImage):
                encoded_image = base64_encode_image(item)
                node = ContentNode(type="image", height=item.height, width=item.width, value=encoded_image)
                parent_node.children.append(node)
            else:
                assert False, str(('Unhandled', item))
            return

        def base64_encode_image(lt_image):

            """Try to save the image data from this LTImage object, and return the file name, if successful"""
            result = None
            if lt_image.stream:
                file_ext = imghdr.what("", lt_image.stream.get_rawdata())
                if file_ext:
                    result = f"data:image/{file_ext};base64,{base64.b64encode(lt_image.stream.get_rawdata()).decode('ascii')}"
            return result

        render(ltpage, self.root)
        return

    def close(self):
        return


class PdfMinerParser:

    def parse_file(self, pdf_path):
        print("Parsing PDF " + pdf_path)
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = ContentNodeConverter(resource_manager, fake_file_handle)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                page_interpreter.process_page(page)

        # close open handles
        converter.close()
        fake_file_handle.close()

        document_metadata = DocumentMetadata(source_path=pdf_path)
        with open("/tmp/output.txt", "w") as text_file:
            text_file.write(json.dumps(converter.root.children[0], indent=4, sort_keys=True))

        return Document(document_metadata, converter.root)
