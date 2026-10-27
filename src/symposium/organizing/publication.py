"""Consent-bound, allowlisted publication staging and standalone public resources."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from icalendar import Calendar, Event
from PIL import Image

from .models import (
    EMAIL,
    PRIVATE_LINK,
    PublicationError,
    PublicBundle,
    canonical_bytes,
    content_hash,
    public_url,
    validate_bundle,
)
from .projection import project_snapshot

BASIS = "published-program-and-affirmative-registration-consent"
MAX_FILE_BYTES = 64 * 1024 * 1024


def _utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise PublicationError("Expected explicit UTC timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise PublicationError("Expected explicit UTC timestamp")
    return parsed


def write_calendar(bundle: PublicBundle, path: Path, *, generated_at: str | None = None) -> Path:
    bundle = validate_bundle(bundle)
    stamp = _utc(generated_at) if generated_at else datetime.now(timezone.utc)
    calendar = Calendar()
    calendar.add("prodid", "-//Active Inference Institute//Public Symposium//EN")
    calendar.add("version", "2.0")
    for session in bundle["sessions"]:
        event = Event()
        event.add("uid", bundle["event"]["id"] + "-" + session["id"])
        event.add("dtstamp", stamp)
        event.add("dtstart", _utc(session["start_utc"]))
        event.add("dtend", _utc(session["end_utc"]))
        event.add("summary", session["title"] or "Session title not yet published")
        event.add("description", "Presenter: " + (session["presenter"] or "Not yet published"))
        calendar.add_component(event)
    with Path(path).open("xb") as stream:
        stream.write(calendar.to_ical())
    return Path(path)


def _literal(value: str) -> str:
    return "\n".join(
        "".join(c if c.isalnum() or c == " " else f"&#{ord(c)};" for c in line).replace(
            "    ", "&#32;&#32;&#32;&#32;"
        )
        for line in value.split("\n")
    )


def write_participant_briefs(bundle: PublicBundle, output_dir: Path) -> list[Path]:
    bundle = validate_bundle(bundle)
    output_dir = Path(output_dir)
    contents = {}
    for person in bundle["participants"]:
        lines = [
            "# " + _literal(person["name"]),
            "",
            "These are self-reported registration answers, not an assessment or a verified identity.",
            "",
        ]
        for key in ("background", "active_inference_application", "learning_needs"):
            lines.extend(
                [
                    "## " + key.replace("_", " ").title(),
                    "",
                    _literal(person[key]) or "No answer provided.",
                    "",
                ]
            )
        lines.extend(
            [
                "## Provided resources",
                "",
                "Starting points supplied by the organizers; relevance and suitability have not been assessed.",
                "",
            ]
        )
        for resource in bundle["resources"]:
            lines.extend(
                [
                    _literal(resource["title"]),
                    "",
                    _literal(resource["description"]),
                    "",
                    _literal(resource["url"]),
                    "",
                ]
            )
        contents[person["id"] + ".md"] = "\n".join(lines).encode()
    _new_directory(output_dir, contents)
    return [output_dir / name for name in contents]


def _no_symlinks(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise PublicationError("Symbolic links are not permitted")


def _read(path: Path) -> bytes:
    _no_symlinks(path)
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise PublicationError("Missing, nonregular, or oversized public file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise PublicationError("Oversized public file")
    return raw


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _allowed_artifacts(bundle: PublicBundle) -> set[str]:
    return (
        {"book.pdf", "book.docx", "program.ics"}
        | {f"dossiers/{p['id']}.md" for p in bundle["presentations"]}
        | {f"participants/{p['id']}.md" for p in bundle["participants"]}
    )


def _scan_text(raw: bytes) -> None:
    import html

    try:
        text = html.unescape(raw.decode("utf-8"))
    except UnicodeError as exc:
        raise PublicationError("Public text must be UTF-8") from exc
    if EMAIL.search(text) or PRIVATE_LINK.search(text) or "/Users/" in text or "/Volumes/" in text:
        raise PublicationError("Private contact, document link, or local path in public artifact")


def _check_pdf(raw: bytes) -> None:
    """Inspect parsed text and objects; this does not replace native visual/OCR review."""
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError
    from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, StreamObject

    if len(raw) > MAX_FILE_BYTES:
        raise PublicationError("Oversized PDF document")
    forbidden = {"/JS", "/JavaScript", "/AA", "/EmbeddedFiles", "/EF", "/XFA"}
    unsafe_types = {"/EmbeddedFile", "/Filespec"}
    unsafe_annotations = {"/FileAttachment", "/RichMedia", "/Movie", "/Sound", "/3D", "/Screen"}
    try:
        reader = PdfReader(io.BytesIO(raw), strict=True)
        if reader.is_encrypted:
            raise PublicationError("Encrypted public PDF is not permitted")
        if not 0 < len(reader.pages) <= 1000:
            raise PublicationError("PDF page count exceeds its bound")
        page_ids = {
            (p.indirect_reference.idnum, p.indirect_reference.generation) for p in reader.pages
        }
        pending = [(reader.trailer, 0, False)]
        seen: set[tuple[int, int]] = set()
        visits = 0
        decoded_bytes = 0
        while pending:
            node, depth, action = pending.pop()
            visits += 1
            if visits > 100000 or depth > 128:
                raise PublicationError("PDF object graph exceeds its bound")
            if isinstance(node, IndirectObject):
                identity = (node.idnum, node.generation)
                resolved = node.get_object()
                if action:
                    if not isinstance(resolved, DictionaryObject) or resolved.get("/S") not in {
                        "/URI",
                        "/GoTo",
                    }:
                        raise PublicationError("Unsafe PDF action")
                if identity in seen:
                    continue
                seen.add(identity)
                node = resolved
            if isinstance(node, DictionaryObject):
                if action and node.get("/S") not in {"/URI", "/GoTo"}:
                    raise PublicationError("Unsafe PDF action")
                if (
                    forbidden.intersection(node)
                    or node.get("/Type") in unsafe_types
                    or node.get("/Subtype") in unsafe_annotations
                ):
                    raise PublicationError("Active content or attachments in public PDF")
                if node.get("/Type") == "/Action" and node.get("/S") not in {"/URI", "/GoTo"}:
                    raise PublicationError("Unsafe PDF action")
                if "/OpenAction" in node:
                    destination = node["/OpenAction"]
                    if (
                        not isinstance(destination, ArrayObject)
                        or len(destination) != 2
                        or not isinstance(destination[0], IndirectObject)
                        or (destination[0].idnum, destination[0].generation) not in page_ids
                        or destination[1] not in {"/Fit", "/FitB"}
                    ):
                        raise PublicationError("PDF initial view must target an internal page")
                if "/URI" in node:
                    destination = node["/URI"]
                    if isinstance(destination, DictionaryObject):
                        if set(destination) != {"/Base"}:
                            raise PublicationError("Unexpected PDF URI configuration")
                        destination = destination["/Base"]
                    public_url(destination, "PDF destination")
                if node.get("/S") == "/URI" and "/URI" not in node:
                    raise PublicationError("PDF URI action has no destination")
                if isinstance(node, StreamObject) and node.get("/Type") == "/Metadata":
                    data = node.get_data()
                    decoded_bytes += len(data)
                    if decoded_bytes > MAX_FILE_BYTES:
                        raise PublicationError("Decoded PDF data exceeds its bound")
                    _scan_text(data)
                pending.extend(
                    (
                        value,
                        depth + 1,
                        key == "/A"
                        or (key == "/Next" and (action or node.get("/Type") == "/Action")),
                    )
                    for key, value in node.items()
                )
            elif isinstance(node, ArrayObject):
                pending.extend((value, depth + 1, action) for value in node)
            elif action:
                raise PublicationError("Malformed PDF action")
            elif isinstance(node, str):
                _scan_text(node.encode("utf-8"))
        for page in reader.pages:
            contents = page.get_contents()
            if contents is not None:
                decoded_bytes += len(contents.get_data())
                if decoded_bytes > MAX_FILE_BYTES:
                    raise PublicationError("Decoded PDF data exceeds its bound")
            text = page.extract_text()
            if not isinstance(text, str):
                raise PublicationError("PDF text extraction failed")
            _scan_text(text.encode("utf-8"))
    except PublicationError:
        raise
    except (PyPdfError, ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        raise PublicationError("Invalid or unsupported public PDF document") from exc


def _check_artifact(name: str, raw: bytes) -> None:
    if name.endswith((".md", ".ics")):
        _scan_text(raw)
    if name.endswith(".ics"):
        calendar = Calendar.from_ical(raw)
        if any(
            "ATTENDEE" in component or "ORGANIZER" in component or "METHOD" in component
            for component in calendar.walk()
        ):
            raise PublicationError("Public calendars must not contain invitations")
    if name.endswith(".docx"):
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if "word/document.xml" not in archive.namelist() or archive.testzip():
                    raise PublicationError("Invalid Word document")
                for entry in archive.infolist():
                    if entry.file_size > MAX_FILE_BYTES:
                        raise PublicationError("Oversized Word member")
                    if entry.filename.endswith((".xml", ".rels")):
                        _scan_text(archive.read(entry))
        except zipfile.BadZipFile as exc:
            raise PublicationError("Invalid Word document") from exc
    if name.endswith(".pdf"):
        _check_pdf(raw)


def write_artifact_index(bundle: PublicBundle, artifacts_dir: Path) -> Path:
    bundle = validate_bundle(bundle)
    root = Path(artifacts_dir)
    _no_symlinks(root)
    files = {}
    for name in sorted(_allowed_artifacts(bundle)):
        path = root / name
        if path.exists() or path.is_symlink():
            raw = _read(path)
            _check_artifact(name, raw)
            files[name] = _digest(raw)
    result = root / "artifact_index.json"
    with result.open("xb") as stream:
        stream.write(
            canonical_bytes(
                {"schema_version": 1, "bundle_sha256": content_hash(bundle), "files": files}
            )
        )
    return result


def _new_directory(target: Path, contents: dict[str, bytes]) -> None:
    from symposium.core.edition import _publish_directory

    _no_symlinks(target)
    if target.exists():
        raise FileExistsError(target)
    if not target.parent.is_dir():
        raise PublicationError("Publication parent must already exist")
    stage = Path(tempfile.mkdtemp(prefix="." + target.name + "-", dir=target.parent))
    for name, raw in contents.items():
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
    _publish_directory(stage, target)


def _picture(raw: bytes) -> None:
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.format not in {"PNG", "JPEG"} or image.width * image.height > 20_000_000:
                raise PublicationError("Unsupported or oversized portrait")
            image.load()
            if image.getexif() or set(image.info) - {
                "jfif",
                "jfif_version",
                "jfif_unit",
                "jfif_density",
            }:
                raise PublicationError("Portrait metadata must be stripped")
    except (OSError, Image.DecompressionBombError) as exc:
        raise PublicationError("Invalid portrait") from exc


def stage_public(
    bundle: PublicBundle,
    snapshot: dict[str, Any],
    ledger: dict[str, Any],
    output_dir: Path,
    *,
    assets_dir: Path | None = None,
    artifacts_dir: Path | None = None,
    apply: bool = False,
    max_age_seconds: int = 3600,
    as_of: str | None = None,
) -> Path:
    if not apply:
        raise PublicationError("Explicit apply is required")
    bundle = validate_bundle(bundle)
    if type(max_age_seconds) is not int or not 0 < max_age_seconds <= 86400:
        raise PublicationError("Snapshot age limit must be positive and at most one day")
    observed = _utc(snapshot.get("observed_at"))
    now = _utc(as_of) if as_of else datetime.now(timezone.utc)
    age = (now - observed).total_seconds()
    if age > max_age_seconds or age < -300:
        raise PublicationError("Source snapshot is stale or future dated")
    if ledger.get("snapshot_sha256") != content_hash(snapshot) or ledger.get(
        "public_sha256"
    ) != content_hash(bundle):
        raise PublicationError("Snapshot or public bundle digest mismatch")
    expected, expected_ledger = project_snapshot(snapshot, bundle["event"], bundle["resources"])
    plain = copy.deepcopy(bundle)
    for talk in plain["presentations"]:
        talk["pictures"] = []
    if plain != expected:
        raise PublicationError("Public text or roster differs from current source projection")
    for key in ("schema_version", "included", "excluded", "media"):
        if ledger.get(key) != expected_ledger[key]:
            raise PublicationError("Private approval ledger differs from current source projection")
    warnings = ledger.get("warnings")
    original_warnings = expected_ledger["warnings"]
    if not isinstance(warnings, list) or warnings[: len(original_warnings)] != original_warnings:
        raise PublicationError("Original projection warnings must remain intact")
    omissions: set[tuple[str, int]] = set()
    reasons = {
        "PublicationError",
        "HTTPError",
        "URLError",
        "TimeoutError",
        "UnidentifiedImageError",
        "OSError",
        "ValueError",
    }
    for warning in warnings[len(original_warnings) :]:
        if not isinstance(warning, dict) or set(warning) != {
            "kind",
            "public_id",
            "attachment_index",
            "reason",
            "source_url_sha256",
        }:
            raise PublicationError("Unrecognized media omission receipt")
        talk_id, index = warning["public_id"], warning["attachment_index"]
        if not isinstance(talk_id, str) or type(index) is not int:
            raise PublicationError("Invalid media omission identity")
        urls = expected_ledger["media"].get(talk_id, [])
        if (
            warning["kind"] != "portrait"
            or warning["reason"] not in reasons
            or not 0 <= index < len(urls)
        ):
            raise PublicationError("Unrecognized media omission reason or attachment")
        if (
            warning["source_url_sha256"] != _digest(urls[index].encode("utf-8"))
            or (talk_id, index) in omissions
        ):
            raise PublicationError("Media omission URL binding mismatch or duplicate")
        omissions.add((talk_id, index))
    if "portrait_count" in ledger and (
        type(ledger["portrait_count"]) is not int
        or ledger["portrait_count"] != sum(len(t["pictures"]) for t in bundle["presentations"])
    ):
        raise PublicationError("Portrait receipt count mismatch")
    contents = {"program.json": canonical_bytes(bundle)}
    prefix = "https://codahosted.io/docs/" + snapshot["mapping"]["public_document"] + "/blobs/"
    for talk in bundle["presentations"]:
        urls = [
            url
            for index, url in enumerate(ledger["media"].get(talk["id"], []))
            if (talk["id"], index) not in omissions
        ]
        if len(talk["pictures"]) != len(urls):
            raise PublicationError("Portrait count differs from published media")
        for picture, url in zip(talk["pictures"], urls):
            if not isinstance(url, str) or not url.startswith(prefix):
                raise PublicationError("Portrait does not originate in the public program")
            if assets_dir is None:
                raise PublicationError("Portrait source directory is required")
            raw = _read(Path(assets_dir) / picture["path"])
            if _digest(raw) != picture["sha256"]:
                raise PublicationError("Portrait digest mismatch")
            _picture(raw)
            contents[picture["path"]] = raw
    if artifacts_dir is not None:
        root = Path(artifacts_dir)
        index = json.loads(_read(root / "artifact_index.json"))
        if (
            not isinstance(index, dict)
            or set(index) != {"schema_version", "bundle_sha256", "files"}
            or type(index["schema_version"]) is not int
            or index["schema_version"] != 1
            or index["bundle_sha256"] != content_hash(bundle)
            or not isinstance(index["files"], dict)
        ):
            raise PublicationError("Artifact index is not bound to this bundle")
        if not set(index["files"]) <= _allowed_artifacts(bundle):
            raise PublicationError("Artifact index contains a forbidden filename")
        for name, digest in index["files"].items():
            raw = _read(root / name)
            if _digest(raw) != digest:
                raise PublicationError("Artifact digest mismatch")
            _check_artifact(name, raw)
            contents[name] = raw
    manifest = {
        "schema_version": 1,
        "bundle_sha256": content_hash(bundle),
        "approval_basis": BASIS,
        "files": {name: _digest(raw) for name, raw in sorted(contents.items())},
    }
    contents["publication.json"] = canonical_bytes(manifest)
    _new_directory(Path(output_dir), contents)
    return Path(output_dir) / "program.json"


def verify_public_tree(root: Path) -> PublicBundle:
    root = Path(root)
    _no_symlinks(root)
    bundle = validate_bundle(json.loads(_read(root / "program.json")))
    manifest = json.loads(_read(root / "publication.json"))
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"schema_version", "bundle_sha256", "approval_basis", "files"}
        or type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != 1
        or manifest["bundle_sha256"] != content_hash(bundle)
        or manifest["approval_basis"] != BASIS
        or not isinstance(manifest["files"], dict)
    ):
        raise PublicationError("Invalid public publication manifest")
    pictures = {
        p["path"]: p["sha256"] for talk in bundle["presentations"] for p in talk["pictures"]
    }
    required = {"program.json"} | set(pictures)
    allowed = required | _allowed_artifacts(bundle)
    names = set(manifest["files"])
    if not required <= names or not names <= allowed:
        raise PublicationError("Public manifest has missing or forbidden filenames")
    actual = set()
    allowed_dirs = {parent.as_posix() for name in names for parent in Path(name).parents} - {"."}
    for path in root.rglob("*"):
        _no_symlinks(path)
        name = path.relative_to(root).as_posix()
        if path.is_dir():
            if name not in allowed_dirs:
                raise PublicationError("Unmanifested public directory")
        elif path.is_file():
            actual.add(name)
        else:
            raise PublicationError("Nonregular public entry")
    if actual != names | {"publication.json"}:
        raise PublicationError("Unmanifested or missing public file")
    for name, digest in manifest["files"].items():
        raw = _read(root / name)
        if _digest(raw) != digest:
            raise PublicationError("Public file digest mismatch")
        if name in pictures:
            if digest != pictures[name]:
                raise PublicationError("Portrait manifest differs from bundle")
            _picture(raw)
        elif name != "program.json":
            _check_artifact(name, raw)
    return bundle
