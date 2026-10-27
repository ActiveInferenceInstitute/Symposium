"""Read-only intake reports over real consent-bound staged trees."""

import copy
import json
import stat

import pytest

from symposium.organizing.models import PublicationError, canonical_bytes, content_hash
from symposium.organizing.projection import project_snapshot
from symposium.organizing.publication import write_artifact_index, write_calendar
from symposium.organizing.review import readiness, review_update
from tests.test_cli_organize import invoke
from tests.test_organizing_publication import NOW, stage
from tests.test_organizing_publication import inputs as inputs


def candidate(inputs, *, complete=False, remove=False, rename=False):
    bundle, snapshot, _ = copy.deepcopy(inputs)
    if complete:
        snapshot["tables"]["sessions"]["rows"][0]["values"]["c-title"]["value"] = "Session"
    snapshot["tables"]["presentations"]["rows"][0]["values"]["c-abstract"]["value"] = ""
    if remove:
        snapshot["tables"]["participants"]["rows"] = []
        snapshot["tables"]["participants"]["totalRows"] = 0
    if rename:
        snapshot["tables"]["presentations"]["rows"][0]["values"]["c-title"]["value"] = "New title"
    projected, ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    return projected, snapshot, ledger


def calendar_artifacts(inputs, path):
    path.mkdir()
    write_calendar(inputs[0], path / "program.ics", generated_at=NOW)
    write_artifact_index(inputs[0], path)
    return path


def test_review_changes_are_deterministic_public_only_and_read_only(inputs, tmp_path):
    previous, current = tmp_path / "previous", tmp_path / "candidate"
    newer = candidate(inputs, complete=True, remove=True)
    stage(inputs, previous, artifacts_dir=calendar_artifacts(inputs, tmp_path / "old-artifacts"))
    stage(newer, current, artifacts_dir=calendar_artifacts(newer, tmp_path / "new-artifacts"))
    original = {
        str(p): p.read_bytes()
        for root in (previous, current)
        for p in root.rglob("*")
        if p.is_file()
    }
    result = review_update(previous, current)
    assert result == review_update(previous, current)
    assert result["previous_bundle_sha256"] == content_hash(inputs[0])
    assert result["candidate_bundle_sha256"] == content_hash(newer[0])
    assert result["records"]["presentations"]["changed"][0]["fields"] == [
        "abstract",
        "abstract_sha256",
    ]
    assert result["records"]["participants"]["removed"][0]["name"] == "Synthetic Learner"
    assert result["participant_removals_require_review"] is True
    assert result["records"]["sessions"]["changed"] == []
    assert len(result["records"]["sessions"]["added"]) == 1
    assert len(result["records"]["sessions"]["removed"]) == 1
    assert review_update(current, previous)["records"]["participants"]["added"]
    assert result["artifacts"] == {"added": [], "removed": [], "changed": ["program.ics"]}
    assert result["candidate_readiness"]["pending_abstracts"]
    assert result["candidate_readiness"]["untitled_sessions"] == []
    raw = canonical_bytes(result)
    assert b"private-row" not in raw and b"superhuman://" not in raw
    assert original == {
        str(p): p.read_bytes()
        for root in (previous, current)
        for p in root.rglob("*")
        if p.is_file()
    }


def test_additions_removals_never_guess_renames(inputs, tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    stage(inputs, old, artifacts_dir=calendar_artifacts(inputs, tmp_path / "artifacts"))
    stage(candidate(inputs, rename=True), new)
    result = review_update(old, new)
    talks = result["records"]["presentations"]
    assert len(talks["added"]) == len(talks["removed"]) == 1
    assert talks["changed"] == []
    assert result["artifacts"]["removed"] == ["program.ics"]
    assert review_update(new, old)["artifacts"]["added"] == ["program.ics"]
    assert review_update(new, old)["records"]["presentations"]["added"] == talks["removed"]


@pytest.mark.parametrize("target", ["previous", "candidate"])
@pytest.mark.parametrize("corruption", ["tamper", "unmanifested"])
def test_either_invalid_tree_prevents_report(inputs, tmp_path, target, corruption):
    old, new = tmp_path / "previous", tmp_path / "candidate"
    stage(inputs, old)
    stage(inputs, new)
    root = tmp_path / target
    if corruption == "tamper":
        (root / "program.json").write_bytes((root / "program.json").read_bytes() + b" ")
    else:
        (root / "extra.txt").write_text("Unexpected")
    with pytest.raises(PublicationError):
        review_update(old, new)
    output = tmp_path / "private" / "report.json"
    assert (
        invoke(
            "review-update",
            "--previous-public-dir",
            old,
            "--candidate-public-dir",
            new,
            "--output",
            output,
            "--public-root",
            tmp_path / "public",
        )
        == 1
    )
    assert not output.exists()
    with pytest.raises(PublicationError):
        readiness(root)


def test_readiness_pending_and_strict_exit_without_portrait_requirement(inputs, tmp_path, capsys):
    tree = tmp_path / "tree"
    stage(inputs, tree)
    assert readiness(tree)["source_freshness"] == "not_checked"
    assert invoke("readiness", "--public-dir", tree) == 0
    assert json.loads(capsys.readouterr().out)["content_complete"] is False
    assert invoke("readiness", "--public-dir", tree, "--require-complete") == 1
    assert json.loads(capsys.readouterr().out)["snapshot_integrity"] == "verified"
    complete = copy.deepcopy(inputs)
    complete[1]["tables"]["sessions"]["rows"][0]["values"]["c-title"]["value"] = "Published"
    bundle, ledger = project_snapshot(complete[1], complete[0]["event"], complete[0]["resources"])
    ready = tmp_path / "ready"
    stage((bundle, complete[1], ledger), ready)
    assert bundle["presentations"][0]["pictures"] == []
    assert invoke("readiness", "--public-dir", ready, "--require-complete") == 0
    assert json.loads(capsys.readouterr().out)["content_complete"] is True


def test_private_report_refuses_public_paths_and_collision(inputs, tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    stage(inputs, old)
    stage(inputs, new)
    public = tmp_path / "public"
    output = tmp_path / "private" / "review.json"

    def run(destination):
        return invoke(
            "review-update",
            "--previous-public-dir",
            old,
            "--candidate-public-dir",
            new,
            "--output",
            destination,
            "--public-root",
            public,
        )

    assert run(public / "report.json") == 1
    assert not (public / "report.json").exists()
    assert run(old / "report.json") == 1
    assert run(new / "report.json") == 1
    assert run(output) == 0
    original = output.read_bytes()
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
    assert json.loads(original)["snapshot_integrity"] == "both_verified"
    assert run(output) == 1
    assert output.read_bytes() == original
    link = tmp_path / "alias.json"
    link.symlink_to(output)
    assert run(link) == 1
    assert output.read_bytes() == original


def test_event_resources_and_participant_field_changes(inputs, tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    stage(inputs, old)
    bundle, snapshot, _ = copy.deepcopy(inputs)
    bundle["event"]["title"] = "Updated event"
    bundle["resources"][0]["description"] = "Updated description"
    snapshot["tables"]["participants"]["rows"][0]["values"]["c-background"]["value"] = (
        "New background"
    )
    changed, ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    stage((changed, snapshot, ledger), new)
    report = review_update(old, new)
    assert report["event_changed_fields"] == ["title"]
    assert report["records"]["resources"]["changed"][0]["fields"] == ["description"]
    assert report["records"]["participants"]["changed"][0]["fields"] == ["background"]
    assert report["participant_removals_require_review"] is False
    assert report["warnings"] == []


def test_empty_program_is_not_content_complete(inputs, tmp_path, capsys):
    bundle, snapshot, _ = copy.deepcopy(inputs)
    for name in ("presentations", "sessions", "participants"):
        snapshot["tables"][name]["rows"] = []
        snapshot["tables"][name]["totalRows"] = 0
    projected, ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    tree = tmp_path / "empty"
    stage((projected, snapshot, ledger), tree)
    report = readiness(tree)
    assert report["snapshot_integrity"] == "verified"
    assert report["content_complete"] is False
    assert report["warnings"] == ["No presentations have been published."]
    assert invoke("readiness", "--public-dir", tree, "--require-complete") == 1
    assert json.loads(capsys.readouterr().out)["content_complete"] is False
