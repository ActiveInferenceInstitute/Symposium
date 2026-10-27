"""Adversarial source projection and real image tests; no live data or API calls."""

from __future__ import annotations

import copy
import hashlib
import io

import pytest
from PIL import Image, PngImagePlugin, UnidentifiedImageError

from symposium.organizing.media import MAX_MEDIA_BYTES, attach_public_portraits, sanitize_portrait
from symposium.organizing.models import (
    MAX_BUNDLE_BYTES,
    PublicationError,
    canonical_bytes,
    content_hash,
    load_bundle,
    public_url,
    safe_asset_path,
    text_hash,
    validate_bundle,
    write_bundle,
)
from symposium.organizing.projection import cell_text, project_snapshot
from tests.test_organizing_publication import inputs as inputs


def set_cell(snapshot, kind, field, value):
    snapshot["tables"][kind]["rows"][0]["values"]["c-" + field] = {"value": value}


def reproject(inputs):
    bundle, snapshot, _ = inputs
    return project_snapshot(snapshot, bundle["event"], bundle["resources"])


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, ""),
        ("text", "text"),
        (True, "true"),
        (False, "false"),
        (42, "42"),
        (2.5, "2.5"),
        (["a", {"value": "b"}], "a\nb"),
        ({"value": {"text": "nested"}}, "nested"),
        ({"type": "dt", "input": "2026-11-01T12:00:00Z"}, "2026-11-01T12:00:00Z"),
        ({"name": "Visible label", "id": "private-row"}, "Visible label"),
        ({"root": {"children": [{"text": "one"}, {"text": "two"}]}}, "one\ntwo"),
        ({"children": [{"text": "one"}, {"text": "two"}]}, "onetwo"),
        ({"type": "urlref", "url": "https://example.org"}, "https://example.org"),
    ],
)
def test_rich_cells_only_visible_text(value, expected):
    assert cell_text(value) == expected


@pytest.mark.parametrize(
    "value",
    [{}, {"unknown": "hidden"}, {"value": object()}, float("nan"), float("inf"), float("-inf")],
)
def test_malformed_rich_cells_are_rejected(value):
    with pytest.raises(PublicationError):
        cell_text(value)


def test_deep_cells_rejected():
    value = "text"
    for _ in range(23):
        value = {"value": value}
    with pytest.raises(PublicationError, match="nesting"):
        cell_text(value)


@pytest.mark.parametrize(
    ("answer", "included"),
    [
        ("Yes", True),
        (" y ", True),
        ("TRUE", True),
        ("1", True),
        (True, True),
        ("No", False),
        ("", False),
        (None, False),
        ("maybe", False),
        ("Yes please", False),
        (0, False),
    ],
)
def test_participant_requires_exact_affirmative_consent(inputs, answer, included):
    set_cell(inputs[1], "participants", "share_publicly", answer)
    bundle, ledger = reproject(inputs)
    assert bool(bundle["participants"]) is included
    if included:
        person = bundle["participants"][0]
        receipt = next(item for item in ledger["included"] if item["kind"] == "participant")
        assert receipt["approval"] == "affirmative-registration-consent"
        assert receipt["content_sha256"] == content_hash(person)
    else:
        assert any(
            row["reason"] == "No affirmative publication consent" for row in ledger["excluded"]
        )
    assert len(bundle["presentations"]) == 1


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("name", "   ", "Blank registration"),
        ("learning_needs", "Contact synthetic@example.org", "contact information"),
        ("background", "https://docs.google.com/document/d/private", "private document links"),
    ],
)
def test_private_or_blank_participant_is_excluded(inputs, field, value, reason):
    set_cell(inputs[1], "participants", field, value)
    bundle, ledger = reproject(inputs)
    assert bundle["participants"] == []
    assert any(reason in entry["reason"] for entry in ledger["excluded"])
    if value.strip():
        assert value not in canonical_bytes(bundle).decode()


def test_duplicate_consent_names_withheld_together(inputs):
    table = inputs[1]["tables"]["participants"]
    duplicate = copy.deepcopy(table["rows"][0])
    duplicate["rowId"] = "second-private-row"
    duplicate["values"]["c-name"]["value"] = " SYNTHETIC LEARNER "
    table["rows"].append(duplicate)
    table["totalRows"] = 2
    bundle, ledger = reproject(inputs)
    assert bundle["participants"] == []
    assert len([e for e in ledger["excluded"] if "Duplicate participant name" in e["reason"]]) == 2


def test_invalid_orcid_omitted_and_null_answers_normalized(inputs):
    set_cell(inputs[1], "participants", "orcid", "not an identifier")
    set_cell(inputs[1], "participants", "background", "NaN")
    set_cell(inputs[1], "participants", "challenges", "N/A")
    bundle, ledger = reproject(inputs)
    assert bundle["participants"][0]["orcid"] == ""
    assert bundle["participants"][0]["background"] == ""
    assert bundle["participants"][0]["challenges"] == ""
    assert any("ORCID" in warning["reason"] for warning in ledger["warnings"])


@pytest.mark.parametrize(
    "picture_cell",
    [
        "https://example.org/portrait",
        {"url": "https://example.org/portrait"},
        [{"url": "https://example.org/portrait"}],
    ],
)
def test_media_urls_retained_only_in_private_ledger(inputs, picture_cell):
    set_cell(inputs[1], "presentations", "pictures", picture_cell)
    bundle, ledger = reproject(inputs)
    assert bundle["presentations"][0]["pictures"] == []
    assert ledger["media"][bundle["presentations"][0]["id"]] == ["https://example.org/portrait"]
    assert "https://example.org/portrait" not in canonical_bytes(bundle).decode()


def test_missing_abstract_and_bad_picture_preserve_text_pending(inputs):
    set_cell(inputs[1], "presentations", "abstract", "")
    set_cell(inputs[1], "presentations", "pictures", [{"private": "bad attachment"}])
    bundle, ledger = reproject(inputs)
    talk = bundle["presentations"][0]
    assert talk["abstract"] == "" and talk["abstract_sha256"] == text_hash("")
    assert talk["title"] == "Synthetic title"
    assert len(ledger["warnings"]) == 2
    assert ledger["media"][talk["id"]] == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("abstract", "synthetic@example.org"),
        ("title", ""),
        ("presenter", "https://coda.io/private"),
    ],
)
def test_invalid_presentation_withheld_without_losing_consenting_roster(inputs, field, value):
    set_cell(inputs[1], "presentations", field, value)
    bundle, ledger = reproject(inputs)
    assert bundle["presentations"] == []
    assert len(bundle["participants"]) == 1
    assert any(e["kind"] == "presentation" for e in ledger["excluded"])


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("", ""),
        ("2026-11-01T12:00:00", "2026-11-01T13:00:00"),
        ("not a date", "2026-11-01T13:00:00Z"),
        ("2026-11-03T12:00:00Z", "2026-11-03T13:00:00Z"),
        ("2026-11-01T13:00:00Z", "2026-11-01T12:00:00Z"),
    ],
)
def test_invalid_or_unscheduled_slots_are_not_inferred(inputs, start, end):
    set_cell(inputs[1], "sessions", "start_utc", start)
    set_cell(inputs[1], "sessions", "end_utc", end)
    bundle, ledger = reproject(inputs)
    assert bundle["sessions"] == []
    assert any(e["kind"] == "session" for e in ledger["excluded"])
    assert len(bundle["presentations"]) == 1


def test_offset_schedule_normalized_and_blank_title_retained(inputs):
    set_cell(inputs[1], "sessions", "start_utc", "2026-11-01T08:00:00-04:00")
    set_cell(inputs[1], "sessions", "end_utc", "2026-11-01T09:00:00-04:00")
    bundle, _ = reproject(inputs)
    assert bundle["sessions"][0]["start_utc"] == "2026-11-01T12:00:00Z"
    assert bundle["sessions"][0]["end_utc"] == "2026-11-01T13:00:00Z"
    assert bundle["sessions"][0]["title"] == ""


@pytest.mark.parametrize(
    "fault", ["mapping", "missing_table", "partial", "duplicate_row", "not_rows"]
)
def test_incomplete_source_snapshot_rejected(inputs, fault):
    snapshot = inputs[1]
    if fault == "mapping":
        snapshot["mapping"]["sources"]["presentations"]["uri"] = (
            "superhuman://docs/synthetic-private/tables/presentations"
        )
    elif fault == "missing_table":
        del snapshot["tables"]["participants"]
    elif fault == "partial":
        snapshot["tables"]["participants"]["totalRows"] = 2
    elif fault == "duplicate_row":
        table = snapshot["tables"]["participants"]
        table["rows"].append(copy.deepcopy(table["rows"][0]))
        table["totalRows"] = 2
    else:
        snapshot["tables"]["participants"]["rows"] = {}
    with pytest.raises(PublicationError):
        reproject(inputs)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org",
        "https://",
        "https://user:password@example.org",
        "https://example.org:8080",
        "https://example.org:bogus",
        "https://example.org:99999",
        "https://[broken",
        "https://localhost/",
        "https://host.local/",
        "https://host.internal/",
        "https://127.0.0.1/",
        "https://10.2.3.4/",
        "https://[::1]/",
        "https://0.0.0.0/",
        "https://example.org/?api_key=private",
        "https://example.org/?signature=private",
        "https://docs.google.com/document/private",
        "https://docs.superhuman.com/private",
    ],
)
def test_nonpublic_or_credential_urls_rejected(url):
    with pytest.raises(PublicationError):
        public_url(url)


@pytest.mark.parametrize(
    "url", ["https://example.org/path?q=public", "https://example.org:443/path", "https://8.8.8.8/"]
)
def test_public_https_urls_retained(url):
    assert public_url(url) == url


@pytest.mark.parametrize(
    "path",
    [
        "../private.png",
        "/assets/portraits/a.jpg",
        "assets/portraits/../../private.jpg",
        "assets\\portraits\\a.jpg",
        "assets/a.jpg",
        "assets/portraits/a.exe",
    ],
)
def test_asset_paths_reject_escape_or_bad_format(path):
    with pytest.raises(PublicationError):
        safe_asset_path(path)


@pytest.mark.parametrize(
    "fault",
    [
        "extra_root",
        "missing_event",
        "bool_version",
        "bad_year",
        "bool_year",
        "bad_date",
        "wrong_year",
        "reversed_dates",
        "timezone",
        "bad_event_id",
        "empty_event_title",
        "bad_livestreams",
        "duplicate_id",
        "duplicate_talk",
        "duplicate_person",
        "bad_orcid",
        "abstract_hash",
        "picture_hash",
        "picture_alt",
        "picture_limit",
        "text_control",
        "text_bound",
        "row_type",
        "row_bound",
        "bad_session",
        "naive_session",
        "offset_session",
        "reversed_session",
        "resource_extra",
    ],
)
def test_closed_bundle_rejects_malformed_public_records(inputs, fault):
    bundle = inputs[0]
    event = bundle["event"]
    if fault == "extra_root":
        bundle["private"] = "leak"
    elif fault == "missing_event":
        del bundle["event"]
    elif fault == "bool_version":
        bundle["schema_version"] = True
    elif fault in {"bad_year", "bool_year"}:
        event["year"] = 1800 if fault == "bad_year" else True
    elif fault == "bad_date":
        event["start_date"] = "not-a-date"
    elif fault == "wrong_year":
        event["start_date"] = "2025-11-01"
    elif fault == "reversed_dates":
        event["end_date"] = "2026-10-31"
    elif fault == "timezone":
        event["timezone"] = "America/New_York"
    elif fault == "bad_event_id":
        event["id"] = "../private"
    elif fault == "empty_event_title":
        event["title"] = " "
    elif fault == "bad_livestreams":
        event["livestreams"] = {}
    elif fault in {"duplicate_id", "duplicate_talk"}:
        duplicate = copy.deepcopy(bundle["presentations"][0])
        if fault == "duplicate_talk":
            duplicate["id"] = "second-talk"
        bundle["presentations"].append(duplicate)
    elif fault == "duplicate_person":
        duplicate = copy.deepcopy(bundle["participants"][0])
        duplicate["id"] = "second-person"
        bundle["participants"].append(duplicate)
    elif fault == "bad_orcid":
        bundle["participants"][0]["orcid"] = "invalid"
    elif fault == "abstract_hash":
        bundle["presentations"][0]["abstract_sha256"] = "0" * 64
    elif fault in {"picture_hash", "picture_alt", "picture_limit"}:
        picture = {"path": "assets/portraits/a.jpg", "sha256": "0" * 64, "alt": "Public portrait"}
        if fault == "picture_hash":
            picture["sha256"] = "xyz"
        elif fault == "picture_alt":
            picture["alt"] = ""
        bundle["presentations"][0]["pictures"] = [picture] * (21 if fault == "picture_limit" else 1)
    elif fault in {"text_control", "text_bound"}:
        bundle["participants"][0]["background"] = (
            "\x00" if fault == "text_control" else "x" * 100001
        )
    elif fault in {"row_type", "row_bound"}:
        bundle["resources"] = [None] if fault == "row_type" else [bundle["resources"][0]] * 10001
    elif fault == "bad_session":
        bundle["sessions"][0]["start_utc"] = "invalid"
    elif fault == "naive_session":
        bundle["sessions"][0]["start_utc"] = "2026-11-01T12:00:00"
    elif fault == "offset_session":
        bundle["sessions"][0]["start_utc"] = "2026-11-01T12:00:00+01:00"
    elif fault == "reversed_session":
        bundle["sessions"][0]["end_utc"] = bundle["sessions"][0]["start_utc"]
    else:
        bundle["resources"][0]["email"] = "private"
    with pytest.raises(PublicationError):
        validate_bundle(bundle)


def test_validated_copy_roundtrip_exclusive_write(inputs, tmp_path):
    bundle = inputs[0]
    detached = validate_bundle(bundle)
    detached["event"]["title"] = "Changed"
    assert bundle["event"]["title"] == "Synthetic Symposium"
    path = tmp_path / "public" / "program.json"
    write_bundle(bundle, path)
    assert load_bundle(path) == bundle
    assert path.read_bytes() == canonical_bytes(bundle)
    with pytest.raises(FileExistsError):
        write_bundle(bundle, path)
    assert content_hash(bundle) == hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("raw", [b"not JSON", b"\xff", b"{}"])
def test_load_invalid_json_or_schema_rejected(tmp_path, raw):
    path = tmp_path / "invalid.json"
    path.write_bytes(raw)
    with pytest.raises(PublicationError):
        load_bundle(path)


def test_load_byte_bound_rejects_real_large_file(tmp_path):
    path = tmp_path / "oversized.json"
    with path.open("wb") as stream:
        stream.seek(MAX_BUNDLE_BYTES)
        stream.write(b" ")
    with pytest.raises(PublicationError, match="byte limit"):
        load_bundle(path)


@pytest.mark.parametrize("format", ["JPEG", "PNG", "WEBP"])
def test_portraits_decode_resize_strip_metadata(format, tmp_path):
    original = io.BytesIO()
    image = Image.new("RGB", (1600, 800), (20, 80, 140))
    exif = Image.Exif()
    exif[315] = "synthetic-private@example.org"
    exif[274] = 6
    if format == "PNG":
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Private", "synthetic-private@example.org")
        image.save(original, format=format, pnginfo=metadata, exif=exif)
    else:
        image.save(original, format=format, exif=exif)
    payload = sanitize_portrait(original.getvalue())
    path = tmp_path / "sanitized.jpg"
    path.write_bytes(payload)
    with Image.open(path) as decoded:
        decoded.load()
        assert decoded.format == "JPEG"
        assert decoded.size == (600, 1200)
        assert decoded.getexif() == {}
        assert "Private" not in decoded.info and "exif" not in decoded.info
        assert decoded.mode == "RGB"
    assert b"synthetic-private" not in payload


def test_portrait_gif_corruption_and_byte_limit_rejected():
    gif = io.BytesIO()
    Image.new("RGB", (2, 2), "blue").save(gif, format="GIF")
    with pytest.raises(PublicationError):
        sanitize_portrait(gif.getvalue())
    with pytest.raises(UnidentifiedImageError):
        sanitize_portrait(b"corrupt image")
    with pytest.raises(PublicationError, match="byte limit"):
        sanitize_portrait(b"x" * (MAX_MEDIA_BYTES + 1))


def test_real_portrait_pixel_bound_rejected(tmp_path):
    path = tmp_path / "large.png"
    Image.new("1", (8001, 5000)).save(path)
    with pytest.raises(PublicationError, match="bounded image"):
        sanitize_portrait(path.read_bytes())


def test_media_invalid_provenance_records_omission_without_network(inputs, tmp_path):
    bundle, _, ledger = inputs
    talk_id = bundle["presentations"][0]["id"]
    url = "https://example.org/private"
    ledger["media"][talk_id] = [url]
    result, receipt = attach_public_portraits(
        bundle, ledger, tmp_path / "portraits", public_document="synthetic-public"
    )
    assert result["presentations"][0]["pictures"] == []
    assert receipt["portrait_count"] == 0
    assert receipt["warnings"][-1] == {
        "kind": "portrait",
        "public_id": talk_id,
        "attachment_index": 0,
        "reason": "PublicationError",
        "source_url_sha256": hashlib.sha256(url.encode()).hexdigest(),
    }
    assert receipt["public_sha256"] == content_hash(result)
    with pytest.raises(PublicationError, match="fresh directory"):
        attach_public_portraits(
            bundle, ledger, tmp_path / "portraits", public_document="synthetic-public"
        )


@pytest.mark.parametrize("fault", ["missing", "null", "list", "nonrecord"])
def test_source_row_identity_is_required(inputs, fault):
    rows = inputs[1]["tables"]["participants"]["rows"]
    if fault == "missing":
        del rows[0]["rowId"]
    elif fault == "null":
        rows[0]["rowId"] = None
    elif fault == "list":
        rows[0]["rowId"] = ["not", "an", "identifier"]
    else:
        rows[0] = None
    with pytest.raises(PublicationError):
        reproject(inputs)


def test_aggregate_bundle_limit_rejects_many_individually_bounded_records(inputs):
    bundle = inputs[0]
    template = bundle["resources"][0]
    bundle["resources"] = [
        {**template, "id": f"resource-{index}", "description": "x " * 50000} for index in range(170)
    ]
    with pytest.raises(PublicationError, match="byte limit"):
        validate_bundle(bundle)


def test_valid_orcid_and_livestream_retained(inputs):
    bundle = inputs[0]
    bundle["participants"][0]["orcid"] = "https://orcid.org/0000-0002-1825-0097"
    bundle["event"]["livestreams"] = [
        {"title": "Public stream", "url": "https://example.org/stream"}
    ]
    assert validate_bundle(bundle) == bundle


def test_invalid_source_values_excluded_with_reason(inputs):
    inputs[1]["tables"]["participants"]["rows"][0]["values"] = None
    bundle, ledger = reproject(inputs)
    assert not bundle["participants"]
    assert any(e["kind"] == "participant" for e in ledger["excluded"])
