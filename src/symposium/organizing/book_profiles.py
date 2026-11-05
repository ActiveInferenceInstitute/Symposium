"""Optional book profiles from separately admitted, exact public source matches."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Final, TypedDict

from .models import PublicationError, PublicBundle, _text, content_hash, validate_bundle
from .visualization_data import PUBLIC_VIEW
from .visualizations import CohortDocument, load_authorized_cohort

TEAM_SOURCE_URL: Final = "https://docs.superhuman.com/d/_dfDPUsAuSgQ/_surazvwP"
TEAM_TABLE_URI: Final = (
    "superhuman://docs/fDPUsAuSgQ/pages/section-tWkVrazvwP/tables/grid-mF1dcaMzj6/views/default"
)
TEAM_NAME: Final = "Co-Organizing Team ~ 2026 Symposium"
TEAM_DOCUMENT: Final = "6th Applied Active Inference Symposium ~ Public Program"
BINDING_RULE: Final = "Exact, case-sensitive, trimmed whole presentation display label; composite labels are not split."
MAX_BYTES: Final = 16 * 1024 * 1024
SHA256: Final = re.compile(r"[a-f0-9]{64}")
ORCID: Final = re.compile(r"(?:https://orcid\.org/)?[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]")


@dataclass(frozen=True, slots=True)
class BookProfilesError(PublicationError):
    """An optional profile source or detached projection failed admission."""

    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class PresenterProfile:
    """Public display values only; raw source identifiers never enter this value."""

    presenter: str
    affiliations: str
    orcid: str
    background: str
    source_urls: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BookProfiles:
    """Frozen profile projection and content bindings, without source row IDs."""

    profiles: tuple[PresenterProfile, ...]
    bundle_sha256: str
    cohort_file_sha256: str
    cohort_records_sha256: str
    cohort_capture_sha256: str
    team_file_sha256: str | None
    team_source_url: str | None
    projection_sha256: str


class TeamRow(TypedDict):
    source_row_id: str
    name: str
    affiliations: str
    presentation_ids: list[str]


class TeamCapture(TypedDict):
    schema_version: int
    year: int
    captured_utc: str
    source_url: str
    source_table_uri: str
    source_table_name: str
    source_document_title: str
    columns: dict[str, str]
    source_total_rows: int
    has_more: bool
    binding_rule: str
    program_bundle_sha256: str
    rows: list[TeamRow]


def _read_source(path: Path) -> bytes:
    """Read a bounded regular file without following a final symlink or FIFO."""
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise BookProfilesError("Profile source must be a bounded regular JSON file")
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        with os.fdopen(os.open(path, flags), "rb") as stream:
            current = os.fstat(stream.fileno())
            if not stat.S_ISREG(current.st_mode) or (current.st_dev, current.st_ino) != (
                before.st_dev,
                before.st_ino,
            ):
                raise BookProfilesError("Profile source changed while opening")
            raw = stream.read(MAX_BYTES + 1)
    except OSError as exc:
        raise BookProfilesError("Profile source cannot be read safely") from exc
    if len(raw) > MAX_BYTES:
        raise BookProfilesError("Profile source exceeds its byte limit")
    return raw


def _team_rows(raw: bytes, bundle: PublicBundle) -> tuple[TeamRow, ...]:
    """Admit only the complete projected public organizer affiliation capture."""
    try:
        capture: TeamCapture = json.loads(raw)
        if not isinstance(capture, dict) or set(capture) != set(TeamCapture.__annotations__):
            raise BookProfilesError("Organizer capture has unexpected or missing fields")
        if (
            type(capture["schema_version"]) is not int
            or capture["schema_version"] != 1
            or type(capture["year"]) is not int
            or capture["year"] != 2026
            or capture["source_url"] != TEAM_SOURCE_URL
            or capture["source_table_uri"] != TEAM_TABLE_URI
            or capture["source_table_name"] != TEAM_NAME
            or capture["source_document_title"] != TEAM_DOCUMENT
            or capture["binding_rule"] != BINDING_RULE
            or capture["columns"] != {"name": "c-1kiQbsVXN6", "affiliations": "c-R4PPTTkDm6"}
            or capture["program_bundle_sha256"] != content_hash(bundle)
        ):
            raise BookProfilesError("Organizer capture differs from its approved public source")
        stamp = datetime.strptime(capture["captured_utc"], "%Y-%m-%d %H:%M:%S UTC")
        if stamp.year != 2026 or stamp.strftime("%Y-%m-%d %H:%M:%S UTC") != capture["captured_utc"]:
            raise BookProfilesError("Organizer capture needs a canonical 2026 UTC timestamp")
        rows = capture["rows"]
        if (
            not isinstance(rows, list)
            or len(rows) > 10000
            or type(capture["source_total_rows"]) is not int
            or capture["source_total_rows"] != len(rows)
            or capture["has_more"] is not False
        ):
            raise BookProfilesError("Organizer capture does not account for every source row")
        seen_ids: set[str] = set()
        seen_names: set[str] = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != set(TeamRow.__annotations__):
                raise BookProfilesError("Organizer row has unexpected or missing fields")
            name = _text(row["name"], "Organizer name", required=True).strip()
            _text(row["affiliations"], "Organizer affiliations")
            identifier = row["source_row_id"]
            if not isinstance(identifier, str) or not re.fullmatch(
                r"i-[A-Za-z0-9_-]{1,128}", identifier
            ):
                raise BookProfilesError("Organizer source row ID is malformed")
            if identifier in seen_ids or name in seen_names:
                raise BookProfilesError("Organizer source has duplicate row IDs or names")
            expected = [
                talk["id"] for talk in bundle["presentations"] if talk["presenter"].strip() == name
            ]
            if row["presentation_ids"] != expected:
                raise BookProfilesError(
                    "Organizer contribution binding differs from the whole presenter label"
                )
            seen_ids.add(identifier)
            seen_names.add(name)
        return tuple(rows)
    except (KeyError, TypeError, ValueError) as exc:
        raise BookProfilesError("Malformed public organizer affiliation capture") from exc


def _projection_hash(value: BookProfiles) -> str:
    payload = asdict(value)
    del payload["projection_sha256"]
    return content_hash(payload)


def verify_book_profiles(value: BookProfiles, bundle: PublicBundle) -> tuple[PresenterProfile, ...]:
    """Check detached profile values and bindings before any workspace is written."""
    checked = validate_bundle(bundle)
    digests = (
        value.bundle_sha256,
        value.cohort_file_sha256,
        value.cohort_records_sha256,
        value.cohort_capture_sha256,
        value.projection_sha256,
    )
    if (
        checked["event"]["year"] != 2026
        or value.bundle_sha256 != content_hash(checked)
        or any(not isinstance(item, str) or not SHA256.fullmatch(item) for item in digests)
        or not isinstance(value.profiles, tuple)
    ):
        raise BookProfilesError("Book profiles are not bound to the admitted 2026 program")
    if value.team_file_sha256 is None:
        if value.team_source_url is not None:
            raise BookProfilesError("Organizer source URL has no capture binding")
    elif (
        not isinstance(value.team_file_sha256, str)
        or not SHA256.fullmatch(value.team_file_sha256)
        or value.team_source_url != TEAM_SOURCE_URL
    ):
        raise BookProfilesError("Organizer capture binding is invalid")
    labels = tuple(dict.fromkeys(talk["presenter"].strip() for talk in checked["presentations"]))
    seen: list[str] = []
    for profile in value.profiles:
        if not isinstance(profile, PresenterProfile):
            raise BookProfilesError("Book profile has the wrong value type")
        name = _text(profile.presenter, "Profile presenter", required=True)
        for field in (profile.affiliations, profile.orcid, profile.background):
            _text(field, "Profile public text")
        if (
            name != name.strip()
            or name not in labels
            or name in seen
            or not any(
                field.strip() for field in (profile.affiliations, profile.orcid, profile.background)
            )
            or (profile.orcid and not ORCID.fullmatch(profile.orcid))
        ):
            raise BookProfilesError("Profile fields or exact presenter scope are invalid")
        if not isinstance(profile.source_urls, tuple):
            raise BookProfilesError("Profile source URLs must be an immutable tuple")
        expected_urls = tuple(
            url for url in (PUBLIC_VIEW, TEAM_SOURCE_URL) if url in profile.source_urls
        )
        if (
            not profile.source_urls
            or profile.source_urls != expected_urls
            or (TEAM_SOURCE_URL in profile.source_urls and value.team_file_sha256 is None)
        ):
            raise BookProfilesError("Profile source URLs are not admitted public sources")
        seen.append(name)
    if tuple(seen) != tuple(
        label for label in labels if label in seen
    ) or value.projection_sha256 != _projection_hash(value):
        raise BookProfilesError(
            "Profile projection differs from its admitted values or program order"
        )
    return value.profiles


def load_book_profiles(
    cohort_path: Path, bundle: PublicBundle, organizer_affiliations_path: Path | None = None
) -> BookProfiles:
    """Join supplied public fields to exact whole contribution labels, with no fallback."""
    checked = validate_bundle(bundle)
    raw = _read_source(cohort_path)
    cohort = load_authorized_cohort(cohort_path, checked)
    if _read_source(cohort_path) != raw:
        raise BookProfilesError("Authorized participant source changed during admission")
    document: CohortDocument = json.loads(raw)
    if content_hash(document["participants"]) != cohort.records_sha256:
        raise BookProfilesError("Participant profile fields differ from admitted cohort records")
    team_raw = (
        _read_source(organizer_affiliations_path)
        if organizer_affiliations_path is not None
        else None
    )
    team = _team_rows(team_raw, checked) if team_raw is not None else ()
    participants = {row["name"].strip(): row for row in document["participants"]}
    organizers = {row["name"].strip(): row for row in team}
    profiles: list[PresenterProfile] = []
    for label in dict.fromkeys(talk["presenter"].strip() for talk in checked["presentations"]):
        participant = participants.get(label)
        organizer = organizers.get(label)
        affiliations, orcid, background = (
            (participant[key] for key in ("affiliations", "orcid", "background"))
            if participant
            else ("", "", "")
        )
        team_affiliations = organizer["affiliations"] if organizer else ""
        if (
            affiliations.strip()
            and team_affiliations.strip()
            and affiliations.strip() != team_affiliations.strip()
        ):
            raise BookProfilesError("Conflicting public affiliations require source reconciliation")
        urls = tuple(
            url
            for url, present in (
                (PUBLIC_VIEW, any(field.strip() for field in (affiliations, orcid, background))),
                (TEAM_SOURCE_URL, bool(team_affiliations.strip())),
            )
            if present
        )
        if urls:
            profiles.append(
                PresenterProfile(
                    label,
                    affiliations if affiliations.strip() else team_affiliations,
                    orcid,
                    background,
                    urls,
                )
            )
    value = BookProfiles(
        tuple(profiles),
        content_hash(checked),
        hashlib.sha256(raw).hexdigest(),
        cohort.records_sha256,
        cohort.capture_sha256,
        hashlib.sha256(team_raw).hexdigest() if team_raw is not None else None,
        TEAM_SOURCE_URL if team_raw is not None else None,
        "",
    )
    value = replace(value, projection_sha256=_projection_hash(value))
    verify_book_profiles(value, checked)
    return value
