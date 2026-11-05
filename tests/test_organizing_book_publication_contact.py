"""Real book artifact admission keeps the cover contact exception narrow."""

from __future__ import annotations

import io
import zipfile
from typing import Literal, assert_never
from xml.sax.saxutils import escape

import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from symposium.organizing.book_cover_facts import PUBLIC_CONTACT
from symposium.organizing.models import PublicationError, _text
from symposium.organizing.publication import _check_artifact, _check_pdf, _scan_text


def _pdf(text: str, *, uri: str = "https://example.org/", active: bool = False) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )
    literal = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 72 720 Td ({literal}) Tj ET".encode())
    page[NameObject("/Contents")] = stream
    action = DictionaryObject(
        {NameObject("/S"): NameObject("/URI"), NameObject("/URI"): TextStringObject(uri)}
    )
    annotation = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Rect"): ArrayObject([NumberObject(n) for n in (72, 700, 300, 720)]),
            NameObject("/A"): action,
        }
    )
    page[NameObject("/Annots")] = ArrayObject([annotation])
    writer.add_metadata({"/Title": "Synthetic public book"})
    if active:
        writer.add_js("app.alert('synthetic');")
    target = io.BytesIO()
    writer.write(target)
    return target.getvalue()


def _docx(text: str) -> bytes:
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w") as package:
        package.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        package.writestr(
            "_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/></Relationships>',
        )
        package.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body><w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p></w:body></w:document>",
        )
    return target.getvalue()


def _document(kind: Literal["pdf", "docx"], text: str) -> bytes:
    match kind:
        case "pdf":
            return _pdf(text)
        case "docx":
            return _docx(text)
        case unreachable:
            assert_never(unreachable)


@pytest.mark.parametrize("kind", ["pdf", "docx"])
def test_book_contact_is_admitted_when_exact_reviewed_artifact_name(
    kind: Literal["pdf", "docx"],
) -> None:
    # Given a real document with the approved organizational cover contact.
    raw = _document(kind, PUBLIC_CONTACT)
    # When that document is admitted under the exact book artifact name.
    result = _check_artifact("book." + kind, raw)
    # Then the real parser accepts the artifact.
    assert result is None


@pytest.mark.parametrize("name", ["other.pdf", "downloads/book.pdf", "other.docx"])
def test_book_contact_is_rejected_when_other_document_name(name: str) -> None:
    # Given a contact-bearing real document outside the two exact book names.
    raw = _docx(PUBLIC_CONTACT) if name.endswith("docx") else _pdf(PUBLIC_CONTACT)
    # When the recognized document types are scanned, the exception does not apply.
    with pytest.raises(PublicationError):
        _check_artifact(name, raw)


@pytest.mark.parametrize(
    "name", ["dossiers/synthetic.md", "participants/synthetic.md", "program.ics"]
)
def test_book_contact_is_rejected_when_public_text_artifact(name: str) -> None:
    # Given the organizational contact in a non-book public resource.
    raw = PUBLIC_CONTACT.encode()
    # When the resource is scanned, ordinary contact restrictions remain.
    with pytest.raises(PublicationError):
        _check_artifact(name, raw)


@pytest.mark.parametrize("kind", ["pdf", "docx"])
@pytest.mark.parametrize(
    "private",
    [
        "other@example.org",
        "prefix+" + PUBLIC_CONTACT,
        PUBLIC_CONTACT + ".private",
        "https://docs.google.com/document/d/synthetic",
        "/Users/synthetic/private",
        "/Volumes/synthetic/private",
    ],
)
def test_book_contact_exception_rejects_when_other_private_content(
    kind: Literal["pdf", "docx"], private: str
) -> None:
    # Given approved contact text accompanied by private content.
    text = PUBLIC_CONTACT + " " + private
    raw = _document(kind, text)
    # When the book is checked, the approved contact does not mask another violation.
    with pytest.raises(PublicationError):
        _check_artifact("book." + kind, raw)


def test_pdf_mailto_is_admitted_when_exact_book_contact() -> None:
    # Given a real book with one exact authorized contact destination.
    raw = _pdf(PUBLIC_CONTACT, uri="mailto:" + PUBLIC_CONTACT)
    # When parsed as the reviewed book, the bounded mailto is accepted.
    assert _check_artifact("book.pdf", raw) is None


@pytest.mark.parametrize(
    "uri",
    [
        "mailto:other@example.org",
        "mailto:" + PUBLIC_CONTACT + "?subject=synthetic",
        "mailto:" + PUBLIC_CONTACT + ",other@example.org",
        "http://example.org/",
        "https://example.org/?token=synthetic",
        "https://127.0.0.1/",
        "https://coda.io/synthetic",
    ],
)
def test_pdf_contact_exception_rejects_when_destination_not_approved(uri: str) -> None:
    # Given an authorized contact and an unapproved PDF destination.
    raw = _pdf(PUBLIC_CONTACT, uri=uri)
    # When parsed as the book, destination checks remain strict.
    with pytest.raises(PublicationError):
        _check_artifact("book.pdf", raw)


def test_pdf_contact_exception_rejects_when_active_content() -> None:
    # Given the authorized contact plus real PDF JavaScript objects.
    raw = _pdf(PUBLIC_CONTACT, active=True)
    # When parsed as a book, the active-content boundary still rejects it.
    with pytest.raises(PublicationError):
        _check_artifact("book.pdf", raw)


@pytest.mark.parametrize("boundary", ["text", "pdf", "participant"])
def test_contact_is_rejected_when_default_boundary(
    boundary: Literal["text", "pdf", "participant"],
) -> None:
    # Given organizational contact data without book artifact admission.
    # When the default scanner or public participant text boundary is used.
    with pytest.raises(PublicationError):
        match boundary:
            case "text":
                _scan_text(PUBLIC_CONTACT.encode())
            case "pdf":
                _check_pdf(_pdf(PUBLIC_CONTACT, uri="mailto:" + PUBLIC_CONTACT))
            case "participant":
                _text(PUBLIC_CONTACT, "Synthetic participant")
            case unreachable:
                assert_never(unreachable)
