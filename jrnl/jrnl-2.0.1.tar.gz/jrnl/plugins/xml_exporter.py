#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals
from .json_exporter import JSONExporter
from .util import get_tags_count
from ..util import u
from xml.dom import minidom


class XMLExporter(JSONExporter):
    """This Exporter can convert entries and journals into XML."""
    names = ["xml"]
    extension = "xml"

    @classmethod
    def export_entry(cls, entry, doc=None):
        """Returns an XML representation of a single entry."""
        doc_el = doc or minidom.Document()
        entry_el = doc_el.createElement('entry')
        for key, value in cls.entry_to_dict(entry).items():
            elem = doc_el.createElement(key)
            elem.appendChild(doc_el.createTextNode(u(value)))
            entry_el.appendChild(elem)
        if not doc:
            doc_el.appendChild(entry_el)
            return doc_el.toprettyxml()
        else:
            return entry_el

    @classmethod
    def entry_to_xml(cls, entry, doc):
        entry_el = doc.createElement('entry')
        entry_el.setAttribute('date', entry.date.isoformat())
        if hasattr(entry, "uuid"):
            entry_el.setAttribute('uuid', u(entry.uuid))
        entry_el.setAttribute('starred', u(entry.starred))
        entry_el.appendChild(doc.createTextNode(entry.fulltext))
        return entry_el

    @classmethod
    def export_journal(cls, journal):
        """Returns an XML representation of an entire journal."""
        tags = get_tags_count(journal)
        doc = minidom.Document()
        xml = doc.createElement('journal')
        tags_el = doc.createElement('tags')
        entries_el = doc.createElement('entries')
        for count, tag in tags:
            tag_el = doc.createElement('tag')
            tag_el.setAttribute('name', tag)
            count_node = doc.createTextNode(u(count))
            tag_el.appendChild(count_node)
            tags_el.appendChild(tag_el)
        for entry in journal.entries:
            entries_el.appendChild(cls.entry_to_xml(entry, doc))
        xml.appendChild(entries_el)
        xml.appendChild(tags_el)
        doc.appendChild(xml)
        return doc.toprettyxml()
