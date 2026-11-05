"""Optional reserved DOI appears on both covers without changing submitted content."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from PIL import Image

from symposium.organizing.book_design import BookDesign, prepare_book_design, stage_book_design
from symposium.organizing.book_design_docx import W, prepend_book_design
from symposium.organizing.models import PublicationError, validate_bundle
from tests.test_organizing_artifacts import bundle
from tests.test_organizing_book_design import _native_docx

SYNTHETIC_DOI = "10.1000/synthetic-symposium_2026"


@pytest.fixture
def doi_artwork(tmp_path: Path) -> BookDesign:
    cover, spread = tmp_path / "cover.png", tmp_path / "spread.png"
    Image.new("RGB", (300, 100), "#126478").save(cover)
    Image.new("RGB", (100, 160), "#82b9a3").save(spread)
    return BookDesign(cover, spread, "Synthetic Symposium", doi=SYNTHETIC_DOI)


def test_pdf_cover_when_doi_supplied_stages_exact_identifier_and_link(
    tmp_path: Path, doi_artwork: BookDesign
) -> None:
    # Given a synthetic fixture DOI used only in this local test.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(
        data["presentations"], doi_artwork, "Fallback", event=data["event"]
    )
    project = tmp_path / "project"
    project.mkdir()
    # When native cover text and the design receipt are staged.
    receipt = stage_book_design(project, prepared)
    # Then the reserved identifier is escaped as literal text and bound in metadata.
    assert receipt["doi"] == SYNTHETIC_DOI
    assert receipt["doi_url"] == "https://doi.org/" + SYNTHETIC_DOI
    frontmatter = (project / "frontmatter.tex").read_text()
    escaped = SYNTHETIC_DOI.replace("_", r"\_")
    assert r"\href{https://doi.org/" + escaped + "}{DOI: " + escaped + "}" in frontmatter
    assert frontmatter.index("DOI: ") < frontmatter.index(r"\end{titlepage}")
    assert prepared.credits == ("Active Inference Institute", "Synthetic Presenter")


def test_word_cover_when_doi_added_retains_body_and_art_page_break(
    tmp_path: Path, doi_artwork: BookDesign
) -> None:
    # Given a genuine OOXML fixture with source title bookmarks and abstract text.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(
        data["presentations"], doi_artwork, "Fallback", event=data["event"]
    )
    path = tmp_path / "native.docx"
    _native_docx(path, data)
    # When the optional DOI-bearing cover is prepended.
    prepend_book_design(path, prepared, data["presentations"])
    # Then its DOI is on the cover before art and the native prose remains exact.
    with zipfile.ZipFile(path) as package:
        document = ET.fromstring(package.read("word/document.xml"))
    body = document.find(W + "body")
    assert body is not None
    texts = ["".join(item.text or "" for item in row.iter(W + "t")) for row in body]
    breaks = [
        index
        for index, row in enumerate(body)
        if row.find(W + "pPr/" + W + "pageBreakBefore") is not None
    ]
    assert (
        texts.index("DOI: " + SYNTHETIC_DOI) < texts.index("Active Inference Institute") < breaks[0]
    )
    assert len(breaks) == 3 and texts[breaks[1]] == "Contents"
    assert data["presentations"][0]["abstract"] in texts


@pytest.mark.parametrize("doi", (None, ""))
def test_cover_when_doi_omitted_preserves_identifier_free_behavior(
    tmp_path: Path, doi_artwork: BookDesign, doi: str | None
) -> None:
    # Given the original optional design API without a DOI.
    data = validate_bundle(bundle())
    design = BookDesign(doi_artwork.cover_image, doi_artwork.frontispiece_image, doi=doi)
    prepared = prepare_book_design(data["presentations"], design, "Fallback")
    project = tmp_path / "project"
    project.mkdir()
    # When the legacy cover is staged.
    receipt = stage_book_design(project, prepared)
    # Then no DOI is invented or displayed.
    assert receipt["doi"] is None and receipt["doi_url"] is None
    assert "DOI:" not in (project / "frontmatter.tex").read_text()


@pytest.mark.parametrize(
    "doi",
    (
        "https://doi.org/10.1000/example",
        "10.12/example",
        "10.1000/",
        "10.1000/example\nInjected text",
        "10.1000/example#fragment",
        "10.1000/example%20text",
        "10.1000/{unsafe}",
        " 10.1000/example",
    ),
)
def test_cover_when_doi_is_not_bare_safe_syntax_refuses(doi_artwork: BookDesign, doi: str) -> None:
    # Given URL, malformed registration prefix, whitespace, or unsafe delimiter text.
    data = validate_bundle(bundle())
    design = BookDesign(doi_artwork.cover_image, doi_artwork.frontispiece_image, doi=doi)
    # When cover preparation crosses the input boundary.
    with pytest.raises(PublicationError):
        prepare_book_design(data["presentations"], design, "Fallback")
    # Then no invalid identifier reaches staged TeX or Word.
