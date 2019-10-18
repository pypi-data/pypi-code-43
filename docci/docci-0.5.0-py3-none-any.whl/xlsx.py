"""
Utils for working with openpyxl.Workbook
"""

from io import BytesIO

from openpyxl import Workbook

from docci.file import FileAttachment


def xlsx_to_file(xlsx: Workbook, name: str) -> FileAttachment:
    """
    Convert openpyxl.Workbook to FileAttachment
    """
    return FileAttachment(name, xlsx_to_bytes(xlsx))


def xlsx_to_bytes(xlsx: Workbook) -> bytes:
    """
    Convert openpyxl.Workbook to bytes
    """
    excel_stream = BytesIO()
    xlsx.save(excel_stream)
    return excel_stream.getvalue()
