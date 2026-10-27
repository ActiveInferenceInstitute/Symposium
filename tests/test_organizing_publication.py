"""Real publication files, consent revocation, and deliberate negative controls."""

import hashlib
import html
import json
import zipfile

import pytest
from icalendar import Calendar
from PIL import Image, PngImagePlugin

from symposium.organizing.bridge import FIELDS
from symposium.organizing.models import PublicationError, content_hash
from symposium.organizing.projection import project_snapshot
from symposium.organizing.publication import (
    stage_public,
    verify_public_tree,
    write_artifact_index,
    write_calendar,
    write_participant_briefs,
)

NOW = "2026-10-26T12:00:00Z"


@pytest.fixture
def inputs():
    event = {
        "id": "synthetic-2026",
        "title": "Synthetic Symposium",
        "year": 2026,
        "start_date": "2026-11-01",
        "end_date": "2026-11-02",
        "timezone": "UTC",
        "livestreams": [],
    }
    for key in (
        "program_url",
        "participant_registration_url",
        "presenter_registration_url",
        "community_url",
        "donate_url",
    ):
        event[key] = "https://example.org/" + key
    mapping = {
        "schema_version": 1,
        "public_document": "synthetic-public",
        "organizer_document": "synthetic-private",
        "sources": {
            kind: {
                "uri": f"superhuman://docs/synthetic-{'private' if kind == 'participants' else 'public'}/tables/{kind}",
                "fields": {key: "c-" + key for key in fields},
            }
            for kind, fields in FIELDS.items()
        },
    }
    values = {
        "presentations": {
            "presenter": "Synthetic Presenter",
            "title": "Synthetic title",
            "abstract": "A full abstract.",
            "contribution_type": "Talk",
            "pictures": [],
        },
        "participants": {
            "name": "Synthetic Learner",
            "share_publicly": "Yes",
            "learning_needs": "Literal <script>x</script> $x$",
        },
        "sessions": {
            "title": "",
            "presenter": "",
            "kind": "Talk",
            "start_utc": "2026-11-01T12:00:00Z",
            "end_utc": "2026-11-01T13:00:00Z",
        },
    }
    tables = {
        kind: {
            "schema": [],
            "totalRows": 1,
            "rows": [
                {
                    "rowId": kind + "-private-row",
                    "values": {"c-" + key: {"value": values[kind].get(key, "")} for key in fields},
                }
            ],
        }
        for kind, fields in FIELDS.items()
    }
    snapshot = {"schema_version": 1, "mapping": mapping, "observed_at": NOW, "tables": tables}
    resources = [
        {
            "id": "resource-a",
            "title": "Methods",
            "description": "Provided starting point",
            "url": "https://example.org/methods",
            "category": "Methods",
        }
    ]
    bundle, ledger = project_snapshot(snapshot, event, resources)
    assert (
        len(bundle["participants"]) == len(bundle["presentations"]) == len(bundle["sessions"]) == 1
    )
    return bundle, snapshot, ledger


def stage(inputs, path, **kwargs):
    return stage_public(*inputs, path, apply=True, as_of=NOW, **kwargs)


def test_calendar_roundtrip_pending_stable_uid_no_invites(inputs, tmp_path):
    bundle = inputs[0]
    first = write_calendar(bundle, tmp_path / "one.ics", generated_at=NOW)
    second = write_calendar(bundle, tmp_path / "two.ics", generated_at=NOW)
    assert first.read_bytes() == second.read_bytes()
    parsed = Calendar.from_ical(first.read_bytes())
    events = parsed.walk("VEVENT")
    assert len(events) == 1
    event = events[0]
    assert str(event["summary"]) == "Session title not yet published"
    assert event.decoded("dtstart").isoformat() == "2026-11-01T12:00:00+00:00"
    assert event.decoded("dtend").isoformat() == "2026-11-01T13:00:00+00:00"
    assert all(not any(k in c for k in ("ATTENDEE", "ORGANIZER", "METHOD")) for c in parsed.walk())
    with pytest.raises(FileExistsError):
        write_calendar(bundle, first)


def test_briefs_literal_source_answers_and_resources(inputs, tmp_path):
    bundle = inputs[0]
    paths = write_participant_briefs(bundle, tmp_path / "participants")
    text = paths[0].read_text()
    assert bundle["participants"][0]["learning_needs"] in html.unescape(text)
    assert "<script>" not in text and "$x$" not in text
    assert "not an assessment" in text and "https://example.org/methods" in html.unescape(text)
    with pytest.raises(FileExistsError):
        write_participant_briefs(bundle, tmp_path / "participants")


def test_stage_manifest_allowlist_and_real_docx(inputs, tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    write_calendar(inputs[0], artifacts / "program.ics", generated_at=NOW)
    write_participant_briefs(inputs[0], artifacts / "participants")
    with zipfile.ZipFile(artifacts / "book.docx", "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Synthetic public abstract</w:t></w:r></w:p></w:body></w:document>',
        )
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
    (artifacts / "private.json").write_text('{"email":"private@example.org"}')
    index = write_artifact_index(inputs[0], artifacts)
    assert "private.json" not in index.read_text()
    output = tmp_path / "public"
    assert stage(inputs, output, artifacts_dir=artifacts) == output / "program.json"
    assert verify_public_tree(output) == inputs[0]
    assert not (output / "private.json").exists()
    assert (output / "book.docx").read_bytes() == (artifacts / "book.docx").read_bytes()
    assert "synthetic-private" not in (output / "publication.json").read_text()
    with pytest.raises(FileExistsError):
        stage(inputs, output, artifacts_dir=artifacts)


@pytest.mark.parametrize(
    "fault", ["noapply", "snapshot", "bundle", "ledger", "stale", "future", "consent", "text"]
)
def test_rejection_before_output(inputs, tmp_path, fault):
    bundle, snapshot, ledger = inputs
    if fault == "snapshot":
        snapshot["tables"]["participants"]["rows"][0]["rowId"] = "modified"
    elif fault == "bundle":
        bundle["participants"][0]["background"] = "forged"
    elif fault == "ledger":
        ledger["included"][0]["approval"] = "forged"
    elif fault in ("stale", "future"):
        snapshot["observed_at"] = (
            "2026-10-25T12:00:00Z" if fault == "stale" else "2026-10-26T12:06:00Z"
        )
        ledger["snapshot_sha256"] = content_hash(snapshot)
    elif fault == "consent":
        snapshot["tables"]["participants"]["rows"][0]["values"]["c-share_publicly"]["value"] = "No"
        ledger["snapshot_sha256"] = content_hash(snapshot)
    elif fault == "text":
        bundle["participants"][0]["background"] = "forged"
        ledger["public_sha256"] = content_hash(bundle)
    with pytest.raises(PublicationError):
        stage_public(
            bundle, snapshot, ledger, tmp_path / "rejected", apply=fault != "noapply", as_of=NOW
        )
    assert not (tmp_path / "rejected").exists()


@pytest.mark.parametrize(
    "fault", ["extra", "hidden", "modified", "symlink", "directory", "manifest"]
)
def test_tree_rejects_private_and_altered_entries(inputs, tmp_path, fault):
    output = tmp_path / "public"
    stage(inputs, output)
    if fault in ("extra", "hidden"):
        (output / (".env" if fault == "hidden" else "private.json")).write_text("private")
    elif fault == "modified":
        (output / "program.json").write_text("{}")
    elif fault == "symlink":
        (output / "leak").symlink_to(tmp_path)
    elif fault == "directory":
        (output / "private").mkdir()
    else:
        manifest = json.loads((output / "publication.json").read_text())
        manifest["files"]["../outside"] = "0" * 64
        (output / "publication.json").write_text(json.dumps(manifest))
    with pytest.raises(PublicationError):
        verify_public_tree(output)


def test_modified_artifact_rejected_and_revocation_removes_brief(inputs, tmp_path):
    bundle, snapshot, ledger = inputs
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    briefs = write_participant_briefs(bundle, artifacts / "participants")
    write_artifact_index(bundle, artifacts)
    stage(inputs, tmp_path / "before", artifacts_dir=artifacts)
    briefs[0].write_text("altered")
    with pytest.raises(PublicationError):
        stage(inputs, tmp_path / "altered", artifacts_dir=artifacts)
    snapshot["tables"]["participants"]["rows"][0]["values"]["c-share_publicly"]["value"] = "No"
    revised, fresh_ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    stage((revised, snapshot, fresh_ledger), tmp_path / "after")
    assert verify_public_tree(tmp_path / "after")["participants"] == []
    assert not (tmp_path / "after" / "participants").exists()
    assert list((tmp_path / "before" / "participants").glob("*.md"))


@pytest.mark.parametrize("fault", ["none", "metadata", "sha", "origin", "symlink"])
def test_real_portrait_validation(inputs, tmp_path, fault):
    bundle, snapshot, ledger = inputs
    url = "https://codahosted.io/docs/synthetic-public/blobs/portrait"
    if fault == "origin":
        url = "https://example.org/private-portrait"
    snapshot["tables"]["presentations"]["rows"][0]["values"]["c-pictures"]["value"] = [{"url": url}]
    bundle, ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    assets = tmp_path / "assets" / "portraits"
    assets.mkdir(parents=True)
    metadata = PngImagePlugin.PngInfo()
    if fault == "metadata":
        metadata.add_text("Contact", "private@example.org")
    Image.new("RGB", (8, 8), "blue").save(assets / "portrait.png", pnginfo=metadata)
    raw = (assets / "portrait.png").read_bytes()
    bundle["presentations"][0]["pictures"] = [
        {
            "path": "assets/portraits/portrait.png",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "alt": "Synthetic portrait",
        }
    ]
    if fault == "sha":
        bundle["presentations"][0]["pictures"][0]["sha256"] = "0" * 64
    if fault == "symlink":
        (assets / "portrait.png").rename(assets / "original.png")
        (assets / "portrait.png").symlink_to(assets / "original.png")
    ledger["public_sha256"] = content_hash(bundle)
    if fault == "none":
        stage((bundle, snapshot, ledger), tmp_path / "public", assets_dir=tmp_path)
        assert verify_public_tree(tmp_path / "public") == bundle
    else:
        with pytest.raises(PublicationError):
            stage((bundle, snapshot, ledger), tmp_path / "public", assets_dir=tmp_path)
        assert not (tmp_path / "public").exists()


@pytest.mark.parametrize(
    "fault", ["private", "symlink", "traversal", "wrong_bundle", "bad_pdf", "bad_zip"]
)
def test_artifact_boundaries(inputs, tmp_path, fault):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    if fault == "private":
        (artifacts / "program.ics").write_text("private@example.org")
    elif fault == "symlink":
        (tmp_path / "outside").write_text("private")
        (artifacts / "program.ics").symlink_to(tmp_path / "outside")
    elif fault == "bad_pdf":
        (artifacts / "book.pdf").write_text("not a PDF")
    elif fault == "bad_zip":
        (artifacts / "book.docx").write_text("not a ZIP")
    if fault in {"private", "symlink", "bad_pdf", "bad_zip"}:
        with pytest.raises(PublicationError):
            write_artifact_index(inputs[0], artifacts)
        assert not (artifacts / "artifact_index.json").exists()
    else:
        path = write_artifact_index(inputs[0], artifacts)
        index = json.loads(path.read_text())
        if fault == "traversal":
            index["files"]["../private.json"] = "0" * 64
        else:
            index["bundle_sha256"] = "0" * 64
        path.write_text(json.dumps(index))
        with pytest.raises(PublicationError):
            stage(inputs, tmp_path / "public", artifacts_dir=artifacts)
        assert not (tmp_path / "public").exists()


@pytest.mark.parametrize(
    "fault",
    ["none", "url_hash", "index", "reason", "duplicate", "missing_receipt", "projection_warning"],
)
def test_explicit_portrait_omission_receipt(inputs, tmp_path, fault):
    bundle, snapshot, ledger = inputs
    url = "https://codahosted.io/docs/synthetic-public/blobs/withheld"
    snapshot["tables"]["presentations"]["rows"][0]["values"]["c-pictures"]["value"] = [{"url": url}]
    bundle, ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    warning = {
        "kind": "portrait",
        "public_id": bundle["presentations"][0]["id"],
        "attachment_index": 0,
        "reason": "HTTPError",
        "source_url_sha256": hashlib.sha256(url.encode()).hexdigest(),
    }
    if fault == "url_hash":
        warning["source_url_sha256"] = "0" * 64
    elif fault == "index":
        warning["attachment_index"] = 1
    elif fault == "reason":
        warning["reason"] = "IgnoreEverything"
    ledger["warnings"].append(warning)
    ledger["portrait_count"] = 0
    if fault == "duplicate":
        ledger["warnings"].append(dict(warning))
    elif fault == "missing_receipt":
        ledger["warnings"] = []
    elif fault == "projection_warning":
        ledger["warnings"].insert(0, {"kind": "participant", "reason": "forged"})
    if fault == "none":
        stage((bundle, snapshot, ledger), tmp_path / "public")
        assert verify_public_tree(tmp_path / "public") == bundle
        assert len(bundle["presentations"]) == len(bundle["participants"]) == 1
    else:
        with pytest.raises(PublicationError):
            stage((bundle, snapshot, ledger), tmp_path / "public")
        assert not (tmp_path / "public").exists()


def pdf_fixture(
    *,
    text="Approved synthetic abstract.",
    metadata="Public book",
    uri="https://example.org/program",
    annotation="Public reference",
    catalog_extra="",
    action=None,
    xmp=None,
):
    """Create a real one-page PDF with byte-accurate xref and a Helvetica text stream."""

    def literal(value):
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    stream = f"BT /F1 12 Tf 72 720 Td ({literal(text)}) Tj ET".encode("ascii")
    action = action or f"<< /S /URI /URI ({literal(uri)}) >>"
    objects = [
        f"<< /Type /Catalog /Pages 2 0 R {catalog_extra} {'/Metadata 8 0 R' if xmp else ''} >>".encode(),
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R /Annots [7 0 R] >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        f"<< /Title ({literal(metadata)}) >>".encode(),
        f"<< /Type /Annot /Subtype /Link /Rect [72 700 300 720] /Contents ({literal(annotation)}) /A {action} >>".encode(),
    ]
    if xmp:
        payload = xmp.encode()
        objects.append(
            b"<< /Type /Metadata /Subtype /XML /Length "
            + str(len(payload)).encode()
            + b" >>\nstream\n"
            + payload
            + b"\nendstream"
        )
    result = bytearray(b"%PDF-1.7\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info 6 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(result)


def test_pdf_real_parse_public_text_links_and_metadata(inputs, tmp_path):
    from pypdf import PdfReader

    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    raw = pdf_fixture()
    (artifacts / "book.pdf").write_bytes(raw)
    parsed = PdfReader(artifacts / "book.pdf", strict=True)
    assert parsed.pages[0].extract_text() == "Approved synthetic abstract."
    assert parsed.metadata.title == "Public book"
    index = write_artifact_index(inputs[0], artifacts)
    assert json.loads(index.read_text())["files"]["book.pdf"] == hashlib.sha256(raw).hexdigest()
    stage(inputs, tmp_path / "public", artifacts_dir=artifacts)
    assert verify_public_tree(tmp_path / "public") == inputs[0]


@pytest.mark.parametrize(
    "fault",
    [
        "email",
        "private_link",
        "metadata",
        "annotation",
        "uri_private",
        "uri_local",
        "uri_credential",
        "uri_http",
        "javascript",
        "open_action",
        "additional_action",
        "embedded_file",
        "launch",
        "remote_goto",
        "xmp",
        "fake_header_eof",
        "encrypted",
    ],
)
def test_pdf_rejects_private_content_and_active_features(inputs, tmp_path, fault):
    options = {}
    if fault == "email":
        options["text"] = "Private synthetic@example.org"
    elif fault == "private_link":
        options["text"] = "https://docs.google.com/document/d/private"
    elif fault == "metadata":
        options["metadata"] = "/Users/synthetic/private-book"
    elif fault == "annotation":
        options["annotation"] = "private@example.org"
    elif fault.startswith("uri_"):
        options["uri"] = {
            "uri_private": "https://coda.io/private",
            "uri_local": "https://127.0.0.1/private",
            "uri_credential": "https://example.org/?token=secret",
            "uri_http": "http://example.org",
        }[fault]
    elif fault == "javascript":
        options["catalog_extra"] = (
            "/Names << /JavaScript << /Names [(script) << /S /JavaScript /JS (alert) >>] >> >>"
        )
    elif fault == "open_action":
        options["catalog_extra"] = "/OpenAction << /S /JavaScript /JS (alert) >>"
    elif fault == "additional_action":
        options["catalog_extra"] = "/AA << /WC << /S /JavaScript /JS (alert) >> >>"
    elif fault == "embedded_file":
        options["catalog_extra"] = (
            "/Names << /EmbeddedFiles << /Names [(private.txt) << /Type /Filespec /F (private.txt) /EF << /F 5 0 R >> >>] >> >>"
        )
    elif fault == "launch":
        options["action"] = "<< /S /Launch /F (private.txt) >>"
    elif fault == "remote_goto":
        options["action"] = "<< /S /GoToR /F (private.pdf) /D [0 /Fit] >>"
    elif fault == "xmp":
        options["xmp"] = '<?xml version="1.0"?><metadata>private@example.org</metadata>'
    raw = pdf_fixture(**options)
    if fault == "fake_header_eof":
        raw = b"%PDF-1.7\nThis is not a real PDF.\n%%EOF\n"
    elif fault == "encrypted":
        import io

        from pypdf import PdfWriter

        writer = PdfWriter(clone_from=io.BytesIO(raw))
        writer.encrypt("synthetic-password")
        target = io.BytesIO()
        writer.write(target)
        raw = target.getvalue()
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "book.pdf").write_bytes(raw)
    with pytest.raises(PublicationError):
        write_artifact_index(inputs[0], artifacts)
    assert not (artifacts / "artifact_index.json").exists()


@pytest.mark.parametrize("view", ["[3 0 R /Fit]", "[3 0 R /FitB]"])
def test_pdf_initial_view_is_bounded_internal_destination(inputs, tmp_path, view):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "book.pdf").write_bytes(pdf_fixture(catalog_extra="/OpenAction " + view))
    write_artifact_index(inputs[0], artifacts)
    stage(inputs, tmp_path / "public", artifacts_dir=artifacts)
    assert verify_public_tree(tmp_path / "public") == inputs[0]


@pytest.mark.parametrize(
    "view",
    [
        "<< /S /JavaScript /JS (alert) >>",
        "<< /S /URI /URI (https://example.org/) >>",
        "[4 0 R /Fit]",
        "[3 0 R /Fit 99]",
        "[3 0 R /Launch]",
        "[0 /Fit]",
    ],
)
def test_pdf_initial_view_rejects_actions_or_nonpage_destinations(inputs, tmp_path, view):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "book.pdf").write_bytes(pdf_fixture(catalog_extra="/OpenAction " + view))
    with pytest.raises(PublicationError):
        write_artifact_index(inputs[0], artifacts)
