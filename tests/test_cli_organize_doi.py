"""Drive the real book CLI's DOI and paired-artwork publication boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from symposium.organizing.models import canonical_bytes
from tests.test_cli_organize import invoke
from tests.test_organizing_artifacts import bundle

SYNTHETIC_DOI = "10.1000/synthetic-symposium-2026"


@pytest.fixture
def cli_artwork(tmp_path: Path) -> tuple[Path, Path]:
    cover, spread = tmp_path / "cover.png", tmp_path / "spread.png"
    Image.new("RGB", (300, 100), "#126478").save(cover)
    Image.new("RGB", (100, 160), "#82b9a3").save(spread)
    return cover, spread


def test_book_cli_when_doi_and_artwork_supplied_binds_cover_and_template_config(
    tmp_path: Path, cli_artwork: tuple[Path, Path]
) -> None:
    # Given a public source and a synthetic reserved DOI used only by this test.
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle()))
    workspace = tmp_path / "book"
    # When the real CLI stages the paired-artwork book with its explicit identifier.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        workspace,
        "--public-root",
        tmp_path / "public",
        "--cover-image",
        cli_artwork[0],
        "--frontispiece-image",
        cli_artwork[1],
        "--doi",
        SYNTHETIC_DOI,
    )
    # Then native Template configuration, cover and manifest carry the same exact identifier.
    assert result == 0
    project = workspace / "projects/symposium_2026"
    config = json.loads((project / "manuscript/config.yaml").read_text())
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert config["publication"]["doi"] == manifest["design"]["doi"] == SYNTHETIC_DOI
    assert manifest["design"]["doi_url"] == "https://doi.org/" + SYNTHETIC_DOI
    assert "DOI: " + SYNTHETIC_DOI in (project / "frontmatter.tex").read_text()


@pytest.mark.parametrize("with_cover", (False, True))
def test_book_cli_when_doi_lacks_paired_artwork_refuses_before_output(
    tmp_path: Path, cli_artwork: tuple[Path, Path], with_cover: bool
) -> None:
    # Given an identifier but zero or only one of the two required artwork inputs.
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle()))
    workspace = tmp_path / "rejected"
    flags = ("--cover-image", cli_artwork[0]) if with_cover else ()
    # When the request crosses the public CLI boundary.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        workspace,
        "--public-root",
        tmp_path / "public",
        "--doi",
        SYNTHETIC_DOI,
        *flags,
    )
    # Then no partial project is staged.
    assert result == 1 and not workspace.exists()


def test_book_cli_when_doi_syntax_invalid_refuses_before_output(
    tmp_path: Path, cli_artwork: tuple[Path, Path]
) -> None:
    # Given both artworks but a URL instead of a bare DOI.
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle()))
    workspace = tmp_path / "rejected"
    # When the real CLI requests staging.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        workspace,
        "--public-root",
        tmp_path / "public",
        "--cover-image",
        cli_artwork[0],
        "--frontispiece-image",
        cli_artwork[1],
        "--doi",
        "https://doi.org/" + SYNTHETIC_DOI,
    )
    # Then the identifier is rejected without producing output.
    assert result == 1 and not workspace.exists()


def test_book_cli_when_doi_omitted_preserves_config_without_identifier(
    tmp_path: Path, cli_artwork: tuple[Path, Path]
) -> None:
    # Given the previously supported paired-artwork CLI call.
    source = tmp_path / "program.json"
    source.write_bytes(canonical_bytes(bundle()))
    workspace = tmp_path / "book"
    # When no DOI option is provided.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        workspace,
        "--public-root",
        tmp_path / "public",
        "--cover-image",
        cli_artwork[0],
        "--frontispiece-image",
        cli_artwork[1],
    )
    # Then no synthetic or default DOI is introduced into Template metadata.
    assert result == 0
    project = workspace / "projects/symposium_2026"
    config = json.loads((project / "manuscript/config.yaml").read_text())
    assert "doi" not in config["publication"]
    assert "DOI:" not in (project / "frontmatter.tex").read_text()
