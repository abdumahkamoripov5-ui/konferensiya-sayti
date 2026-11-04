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
                names = [entry.filename for entry in entries]
                if (len(entries) > 2000
                        or len(names) != len(set(names))
                        or sum(e.file_size for e in entries) > 50 * 1024 * 1024
                        or any(e.flag_bits & 1 for e in entries)
                        or any(name.lower().endswith("vbaproject.bin") for name in names)):
                    return False
                for name in ("[Content_Types].xml", "word/document.xml"):
                    info = document.getinfo(name)
                    if info.file_size > 5 * 1024 * 1024:
                        return False
                    xml = document.read(name)
                    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
                        return False
                    root = ElementTree.fromstring(xml)
                    if name == "[Content_Types].xml":
                        namespace = "{http://schemas.openxmlformats.org/package/2006/content-types}"
                        if root.tag != namespace + "Types":
                            return False
                        if not any(item.tag == namespace + "Override"
                                   and item.get("PartName") == "/word/document.xml"
                                   and item.get("ContentType") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
                                   for item in root):
                            return False
                        if any("macroenabled" in item.get("ContentType", "").lower()
                               or "vbaproject" in item.get("ContentType", "").lower()
                               for item in root):
                            return False
                    if name == "word/document.xml" and root.tag != "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document":
                        return False
                return True
    except Exception:
        # Malformed or unsupported documents must never reach storage.
        return False
    return False
