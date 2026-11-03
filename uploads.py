"""Validate document structure before persisting an untrusted upload."""
import io
import zipfile
from xml.etree import ElementTree

import olefile
from pypdf import PdfReader


def validate_document(data, extension):
    if not data:
        return False
    try:
        if extension == "pdf":
            if not data.startswith(b"%PDF-"):
                return False
            reader = PdfReader(io.BytesIO(data), strict=True)
            return not reader.is_encrypted and len(reader.pages) > 0
        if extension == "doc":
            if not olefile.isOleFile(io.BytesIO(data)):
                return False
            with olefile.OleFileIO(io.BytesIO(data)) as document:
                return (document.exists("WordDocument")
                        and (document.exists("0Table") or document.exists("1Table")))
        if extension == "docx":
            with zipfile.ZipFile(io.BytesIO(data)) as document:
                entries = document.infolist()
                if (len(entries) > 2000
                        or sum(e.file_size for e in entries) > 50 * 1024 * 1024
                        or any(e.flag_bits & 1 for e in entries)
                        or "word/vbaProject.bin" in document.namelist()):
                    return False
                for name in ("[Content_Types].xml", "word/document.xml"):
                    info = document.getinfo(name)
                    if info.file_size > 5 * 1024 * 1024:
                        return False
                    xml = document.read(name)
                    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
                        return False
                    root = ElementTree.fromstring(xml)
                    if name == "word/document.xml" and root.tag != "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document":
                        return False
                return True
    except Exception:
        # Malformed or unsupported documents must never reach storage.
        return False
    return False
