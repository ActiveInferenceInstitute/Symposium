"""Real PNG and OOXML checks for the optional, exact-credit abstract-book design."""

from __future__ import annotations

import copy
import hashlib
import html
import io
import json
import os
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from PIL import Image

from symposium.organizing.artifacts import stage_abstract_book
from symposium.organizing.book_design import BookDesign, BookDesignError, prepare_book_design
from symposium.organizing.book_design_docx import W, prepend_book_design
from symposium.organizing.models import PublicBundle, canonical_bytes, validate_bundle
from tests.test_cli_organize import invoke
from tests.test_organizing_artifacts import bundle


@pytest.fixture
def artwork(tmp_path: Path) -> BookDesign:
    cover = tmp_path / "cover.png"
    spread = tmp_path / "spread.png"
    Image.new("RGB", (300, 100), "#126478").save(cover)
    Image.new("RGB", (100, 160), "#82b9a3").save(spread)
    return BookDesign(cover, spread, "2026 Synthetic Symposium — Presenter Program")


def test_cover_credits_when_exact_labels_repeat_preserve_composites(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a published composite label, an independent individual, and an exact repeat.
    data = bundle()
    labels = ("Ada & Bob", "Ada", "Ada & Bob", "Áda", "ada")
    talks = []
    for index, label in enumerate(labels):
        talk = copy.deepcopy(data["presentations"][0])
        talk.update(id=f"talk-{index}", presenter=label, title=f"Synthetic contribution {index}")
        talks.append(talk)
    data["presentations"] = talks
    # When the optional book is staged.
    project = stage_abstract_book(data, tmp_path / "book", design=artwork)
    # Then source display labels are exact, deduplicated only by equality, and institutional-first.
    config = json.loads((project / "manuscript/config.yaml").read_text())
    credits = [author["name"] for author in config["authors"]]
    assert credits == ["Active Inference Institute", "Ada", "ada", "Ada & Bob", "Áda"]
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert manifest["design"]["authors"] == credits
    assert [name for column in manifest["design"]["credit_columns"] for name in column] == credits[
        1:
    ]


def test_designed_book_when_staged_preserves_abstracts_and_bound_artwork(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given literal non-ASCII/markup content and pending abstracts.
    data = bundle()
    data["presentations"][0]["abstract"] += " Hawaiʻi ~ ·"
    data["presentations"][0]["abstract_sha256"] = hashlib.sha256(
        data["presentations"][0]["abstract"].encode()
    ).hexdigest()
    for index in range(3):
        talk = copy.deepcopy(data["presentations"][0])
        talk.update(
            id=f"pending-{index}",
            title=f"Pending contribution {index}",
            abstract="",
            abstract_sha256=hashlib.sha256(b"").hexdigest(),
        )
        data["presentations"].append(talk)
    # When the designed manuscript is staged.
    project = stage_abstract_book(data, tmp_path / "book", design=artwork)
    # Then all submitted prose and missing-abstract records survive without image substitution.
    source = (project / "manuscript/01_abstract_book.md").read_text()
    assert data["presentations"][0]["abstract"] in html.unescape(source)
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert manifest["talk_count"] == 4
    assert (
        sum(
            talk["abstract_sha256"] == hashlib.sha256(b"").hexdigest() for talk in manifest["talks"]
        )
        == 3
    )
    for key, original in (
        ("cover", artwork.cover_image),
        ("frontispiece", artwork.frontispiece_image),
    ):
        receipt = manifest["design"][key]
        assert (project / receipt["path"]).read_bytes() == original.read_bytes()
        assert hashlib.sha256(original.read_bytes()).hexdigest() == receipt["sha256"]


def test_designed_book_when_output_exists_refuses_without_replacement(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given an existing designed project.
    project = stage_abstract_book(bundle(), tmp_path / "book", design=artwork)
    original = {
        str(path.relative_to(project)): path.read_bytes()
        for path in project.rglob("*")
        if path.is_file()
    }
    # When a second stage targets its occupied project.
    with pytest.raises(FileExistsError):
        stage_abstract_book(bundle(), tmp_path / "book", design=artwork)
    # Then every existing byte is preserved.
    assert {
        str(path.relative_to(project)): path.read_bytes()
        for path in project.rglob("*")
        if path.is_file()
    } == original


def test_design_when_asset_path_is_relative_refuses_before_output(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a relative artwork path.
    design = BookDesign(Path("cover.png"), artwork.frontispiece_image)
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(bundle(), tmp_path / "rejected", design=design)
    # Then no output namespace is created.
    assert not (tmp_path / "rejected").exists()


def test_design_when_asset_path_traverses_refuses_before_output(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given an absolute path with traversal components, even if it resolves to real artwork.
    design = BookDesign(tmp_path / "unused/../cover.png", artwork.frontispiece_image)
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(bundle(), tmp_path / "rejected", design=design)
    # Then the traversal path grants no output creation.
    assert not (tmp_path / "rejected").exists()


def test_design_when_asset_is_symlink_refuses_before_output(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given an artwork symlink.
    link = tmp_path / "linked.png"
    link.symlink_to(artwork.cover_image)
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(
            bundle(), tmp_path / "rejected", design=BookDesign(link, artwork.frontispiece_image)
        )
    # Then neither the linked source nor an output is modified.
    assert link.is_symlink() and not (tmp_path / "rejected").exists()


def test_design_when_parent_is_symlink_refuses_before_output(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a directory alias hiding an otherwise regular PNG.
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(
            bundle(),
            tmp_path / "rejected",
            design=BookDesign(alias / "cover.png", artwork.frontispiece_image),
        )
    # Then the alias is not followed.
    assert not (tmp_path / "rejected").exists()


def test_design_when_credits_exceed_cover_refuses_without_omission(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given more exact presenter labels than fit at nine points on one cover.
    data = bundle()
    data["presentations"] = [
        dict(data["presentations"][0], id=f"talk-{i}", presenter=f"Synthetic presenter {i}")
        for i in range(150)
    ]
    # When staging is requested.
    with pytest.raises(BookDesignError, match="budget"):
        stage_abstract_book(data, tmp_path / "rejected", design=artwork)
    # Then no author is silently omitted or reduced below the declared readable size.
    assert not (tmp_path / "rejected").exists()


def _native_docx(path: Path, data: PublicBundle) -> None:
    body = ET.Element(W + "body")
    for index, text in enumerate(
        ("About this program", *[talk["title"] for talk in data["presentations"]])
    ):
        paragraph = ET.SubElement(body, W + "p")
        ET.SubElement(
            paragraph, W + "bookmarkStart", {W + "id": str(index), W + "name": f"heading-{index}"}
        )
        ET.SubElement(ET.SubElement(paragraph, W + "r"), W + "t").text = text
        ET.SubElement(paragraph, W + "bookmarkEnd", {W + "id": str(index)})
    ET.SubElement(ET.SubElement(body, W + "p"), W + "r").append(ET.Element(W + "t"))
    body[-1][0][0].text = data["presentations"][0]["abstract"]
    document = ET.Element(W + "document")
    document.append(body)
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("word/document.xml", ET.tostring(document))
        package.writestr(
            "word/_rels/document.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
        )
        package.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        package.writestr(
            "docProps/core.xml",
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dcterms:created xsi:type="dcterms:W3CDTF">2026-11-05T15:32:40Z</dcterms:created>'
            '<dcterms:modified xsi:type="dcterms:W3CDTF">2026-11-05T15:32:40Z</dcterms:modified>'
            "</cp:coreProperties>",
        )
        package.writestr("sentinel.bin", b"Native unrelated member")


def test_docx_design_when_prepended_preserves_body_and_declares_physical_breaks(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a native package with actual heading bookmarks and literal abstract XML.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(data["presentations"], artwork, "Unused fallback")
    path = tmp_path / "native.docx"
    _native_docx(path, data)
    # When front matter is prepended.
    prepend_book_design(path, prepared, data["presentations"])
    # Then the art starts a new physical page, contents follows it, and native prose remains exact.
    with zipfile.ZipFile(path) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        paragraphs = document.findall(".//" + W + "p")
        texts = [
            "".join(node.text or "" for node in paragraph.iter(W + "t")) for paragraph in paragraphs
        ]
        assert texts.index("Active Inference Institute") < texts.index("Synthetic Presenter")
        assert data["presentations"][0]["abstract"] in texts
        body = document.find(W + "body")
        breaks = [
            node for node in body if node.find(W + "pPr/" + W + "pageBreakBefore") is not None
        ]
        assert len(breaks) == 3
        assert (
            breaks[0].find(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"
            )
            is not None
        )
        assert "".join(node.text or "" for node in breaks[1].iter(W + "t")) == "Contents"
        assert "".join(node.text or "" for node in breaks[2].iter(W + "t")) == "About this program"
        links = document.findall(".//" + W + "hyperlink")
        assert [link.get(W + "anchor") for link in links] == ["heading-1"]
        assert package.read("sentinel.bin") == b"Native unrelated member"
        assert package.read("word/media/symposium-cover.png") == artwork.cover_image.read_bytes()


def test_docx_design_when_reapplied_refuses_without_replacing(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given an already designed native package.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(data["presentations"], artwork, "Unused fallback")
    path = tmp_path / "native.docx"
    _native_docx(path, data)
    prepend_book_design(path, prepared, data["presentations"])
    original = path.read_bytes()
    # When the same mutation is attempted again.
    with pytest.raises(BookDesignError):
        prepend_book_design(path, prepared, data["presentations"])
    # Then the package remains the prior complete version.
    assert path.read_bytes() == original


@pytest.mark.parametrize(
    ("part", "root_name", "namespace", "child_name"),
    (
        (
            "[Content_Types].xml",
            "Types",
            "http://schemas.openxmlformats.org/package/2006/content-types",
            "Default",
        ),
        (
            "word/_rels/document.xml.rels",
            "Relationships",
            "http://schemas.openxmlformats.org/package/2006/relationships",
            "Relationship",
        ),
    ),
)
def test_docx_design_when_package_parts_written_preserves_native_default_namespaces(
    tmp_path: Path,
    artwork: BookDesign,
    part: str,
    root_name: str,
    namespace: str,
    child_name: str,
) -> None:
    # Given native default-namespace OPC parts, as emitted by Template's DOCX writer.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(data["presentations"], artwork, "Unused fallback")
    path = tmp_path / "native.docx"
    _native_docx(path, data)
    # When designed image relationships and their content type are added.
    prepend_book_design(path, prepared, data["presentations"])
    with zipfile.ZipFile(path) as package:
        raw = package.read(part)
    # Then both raw roots retain default namespaces accepted by LibreOffice's package reader.
    root_xml = raw.split(b"?>", 1)[-1].lstrip()
    assert root_xml.startswith(f'<{root_name} xmlns="{namespace}"'.encode())
    root = ET.fromstring(raw)
    assert root.tag == f"{{{namespace}}}{root_name}"
    assert all(node.tag == f"{{{namespace}}}{child_name}" for node in root)
    assert len(root) > 0


def test_docx_design_when_core_dates_use_qnames_preserves_their_namespace_bindings(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a native core-properties part with real typed creation/modification dates.
    data = validate_bundle(bundle())
    prepared = prepare_book_design(data["presentations"], artwork, "Unused fallback")
    path = tmp_path / "native.docx"
    _native_docx(path, data)
    # When designed metadata is written into the native package.
    prepend_book_design(path, prepared, data["presentations"])
    # Then retained QName-valued date types resolve to the original namespace and values.
    with zipfile.ZipFile(path) as package:
        raw = package.read("docProps/core.xml")
    namespaces = dict(value for _, value in ET.iterparse(io.BytesIO(raw), events=("start-ns",)))
    core = ET.fromstring(raw)
    for name in ("created", "modified"):
        date = core.find("{http://purl.org/dc/terms/}" + name)
        assert date is not None and date.text == "2026-11-05T15:32:40Z"
        value = date.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        assert value is not None
        prefix, local = value.split(":", 1)
        assert namespaces[prefix] == "http://purl.org/dc/terms/" and local == "W3CDTF"


def test_design_when_png_bytes_are_invalid_refuses_before_output(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a regular file carrying invalid PNG content.
    invalid = tmp_path / "invalid.png"
    invalid.write_bytes(b"This is not PNG artwork")
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(
            bundle(), tmp_path / "rejected", design=BookDesign(invalid, artwork.frontispiece_image)
        )
    # Then no partial manuscript has been created.
    assert not (tmp_path / "rejected").exists()


def test_design_when_workspace_has_tex_comment_delimiter_refuses(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a workspace path that would comment out a staged TeX image argument.
    workspace = tmp_path / "unsafe%workspace"
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(bundle(), workspace, design=artwork)
    # Then no broken TeX document or partial project is created.
    assert not workspace.exists()


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="Requires a real filesystem FIFO")
def test_design_when_artwork_is_fifo_refuses_before_open(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a real FIFO with no writer, which must never be opened in blocking mode.
    fifo = tmp_path / "artwork-fifo"
    os.mkfifo(fifo)
    # When staging is requested.
    with pytest.raises(BookDesignError):
        stage_abstract_book(
            bundle(), tmp_path / "rejected", design=BookDesign(fifo, artwork.frontispiece_image)
        )
    # Then the nonregular input is refused without creating a project.
    assert not (tmp_path / "rejected").exists()


def test_cli_book_when_one_artwork_flag_missing_refuses_before_output(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given a valid source bundle but an incomplete design request.
    source = tmp_path / "bundle.json"
    source.write_bytes(canonical_bytes(bundle()))
    # When the real CLI dispatcher receives only a cover.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        tmp_path / "rejected",
        "--public-root",
        tmp_path / "public",
        "--cover-image",
        artwork.cover_image,
    )
    # Then it refuses without creating a staged project.
    assert result == 1 and not (tmp_path / "rejected").exists()


def test_cli_book_when_artwork_paired_stages_designed_title(
    tmp_path: Path, artwork: BookDesign
) -> None:
    # Given valid paired PNGs and a distinct explicit cover title.
    source = tmp_path / "bundle.json"
    source.write_bytes(canonical_bytes(bundle()))
    # When the real CLI dispatcher stages the optional design.
    result = invoke(
        "book",
        "--bundle",
        source,
        "--workspace",
        tmp_path / "book",
        "--public-root",
        tmp_path / "public",
        "--cover-image",
        artwork.cover_image,
        "--frontispiece-image",
        artwork.frontispiece_image,
        "--book-title",
        artwork.title,
    )
    # Then the selected title and institutional-first source credits reach the artifact contract.
    config = json.loads(
        (tmp_path / "book/projects/symposium_2026/manuscript/config.yaml").read_text()
    )
    assert result == 0 and config["paper"]["title"] == artwork.title
    assert [author["name"] for author in config["authors"]] == [
        "Active Inference Institute",
        "Synthetic Presenter",
    ]
