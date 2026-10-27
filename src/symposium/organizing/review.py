"""Read-only intake comparisons of verified public publication trees."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TypedDict

from .models import PublicBundle, PublicLink, PublicPicture, content_hash
from .publication import verify_public_tree


class PublicReference(TypedDict):
    id: str
    name: str


class ChangedRecord(TypedDict):
    id: str
    before_name: str
    after_name: str
    fields: list[str]


class RecordChanges(TypedDict):
    added: list[PublicReference]
    removed: list[PublicReference]
    changed: list[ChangedRecord]


class ArtifactChanges(TypedDict):
    added: list[str]
    removed: list[str]
    changed: list[str]


class ReadinessReport(TypedDict):
    schema_version: int
    bundle_sha256: str
    snapshot_integrity: str
    source_freshness: str
    content_complete: bool
    pending_abstracts: list[PublicReference]
    untitled_sessions: list[PublicReference]
    warnings: list[str]


class UpdateReport(TypedDict):
    schema_version: int
    previous_bundle_sha256: str
    candidate_bundle_sha256: str
    snapshot_integrity: str
    source_freshness: str
    event_changed_fields: list[str]
    records: dict[str, RecordChanges]
    artifacts: ArtifactChanges
    participant_removals_require_review: bool
    warnings: list[str]
    candidate_readiness: ReadinessReport


def _content_readiness(bundle: PublicBundle) -> ReadinessReport:
    abstracts = sorted(
        (
            {"id": talk["id"], "name": talk["presenter"]}
            for talk in bundle["presentations"]
            if not talk["abstract"].strip()
        ),
        key=lambda item: item["id"],
    )
    sessions = sorted(
        (
            {"id": session["id"], "name": session["presenter"]}
            for session in bundle["sessions"]
            if not session["title"].strip()
        ),
        key=lambda item: item["id"],
    )
    warnings = []
    if not bundle["presentations"]:
        warnings.append("No presentations have been published.")
    if abstracts or sessions:
        warnings.append("Public abstracts or session titles remain pending.")
    return {
        "schema_version": 1,
        "bundle_sha256": content_hash(bundle),
        "snapshot_integrity": "verified",
        "source_freshness": "not_checked",
        "content_complete": bool(bundle["presentations"]) and not abstracts and not sessions,
        "pending_abstracts": abstracts,
        "untitled_sessions": sessions,
        "warnings": warnings,
    }


def readiness(public_dir: Path) -> ReadinessReport:
    """Verify snapshot integrity and report pending text; never query live sources."""
    return _content_readiness(verify_public_tree(public_dir))


def _changes(
    previous: Sequence[Mapping[str, str | list[PublicPicture] | list[PublicLink] | int]],
    candidate: Sequence[Mapping[str, str | list[PublicPicture] | list[PublicLink] | int]],
    label: str,
) -> RecordChanges:
    before = {str(row["id"]): row for row in previous}
    after = {str(row["id"]): row for row in candidate}
    return {
        "added": [
            {"id": key, "name": str(after[key][label])}
            for key in sorted(after.keys() - before.keys())
        ],
        "removed": [
            {"id": key, "name": str(before[key][label])}
            for key in sorted(before.keys() - after.keys())
        ],
        "changed": [
            {
                "id": key,
                "before_name": str(before[key][label]),
                "after_name": str(after[key][label]),
                "fields": sorted(
                    field for field in before[key] if before[key][field] != after[key][field]
                ),
            }
            for key in sorted(before.keys() & after.keys())
            if before[key] != after[key]
        ],
    }


def _artifacts(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and path.name not in {"program.json", "publication.json"}
    }


def review_update(previous_public_dir: Path, candidate_public_dir: Path) -> UpdateReport:
    """Compare public IDs exactly; changed IDs are removals/additions, never renames."""
    before = verify_public_tree(previous_public_dir)
    after = verify_public_tree(candidate_public_dir)
    records = {
        "presentations": _changes(before["presentations"], after["presentations"], "presenter"),
        "participants": _changes(before["participants"], after["participants"], "name"),
        "sessions": _changes(before["sessions"], after["sessions"], "title"),
        "resources": _changes(before["resources"], after["resources"], "title"),
    }
    old_files, new_files = _artifacts(previous_public_dir), _artifacts(candidate_public_dir)
    removals = bool(records["participants"]["removed"])
    return {
        "schema_version": 1,
        "previous_bundle_sha256": content_hash(before),
        "candidate_bundle_sha256": content_hash(after),
        "snapshot_integrity": "both_verified",
        "source_freshness": "not_checked",
        "event_changed_fields": sorted(
            key for key in before["event"] if before["event"][key] != after["event"][key]
        ),
        "records": records,
        "artifacts": {
            "added": sorted(new_files.keys() - old_files.keys()),
            "removed": sorted(old_files.keys() - new_files.keys()),
            "changed": sorted(
                key
                for key in old_files.keys() & new_files.keys()
                if old_files[key] != new_files[key]
            ),
        },
        "participant_removals_require_review": removals,
        "warnings": ["Participant removals require human review; no reason is inferred."]
        if removals
        else [],
        "candidate_readiness": _content_readiness(after),
    }
