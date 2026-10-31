"""Turn a raw document into Markdown.

Docx uses Pandoc when the binary is installed. Otherwise the text is read
from the docx XML. Pdf text is extracted with pypdf.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


class UnsupportedDocument(ValueError):
    pass


def convert_to_markdown(filename: str, data: bytes) -> str:
    name = (filename or "document").lower()
    if name.endswith((".md", ".markdown", ".txt")):
        return data.decode("utf-8", errors="replace").strip()
    if name.endswith(".docx"):
        return _docx_to_markdown(data).strip()
    if name.endswith(".pdf"):
        return _pdf_to_markdown(data).strip()
    raise UnsupportedDocument("Send a .docx, .pdf, .md, or .txt file.")


def _docx_to_markdown(data: bytes) -> str:
    pandoc = shutil.which("pandoc")
    if pandoc:
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.docx"
            source.write_bytes(data)
            result = subprocess.run(
                [pandoc, "-f", "docx", "-t", "gfm", str(source)],
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    return _docx_xml_text(data)


def _docx_xml_text(data: bytes) -> str:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return "\n\n".join(paragraphs)


def _pdf_to_markdown(data: bytes) -> str:
    from pypdf import PdfReader
    import io

    reader = PdfReader(io.BytesIO(data))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"## Page {index}\n\n{text}")
    return "\n\n".join(pages)
