"""Prepend designed front matter to a native Template DOCX without rewriting prose."""

from __future__ import annotations

import copy
import zipfile
from collections.abc import Sequence
from pathlib import Path
from typing import Final
from xml.etree import ElementTree as ET

from .book_cover_facts import cover_metadata_rows
from .book_design import BookDesignError, PreparedBookDesign
from .models import PublicPresentation

W: Final = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R: Final = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL: Final = "{http://schemas.openxmlformats.org/package/2006/relationships}"
MAX_PACKAGE_BYTES: Final = 250 * 1024 * 1024


def _package_xml(element: ET.Element, namespace: str) -> bytes:
    """Retain native OPC default namespaces required by LibreOffice's package reader."""
    root = copy.deepcopy(element)
    for node in root.iter():
        if not node.tag.startswith(namespace):
            raise BookDesignError("Native DOCX package vocabulary has an unexpected namespace")
        node.tag = node.tag[len(namespace) :]
    root.set("xmlns", namespace[1:-1])
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _paragraph(
    text: str,
    *,
    size: int = 18,
    bold: bool = False,
    center: bool = False,
    page_before: bool = False,
) -> ET.Element:
    paragraph = ET.Element(W + "p")
    properties = ET.SubElement(paragraph, W + "pPr")
    ET.SubElement(
        properties, W + "spacing", {W + "after": "40", W + "line": "240", W + "lineRule": "auto"}
    )
    if center:
        ET.SubElement(properties, W + "jc", {W + "val": "center"})
    if page_before:
        ET.SubElement(properties, W + "pageBreakBefore")
    run = ET.SubElement(paragraph, W + "r")
    run_properties = ET.SubElement(run, W + "rPr")
    ET.SubElement(
        run_properties, W + "rFonts", {W + "ascii": "DejaVu Serif", W + "hAnsi": "DejaVu Serif"}
    )
    ET.SubElement(run_properties, W + "sz", {W + "val": str(size)})
    if bold:
        ET.SubElement(run_properties, W + "b")
    ET.SubElement(run, W + "t").text = text
    return paragraph


def _picture(
    relationship: str,
    dimensions: tuple[int, int],
    *,
    height_pt: float,
    drawing_id: int,
    max_width_pt: float,
    page_before: bool = False,
) -> ET.Element:
    width, height = dimensions
    scale = min(max_width_pt / width, height_pt / height)
    cx, cy = round(width * scale * 12700), round(height * scale * 12700)
    paragraph = _paragraph("", center=True, page_before=page_before)
    run = paragraph.find(W + "r")
    if run is None:
        raise BookDesignError("Image paragraph has no native run")
    drawing = ET.fromstring(
        f'''<w:drawing xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{drawing_id}" name="Symposium artwork {drawing_id}" descr="Generated conceptual active inference artwork"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{drawing_id}" name="Symposium artwork"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{relationship}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>'''
    )
    run.append(drawing)
    return paragraph


def _credits(prepared: PreparedBookDesign) -> ET.Element:
    table = ET.Element(W + "tbl")
    width = round(prepared.content_width_pt * 20)
    column_width, remainder = divmod(width, len(prepared.columns))
    widths = [column_width + (index < remainder) for index in range(len(prepared.columns))]
    properties = ET.SubElement(table, W + "tblPr")
    ET.SubElement(properties, W + "tblW", {W + "w": str(width), W + "type": "dxa"})
    ET.SubElement(properties, W + "tblLayout", {W + "type": "fixed"})
    grid = ET.SubElement(table, W + "tblGrid")
    for size in widths:
        ET.SubElement(grid, W + "gridCol", {W + "w": str(size)})
    row = ET.SubElement(table, W + "tr")
    ET.SubElement(ET.SubElement(row, W + "trPr"), W + "cantSplit")
    for column, size in zip(prepared.columns, widths, strict=True):
        cell = ET.SubElement(row, W + "tc")
        properties = ET.SubElement(cell, W + "tcPr")
        ET.SubElement(properties, W + "tcW", {W + "w": str(size), W + "type": "dxa"})
        margins = ET.SubElement(properties, W + "tcMar")
        for name in ("left", "right"):
            ET.SubElement(margins, W + name, {W + "w": "40", W + "type": "dxa"})
        for label in column:
            cell.append(_paragraph(label))
        if not column:
            cell.append(_paragraph(""))
    return table


def _contents(body: ET.Element, presentations: Sequence[PublicPresentation]) -> list[ET.Element]:
    """Link each contents entry to its exact native heading bookmark, including duplicates."""
    headings: dict[str, list[str]] = {}
    for paragraph in body.findall(W + "p"):
        bookmark = paragraph.find(W + "bookmarkStart")
        if bookmark is not None:
            name = bookmark.get(W + "name")
            if name:
                text = "".join(node.text or "" for node in paragraph.iter(W + "t"))
                headings.setdefault(text, []).append(name)
    result = [_paragraph("Contents", size=30, bold=True, page_before=True)]
    for number, talk in enumerate(presentations, 1):
        candidates = headings.get(talk["title"], [])
        if not candidates:
            raise BookDesignError("Native DOCX heading bookmark differs from the submitted title")
        paragraph = _paragraph("")
        run = paragraph.find(W + "r")
        if run is None:
            raise BookDesignError("Contents paragraph has no native run")
        paragraph.remove(run)
        link = ET.SubElement(paragraph, W + "hyperlink", {W + "anchor": candidates.pop(0)})
        contents_run = _paragraph(f"{number}. {talk['title']}").find(W + "r")
        if contents_run is None:
            raise BookDesignError("Contents link has no native run")
        link.append(contents_run)
        result.append(paragraph)
    return result


def prepend_book_design(
    path: Path, prepared: PreparedBookDesign, presentations: Sequence[PublicPresentation]
) -> None:
    """Preserve native body XML while adding cover, physical-page-two art and linked contents."""
    if path.is_symlink() or path.stat().st_size > MAX_PACKAGE_BYTES:
        raise BookDesignError("Native DOCX is not a bounded regular package", path)
    with zipfile.ZipFile(path) as source:
        members = source.infolist()
        if len(members) > 20_000 or sum(row.file_size for row in members) > MAX_PACKAGE_BYTES:
            raise BookDesignError("Native DOCX exceeds the archive budget", path)
        document = ET.fromstring(source.read("word/document.xml"))
        relationships = ET.fromstring(source.read("word/_rels/document.xml.rels"))
        content_types = ET.fromstring(source.read("[Content_Types].xml"))
        body = document.find(W + "body")
        if body is None or not len(body):
            raise BookDesignError("Native DOCX has no manuscript body", path)
        ids = {node.get("Id") for node in relationships}
        if "rIdSymposiumCover" in ids or "rIdSymposiumFrontispiece" in ids:
            raise BookDesignError("Native DOCX already contains designed front matter", path)
        drawings = [
            int(node.get("id", "0"))
            for node in document.iter()
            if node.tag.endswith("}docPr") and node.get("id", "0").isdigit()
        ]
        first_id = max(drawings, default=0) + 1
        contents = _contents(body, presentations)
        nodes = [
            _paragraph(prepared.title, size=42, bold=True, center=True),
            _paragraph("Working Program", size=24, center=True),
            *(
                _paragraph(text, size=size, center=True)
                for text, size in cover_metadata_rows(prepared)
            ),
            _picture(
                "rIdSymposiumCover",
                prepared.cover_size,
                height_pt=170,
                drawing_id=first_id,
                max_width_pt=prepared.content_width_pt,
            ),
            _paragraph(prepared.credits[0], size=28, bold=True, center=True),
            _paragraph("Contributing presenters", size=18, center=True),
            _credits(prepared),
            _picture(
                "rIdSymposiumFrontispiece",
                prepared.frontispiece_size,
                height_pt=650,
                drawing_id=first_id + 1,
                max_width_pt=prepared.content_width_pt,
                page_before=True,
            ),
            *contents,
        ]
        first = body[0]
        if first.tag != W + "p":
            raise BookDesignError("Native DOCX opening must be a paragraph", path)
        properties = first.find(W + "pPr")
        if properties is None:
            properties = ET.Element(W + "pPr")
            first.insert(0, properties)
        if properties.find(W + "pageBreakBefore") is None:
            ET.SubElement(properties, W + "pageBreakBefore")
        for index, node in enumerate(nodes):
            body.insert(index, node)
        image_parts = {
            "word/media/symposium-cover.png": prepared.cover,
            "word/media/symposium-frontispiece.png": prepared.frontispiece,
        }
        if image_parts.keys() & {row.filename for row in members}:
            raise BookDesignError("Native DOCX artwork part already exists", path)
        for identifier, name in (
            ("rIdSymposiumCover", "symposium-cover.png"),
            ("rIdSymposiumFrontispiece", "symposium-frontispiece.png"),
        ):
            ET.SubElement(
                relationships,
                REL + "Relationship",
                {"Id": identifier, "Type": R[1:-1] + "/image", "Target": "media/" + name},
            )
        namespace = "{http://schemas.openxmlformats.org/package/2006/content-types}"
        if not any(node.get("Extension") == "png" for node in content_types):
            ET.SubElement(
                content_types,
                namespace + "Default",
                {"Extension": "png", "ContentType": "image/png"},
            )
        # Core date attributes contain lexical QNames (dcterms:W3CDTF).
        # ElementTree does not rewrite those values when it renames tag prefixes.
        # Keep canonical bindings so every retained xsi:type prefix still resolves.
        for prefix, namespace_uri in (
            ("cp", "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"),
            ("dc", "http://purl.org/dc/elements/1.1/"),
            ("dcterms", "http://purl.org/dc/terms/"),
            ("dcmitype", "http://purl.org/dc/dcmitype/"),
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"),
        ):
            ET.register_namespace(prefix, namespace_uri)
        core = ET.fromstring(source.read("docProps/core.xml"))
        creator_tag = "{http://purl.org/dc/elements/1.1/}creator"
        creator = core.find(creator_tag)
        if creator is None:
            creator = ET.SubElement(core, creator_tag)
        creator.text = "; ".join(prepared.credits)
        title_tag = "{http://purl.org/dc/elements/1.1/}title"
        title = core.find(title_tag)
        if title is None:
            title = ET.SubElement(core, title_tag)
        title.text = prepared.title
        replacements = {
            "word/document.xml": ET.tostring(document, encoding="utf-8", xml_declaration=True),
            "word/_rels/document.xml.rels": _package_xml(relationships, REL),
            "[Content_Types].xml": _package_xml(content_types, namespace),
            "docProps/core.xml": ET.tostring(core, encoding="utf-8", xml_declaration=True),
        }
        target = path.with_suffix(".designed.docx")
        with (
            target.open("xb") as stream,
            zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as output,
        ):
            for member in members:
                payload = replacements.get(member.filename)
                output.writestr(
                    member,
                    payload if payload is not None else source.read(member),
                )
            for name, payload in image_parts.items():
                output.writestr(name, payload)
    target.replace(path)
