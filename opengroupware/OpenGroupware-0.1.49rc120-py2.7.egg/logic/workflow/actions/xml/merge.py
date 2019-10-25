#
# Copyright (c) 2010, 2014, 2015
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
from lxml import etree
from coils.core import CoilsException
from coils.core.logic import ActionCommand

COILS_DEFAULT_NAMESPACES = {
    'OGo': 'http://www.opengroupware.us/model',
    'OIE': 'http://www.opengroupware.us/oie',
    'OGoLegacy': 'http://www.opengroupware.org/',
    'OGoDAV': '57c7fc84-3cea-417d-af54-b659eb87a046',
    'OGoCloud': '2f85ddbe-28f5-4de3-8de9-c96bdd5230dd',
}


class XPathMerge(ActionCommand):
    __domain__ = "action"
    __operation__ = "xpath-merge"
    __aliases__ = ['xpathMergeAction', 'xpathMerge', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _construct_nsmap(self, element_):
        for key, value, in COILS_DEFAULT_NAMESPACES.items():
            if key not in element_.nsmap:
                if value not in element_.nsmap.values():
                    element_.nsmap[key] = value

    def _get_handle_for_document_b(self):
        message = self._ctx.run_command(
            'message::get',
            process=self.process,
            label=self._input_label,
        )
        self.log.debug('Merging with message {0}'.format(message.uuid))
        input_handle = self._ctx.run_command(
            'message::get-handle', object=message,
        )
        return input_handle

    @property
    def result_mimetype(self):
        return 'application/xml'

    def do_action(self):
        doc_a = etree.parse(self.rfile)  # Parse target document, document A

        input_handle = self._get_handle_for_document_b()
        doc_b = etree.parse(input_handle)  # Parse souce document, document B

        # Find the point to insert elementes into document A
        if self._insert_at_xpath:
            root_a = doc_a.xpath(
                self._insert_at_xpath, namespaces=doc_a.getroot().nsmap
            )[0]
        else:
            root_a = doc_a.getroot()

        self._construct_nsmap(root_a)

        xpath_nsmap = doc_b.getroot().nsmap
        if None in xpath_nsmap:
            xpath_nsmap['default'] = xpath_nsmap[None]
            xpath_nsmap.pop(None)

        # Optionally insert a container element into document A
        if self._container_element:
            container = etree.Element(
                self._container_element, nsmap=xpath_nsmap,
            )
            root_a.append(container)
            root_a = container
        else:
            if 'default' in xpath_nsmap:
                if xpath_nsmap['default'] not in root_a.nsmap.values():
                    root_a.nsmap['source'] = xpath_nsmap['default']

        # Find the elements to be copied from document B
        elements = doc_b.xpath(
            self._source_xpath,
            namespaces=xpath_nsmap,
        )

        self.log.debug(
            'Merging {0} elements from message.'.format(len(elements), )
        )

        # Insert elements from document B into document A
        for element in elements:
            root_a.append(element)
        self.log.debug('Document merge complete, writing output.')

        # Send the extended document A to the output [wfile]
        self.wfile.write(etree.tostring(doc_a.getroot()))

        doc_b = None
        doc_a = None
        input_handle.close()

    def parse_action_parameters(self):
        self._input_label = self.action_parameters.get('label', None)
        self._source_xpath = self.action_parameters.get('xpath', None)
        if (self._source_xpath is None):
            raise CoilsException('No path provided for xpath query')
        else:
            self._source_xpath = self.decode_text(self._source_xpath)
        self._container_element = self.process_label_substitutions(
            self.action_parameters.get(
                'containerElement', None
            )
        )
        self._insert_at_xpath = self.process_label_substitutions(
            self.action_parameters.get(
                'insertAtPath', None
            )
        )

    def do_epilogue(self):
        pass
