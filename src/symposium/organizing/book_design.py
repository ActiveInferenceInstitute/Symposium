"""Optional, source-bound book artwork and exact presenter cover credits."""

from __future__ import annotations

import hashlib
import io
import os
import stat
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final, TypedDict

from matplotlib import get_data_path
from PIL import Image, ImageFont, UnidentifiedImageError

from .book_cover_facts import (
    BOOK_MARGIN_MM,
    PUBLIC_CONTACT,
    PUBLIC_WEBSITE,
    cover_metadata_latex,
    cover_metadata_rows,
    parse_cover_doi,
    prepare_cover_facts,
)
from .book_cover_facts import (
    latex_text as _latex,
)
from .models import PublicationError, PublicEvent, PublicPresentation

INSTITUTION: Final = "Active Inference Institute"
MAX_IMAGE_BYTES: Final = 20 * 1024 * 1024


class BookDesignError(PublicationError):
    """A design input cannot safely become single-page front matter."""

    def __init__(self, reason: str, path: Path | None = None) -> None:
        self.reason = reason
        self.path = path
        super().__init__(reason)


@dataclass(frozen=True, slots=True)
class BookDesign:
    """Explicit local PNG inputs; submitted presenter labels remain authoritative."""

    cover_image: Path
    frontispiece_image: Path
    title: str | None = None
    website_url: str = PUBLIC_WEBSITE
    contact_email: str = PUBLIC_CONTACT
    doi: str | None = None


@dataclass(frozen=True, slots=True)
class PreparedBookDesign:
    """Validated image bytes and measured, contiguous cover-credit columns."""

    title: str
    credits: tuple[str, ...]
    columns: tuple[tuple[str, ...], ...]
    cover: bytes
    frontispiece: bytes
    cover_size: tuple[int, int]
    frontispiece_size: tuple[int, int]
    event_dates: str
    website_url: str
    contact_email: str
    content_width_pt: float
    doi: str | None = None


class ImageReceipt(TypedDict):
    path: str
    sha256: str
    size: int


class DesignReceipt(TypedDict):
    title: str
    authors: list[str]
    credit_columns: list[list[str]]
    author_font_pt: int
    cover_physical_page: int
    frontispiece_physical_page: int
    contents_after_frontispiece: bool
    event_dates: str
    website_url: str
    contact_email: str
    margin_mm: int
    doi: str | None
    doi_url: str | None
    cover: ImageReceipt
    frontispiece: ImageReceipt


def _image(path: Path) -> tuple[bytes, tuple[int, int]]:
    """Read a bounded regular PNG without following a supplied symlink path."""
    if not path.is_absolute() or ".." in path.parts:
        raise BookDesignError("Artwork paths must be absolute without traversal", path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise BookDesignError("Artwork paths cannot contain symlinks", path)
    if not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
        raise BookDesignError("Artwork must be a regular file", path)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise BookDesignError("Artwork must be a regular file", path)
        payload = stream.read(MAX_IMAGE_BYTES + 1)
    if len(payload) > MAX_IMAGE_BYTES:
        raise BookDesignError("Artwork exceeds the image byte budget", path)
    try:
        with Image.open(io.BytesIO(payload)) as image:
            if image.format != "PNG" or image.width < 32 or image.height < 32:
                raise BookDesignError("Artwork must be a nonempty PNG of at least 32 pixels", path)
            if image.width * image.height > 40_000_000:
                raise BookDesignError("Artwork exceeds the pixel budget", path)
            size = image.size
            image.verify()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as error:
        raise BookDesignError("Artwork is not a valid bounded PNG", path) from error
    return payload, size


def _lines(text: str, font: ImageFont.FreeTypeFont, width_pt: float) -> int:
    """Measure wrapping with the same staged font, at ten pixels per point."""
    lines, width = 1, 0.0
    for word in text.split():
        length = font.getlength(word + " ") / 10
        if length > width_pt:
            raise BookDesignError("Cover text contains a word wider than its layout column")
        if width and width + length > width_pt:
            lines, width = lines + 1, 0.0
        width += length
    return lines


def _credit_columns(
    credits: tuple[str, ...], width_pt: float
) -> tuple[tuple[tuple[str, ...], ...], int]:
    """Partition exact labels into contiguous columns using nine-point glyph widths."""
    font = ImageFont.truetype(str(Path(get_data_path()) / "fonts/ttf/DejaVuSerif.ttf"), 90)
    heights = [_lines(label, font, width_pt * 0.315) * 11 + 3 for label in credits]
    target = sum(heights) / 3
    columns: list[list[str]] = [[], [], []]
    used = [0, 0, 0]
    column = 0
    for label, height in zip(credits, heights, strict=True):
        if column < 2 and used[column] and used[column] + height > target:
            column += 1
        columns[column].append(label)
        used[column] += height
    if max(used) > 310:
        raise BookDesignError("Presenter credits exceed the single-page nine-point cover budget")
    return tuple(tuple(column) for column in columns), max(used)


def prepare_book_design(
    presentations: Sequence[PublicPresentation],
    design: BookDesign,
    default_title: str,
    *,
    event: PublicEvent | None = None,
) -> PreparedBookDesign:
    """Parse assets before output creation and deduplicate only exact display labels."""
    title = design.title if design.title is not None else default_title
    if not title.strip() or len(title) > 240 or any(ord(c) < 32 for c in title):
        raise BookDesignError("Cover title must be bounded single-line text")
    facts = replace(
        prepare_cover_facts(design.website_url, design.contact_email, event),
        doi=parse_cover_doi(design.doi),
    )
    content_width = facts.content_width_pt
    labels = tuple(dict.fromkeys(talk["presenter"] for talk in presentations))
    credits = (INSTITUTION,) + tuple(label for label in labels if label != INSTITUTION)
    columns, credit_height = _credit_columns(credits[1:], content_width)
    title_font = ImageFont.truetype(
        str(Path(get_data_path()) / "fonts/ttf/DejaVuSerif-Bold.ttf"), 240
    )
    metadata_font = ImageFont.truetype(
        str(Path(get_data_path()) / "fonts/ttf/DejaVuSerif.ttf"), 100
    )
    metadata_height = sum(
        _lines(text, metadata_font, content_width) * 12 + 2
        for text, _ in cover_metadata_rows(facts)
    )
    if (
        _lines(title, title_font, content_width) * 27 + credit_height + 280 + metadata_height
        > facts.content_height_pt - 20
    ):
        raise BookDesignError("Title and presenter credits exceed the single-page cover budget")
    cover, cover_size = _image(design.cover_image)
    frontispiece, frontispiece_size = _image(design.frontispiece_image)
    return PreparedBookDesign(
        title,
        credits,
        columns,
        cover,
        frontispiece,
        cover_size,
        frontispiece_size,
        facts.event_dates,
        facts.website_url,
        facts.contact_email,
        content_width,
        facts.doi,
    )


def stage_book_design(project: Path, prepared: PreparedBookDesign) -> DesignReceipt:
    """Write exclusive artwork and native PDF front matter into the staged project."""
    assets = project / "artwork"
    assets.mkdir()
    receipts = []
    for name, payload in (
        ("cover.png", prepared.cover),
        ("frontispiece.png", prepared.frontispiece),
    ):
        path = assets / name
        with path.open("xb") as stream:
            stream.write(payload)
        receipts.append(
            ImageReceipt(
                path=str(path.relative_to(project)),
                sha256=hashlib.sha256(payload).hexdigest(),
                size=len(payload),
            )
        )
    columns = []
    for column in prepared.columns:
        labels = "\n".join(_latex(label) + r"\par\vspace{2pt}" for label in column)
        columns.append(
            r"\begin{minipage}[t]{0.315\textwidth}\raggedright\fontsize{9}{11}\selectfont "
            + labels
            + r"\end{minipage}"
        )
    # Paths are trusted staged names. detokenize also supports a workspace containing spaces.
    cover = r"\detokenize{" + str(assets / "cover.png") + "}"
    spread = r"\detokenize{" + str(assets / "frontispiece.png") + "}"
    body = "\n".join(
        [
            r"\begin{titlepage}\centering\vspace*{-6mm}",
            r"{\fontsize{24}{27}\selectfont\bfseries " + _latex(prepared.title) + r"\par}",
            r"\vspace{3mm}{\large Working Program\par}\vspace{4mm}",
            *cover_metadata_latex(prepared),
            r"\includegraphics[width=\textwidth,height=60mm,keepaspectratio]{" + cover + "}",
            r"\par\vspace{4mm}{\large\bfseries " + _latex(prepared.credits[0]) + r"\par}",
            r"\vspace{2mm}{\small Contributing presenters\par}\vspace{2mm}",
            r"\noindent " + r"\hfill".join(columns),
            r"\vfill{\small Book of Abstracts\par}\end{titlepage}",
            r"\setcounter{page}{2}\thispagestyle{empty}\begingroup\centering",
            r"\vspace*{\fill}\includegraphics[width=\textwidth,height=0.94\textheight,keepaspectratio]{"
            + spread
            + "}",
            r"\par\vspace*{\fill}\endgroup\clearpage",
            r"\makeatletter\renewcommand*\l@section{\@dottedtocline{1}{0em}{2.8em}}\makeatother",
            r"\tableofcontents\clearpage",
        ]
    )
    with (project / "frontmatter.tex").open("x", encoding="utf-8") as stream:
        stream.write(body + "\n")
    return DesignReceipt(
        title=prepared.title,
        authors=list(prepared.credits),
        credit_columns=[list(column) for column in prepared.columns],
        author_font_pt=9,
        cover_physical_page=1,
        frontispiece_physical_page=2,
        contents_after_frontispiece=True,
        event_dates=prepared.event_dates,
        website_url=prepared.website_url,
        contact_email=prepared.contact_email,
        margin_mm=BOOK_MARGIN_MM,
        doi=prepared.doi,
        doi_url="https://doi.org/" + prepared.doi if prepared.doi else None,
        cover=receipts[0],
        frontispiece=receipts[1],
    )
