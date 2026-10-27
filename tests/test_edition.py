"""Offline edition scenarios using real files and real CLI subprocesses."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from symposium.core.edition import (
    Edition,
    EditionError,
    _publish_directory,
    init_edition,
    validate_edition,
)


def cli(*args, env=None):
    return subprocess.run(
        [sys.executable, "-c", "from symposium.cli import main; main()", *map(str, args)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_default_edition_paths():
    edition = Edition()
    assert edition.input_dir == Path("data/inputs/aif_2026")
    assert edition.participants_csv == edition.input_dir / "Public_Participant_Information.csv"
    assert edition.presenters_dir == edition.input_dir / "presenters"
    assert edition.output_dir == Path("outputs/2026_symposium")


@pytest.mark.parametrize("year", [True, False, "2026", 2026.0, 1999, 2101])
def test_invalid_year_rejected(year):
    with pytest.raises(EditionError, match="year"):
        Edition(year=year)


def test_empty_scaffold_cli_and_safe_rerun(tmp_path):
    args = ["--year", "2026", "--data-dir", tmp_path / "data", "--output-dir", tmp_path / "outputs"]
    first = cli("edition", "init", *args)
    assert first.returncode == 0, first.stderr + first.stdout
    edition = Edition(data_dir=tmp_path / "data", outputs_dir=tmp_path / "outputs")
    before = {
        p.relative_to(edition.input_dir): p.read_bytes()
        for p in edition.input_dir.rglob("*")
        if p.is_file()
    }
    second = cli("edition", "init", *args)
    assert second.returncode == 0
    assert "no files changed" in second.stdout
    assert before == {
        p.relative_to(edition.input_dir): p.read_bytes()
        for p in edition.input_dir.rglob("*")
        if p.is_file()
    }
    valid = cli("edition", "validate", *args)
    assert valid.returncode == 0
    assert "0 public participants, 0 complete presenters" in valid.stdout
    assert "Awaiting" in valid.stdout
    strict = cli("edition", "validate", *args, "--require-data")
    assert strict.returncode == 1
    assert "--require-data needs" in strict.stdout
    assert list(edition.presenters_dir.iterdir()) == [edition.presenters_dir / "README.md"]


def test_conflict_is_rejected_before_partial_writes(tmp_path):
    edition = Edition(data_dir=tmp_path)
    edition.input_dir.mkdir(parents=True)
    existing = edition.input_dir / "keep.txt"
    existing.write_bytes(b"preserve")
    with pytest.raises(EditionError, match="conflicts"):
        init_edition(edition)
    assert existing.read_bytes() == b"preserve"
    assert list(edition.input_dir.iterdir()) == [existing]


def test_atomic_publish_never_replaces_empty_directory(tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "keep").write_text("source")
    with pytest.raises(OSError):
        _publish_directory(source, destination)
    assert (source / "keep").read_text() == "source"
    assert list(destination.iterdir()) == []


def populated_edition(tmp_path):
    edition = Edition(data_dir=tmp_path)
    init_edition(edition)
    edition.participants_csv.write_text("name,share_publicly\nTest Participant,yes\n")
    folder = edition.presenters_dir / "Test Presenter"
    folder.mkdir()
    (folder / "works-test.csv").write_text(
        "title,publication_year,cited_by_count\nTest work,2025,0\n"
    )
    (folder / "openalex-group-by-test.csv").write_text("topic,count\nTest topic,1\n")
    return edition, folder


def test_complete_inputs_pass_readiness(tmp_path):
    edition, _ = populated_edition(tmp_path)
    report = validate_edition(edition, require_data=True)
    assert report.valid
    assert report.participants == report.presenters == 1


def test_historical_openalex_topic_schema(tmp_path):
    edition, folder = populated_edition(tmp_path)
    (folder / "openalex-group-by-test.csv").write_text(
        "Primary Topic Id,,\nname,count,\nTest topic,4,\n"
    )
    assert validate_edition(edition, require_data=True).valid


@pytest.mark.parametrize(
    "filename,contents",
    [
        ("works-test.csv", "wrong,columns\nvalue,value\n"),
        ("works-test.csv", "title,publication_year,cited_by_count\nTest,2025,-1\n"),
        ("works-test.csv", "title,publication_year,cited_by_count\nTest,2025,1,extra\n"),
        ("works-test.csv", "title,publication_year,cited_by_count\n"),
        ("openalex-group-by-test.csv", "topic,count\nTest,invalid\n"),
        ("openalex-group-by-test.csv", "topic,count\n,1\n"),
        ("openalex-group-by-test.csv", "wrong,count\nTest,1\n"),
    ],
)
def test_bad_presenter_data_fails_even_without_require_data(tmp_path, filename, contents):
    edition, folder = populated_edition(tmp_path)
    (folder / filename).write_text(contents)
    report = validate_edition(edition)
    assert not report.valid
    assert report.presenters == 0


def test_incomplete_presenter_folder_is_error(tmp_path):
    edition = Edition(data_dir=tmp_path)
    init_edition(edition)
    (edition.presenters_dir / "Test Presenter").mkdir()
    assert "Incomplete presenter" in validate_edition(edition).errors[0]


@pytest.mark.parametrize("args", [["analyze"], ["generate"], ["visualize"], ["edition"]])
def test_missing_subcommand_is_argparse_error(args):
    result = cli(*args)
    assert result.returncode == 2
    assert "required" in result.stderr
    assert "Traceback" not in result.stderr


def test_version_is_available_without_data():
    from symposium import __version__

    result = cli("--version")
    assert result.returncode == 0
    assert __version__ in result.stdout


@pytest.mark.parametrize("existing", [False, True])
def test_output_conflict_prevents_any_initialization(tmp_path, existing):
    edition = Edition(data_dir=tmp_path / "data", outputs_dir=tmp_path / "outputs")
    if existing:
        init_edition(edition)
    edition.output_dir.parent.mkdir(parents=True)
    edition.output_dir.write_bytes(b"keep")
    with pytest.raises(EditionError, match="output path conflicts"):
        init_edition(edition)
    assert edition.output_dir.read_bytes() == b"keep"
    assert edition.input_dir.exists() == existing


def test_symlink_input_parent_is_rejected(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    link = tmp_path / "link"
    link.symlink_to(original, target_is_directory=True)
    with pytest.raises(EditionError, match="parent"):
        init_edition(Edition(data_dir=link))
    assert list(original.iterdir()) == []


def test_invalid_folder_and_collision_are_errors(tmp_path):
    edition, folder = populated_edition(tmp_path)
    (edition.presenters_dir / "invalid!").mkdir()
    (edition.presenters_dir / "Test_Presenter").mkdir()
    report = validate_edition(edition)
    assert any("invalid name" in error for error in report.errors)
    assert any("collide" in error for error in report.errors)


def test_cli_config_environment_and_explicit_precedence(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "edition": {"year": 2028},
                "paths": {
                    "data_dir": str(tmp_path / "configured"),
                    "outputs_dir": str(tmp_path / "out"),
                },
            }
        )
    )
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"SYMPOSIUM_YEAR", "SYMPOSIUM_DATA_DIR", "SYMPOSIUM_OUTPUTS_DIR"}
    }
    result = cli("--config", config, "edition", "init", env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "configured/inputs/aif_2028/Public_Participant_Information.csv").is_file()
    env.update(
        SYMPOSIUM_YEAR="2029",
        SYMPOSIUM_DATA_DIR=str(tmp_path / "environment"),
        SYMPOSIUM_OUTPUTS_DIR=str(tmp_path / "env-out"),
    )
    result = cli("--config", config, "edition", "init", env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "environment/inputs/aif_2029/Public_Participant_Information.csv").is_file()
    assert "env-out/2029_symposium" in result.stdout
    result = cli(
        "--config",
        config,
        "edition",
        "init",
        "--year",
        "2030",
        "--data-dir",
        tmp_path / "explicit",
        "--output-dir",
        tmp_path / "explicit-out",
        env=env,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "explicit/inputs/aif_2030/Public_Participant_Information.csv").is_file()
    assert "explicit-out/2030_symposium" in result.stdout


def test_invalid_environment_year_is_bounded_error():
    env = dict(os.environ, SYMPOSIUM_YEAR="not-a-year")
    result = cli("edition", "validate", env=env)
    assert result.returncode == 1
    assert "SYMPOSIUM_YEAR must be an integer" in result.stdout
    assert "Traceback" not in result.stderr


def test_no_arguments_preserve_help_exit_status():
    result = cli()
    assert result.returncode == 1
    assert "usage:" in result.stdout


def test_output_parent_file_prevents_partial_initialization(tmp_path):
    output_parent = tmp_path / "outputs"
    output_parent.write_bytes(b"preserve")
    edition = Edition(data_dir=tmp_path / "data", outputs_dir=output_parent)
    with pytest.raises(EditionError, match="output parent"):
        init_edition(edition)
    assert not edition.input_dir.exists()
    assert output_parent.read_bytes() == b"preserve"
