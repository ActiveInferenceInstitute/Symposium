"""Public site safety and source-readable export scenarios; fixtures are synthetic."""

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest
from PIL import Image

from symposium.organizing.models import (
    PublicParticipant,
    canonical_bytes,
    text_hash,
    validate_bundle,
)
from symposium.organizing.site import build_site


@pytest.fixture
def bundle():
    return {
        "schema_version": 1,
        "event": {
            "id": "test-event",
            "title": "Synthetic Symposium",
            "year": 2026,
            "start_date": "2026-11-01",
            "end_date": "2026-11-02",
            "timezone": "UTC",
            **{
                key: "https://example.org/" + key
                for key in [
                    "program_url",
                    "participant_registration_url",
                    "presenter_registration_url",
                    "community_url",
                    "donate_url",
                ]
            },
            "livestreams": [],
        },
        "presentations": [
            {
                "id": "test-talk",
                "presenter": "Synthetic Researcher",
                "title": "A & B",
                "abstract": "First paragraph.\n\nSecond paragraph.",
                "contribution_type": "Talk",
                "source_url": "https://example.org/talk",
                "pictures": [],
                "abstract_sha256": text_hash("First paragraph.\n\nSecond paragraph."),
            }
        ],
        "participants": [
            {
                **{key: "" for key in PublicParticipant.__annotations__},
                "id": "test-person",
                "name": "Synthetic Learner",
                "learning_needs": "Learn models",
            }
        ],
        "sessions": [
            {
                "id": "test-session",
                "title": "A & B",
                "presenter": "Synthetic Researcher",
                "kind": "Talk",
                "start_utc": "2026-11-01T12:00:00Z",
                "end_utc": "2026-11-01T13:00:00Z",
            }
        ],
        "resources": [
            {
                "id": "test-resource",
                "title": "Methods",
                "description": "Synthetic resource",
                "url": "https://example.org/methods",
                "category": "Methods",
            }
        ],
    }


class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def test_readable_content_navigation_and_filters(bundle, tmp_path):
    index = build_site(bundle, tmp_path / "site")
    source = index.read_text()
    tags = Tags(source).tags
    ids = {attrs["id"] for _, attrs in tags if "id" in attrs}
    assert {
        "presentations",
        "participants",
        "schedule",
        "resources",
        "presentation-test-talk",
    } <= ids
    assert "A &amp; B" in source
    assert "First paragraph.\n\nSecond paragraph." in source
    assert "Learn models" in source
    assert any(attrs.get("data-category") == "Talk" for _, attrs in tags)
    assert 'datetime="2026-11-01T12:00:00Z"' in source
    assert not any("downloads/" in attrs.get("href", "") for _, attrs in tags)
    for _, attrs in tags:
        if attrs.get("href", "").startswith("#"):
            assert attrs["href"][1:] in ids
    assert (index.parent / "static/site.js").is_file()
    assert (index.parent / ".nojekyll").is_file()


def test_prose_cannot_close_script_or_inject_markup(bundle, tmp_path):
    attack = '</script><script>alert("test")</script><img src=x onerror=alert(1)>'
    bundle["presentations"][0]["abstract"] = attack
    bundle["presentations"][0]["abstract_sha256"] = text_hash(attack)
    source = build_site(bundle, tmp_path / "site").read_text()
    tags = Tags(source).tags
    assert [(tag, attrs) for tag, attrs in tags if tag == "script"] == [
        ("script", {"src": "static/site.js", "defer": None})
    ]
    assert not any(tag == "img" for tag, _ in tags)
    assert "&lt;/script&gt;" in source


def test_no_overwrite(bundle, tmp_path):
    output = tmp_path / "site"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("preserve")
    with pytest.raises(FileExistsError):
        build_site(bundle, output)
    assert marker.read_text() == "preserve"
    assert not (output / "index.html").exists()


def test_only_named_artifacts_copied(bundle, tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "book.pdf").write_bytes(b"synthetic PDF fixture")
    (artifacts / "private-log.json").write_text("DO NOT EXPORT")
    index = build_site(bundle, tmp_path / "site", artifacts_dir=artifacts)
    assert (index.parent / "downloads/book.pdf").read_bytes() == b"synthetic PDF fixture"
    assert "downloads/book.pdf" in index.read_text()
    assert not list(index.parent.rglob("private-log.json"))


def add_picture(bundle, tmp_path):
    assets = tmp_path / "input"
    picture = assets / "assets/portraits/portrait.png"
    picture.parent.mkdir(parents=True)
    Image.new("RGB", (2, 2), "white").save(picture)
    content = picture.read_bytes()
    bundle["presentations"][0]["pictures"] = [
        {
            "path": "assets/portraits/portrait.png",
            "sha256": hashlib.sha256(content).hexdigest(),
            "alt": "Synthetic portrait",
        }
    ]
    return assets, picture


def test_verified_picture_preserved(bundle, tmp_path):
    assets, picture = add_picture(bundle, tmp_path)
    index = build_site(bundle, tmp_path / "site", assets_dir=assets)
    images = list((index.parent / "media").iterdir())
    assert len(images) == 1 and images[0].read_bytes() == picture.read_bytes()
    assert 'alt="Synthetic portrait"' in index.read_text()


@pytest.mark.parametrize("failure", ["hash", "traversal", "missing", "symlink", "no-root"])
def test_reject_invalid_assets_before_output(bundle, tmp_path, failure):
    assets, picture = add_picture(bundle, tmp_path)
    p = bundle["presentations"][0]["pictures"][0]
    if failure == "hash":
        p["sha256"] = "0" * 64
    elif failure == "traversal":
        p["path"] = "assets/portraits/../../secret.png"
    elif failure == "missing":
        p["path"] = "assets/portraits/missing.png"
    elif failure == "symlink":
        external = tmp_path / "outside.png"
        external.write_bytes(picture.read_bytes())
        link = picture.parent / "link.png"
        link.symlink_to(external)
        p["path"] = "assets/portraits/link.png"
    with pytest.raises(ValueError):
        build_site(bundle, tmp_path / "site", assets_dir=None if failure == "no-root" else assets)
    assert not (tmp_path / "site").exists()


def test_invalid_url_rejected(bundle, tmp_path):
    bundle["resources"][0]["url"] = "javascript:alert(1)"
    with pytest.raises(ValueError):
        build_site(bundle, tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_participant_brief_download_is_explicit(bundle, tmp_path):
    artifacts = tmp_path / "artifacts"
    (artifacts / "participants").mkdir(parents=True)
    brief = artifacts / "participants/test-person.md"
    brief.write_text("# Synthetic Learner\nSelf-reported learning needs.")
    (artifacts / "participants/unapproved-person.md").write_text("must not ship")
    index = build_site(bundle, tmp_path / "site", artifacts_dir=artifacts)
    assert 'href="downloads/participants/test-person.md"' in index.read_text()
    assert (
        index.parent / "downloads/participants/test-person.md"
    ).read_bytes() == brief.read_bytes()
    assert not (index.parent / "downloads/participants/unapproved-person.md").exists()


def test_program_json_matches_validated_bundle_and_relative_link(bundle, tmp_path):
    index = build_site(bundle, tmp_path / "site")
    exported = index.parent / "program.json"
    assert exported.read_bytes() == canonical_bytes(validate_bundle(bundle))
    links = [attrs for tag, attrs in Tags(index.read_text()).tags if tag == "a"]
    assert any(attrs.get("href") == "program.json" and "download" in attrs for attrs in links)


def test_program_json_rejects_unapproved_fields(bundle, tmp_path):
    bundle["private_ledger"] = {"source_row": "private"}
    with pytest.raises(ValueError):
        build_site(bundle, tmp_path / "site")
    assert not (tmp_path / "site/program.json").exists()
    assert not (tmp_path / "site").exists()


@pytest.mark.parametrize(
    "year,start,end", [(2026, "2026-04-03", "2026-04-04"), (2027, "2027-09-21", "2027-09-23")]
)
def test_event_dates_are_source_driven(bundle, tmp_path, year, start, end):
    bundle["event"].update(year=year, start_date=start, end_date=end)
    bundle["sessions"] = []
    source = build_site(bundle, tmp_path / "site").read_text()
    assert start in source and end in source
    assert "November 12" not in source
    assert "Online and free" not in source


@pytest.mark.parametrize("payload", [b"not an image", bytes.fromhex("89504e470d0a1a0a")])
def test_hash_matching_malformed_image_rejected_before_output(bundle, tmp_path, payload):
    assets, picture = add_picture(bundle, tmp_path)
    picture.write_bytes(payload)
    bundle["presentations"][0]["pictures"][0]["sha256"] = hashlib.sha256(
        picture.read_bytes()
    ).hexdigest()
    with pytest.raises(ValueError, match="image"):
        build_site(bundle, tmp_path / "site", assets_dir=assets)
    assert not (tmp_path / "site").exists()


def test_pending_content_is_visible_without_opening_records(bundle, tmp_path):
    bundle["presentations"][0].update(abstract="", abstract_sha256=text_hash(""))
    bundle["sessions"][0]["title"] = ""
    source = build_site(bundle, tmp_path / "site").read_text()
    summary = source.split("<summary>", 1)[1].split("</summary>", 1)[0]
    assert "Abstract pending" in summary
    assert "1 abstract pending" in source
    assert "1 session title pending" in source
    assert "Session title pending" in source


def test_public_methods_and_download_guidance(bundle, tmp_path):
    source = build_site(bundle, tmp_path / "site").read_text()
    assert "About this public program" in source
    assert "no automatic live synchronization" in source
    assert "public-sharing consent" in source
    assert "not independent verification" in source
    assert 'id="downloads"' in source
    assert 'id="working-book"' in source
    assert 'href="#working-book"' in source


def test_image_extension_must_match_decoded_format(bundle, tmp_path):
    assets, picture = add_picture(bundle, tmp_path)
    Image.new("RGB", (2, 2), "white").save(picture, format="JPEG")
    bundle["presentations"][0]["pictures"][0]["sha256"] = hashlib.sha256(
        picture.read_bytes()
    ).hexdigest()
    with pytest.raises(ValueError, match="image"):
        build_site(bundle, tmp_path / "site", assets_dir=assets)
    assert not (tmp_path / "site").exists()


def test_no_javascript_keeps_records_and_hides_nonfunctional_controls(bundle, tmp_path):
    source = build_site(bundle, tmp_path / "site").read_text()
    tags = Tags(source).tags
    records = [attrs for tag, attrs in tags if tag == "details"]
    assert len(records) == 2
    assert all("hidden" not in attrs for attrs in records)
    enhancements = [attrs for _, attrs in tags if "data-enhancement" in attrs]
    assert enhancements and all("hidden" in attrs for attrs in enhancements)
    assert "First paragraph." in source and "Learn models" in source


def test_public_bundle_build_preserves_source_bytes(tmp_path):
    root = Path(__file__).resolve().parents[1] / "data/public/2026"
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    bundle = json.loads(before[Path("program.json")])
    index = build_site(bundle, tmp_path / "site", assets_dir=root, artifacts_dir=root)
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    tags = Tags(index.read_text()).tags
    assert len(
        [attrs for _, attrs in tags if attrs.get("id", "").startswith("presentation-")]
    ) == len(bundle["presentations"])
    assert "2 abstracts pending; 1 session title pending" in index.read_text()
    assert (index.parent / "program.json").read_bytes() == canonical_bytes(validate_bundle(bundle))


def test_form_identifiers_and_intrinsic_image_dimensions(bundle, tmp_path):
    assets, _ = add_picture(bundle, tmp_path)
    source = build_site(bundle, tmp_path / "site", assets_dir=assets).read_text()
    tags = Tags(source).tags
    fields = [attrs for tag, attrs in tags if tag in {"input", "select"}]
    assert fields and all(attrs.get("id") or attrs.get("name") for attrs in fields)
    images = [attrs for tag, attrs in tags if tag == "img"]
    assert images and all(
        attrs.get("width") == "2" and attrs.get("height") == "2" for attrs in images
    )


def test_whitespace_abstract_has_readable_pending_body(bundle, tmp_path):
    bundle["presentations"][0]["abstract"] = " \n "
    bundle["presentations"][0]["abstract_sha256"] = text_hash(" \n ")
    source = build_site(bundle, tmp_path / "site").read_text()
    assert "No program abstract has been published for this presentation yet." in source
