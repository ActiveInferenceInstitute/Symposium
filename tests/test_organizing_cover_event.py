"""Source-bound event facts and the shared eighteen-millimetre cover geometry."""

from __future__ import annotations

import copy
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from PIL import Image

from symposium.organizing.book_design import (
    BOOK_MARGIN_MM,
    PUBLIC_CONTACT,
    PUBLIC_WEBSITE,
    BookDesign,
    prepare_book_design,
    stage_book_design,
)
from symposium.organizing.book_design_docx import W, prepend_book_design
from symposium.organizing.models import PublicationError, validate_bundle
from tests.test_organizing_artifacts import bundle
from tests.test_organizing_book_design import _native_docx


@pytest.fixture
def event_artwork(tmp_path: Path) -> BookDesign:
    cover, spread = tmp_path / "cover.png", tmp_path / "spread.png"
    Image.new("RGB", (300, 100), "#126478").save(cover)
    Image.new("RGB", (100, 160), "#82b9a3").save(spread)
    return BookDesign(cover, spread, "Synthetic Symposium — Presenter Program")


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    (
        ("2026-11-12", "2026-11-13", "November 12–13, 2026 (UTC)"),
        ("2026-11-12", "2026-11-12", "November 12, 2026 (UTC)"),
        ("2026-10-31", "2026-11-01", "October 31–November 1, 2026 (UTC)"),
    ),
)
def test_cover_dates_when_event_supplied_use_its_calendar_range(
    event_artwork: BookDesign, start: str, end: str, expected: str
) -> None:
    # Given exact public calendar dates, independently of the title or runtime clock.
    data = validate_bundle(bundle())
    event = copy.deepcopy(data["event"])
    event.update(start_date=start, end_date=end)
    # When cover facts are prepared from that event.
    prepared = prepare_book_design(data["presentations"], event_artwork, "Fallback", event=event)
    # Then the calendar range and approved organizational contacts are preserved.
    assert prepared.event_dates == expected
    assert prepared.website_url == PUBLIC_WEBSITE
    assert prepared.contact_email == PUBLIC_CONTACT


def test_cover_when_event_omitted_keeps_existing_prepare_call_compatible(
    event_artwork: BookDesign,
) -> None:
    # Given an existing caller supplying only the three original preparation arguments.
    data = validate_bundle(bundle())
    # When it prepares a cover without an event record.
    prepared = prepare_book_design(data["presentations"], event_artwork, "Fallback")
    # Then no calendar dates are inferred from the title or current clock.
    assert prepared.event_dates == ""
    assert prepared.credits == ("Active Inference Institute", "Synthetic Presenter")


def test_cover_when_event_staged_records_facts_and_all_exact_presenter_credits(
    tmp_path: Path, event_artwork: BookDesign
) -> None:
    # Given fifty-two exact published labels, including a three-person composite.
    data = validate_bundle(bundle())
    presentations = [
        dict(data["presentations"][0], presenter=f"Presenter {index:02d}") for index in range(52)
    ]
    presentations[20]["presenter"] = "Ada Example, Benoît Sample, Chen Exemplar"
    prepared = prepare_book_design(presentations, event_artwork, "Fallback", event=data["event"])
    project = tmp_path / "project"
    project.mkdir()
    # When the native PDF front matter and its manifest are staged.
    receipt = stage_book_design(project, prepared)
    # Then every named person and the source-bound cover facts survive in the shared design.
    individuals = [talk["presenter"] for talk in presentations]
    individuals[20:21] = ["Ada Example", "Benoît Sample", "Chen Exemplar"]
    assert receipt["authors"] == ["Active Inference Institute"] + individuals
    assert receipt["event_dates"] == "November 4–6, 2026 (UTC)"
    assert receipt["website_url"] == PUBLIC_WEBSITE and receipt["contact_email"] == PUBLIC_CONTACT
    assert receipt["margin_mm"] == BOOK_MARGIN_MM == 18
    assert prepared.content_width_pt == pytest.approx(174 * 72 / 25.4)
    frontmatter = (project / "frontmatter.tex").read_text()
    assert all(
        value in frontmatter for value in (receipt["event_dates"], PUBLIC_WEBSITE, PUBLIC_CONTACT)
    )


def test_word_cover_when_facts_added_keeps_art_break_and_uses_printable_width(
    tmp_path: Path, event_artwork: BookDesign
) -> None:
    # Given a native Word package and prepared source-bound event facts.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(
        data["presentations"], event_artwork, "Fallback", event=data["event"]
    )
    path = tmp_path / "native.docx"
    _native_docx(path, data)
    # When the shared cover is prepended.
    prepend_book_design(path, prepared, data["presentations"])
    # Then cover facts precede its art, the portrait starts a new page, and columns fit.
    with zipfile.ZipFile(path) as package:
        document = ET.fromstring(package.read("word/document.xml"))
    body = document.find(W + "body")
    assert body is not None
    text = ["".join(item.text or "" for item in row.iter(W + "t")) for row in body]
    for value in (prepared.event_dates, PUBLIC_WEBSITE, PUBLIC_CONTACT):
        assert text.index(value) < text.index("Active Inference Institute")
    breaks = [node for node in body if node.find(W + "pPr/" + W + "pageBreakBefore") is not None]
    assert (
        len(breaks) == 3
        and breaks[0].find(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"
        )
        is not None
    )
    table = body.find(W + "tbl")
    assert table is not None
    width = int(table.find(W + "tblPr/" + W + "tblW").get(W + "w"))
    assert width == round(prepared.content_width_pt * 20)
    assert (
        sum(int(node.get(W + "w")) for node in table.findall(W + "tblGrid/" + W + "gridCol"))
        == width
    )
    assert all(
        int(node.get("cx")) <= round(prepared.content_width_pt * 12700)
        for node in document.iter(
            "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent"
        )
    )


@pytest.mark.parametrize("website", ("http://example.com/", "https://localhost/"))
def test_cover_when_website_is_not_public_https_refuses(
    event_artwork: BookDesign, website: str
) -> None:
    # Given an explicitly supplied unsafe cover destination.
    data = validate_bundle(bundle())
    design = BookDesign(
        event_artwork.cover_image, event_artwork.frontispiece_image, website_url=website
    )
    # When cover preparation is requested.
    with pytest.raises(PublicationError):
        prepare_book_design(data["presentations"], design, "Fallback")
    # Then no invalid destination can become cover text.


def test_cover_when_contact_contains_line_break_refuses(event_artwork: BookDesign) -> None:
    # Given contact text that is not a single organizational email address.
    data = validate_bundle(bundle())
    design = BookDesign(
        event_artwork.cover_image,
        event_artwork.frontispiece_image,
        contact_email="blanket@example.com\nInjected text",
    )
    # When cover preparation is requested.
    with pytest.raises(PublicationError):
        prepare_book_design(data["presentations"], design, "Fallback")
    # Then no second metadata line is accepted as a contact address.
