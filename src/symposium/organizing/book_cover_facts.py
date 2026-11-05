"""Public organizational cover contacts and validated event calendar facts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Final, Protocol

from .models import PublicationError, PublicEvent, public_url

BOOK_MARGIN_MM: Final = 18
PUBLIC_WEBSITE: Final = "https://symposium.activeinference.institute/"
PUBLIC_CONTACT: Final = "blanket@activeinference.institute"
_MONTHS: Final = (
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


@dataclass(frozen=True, slots=True)
class CoverEventFacts:
    """Parsed public facts with the shared eighteen-millimetre A4 content area."""

    event_dates: str
    website_url: str
    contact_email: str
    content_width_pt: float = (210 - 2 * BOOK_MARGIN_MM) * 72 / 25.4
    content_height_pt: float = (297 - 2 * BOOK_MARGIN_MM) * 72 / 25.4
    doi: str | None = None


class CoverMetadata(Protocol):
    """Read-only metadata shared by prepared facts and rendered covers."""

    @property
    def event_dates(self) -> str: ...

    @property
    def website_url(self) -> str: ...

    @property
    def contact_email(self) -> str: ...

    @property
    def doi(self) -> str | None: ...


def parse_cover_doi(value: str | None) -> str | None:
    """Accept one bounded bare DOI, without URLs, whitespace, or TeX delimiters."""
    if value is None or value == "":
        return None
    if len(value) > 256 or not re.fullmatch(
        r"10\.[0-9]{4,9}/[A-Za-z0-9][-._;()/:A-Za-z0-9]*", value
    ):
        raise PublicationError("Cover DOI must be a bounded bare DOI identifier")
    return value


def cover_metadata_rows(value: CoverMetadata) -> tuple[tuple[str, int], ...]:
    """Keep the same visible metadata order and Word half-point sizes in every cover."""
    rows = ((value.event_dates, 20), (value.website_url, 18), (value.contact_email, 18))
    if value.doi:
        rows += (("DOI: " + value.doi, 18),)
    return tuple(row for row in rows if row[0])


def latex_text(text: str) -> str:
    """Escape plain cover text without interpreting submitted display labels as TeX."""
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "$": r"\$",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def cover_metadata_latex(value: CoverMetadata) -> tuple[str, ...]:
    """Render checked cover metadata, linking only the explicitly supplied DOI."""
    lines = []
    for text, _ in cover_metadata_rows(value):
        content = latex_text(text)
        if value.doi and text == "DOI: " + value.doi:
            content = r"\href{https://doi.org/" + latex_text(value.doi) + "}{" + content + "}"
        lines.append(r"{\small " + content + r"\par}")
    lines[-1] += r"\vspace{2mm}"
    return tuple(lines)


def _event_dates(event: PublicEvent | None) -> str:
    """Use only the validated event's calendar dates and explicit UTC timezone."""
    if event is None:
        return ""
    try:
        start, end = date.fromisoformat(event["start_date"]), date.fromisoformat(event["end_date"])
    except ValueError as error:
        raise PublicationError("Cover event dates must be ISO calendar dates") from error
    if start > end or start.year != end.year or event["timezone"] != "UTC":
        raise PublicationError("Cover event dates must be an ordered UTC range within one year")
    days = str(start.day)
    if end != start:
        days += "–" + ("" if start.month == end.month else _MONTHS[end.month] + " ") + str(end.day)
    return f"{_MONTHS[start.month]} {days}, {start.year} (UTC)"


def prepare_cover_facts(
    website_url: str, contact_email: str, event: PublicEvent | None
) -> CoverEventFacts:
    """Parse explicit organizational contacts without reading participant contact fields."""
    website = public_url(website_url, "Cover website")
    if (
        not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}", contact_email)
        or len(contact_email) > 254
    ):
        raise PublicationError("Cover contact must be one bounded organizational email address")
    return CoverEventFacts(_event_dates(event), website, contact_email)
