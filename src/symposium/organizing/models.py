"""Closed public interchange schema; private source records never belong here."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, TypedDict, cast
from urllib.parse import urlsplit

SCHEMA_VERSION = 1
MAX_BUNDLE_BYTES = 16 * 1024 * 1024
EMAIL = re.compile(
    r"(?<![\w.!#$%&'*+/=?^`{|}~-])[\w.!#$%&'*+/=?^`{|}~-]{1,64}@[\w-]{1,63}(?:\.[\w-]{1,63})+",
    re.UNICODE,
)
PRIVATE_LINK = re.compile(
    r"(?<![\w.-])(?:https?://)?(?:docs\.superhuman\.com|coda\.io|drive\.google\.com|docs\.google\.com|[a-z0-9.-]{0,253}sharepoint\.com)/",
    re.I,
)
SHA256 = re.compile(r"[a-f0-9]{64}")
IDENTIFIER = re.compile(r"[a-z][a-z0-9_-]{0,95}")


class PublicationError(ValueError):
    """Input cannot be safely projected, rendered, or published."""


class PublicLink(TypedDict):
    title: str
    url: str


class PublicPicture(TypedDict):
    path: str
    sha256: str
    alt: str


class PublicEvent(TypedDict):
    id: str
    title: str
    year: int
    start_date: str
    end_date: str
    timezone: str
    program_url: str
    participant_registration_url: str
    presenter_registration_url: str
    community_url: str
    donate_url: str
    livestreams: list[PublicLink]


class PublicPresentation(TypedDict):
    id: str
    presenter: str
    title: str
    abstract: str
    contribution_type: str
    source_url: str
    pictures: list[PublicPicture]
    abstract_sha256: str


class PublicParticipant(TypedDict):
    id: str
    name: str
    affiliations: str
    orcid: str
    background: str
    pragmatic_value: str
    epistemic_value: str
    active_inference_application: str
    challenges: str
    learning_needs: str
    future_impact: str


class PublicSession(TypedDict):
    id: str
    title: str
    presenter: str
    kind: str
    start_utc: str
    end_utc: str


class PublicResource(TypedDict):
    id: str
    title: str
    description: str
    url: str
    category: str


class PublicBundle(TypedDict):
    schema_version: int
    event: PublicEvent
    presentations: list[PublicPresentation]
    participants: list[PublicParticipant]
    sessions: list[PublicSession]
    resources: list[PublicResource]


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    ).encode("utf-8")


def content_hash(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def public_id(prefix: str, *parts: str) -> str:
    return prefix + "-" + text_hash("\x1f".join(parts))[:16]


def _record(value: object, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise PublicationError(f"{label}: unexpected or missing public fields")
    return value


def _text(value: object, label: str, *, required: bool = False) -> str:
    if not isinstance(value, str) or len(value) > 100000 or (required and not value.strip()):
        raise PublicationError(f"{label}: expected bounded text")
    if any(ord(ch) < 32 and ch not in "\n\r\t" for ch in value):
        raise PublicationError(f"{label}: control characters are not permitted")
    if ("@" in value and EMAIL.search(value)) or PRIVATE_LINK.search(value):
        raise PublicationError(
            f"{label}: contact information or private document links require review"
        )
    return value


def public_url(value: object, label: str = "URL") -> str:
    url = _text(value, label, required=True)
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise PublicationError(f"{label}: malformed URL") from exc
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or port not in (None, 443)
    ):
        raise PublicationError(f"{label}: expected a public HTTPS URL")
    host = parts.hostname.casefold().rstrip(".")
    if host in {"localhost", "0.0.0.0", "127.0.0.1", "::1"} or host.endswith(
        (".local", ".internal")
    ):
        raise PublicationError(f"{label}: local destinations are not public")
    import ipaddress

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise PublicationError(f"{label}: nonpublic address")
    if re.search(r"(?:token|secret|signature|api[_-]?key|auth|credential)", parts.query, re.I):
        raise PublicationError(f"{label}: credential-like URL query")
    return url


def safe_asset_path(value: object) -> str:
    path = _text(value, "picture path", required=True)
    parts = PurePosixPath(path)
    if (
        parts.is_absolute()
        or ".." in parts.parts
        or "\\" in path
        or not path.startswith("assets/portraits/")
        or parts.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}
    ):
        raise PublicationError("Picture path must stay under assets/portraits")
    return path


def _rows(value: object, label: str) -> list[dict[str, Any]]:
    if (
        not isinstance(value, list)
        or len(value) > 10000
        or any(not isinstance(row, dict) for row in value)
    ):
        raise PublicationError(f"{label}: expected a bounded record list")
    ids = [row.get("id") for row in value]
    if any(not isinstance(key, str) or not IDENTIFIER.fullmatch(key) for key in ids) or len(
        ids
    ) != len(set(ids)):
        raise PublicationError(f"{label}: invalid or duplicate public IDs")
    return value


def validate_bundle(value: object) -> PublicBundle:
    """Return a detached, strictly allowlisted projection or reject it entirely."""
    fields = {"schema_version", "event", "presentations", "participants", "sessions", "resources"}
    bundle = _record(value, fields, "Bundle")
    if type(bundle["schema_version"]) is not int or bundle["schema_version"] != SCHEMA_VERSION:
        raise PublicationError("Unsupported public interchange schema version")
    event_fields = set(PublicEvent.__annotations__)
    event = _record(bundle["event"], event_fields, "Event")
    if type(event["year"]) is not int or not 2000 <= event["year"] <= 2100:
        raise PublicationError("Event year is invalid")
    for field in event_fields - {"year", "livestreams"}:
        _text(event[field], "Event " + field, required=True)
    if not IDENTIFIER.fullmatch(event["id"]) or event["timezone"] != "UTC":
        raise PublicationError("Event needs a safe ID and explicit UTC timezone")
    try:
        start, end = date.fromisoformat(event["start_date"]), date.fromisoformat(event["end_date"])
    except ValueError as exc:
        raise PublicationError("Event dates must be ISO calendar dates") from exc
    if start.year != event["year"] or end.year != event["year"] or end < start:
        raise PublicationError("Event dates must belong to the selected edition")
    for field in (
        "program_url",
        "participant_registration_url",
        "presenter_registration_url",
        "community_url",
        "donate_url",
    ):
        public_url(event[field], "Event " + field)
    if not isinstance(event["livestreams"], list):
        raise PublicationError("Livestreams must be a list")
    for link in event["livestreams"]:
        _record(link, {"title", "url"}, "Livestream")
        _text(link["title"], "Livestream title", required=True)
        public_url(link["url"])
    titles: set[tuple[str, str]] = set()
    for row in _rows(bundle["presentations"], "Presentations"):
        _record(row, set(PublicPresentation.__annotations__), "Presentation")
        for key in ("presenter", "title", "abstract", "contribution_type"):
            _text(row[key], "Presentation " + key, required=key != "abstract")
        public_url(row["source_url"], "Presentation source")
        identity = (row["presenter"].casefold().strip(), row["title"].casefold().strip())
        if identity in titles:
            raise PublicationError("Duplicate presentation identity")
        titles.add(identity)
        if row["abstract_sha256"] != text_hash(row["abstract"]):
            raise PublicationError("Submitted abstract hash does not match its text")
        if not isinstance(row["pictures"], list) or len(row["pictures"]) > 20:
            raise PublicationError("Pictures must be a bounded list")
        for picture in row["pictures"]:
            _record(picture, set(PublicPicture.__annotations__), "Picture")
            safe_asset_path(picture["path"])
            if not isinstance(picture["sha256"], str) or not SHA256.fullmatch(picture["sha256"]):
                raise PublicationError("Invalid picture digest")
            _text(picture["alt"], "Picture alternative text", required=True)
    participant_names: set[str] = set()
    for row in _rows(bundle["participants"], "Participants"):
        _record(row, set(PublicParticipant.__annotations__), "Participant")
        for key in set(PublicParticipant.__annotations__) - {"id"}:
            _text(row[key], "Participant " + key, required=key == "name")
        name = row["name"].strip().casefold()
        if name in participant_names:
            raise PublicationError(
                "Duplicate consenting participant name requires private reconciliation"
            )
        participant_names.add(name)
        if row["orcid"] and not re.fullmatch(
            r"(?:https://orcid\.org/)?[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]", row["orcid"]
        ):
            raise PublicationError("Unrecognized ORCID format requires review")
    for row in _rows(bundle["sessions"], "Sessions"):
        _record(row, set(PublicSession.__annotations__), "Session")
        for key in set(PublicSession.__annotations__) - {"id"}:
            _text(row[key], "Session " + key, required=key not in {"presenter", "title"})
        try:
            times = [
                datetime.fromisoformat(row[key].replace("Z", "+00:00"))
                for key in ("start_utc", "end_utc")
            ]
        except ValueError as exc:
            raise PublicationError("Session timestamps must be ISO-8601 UTC") from exc
        if (
            any(t.utcoffset() is None or t.utcoffset().total_seconds() != 0 for t in times)
            or times[1] <= times[0]
        ):
            raise PublicationError("Session needs an increasing explicit UTC interval")
        if any(not start <= t.date() <= end for t in times):
            raise PublicationError("Session falls outside the approved event dates")
    for row in _rows(bundle["resources"], "Resources"):
        _record(row, set(PublicResource.__annotations__), "Resource")
        for key in ("title", "description", "category"):
            _text(row[key], "Resource " + key, required=True)
        public_url(row["url"], "Resource URL")
    raw = canonical_bytes(bundle)
    if len(raw) > MAX_BUNDLE_BYTES:
        raise PublicationError("Public bundle exceeds its byte limit")
    return cast(PublicBundle, json.loads(raw))


def load_bundle(path: Path) -> PublicBundle:
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BUNDLE_BYTES + 1)
    if len(raw) > MAX_BUNDLE_BYTES:
        raise PublicationError("Public bundle exceeds its byte limit")
    try:
        value = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise PublicationError("Public bundle must be valid UTF-8 JSON") from exc
    return validate_bundle(value)


def write_bundle(bundle: PublicBundle, path: Path) -> None:
    raw = canonical_bytes(validate_bundle(bundle))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("xb") as stream:
        stream.write(raw)
