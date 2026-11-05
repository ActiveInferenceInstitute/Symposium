"""Public profile admission uses real files and exact display-label membership."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from dataclasses import asdict, replace
from pathlib import Path
from typing import Literal, assert_never

import pytest

from symposium.organizing.book_profiles import (
    BINDING_RULE,
    TEAM_DOCUMENT,
    TEAM_NAME,
    TEAM_SOURCE_URL,
    TEAM_TABLE_URI,
    BookProfilesError,
    TeamCapture,
    load_book_profiles,
    verify_book_profiles,
)
from symposium.organizing.models import (
    PublicationError,
    PublicBundle,
    canonical_bytes,
    content_hash,
)
from symposium.organizing.visualization_data import FIELDS, PUBLIC_VIEW
from symposium.organizing.visualizations import CohortDocument
from tests.test_organizing_site import bundle as bundle
from tests.test_organizing_visualizations import person


@pytest.fixture
def program(bundle: PublicBundle) -> PublicBundle:
    first = bundle["presentations"][0]
    first["presenter"] = "Synthetic A"
    for number, presenter in enumerate(
        ("Synthetic B", "Synthetic A, Synthetic B", "Synthetic Learner"), 2
    ):
        talk = copy.deepcopy(first)
        talk.update(id=f"talk-{number}", presenter=presenter, title=f"Contribution {number}")
        bundle["presentations"].append(talk)
    bundle["participants"][0]["affiliations"] = "Outdated institution, never used"
    return bundle


@pytest.fixture
def cohort_document() -> CohortDocument:
    rows = [
        person("Synthetic A", "A supplied self-report."),
        person("Synthetic B"),
        person("Other Public Participant"),
    ]
    rows[0].update(affiliations="Current A University", orcid="0000-0001-2345-678X")
    return CohortDocument(
        schema_version=1,
        year=2026,
        participants=rows,
        participant_order=[row["id"] for row in rows],
        substantive_fields=list(FIELDS),
        records_sha256=content_hash(rows),
        source={
            "source_url": PUBLIC_VIEW,
            "capture_file_sha256": "a" * 64,
            "historical_data_used": False,
            "private_intake_used": False,
            "included_participants": len(rows),
            "public_view_total_rows": len(rows),
        },
    )


@pytest.fixture
def team_capture(program: PublicBundle) -> TeamCapture:
    return TeamCapture(
        schema_version=1,
        year=2026,
        captured_utc="2026-11-05 17:06:16 UTC",
        source_url=TEAM_SOURCE_URL,
        source_table_uri=TEAM_TABLE_URI,
        source_table_name=TEAM_NAME,
        source_document_title=TEAM_DOCUMENT,
        columns={"name": "c-1kiQbsVXN6", "affiliations": "c-R4PPTTkDm6"},
        source_total_rows=2,
        has_more=False,
        binding_rule=BINDING_RULE,
        program_bundle_sha256=content_hash(program),
        rows=[
            {
                "source_row_id": "i-synthetic-b",
                "name": "Synthetic B",
                "affiliations": "Team B Institute",
                "presentation_ids": ["talk-2"],
            },
            {
                "source_row_id": "i-unmatched",
                "name": "Other Organizer",
                "affiliations": "Other Institute",
                "presentation_ids": [],
            },
        ],
    )


def save_cohort(document: CohortDocument, path: Path) -> Path:
    document["records_sha256"] = content_hash(document["participants"])
    path.write_bytes(canonical_bytes(document))
    return path


def test_book_profiles_join_only_current_whole_labels_and_bind_sources(
    program: PublicBundle,
    cohort_document: CohortDocument,
    team_capture: TeamCapture,
    tmp_path: Path,
) -> None:
    # Given: eligible new participant fields, a public team row, and an older roster.
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    team = tmp_path / "team.json"
    team.write_bytes(canonical_bytes(team_capture))
    # When: optional book profile inputs are admitted and independently verified.
    value = load_book_profiles(cohort, program, team)
    profiles = verify_book_profiles(value, program)
    # Then: neither composite labels nor the old bundle participant record acquire info.
    assert [profile.presenter for profile in profiles] == ["Synthetic A", "Synthetic B"]
    assert profiles[0].affiliations == "Current A University"
    assert profiles[0].orcid == "0000-0001-2345-678X"
    assert profiles[0].background == "A supplied self-report."
    assert profiles[0].source_urls == (PUBLIC_VIEW,)
    assert profiles[1].affiliations == "Team B Institute"
    assert profiles[1].source_urls == (TEAM_SOURCE_URL,)
    assert value.cohort_file_sha256 == hashlib.sha256(cohort.read_bytes()).hexdigest()
    assert value.team_file_sha256 == hashlib.sha256(team.read_bytes()).hexdigest()
    assert "i-synthetic-b" not in json.dumps(asdict(value))
    assert "source_row_id" not in json.dumps(asdict(value))


def test_cohort_only_profiles_omit_empty_rows_without_inventing_a_fallback(
    program: PublicBundle, cohort_document: CohortDocument, tmp_path: Path
) -> None:
    # Given: a source with only one matching nonblank profile.
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    # When: no organizer supplement is supplied.
    value = load_book_profiles(cohort, program)
    # Then: the sparse projection retains its original text and no organizer binding.
    assert len(value.profiles) == 1 and value.profiles[0].presenter == "Synthetic A"
    assert value.team_file_sha256 is None and value.team_source_url is None


def test_case_different_and_composite_presenter_labels_are_not_identity_matches(
    program: PublicBundle, cohort_document: CohortDocument, tmp_path: Path
) -> None:
    # Given: a case-different published label, plus a composite containing a cohort name.
    program["presentations"][0]["presenter"] = "synthetic A"
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    # When: the exact-label projection is built.
    value = load_book_profiles(cohort, program)
    # Then: casefolding, splitting and the older roster are not used.
    assert value.profiles == ()


def test_equal_public_affiliations_merge_only_contributing_sources(
    program: PublicBundle,
    cohort_document: CohortDocument,
    team_capture: TeamCapture,
    tmp_path: Path,
) -> None:
    # Given: the same exact A affiliation in both eligible public sources.
    team_capture["rows"][0].update(
        name="Synthetic A", affiliations="Current A University", presentation_ids=["test-talk"]
    )
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    team = tmp_path / "team.json"
    team.write_bytes(canonical_bytes(team_capture))
    # When: the sources are joined.
    value = load_book_profiles(cohort, program, team)
    # Then: both public source URLs accompany the unchanged self-report.
    assert value.profiles[0].source_urls == (PUBLIC_VIEW, TEAM_SOURCE_URL)


def test_conflicting_public_affiliations_require_reconciliation(
    program: PublicBundle,
    cohort_document: CohortDocument,
    team_capture: TeamCapture,
    tmp_path: Path,
) -> None:
    # Given: two different affiliations supplied for the same exact published label.
    team_capture["rows"][0].update(
        name="Synthetic A", affiliations="Different Institute", presentation_ids=["test-talk"]
    )
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    team = tmp_path / "team.json"
    team.write_bytes(canonical_bytes(team_capture))
    # When / Then: ambiguity stops admission rather than silently choosing a source.
    with pytest.raises(BookProfilesError, match="Conflicting public affiliations"):
        load_book_profiles(cohort, program, team)
    assert not (tmp_path / "workspace").exists()


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ('"year": 2026', '"year": 2025'),
        ('"source_total_rows": 2', '"source_total_rows": 1'),
        ('"has_more": false', '"has_more": true'),
        (TEAM_SOURCE_URL, "https://example.org/unapproved"),
        (TEAM_TABLE_URI, "superhuman://docs/unapproved/tables/private"),
        ('"talk-2"', '"test-talk"'),
        ('"i-unmatched"', '"i-synthetic-b"'),
        ('"Other Organizer"', '"Synthetic B"'),
        ('"Team B Institute"', '"Contact me at hidden@example.org"'),
        ('"Team B Institute"', '"https://drive.google.com/private"'),
        ('"schema_version": 1', '"schema_version": true'),
        ('"source_total_rows": 2', '"unexpected": "secret", "source_total_rows": 2'),
    ],
)
def test_malformed_or_nonpublic_team_capture_fails_closed(
    before: str,
    after: str,
    program: PublicBundle,
    cohort_document: CohortDocument,
    team_capture: TeamCapture,
    tmp_path: Path,
) -> None:
    # Given: a complete capture with one provenance, binding or public-text defect.
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    original = canonical_bytes(team_capture).decode()
    assert before in original
    team = tmp_path / "team.json"
    team.write_text(original.replace(before, after), encoding="utf-8")
    # When / Then: real file admission rejects the defective capture entirely.
    with pytest.raises(PublicationError):
        load_book_profiles(cohort, program, team)


@pytest.mark.parametrize("changed", ["text", "label", "source", "hash"])
def test_detached_projection_rejects_replaced_values_or_stale_bindings(
    changed: Literal["text", "label", "source", "hash"],
    program: PublicBundle,
    cohort_document: CohortDocument,
    tmp_path: Path,
) -> None:
    # Given: a valid admitted projection that is subsequently changed in memory.
    cohort = save_cohort(cohort_document, tmp_path / "cohort.json")
    value = load_book_profiles(cohort, program)
    profile = value.profiles[0]
    mutations = {
        "text": replace(value, profiles=(replace(profile, background="Changed text"),)),
        "label": replace(value, profiles=(replace(profile, presenter="Synthetic B"),)),
        "source": replace(value, profiles=(replace(profile, source_urls=(TEAM_SOURCE_URL,)),)),
        "hash": replace(value, cohort_file_sha256="b" * 64),
    }
    # When / Then: verification observes the changed value before rendering begins.
    with pytest.raises(BookProfilesError):
        verify_book_profiles(mutations[changed], program)


def test_projection_rejects_changed_approved_program(
    program: PublicBundle, cohort_document: CohortDocument, tmp_path: Path
) -> None:
    # Given: a source-bound value and a later changed program title.
    value = load_book_profiles(save_cohort(cohort_document, tmp_path / "cohort.json"), program)
    program["presentations"][0]["title"] = "Changed contribution title"
    # When / Then: the earlier source-bound profile projection is not silently reused.
    with pytest.raises(BookProfilesError):
        verify_book_profiles(value, program)


@pytest.mark.parametrize("kind", ["symlink", "fifo", "invalid-json"])
def test_profile_source_file_boundaries_fail_before_admission(
    kind: Literal["symlink", "fifo", "invalid-json"], program: PublicBundle, tmp_path: Path
) -> None:
    # Given: a path that is not a bounded regular JSON source.
    path = tmp_path / "source.json"
    match kind:
        case "symlink":
            actual = tmp_path / "actual.json"
            actual.write_text("{}")
            path.symlink_to(actual)
        case "fifo":
            os.mkfifo(path)
        case "invalid-json":
            path.write_text("invalid JSON")
        case unreachable:
            assert_never(unreachable)
    # When / Then: the input cannot block on a FIFO or follow a substituted source.
    with pytest.raises(ValueError):
        load_book_profiles(path, program)
