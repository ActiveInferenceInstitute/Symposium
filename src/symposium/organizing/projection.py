"""Build a fresh public projection and a separate private reconciliation ledger."""

from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .models import (
    PublicationError,
    PublicBundle,
    PublicEvent,
    PublicParticipant,
    PublicPresentation,
    PublicResource,
    PublicSession,
    content_hash,
    public_id,
    text_hash,
    validate_bundle,
)

PARTICIPANT_FIELDS = (
    "name",
    "affiliations",
    "orcid",
    "background",
    "pragmatic_value",
    "epistemic_value",
    "active_inference_application",
    "challenges",
    "learning_needs",
    "future_impact",
)
NULL_VALUES = {"None", "NaN", "nan", "NA", "N/A", "NULL", "null", "<NA>"}


def cell_text(value: Any, *, depth: int = 0) -> str:
    """Read documented rich-cell variants without leaking reference metadata."""
    if depth > 20:
        raise PublicationError("Rich cell nesting exceeds its bound")
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise PublicationError("Nonfinite cell value")
        return str(value)
    if isinstance(value, list):
        return "\n".join(cell_text(item, depth=depth + 1) for item in value)
    if isinstance(value, dict):
        if "value" in value:
            return cell_text(value["value"], depth=depth + 1)
        if value.get("type") == "dt" and "epoch" in value:
            epoch = value["epoch"]
            if type(epoch) not in (int, float) or not -62135596800 <= epoch < 253402300800:
                raise PublicationError("Typed datetime requires finite Unix epoch seconds")
            try:
                return (
                    datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")
                )
            except (OverflowError, OSError, ValueError) as exc:
                raise PublicationError(
                    "Typed datetime epoch is outside the supported range"
                ) from exc
        input_text = value.get("input")
        if value.get("type") == "dt" and isinstance(input_text, str):
            return input_text
        name = value.get("name")
        if isinstance(name, str):
            return name
        text = value.get("text")
        if isinstance(text, str):
            return text
        root = value.get("root")
        if isinstance(root, dict):
            return cell_text(root.get("children", []), depth=depth + 1)
        children = value.get("children")
        if isinstance(children, list):
            return "".join(cell_text(child, depth=depth + 1) for child in children)
        url = value.get("url")
        if value.get("type") == "urlref" and isinstance(url, str):
            return url
    raise PublicationError("Unsupported rich-cell value requires private review")


def _values(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, str]:
    values = row.get("values")
    if not isinstance(values, dict):
        raise PublicationError("Source row has no field values")
    return {
        key: cell_text(values.get(column)) for key, column in mapping.items() if key != "pictures"
    }


def _picture_urls(row: dict[str, Any], column: str) -> list[str]:
    value = row.get("values", {}).get(column, {}).get("value", [])
    if value in (None, ""):
        return []
    if isinstance(value, str):
        value = [{"url": value}]
    elif isinstance(value, dict) and isinstance(value.get("url"), str):
        value = [value]
    if not isinstance(value, list):
        raise PublicationError("Presenter picture attachments require review")
    urls = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("url"), str):
            raise PublicationError("Unknown presenter picture attachment")
        urls.append(item["url"])
    return urls


def project_snapshot(
    snapshot: dict[str, Any], event: PublicEvent, resources: list[PublicResource]
) -> tuple[PublicBundle, dict[str, Any]]:
    """Only published program fields and affirmative-consent answers can pass.

    Media URLs, source IDs, workflow state and reasons stay in the private ledger.
    Images are deliberately absent until the separate verified media step.
    """
    from .bridge import validate_mapping

    mapping = validate_mapping(snapshot.get("mapping"))
    tables = snapshot.get("tables")
    if not isinstance(tables, dict) or set(tables) != {"presentations", "participants", "sessions"}:
        raise PublicationError("Incomplete private source snapshot")
    public: PublicBundle = {
        "schema_version": 1,
        "event": event,
        "presentations": [],
        "participants": [],
        "sessions": [],
        "resources": resources,
    }
    ledger: dict[str, Any] = {
        "schema_version": 1,
        "snapshot_sha256": content_hash(snapshot),
        "included": [],
        "excluded": [],
        "warnings": [],
        "media": {},
    }
    for name, table in tables.items():
        if not isinstance(table, dict) or not isinstance(table.get("rows"), list):
            raise PublicationError("Incomplete source table")
        rows = table["rows"]
        if (
            type(table.get("totalRows")) is not int
            or len(rows) != table["totalRows"]
            or any(
                not isinstance(row, dict)
                or not isinstance(row.get("rowId"), str)
                or not row["rowId"]
                for row in rows
            )
            or len({row["rowId"] for row in rows}) != len(rows)
        ):
            raise PublicationError("Partial or duplicate source rows")
    for row in tables["presentations"]["rows"]:
        source_id = row["rowId"]
        try:
            values = _values(row, mapping["sources"]["presentations"]["fields"])
            title, presenter = values["title"], values["presenter"]
            presentation: PublicPresentation = {
                "id": public_id("talk", presenter, title),
                "presenter": presenter,
                "title": title,
                "abstract": values["abstract"],
                "contribution_type": values["contribution_type"],
                "source_url": event["program_url"],
                "pictures": [],
                "abstract_sha256": text_hash(values["abstract"]),
            }
            candidate: PublicBundle = {
                **public,
                "presentations": [*public["presentations"], presentation],
            }
            validate_bundle(candidate)
            try:
                media = _picture_urls(
                    row, mapping["sources"]["presentations"]["fields"]["pictures"]
                )
            except PublicationError:
                media = []
                ledger["warnings"].append(
                    {
                        "kind": "presentation",
                        "source_row": source_id,
                        "reason": "Unrecognized picture attachment withheld; text remains published",
                    }
                )
            if not presentation["abstract"].strip():
                ledger["warnings"].append(
                    {
                        "kind": "presentation",
                        "source_row": source_id,
                        "reason": "No program abstract published yet; keep explicit pending state",
                    }
                )
            public["presentations"].append(presentation)
            ledger["included"].append(
                {
                    "kind": "presentation",
                    "source_row": source_id,
                    "public_id": presentation["id"],
                    "approval": "published-program",
                    "content_sha256": content_hash(presentation),
                }
            )
            ledger["media"][presentation["id"]] = media
        except (ValueError, TypeError, KeyError) as exc:
            ledger["excluded"].append(
                {
                    "kind": "presentation",
                    "source_row": source_id,
                    "reason": type(exc).__name__ + ": " + str(exc),
                }
            )
    eligible: list[tuple[str, PublicParticipant]] = []
    for row in tables["participants"]["rows"]:
        source_id = row["rowId"]
        try:
            fields = mapping["sources"]["participants"]["fields"]
            if not isinstance(row.get("values"), dict):
                raise PublicationError("Source row has no field values")
            consent = (
                cell_text(row.get("values", {}).get(fields["share_publicly"])).strip().casefold()
            )
            if consent not in {"yes", "y", "true", "1"}:
                ledger["excluded"].append(
                    {
                        "kind": "participant",
                        "source_row": source_id,
                        "reason": "No affirmative publication consent",
                    }
                )
                continue
            values = _values(row, fields)
            participant_values = {
                key: (values[key].strip() if values[key].strip() not in NULL_VALUES else "")
                for key in PARTICIPANT_FIELDS
            }
            if not participant_values["name"]:
                ledger["excluded"].append(
                    {"kind": "participant", "source_row": source_id, "reason": "Blank registration"}
                )
                continue
            if participant_values["orcid"] and not re.fullmatch(
                r"(?:https://orcid\.org/)?[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]",
                participant_values["orcid"],
            ):
                participant_values["orcid"] = ""
                ledger["warnings"].append(
                    {
                        "kind": "participant",
                        "source_row": source_id,
                        "reason": "Non-identifier ORCID response omitted; original retained privately",
                    }
                )
            participant: PublicParticipant = {
                "id": public_id("person", participant_values["name"].casefold()),
                "name": participant_values["name"],
                "affiliations": participant_values["affiliations"],
                "orcid": participant_values["orcid"],
                "background": participant_values["background"],
                "pragmatic_value": participant_values["pragmatic_value"],
                "epistemic_value": participant_values["epistemic_value"],
                "active_inference_application": participant_values["active_inference_application"],
                "challenges": participant_values["challenges"],
                "learning_needs": participant_values["learning_needs"],
                "future_impact": participant_values["future_impact"],
            }
            validate_bundle({**public, "participants": [participant]})
            eligible.append((source_id, participant))
        except (ValueError, TypeError, KeyError) as exc:
            ledger["excluded"].append(
                {
                    "kind": "participant",
                    "source_row": source_id,
                    "reason": type(exc).__name__ + ": " + str(exc),
                }
            )
    names = Counter(person["name"].casefold() for _, person in eligible)
    for source_id, person in eligible:
        if names[person["name"].casefold()] > 1:
            ledger["excluded"].append(
                {
                    "kind": "participant",
                    "source_row": source_id,
                    "reason": "Duplicate participant name; reconcile privately before publication",
                }
            )
            continue
        public["participants"].append(person)
        ledger["included"].append(
            {
                "kind": "participant",
                "source_row": source_id,
                "public_id": person["id"],
                "approval": "affirmative-registration-consent",
                "content_sha256": content_hash(person),
            }
        )
    for row in tables["sessions"]["rows"]:
        source_id = row["rowId"]
        try:
            values = _values(row, mapping["sources"]["sessions"]["fields"])
            if not values["start_utc"].strip() or not values["end_utc"].strip():
                ledger["excluded"].append(
                    {
                        "kind": "session",
                        "source_row": source_id,
                        "reason": "No published timed slot; no schedule inferred",
                    }
                )
                continue
            for key in ("start_utc", "end_utc"):
                parsed = datetime.fromisoformat(values[key].replace("Z", "+00:00"))
                if parsed.utcoffset() is None:
                    raise PublicationError("Source timestamp has no timezone")
                values[key] = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            session: PublicSession = {
                "id": public_id("session", values["title"], values["start_utc"]),
                "title": values["title"],
                "presenter": values["presenter"],
                "kind": values["kind"],
                "start_utc": values["start_utc"],
                "end_utc": values["end_utc"],
            }
            validate_bundle({**public, "sessions": [*public["sessions"], session]})
            public["sessions"].append(session)
            ledger["included"].append(
                {
                    "kind": "session",
                    "source_row": source_id,
                    "public_id": session["id"],
                    "approval": "published-schedule",
                    "content_sha256": content_hash(session),
                }
            )
        except (ValueError, TypeError, KeyError) as exc:
            ledger["excluded"].append(
                {
                    "kind": "session",
                    "source_row": source_id,
                    "reason": type(exc).__name__ + ": " + str(exc),
                }
            )
    public["presentations"].sort(
        key=lambda row: (
            row["contribution_type"],
            row["presenter"].casefold(),
            row["title"].casefold(),
        )
    )
    public["participants"].sort(key=lambda row: row["name"].casefold())
    public["sessions"].sort(key=lambda row: (row["start_utc"], row["title"]))
    bundle = validate_bundle(public)
    ledger["public_sha256"] = content_hash(bundle)
    return bundle, ledger
