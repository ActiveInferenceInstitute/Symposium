"""Participant CSV schema shared by edition scaffolds and analysis.

Optional fields retain the legacy pandas null-marker convention. Other text,
including numeric-looking values and ORCID identifiers, is never inferred.
Names and consent are always interpreted as literal text.
"""

import csv
import re
from pathlib import Path
from typing import Final, TypedDict

from symposium.io.writers import ReportWriter


class ParticipantSchemaError(ValueError):
    """A participant CSV cannot safely be processed."""


class Participant(TypedDict):
    name: str
    email: str
    affiliations: str
    orcid: str
    background: str
    pragmatic_value: str
    epistemic_value: str
    active_inference_application: str
    challenges: str
    learning_needs: str
    heard_about: str
    future_impact: str
    comments: str
    share_publicly: str
    row_index: int


OPTIONAL_NULL_MARKERS: Final = frozenset(
    {
        "",
        "#N/A",
        "#N/A N/A",
        "#NA",
        "-1.#IND",
        "-1.#QNAN",
        "-NaN",
        "-nan",
        "1.#IND",
        "1.#QNAN",
        "<NA>",
        "N/A",
        "NA",
        "NULL",
        "NaN",
        "None",
        "n/a",
        "nan",
        "null",
    }
)


SURVEY_COLUMNS: Final = {
    "Can we share this information publicly?": "share_publicly",
    "What is your name?": "name",
    "What is your email?": "email",
    "What are your affiliations?": "affiliations",
    "What is your ORCID?": "orcid",
    "What is your background & prior works? Feel free to provide as much information & links as you like.": "background",
    "What would be useful for you in the Symposium (pragmatic value)?": "pragmatic_value",
    "What would be interesting or informative for you to learn from the Symposium (epistemic value)?": "epistemic_value",
    "How are you applying Active Inference? What domain, stage?": "active_inference_application",
    "What are the biggest hurdles or challenges facing Active Inference research and application?": "challenges",
    "What would help you learn and apply Active Inference? E.g. resource, tool, or community development.": "learning_needs",
    "How did you hear about the Symposium?": "heard_about",
    "How could Active Inference applications make impact in 2026? (Think big!)": "future_impact",
    "Any other comments or questions?": "comments",
}


def participant_headers(year: int = 2026) -> list[str]:
    """Return the survey questions for an edition, with next-year impact."""
    from symposium.core.edition import Edition

    Edition(year=year)
    return [
        header.replace("impact in 2026?", f"impact in {year + 1}?") for header in SURVEY_COLUMNS
    ]


def normalize_headers(headers: list[str]) -> list[str]:
    """Resolve historical, canonical, and short labels without ambiguity."""
    aliases = {header.casefold(): field for header, field in SURVEY_COLUMNS.items()}
    aliases.update({field.casefold(): field for field in SURVEY_COLUMNS.values()})
    aliases.update({"name": "name", "affiliations": "affiliations", "background": "background"})
    normalized: list[str] = []
    for header in headers:
        clean = header.strip().lstrip("\ufeff").strip()
        field = aliases.get(clean.casefold(), clean.casefold())
        if re.fullmatch(
            r"How could Active Inference applications make impact in [0-9]{4}\? \(Think big!\)",
            clean,
        ):
            field = "future_impact"
        if field in normalized:
            raise ParticipantSchemaError(
                "Duplicate or ambiguous participant header; use one column per field"
            )
        normalized.append(field)
    missing = {"name", "share_publicly"} - set(normalized)
    if missing:
        raise ParticipantSchemaError(
            "Missing required participant headers: " + ", ".join(sorted(missing))
        )
    return normalized


def load_participants(path: Path) -> dict[str, Participant]:
    """Read text without numeric inference; reject unsafe output collisions."""
    participants: dict[str, Participant] = {}
    names: set[str] = set()
    filenames: set[str] = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            headers = normalize_headers(next(reader, []))
            for index, row in enumerate(reader):
                if not row:
                    continue
                if len(row) != len(headers):
                    raise ParticipantSchemaError(
                        f"Participant row {index + 2}: expected {len(headers)} columns, got {len(row)}"
                    )
                values = dict(zip(headers, (value.strip() for value in row)))
                values = {
                    key: ""
                    if key not in {"name", "share_publicly"} and value in OPTIONAL_NULL_MARKERS
                    else value
                    for key, value in values.items()
                }
                name = values["name"]
                if not name or values["share_publicly"].casefold() not in {"yes", "y", "true", "1"}:
                    continue
                safe_name = ReportWriter.sanitize_filename(name).casefold()
                if not safe_name:
                    raise ParticipantSchemaError(
                        f"Participant row {index + 2}: name has no safe filename characters"
                    )
                if name.casefold() in names:
                    raise ParticipantSchemaError(
                        f"Participant row {index + 2}: duplicate public participant name"
                    )
                if safe_name in filenames:
                    raise ParticipantSchemaError(
                        f"Participant row {index + 2}: participant filename collision"
                    )
                names.add(name.casefold())
                filenames.add(safe_name)
                participants[name] = Participant(
                    name=name,
                    email=values.get("email", ""),
                    affiliations=values.get("affiliations", ""),
                    orcid=values.get("orcid", ""),
                    background=values.get("background", ""),
                    pragmatic_value=values.get("pragmatic_value", ""),
                    epistemic_value=values.get("epistemic_value", ""),
                    active_inference_application=values.get("active_inference_application", ""),
                    challenges=values.get("challenges", ""),
                    learning_needs=values.get("learning_needs", ""),
                    heard_about=values.get("heard_about", ""),
                    future_impact=values.get("future_impact", ""),
                    comments=values.get("comments", ""),
                    share_publicly=values["share_publicly"],
                    row_index=index,
                )
        except csv.Error as exc:
            raise ParticipantSchemaError(
                f"Malformed participant CSV near line {reader.line_num}"
            ) from exc
    return participants
