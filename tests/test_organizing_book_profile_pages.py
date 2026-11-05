"""Public-profile book pages preserve source prose without visible source footers."""

from __future__ import annotations

import html
import json
from dataclasses import replace
from pathlib import Path

import pytest

from symposium.organizing.artifacts import stage_abstract_book, write_dossiers
from symposium.organizing.book_profiles import BookProfilesError, load_book_profiles
from symposium.organizing.models import PublicBundle, canonical_bytes, content_hash
from symposium.organizing.visualizations import CohortDocument
from tests.test_cli_organize import invoke
from tests.test_organizing_site import bundle as bundle
from tests.test_organizing_visualizations import document as document
from tests.test_organizing_visualizations import person


def public_profile_path(bundle: PublicBundle, document: CohortDocument, tmp_path: Path) -> Path:
    row = person(bundle["presentations"][0]["presenter"].strip(), "Literal <profile> & $text$ ~ ·")
    row["affiliations"] = "Institute A & Lab <B>"
    row["orcid"] = "0000-0002-1825-0097"
    document["participants"] = [row]
    document["participant_order"] = [row["id"]]
    document["records_sha256"] = content_hash([row])
    document["source"].update(included_participants=1, public_view_total_rows=1)
    path = tmp_path / "current-public.json"
    path.write_bytes(canonical_bytes(document))
    return path


def test_book_profile_page_retains_exact_fields_and_abstract_without_source_footer(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    cohort_path = public_profile_path(bundle, document, tmp_path)
    profiles = load_book_profiles(cohort_path, bundle)
    project = stage_abstract_book(bundle, tmp_path / "book", presenter_profiles=profiles)
    raw = (project / "manuscript/01_abstract_book.md").read_text()
    text = html.unescape(raw)
    assert "**Affiliations:** Institute A & Lab <B>" in text
    assert "**ORCID:** [0000-0002-1825-0097](https://orcid.org/0000-0002-1825-0097)" in text
    assert "Literal <profile> & $text$ ~ ·" in text
    assert bundle["presentations"][0]["abstract"] in text
    assert "<profile>" not in raw and "<B>" not in raw
    assert "**Abstract**" in raw
    assert "submitted source" not in raw and "Source:" not in raw
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert manifest["presenter_profiles"]["projection_sha256"] == profiles.projection_sha256
    assert manifest["talks"][0]["source_url"] == bundle["presentations"][0]["source_url"]
    assert manifest["pdf_layout"] == {"paper": "A4", "margins_mm": 18}
    assert manifest["submitted_source_displayed"] is False
    assert (
        json.loads((project / "manuscript/config.yaml").read_text())["metadata"]["geometry"]
        == "a4paper,margin=18mm"
    )


def test_book_profile_tampering_refuses_before_workspace_creation(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    cohort_path = public_profile_path(bundle, document, tmp_path)
    profiles = load_book_profiles(cohort_path, bundle)
    tampered = replace(profiles, profiles=(replace(profiles.profiles[0], affiliations="Changed"),))
    with pytest.raises(BookProfilesError):
        stage_abstract_book(bundle, tmp_path / "rejected", presenter_profiles=tampered)
    assert not (tmp_path / "rejected").exists()


def test_organizer_dossier_keeps_internal_source_provenance(
    bundle: PublicBundle, tmp_path: Path
) -> None:
    dossier = write_dossiers(bundle, tmp_path / "dossiers")[0].read_text()
    assert "Source: [submitted source]" in dossier
    project = stage_abstract_book(bundle, tmp_path / "book")
    assert "submitted source" not in (project / "manuscript/01_abstract_book.md").read_text()


def test_book_cli_stages_public_profile_fields(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    cohort = public_profile_path(bundle, document, tmp_path)
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle))
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        tmp_path / "book",
        "--public-root",
        tmp_path / "public",
        "--public-participants",
        cohort,
    )
    assert result == 0
    manuscript = tmp_path / "book/projects/symposium_2026/manuscript/01_abstract_book.md"
    assert "Affiliations:" in manuscript.read_text()


def test_book_cli_team_capture_requires_public_participant_context(
    bundle: PublicBundle, tmp_path: Path
) -> None:
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle))
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        tmp_path / "rejected",
        "--public-root",
        tmp_path / "public",
        "--public-team",
        tmp_path / "team.json",
    )
    assert result == 1 and not (tmp_path / "rejected").exists()


def test_book_profile_whole_label_join_trims_only_outer_whitespace(
    bundle: PublicBundle, document: CohortDocument, tmp_path: Path
) -> None:
    bundle["presentations"][0]["presenter"] = "  Synthetic Researcher  "
    path = public_profile_path(bundle, document, tmp_path)
    profiles = load_book_profiles(path, bundle)
    project = stage_abstract_book(bundle, tmp_path / "book", presenter_profiles=profiles)
    text = html.unescape((project / "manuscript/01_abstract_book.md").read_text())
    assert "Presenter: " + bundle["presentations"][0]["presenter"] in text
    assert "Affiliations:" in text and "Institute A & Lab <B>" in text
