"""Real-file tests using only synthetic approved-public fixtures."""

import copy
import hashlib
import html
import json
from pathlib import Path

import pytest

from symposium.organizing.artifacts import (
    ArtifactError,
    render_abstract_book,
    stage_abstract_book,
    write_dossiers,
)
from symposium.organizing.models import content_hash


def bundle():
    abstract = "Literal <script>alert(1)</script> & $x$ \\input{secret}\n# Not a heading\n![not an image](secret)"
    talk = {
        "id": "talk-a",
        "presenter": "Synthetic Presenter",
        "title": "Synthetic title",
        "abstract": abstract,
        "contribution_type": "Talk",
        "source_url": "https://example.org/source",
        "pictures": [],
        "abstract_sha256": hashlib.sha256(abstract.encode()).hexdigest(),
    }
    return {
        "schema_version": 1,
        "event": {
            "id": "symposium-2026",
            "title": "Synthetic Symposium",
            "year": 2026,
            "start_date": "2026-11-04",
            "end_date": "2026-11-06",
            "timezone": "UTC",
            "program_url": "https://example.org/program",
            "participant_registration_url": "https://example.org/participants",
            "presenter_registration_url": "https://example.org/presenters",
            "community_url": "https://example.org/community",
            "donate_url": "https://example.org/donate",
            "livestreams": [],
        },
        "presentations": [talk],
        "participants": [],
        "sessions": [],
        "resources": [],
    }


def test_dossier_literal_and_no_overwrite(tmp_path):
    data = bundle()
    paths = write_dossiers(data, tmp_path / "dossiers")
    assert [p.name for p in paths] == ["talk-a.md"]
    text = paths[0].read_text()
    assert data["presentations"][0]["abstract"] in html.unescape(text)
    assert "<script>" not in text
    assert "\\input" not in text
    assert "![not an image]" not in text
    assert "not a verified identity" in text
    with pytest.raises(FileExistsError):
        write_dossiers(data, tmp_path / "dossiers")
    assert paths[0].read_text() == text


def test_stage_full_abstract_order_hash_and_no_overwrite(tmp_path):
    data = bundle()
    second = copy.deepcopy(data["presentations"][0])
    second.update(id="talk-b", presenter="A Synthetic Presenter", contribution_type="Poster")
    data["presentations"].append(second)
    first_source_sha256 = content_hash(data)
    project = stage_abstract_book(data, tmp_path / "first")
    data["presentations"].reverse()
    other = stage_abstract_book(data, tmp_path / "second")
    for relative in (
        "manuscript/config.yaml",
        "manuscript/01_abstract_book.md",
    ):
        assert (project / relative).read_bytes() == (other / relative).read_bytes()
    first_manifest = json.loads((project / "abstract_manifest.json").read_text())
    second_manifest = json.loads((other / "abstract_manifest.json").read_text())
    assert first_manifest.pop("bundle_sha256") == first_source_sha256
    assert second_manifest.pop("bundle_sha256") == content_hash(data)
    assert first_manifest == second_manifest
    text = (project / "manuscript/01_abstract_book.md").read_text()
    assert text.index("A Synthetic Presenter") < text.index("Presenter: Synthetic Presenter")
    assert html.unescape(text).count(data["presentations"][0]["abstract"]) == 2
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert manifest["talk_count"] == 2
    assert [t["id"] for t in manifest["talks"]] == ["talk-b", "talk-a"]
    config = json.loads((project / "manuscript/config.yaml").read_text())
    assert config["authors"] == []
    assert config["publication"]["transmission_bookends"]["enabled"] is False
    assert config["render"]["formats"]["docx"] is True
    with pytest.raises(FileExistsError):
        stage_abstract_book(data, tmp_path / "first")


@pytest.mark.parametrize("fault", ["missing", "duplicate", "traversal", "hash"])
def test_invalid_bundle_never_creates_outputs(tmp_path, fault):
    data = bundle()
    if fault == "missing":
        del data["presentations"][0]["id"]
    elif fault == "duplicate":
        data["presentations"].append(copy.deepcopy(data["presentations"][0]))
    elif fault == "traversal":
        data["presentations"][0]["id"] = "../outside"
    else:
        data["presentations"][0]["abstract_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        stage_abstract_book(data, tmp_path / "invalid")
    assert not (tmp_path / "invalid").exists()


def test_missing_template_refused_before_staging(tmp_path):
    with pytest.raises(ArtifactError):
        render_abstract_book(bundle(), tmp_path / "render", tmp_path / "absent")
    assert not (tmp_path / "render").exists()


def test_invalid_timeout_refused(tmp_path):
    with pytest.raises(ArtifactError, match="positive"):
        render_abstract_book(bundle(), tmp_path / "render", Path("absent"), timeout=0)
    assert not (tmp_path / "render").exists()


def test_native_docx_geometry_preserves_text_and_members(tmp_path):
    import zipfile
    from xml.etree import ElementTree as ET

    from symposium.organizing.artifacts import _set_docx_page_geometry

    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    raw = f'<w:document xmlns:w="{namespace}"><w:body><w:p><w:r><w:t>Literal ~ and · prose</w:t></w:r></w:p><w:sectPr><w:pgSz w:w="12240" w:h="15840"/></w:sectPr></w:body></w:document>'.encode()
    path = tmp_path / "real.docx"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", raw)
        archive.writestr("docProps/core.xml", b"<core>Preserved metadata</core>")
    _set_docx_page_geometry(path)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert archive.read("docProps/core.xml") == b"<core>Preserved metadata</core>"
        document = ET.fromstring(archive.read("word/document.xml"))
        assert document.find(f".//{{{namespace}}}t").text == "Literal ~ and · prose"
        assert len(document.findall(f".//{{{namespace}}}pgSz")) == 1
        assert document.find(f".//{{{namespace}}}pgSz").get(f"{{{namespace}}}w") == "11906"
        assert document.find(f".//{{{namespace}}}pgMar").get(f"{{{namespace}}}left") == "1020"
    assert not path.with_suffix(".a4.docx").exists()


def test_book_has_one_cross_format_page_break_per_contribution(tmp_path):
    data = bundle()
    data["presentations"][0]["abstract"] += " ~ and · literal text"
    data["presentations"][0]["abstract_sha256"] = hashlib.sha256(
        data["presentations"][0]["abstract"].encode()
    ).hexdigest()
    project = stage_abstract_book(data, tmp_path / "book")
    source = (project / "manuscript/01_abstract_book.md").read_text()
    assert source.count("\\newpage") == 1
    assert "{=openxml}" not in source
    assert "Public ID:" not in source and "Abstract SHA256:" not in source
    assert data["presentations"][0]["abstract"] in html.unescape(source)


def test_staged_font_preserves_source_okina_and_spacing(tmp_path):
    from matplotlib.ft2font import FT2Font

    data = bundle()
    abstract = "Hawaiʻi uses thin\u2009space."
    data["presentations"][0]["abstract"] = abstract
    data["presentations"][0]["abstract_sha256"] = hashlib.sha256(abstract.encode()).hexdigest()
    project = stage_abstract_book(data, tmp_path / "unicode")
    manifest = json.loads((project / "abstract_manifest.json").read_text())
    assert manifest["pdf_font_files"]
    for name, digest in manifest["pdf_font_files"].items():
        font = project / "fonts" / name
        assert hashlib.sha256(font.read_bytes()).hexdigest() == digest
        face = FT2Font(str(font))
        assert all(face.get_char_index(ord(c)) for c in abstract if not c.isspace())
        assert face.get_char_index(0x2009)


@pytest.mark.parametrize("state", ["clean", "missing-glyph", "missing-log"])
def test_native_pdf_glyph_check_requires_real_clean_log(tmp_path, state):
    from symposium.organizing.artifacts import _check_pdf_glyphs

    log = tmp_path / "compiler.log"
    if state != "missing-log":
        log.write_text(
            "Output written."
            if state == "clean"
            else "Missing character: There is no ʻ (U+02BB) in font"
        )
    if state == "clean":
        _check_pdf_glyphs(log)
    else:
        with pytest.raises(ArtifactError):
            _check_pdf_glyphs(log)
