"""Individual cover credits and organizer-reviewed presenter identifiers."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from PIL import Image

from symposium.organizing.artifacts import stage_abstract_book
from symposium.organizing.book_design import (
    BookDesign,
    BookDesignError,
    CreditIdentifier,
    credit_names,
    load_credit_identifiers,
)
from symposium.organizing.models import canonical_bytes
from tests.test_cli_organize import invoke
from tests.test_organizing_artifacts import bundle

# ORCID's published example iDs; both carry valid check characters.
EXAMPLE_ORCID = "0000-0002-1825-0097"
SECOND_ORCID = "0000-0001-5109-3700"


@pytest.fixture
def artwork(tmp_path: Path) -> tuple[Path, Path]:
    cover, spread = tmp_path / "cover.png", tmp_path / "spread.png"
    Image.new("RGB", (300, 100), "#126478").save(cover)
    Image.new("RGB", (100, 160), "#82b9a3").save(spread)
    return cover, spread


def _identifiers(tmp_path: Path, people: list[dict[str, object]]) -> Path:
    path = tmp_path / "identifiers.json"
    path.write_text(json.dumps({"schema_version": 1, "people": people}), encoding="utf-8")
    return path


def _person(name: str, orcid: str | None = EXAMPLE_ORCID, affiliation: str | None = "Example Lab"):
    return {"name": name, "orcid": orcid, "affiliation": affiliation, "basis": "presenter email"}


def _bundle_with(labels: tuple[str, ...]):
    data = bundle()
    talks = []
    for index, label in enumerate(labels):
        talk = copy.deepcopy(data["presentations"][0])
        talk.update(id=f"talk-{index}", presenter=label, title=f"Synthetic contribution {index}")
        talks.append(talk)
    data["presentations"] = talks
    return data


@pytest.mark.parametrize(
    ("label", "names"),
    (
        ("Ada Example", ("Ada Example",)),
        ("Ada Example & Bob Sample", ("Ada Example", "Bob Sample")),
        ("Ada Example, Bob Sample", ("Ada Example", "Bob Sample")),
        ("Ada Example, Bob Sample & Chen Exemplar", ("Ada Example", "Bob Sample", "Chen Exemplar")),
        ("Ada Example &", ("Ada Example &",)),
        (", Ada Example", (", Ada Example",)),
    ),
)
def test_credit_names_when_label_lists_people_splits_without_rewriting(
    label: str, names: tuple[str, ...]
) -> None:
    # Given a published label; when it is split; then only commas and ampersands separate
    # people, spellings are kept, and a split that would leave an empty part keeps the label.
    assert credit_names(label) == names


def test_identifiers_when_reviewed_reach_template_authors_and_manifest(
    tmp_path: Path, artwork: tuple[Path, Path]
) -> None:
    # Given a composite label whose two people supplied ORCIDs and an affiliation.
    data = _bundle_with(("Ada Example & Bob Sample", "Chen Exemplar"))
    identifiers = load_credit_identifiers(
        _identifiers(
            tmp_path,
            [_person("Bob Sample", SECOND_ORCID, None), _person("Ada Example")],
        )
    )
    design = BookDesign(*artwork, "Synthetic Program", credit_identifiers=identifiers)
    # When the designed book is staged.
    project = stage_abstract_book(data, tmp_path / "book", design=design)
    # Then each person is a separate author and only reviewed values are attached.
    config = json.loads((project / "manuscript/config.yaml").read_text())
    assert config["authors"] == [
        {"name": "Active Inference Institute"},
        {"name": "Ada Example", "orcid": EXAMPLE_ORCID, "affiliation": "Example Lab"},
        {"name": "Bob Sample", "orcid": SECOND_ORCID},
        {"name": "Chen Exemplar"},
    ]
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert [entry["name"] for entry in manifest["design"]["author_identifiers"]] == [
        "Ada Example",
        "Bob Sample",
    ]
    assert {entry["basis"] for entry in manifest["design"]["author_identifiers"]} == {
        "presenter email"
    }
    # And the published entry keeps its whole presenter label.
    entries = "".join(path.read_text() for path in (project / "manuscript").glob("*.md"))
    assert "Presenter: Ada Example &#38; Bob Sample" in entries


def test_identifiers_when_name_is_not_an_individual_credit_refuse_before_output(
    tmp_path: Path, artwork: tuple[Path, Path]
) -> None:
    # Given an identifier for the whole composite label instead of a person on the cover.
    data = _bundle_with(("Ada Example & Bob Sample",))
    design = BookDesign(
        *artwork,
        credit_identifiers=(
            CreditIdentifier("Ada Example & Bob Sample", EXAMPLE_ORCID, None, "x"),
        ),
    )
    workspace = tmp_path / "book"
    # When staging is requested; then it refuses and creates nothing.
    with pytest.raises(BookDesignError, match="not individual cover credits"):
        stage_abstract_book(data, workspace, design=design)
    assert not workspace.exists()


@pytest.mark.parametrize(
    "people",
    (
        [_person("Ada Example", "0000-0002-1825-0098")],
        [_person("Ada Example", "https://orcid.org/" + EXAMPLE_ORCID)],
        [_person("Ada Example", None, None)],
        [_person("Ada Example"), _person("Ada Example", SECOND_ORCID)],
        [_person(" Ada Example")],
        [{**_person("Ada Example"), "email": "ada@example.org"}],
        [],
    ),
)
def test_identifier_file_when_invalid_is_refused(
    tmp_path: Path, people: list[dict[str, object]]
) -> None:
    # Given a bad check character, URL form, empty values, duplicates, padding, an extra
    # contact field or an empty list; when loaded; then admission fails.
    with pytest.raises(BookDesignError):
        load_credit_identifiers(_identifiers(tmp_path, people))


def test_identifier_file_when_relative_or_not_json_is_refused(tmp_path: Path) -> None:
    # Given a relative path and a non-JSON file; when loaded; then both are refused.
    with pytest.raises(BookDesignError, match="absolute"):
        load_credit_identifiers(Path("identifiers.json"))
    path = tmp_path / "identifiers.json"
    path.write_bytes(b"\xff not json")
    with pytest.raises(BookDesignError, match="UTF-8 JSON"):
        load_credit_identifiers(path)


def test_book_cli_when_identifiers_supplied_binds_them_to_authors(
    tmp_path: Path, artwork: tuple[Path, Path]
) -> None:
    # Given a public program with a composite credit and a private reviewed identifier file.
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(_bundle_with(("Ada Example & Bob Sample",))))
    people = _identifiers(tmp_path, [_person("Bob Sample")])
    workspace = tmp_path / "book"
    # When the real CLI stages the designed book.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        workspace,
        "--public-root",
        tmp_path / "public",
        "--cover-image",
        artwork[0],
        "--frontispiece-image",
        artwork[1],
        "--credit-identifiers",
        people,
    )
    # Then the person's ORCID reaches the Template author list.
    assert result == 0
    config = json.loads((workspace / "projects/symposium_2026/manuscript/config.yaml").read_text())
    assert {"name": "Bob Sample", "orcid": EXAMPLE_ORCID, "affiliation": "Example Lab"} in config[
        "authors"
    ]


def test_book_cli_when_identifiers_lack_artwork_refuses_before_output(tmp_path: Path) -> None:
    # Given identifiers without the designed cover they belong to.
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle()))
    workspace = tmp_path / "rejected"
    # When the CLI is invoked; then it refuses and stages nothing.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        workspace,
        "--public-root",
        tmp_path / "public",
        "--credit-identifiers",
        _identifiers(tmp_path, [_person("Synthetic Presenter")]),
    )
    assert result == 1 and not workspace.exists()
