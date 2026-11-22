"""Published proceedings metadata, separate from approved program content."""

from __future__ import annotations

import json
import re
from datetime import date
from importlib.resources import files
from typing import TypedDict, cast

from .models import PublicationError, PublicEvent, public_url


class Proceedings(TypedDict):
    """Citation and download metadata for an issued book."""

    event_id: str
    title: str
    version: str
    published_on: str
    doi: str
    concept_doi: str
    release_url: str
    pdf_url: str
    docx_url: str


def published_proceedings(event: PublicEvent) -> Proceedings | None:
    """Read the curated release for the selected edition when one is recorded."""
    if event["id"] != "symposium-2026" or event["year"] != 2026:
        return None
    source = files("symposium.organizing").joinpath("resources/proceedings-2026.json")
    record = json.loads(source.read_text(encoding="utf-8"))
    if (
        not isinstance(record, dict)
        or set(record) != set(Proceedings.__annotations__)
        or any(not isinstance(value, str) or not value.strip() for value in record.values())
        or record["event_id"] != event["id"]
    ):
        raise PublicationError("Invalid published proceedings metadata")
    try:
        published = date.fromisoformat(record["published_on"])
    except ValueError as exc:
        raise PublicationError("Invalid proceedings publication date") from exc
    if (
        published.isoformat() != record["published_on"]
        or published < date.fromisoformat(event["end_date"])
        or any(
            not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", record[key])
            for key in ("doi", "concept_doi")
        )
    ):
        raise PublicationError("Proceedings need a canonical publication date and Zenodo DOIs")
    for key in ("release_url", "pdf_url", "docx_url"):
        public_url(record[key], f"Proceedings {key}")
    return cast(Proceedings, record)
