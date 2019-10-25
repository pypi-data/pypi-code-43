from coils.core import AdministrativeContext, initialize_COILS, StandardXML
from coils.foundation.api.elementflow import elementflow
from lxml.etree import Element, SubElement, tostring
from datetime import datetime
import pprint, yaml

from workflow_map import WorkflowMap, get_standardxml_type_name


class StandardXMLToHierarchicMap(WorkflowMap):

    def _process_child(self, parent, rows, r):
        kf = r['keyField']
        working_set = [row for row in rows if row[kf] is not None]
        if not working_set:
            return
        keys = set(
            [row[kf] for row in working_set]
        )
        #print('keys: {0}'.format(keys))
        for key in keys:
            record_set = [row for row in working_set if row[kf] == key]
            root = SubElement(
                parent,
                r['element'],
                id=unicode(record_set[0][kf]),
            )
            for element in r['attributes']:
                if isinstance(element, basestring):
                    en = fk = element
                else:
                    fk, en, = element
                if record_set[0][fk] is not None:
                    SubElement(
                        root,
                        en,
                        dataType=get_standardxml_type_name(rows[0][fk]),
                    ).text = unicode(record_set[0][fk])
                else:
                    SubElement(root, en)
            for child_r in r['children']:
                self._process_child(
                    SubElement(
                        root,
                        child_r['container'],
                        keyField=child_r['keyField'],
                        dataType='container',
                    ),
                    record_set,
                    child_r,
                )

    def _process_rows(self, parent, rows, r):
        key_value = unicode(rows[0][r['keyField']])
        root = SubElement(parent, r['element'], id=key_value)
        for element in r['attributes']:
            if isinstance(element, basestring):
                en = fk = element
            else:
                fk, en, = element
            if rows[0][fk] is not None:
                SubElement(
                    root,
                    en,
                    dataType=get_standardxml_type_name(rows[0][fk]),
                ).text = unicode(rows[0][fk])
            else:
                SubElement(root, en)
        for child_r in r['children']:
            self._process_child(
                SubElement(
                    root,
                    child_r['container'],
                    keyField=child_r['keyField'],
                    dataType='container',
                ),
                rows,
                child_r,
            )

    def run(self, rfile, wfile):

        document = Element(self.map_document['container'])
        rows = list()
        previous_key = None
        for keys, fields in StandardXML.Read_Rows(rfile, fallback_to_text=True):
            fields.update(keys)
            row = fields
            if previous_key is None:
                previous_key = row[self.map_document['keyField']]
            if row[self.map_document['keyField']] != previous_key:
                self._process_rows(document, rows, self.map_document)
                rows = list()
            else:
                rows.append(row)
        self._process_rows(document, rows, self.map_document)

        wfile.write(tostring(document))


if __name__ == '__main__':

    initialize_COILS()
    ctx = AdministrativeContext()

    rfile = open('message.xml', 'rb')
    wfile = open('output.xml', 'wb')

    m = StandardXMLToHierarchicMap(ctx)
    m.load('trworkorder.yaml')
    m.run(rfile, wfile)

    rfile.close()
    wfile.close()
