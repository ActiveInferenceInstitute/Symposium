"""Fetch approved public portraits and remove embedded image metadata."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from PIL import Image, ImageOps

from .models import PublicationError, PublicBundle, validate_bundle

ALLOWED_MEDIA_HOSTS = {"codahosted.io", "cdn.coda.io"}
MAX_MEDIA_BYTES = 16 * 1024 * 1024


class _PublicRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_MEDIA_HOSTS:
            raise PublicationError("Public portrait redirect is outside the approved CDN")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sanitize_portrait(payload: bytes) -> bytes:
    """Re-encode a bounded real image, excluding EXIF, text, and original filenames."""
    if len(payload) > MAX_MEDIA_BYTES:
        raise PublicationError("Portrait exceeds the byte limit")
    with Image.open(io.BytesIO(payload)) as source:
        if source.width * source.height > 40000000 or source.format not in {"JPEG", "PNG", "WEBP"}:
            raise PublicationError("Portrait is not an allowed bounded image")
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((1200, 1200))
        encoded = io.BytesIO()
        image.save(encoded, format="JPEG", quality=90, optimize=True)
    return encoded.getvalue()


def attach_public_portraits(
    bundle: PublicBundle, ledger: dict[str, Any], output_dir: Path, *, public_document: str
) -> tuple[PublicBundle, dict[str, Any]]:
    """Only fetch portrait cells from the already-public program document.

    Failures remain explicit in the private ledger. They never justify copying
    private blob URLs or unprocessed metadata into the public output.
    """
    public = validate_bundle(bundle)
    output_dir = Path(output_dir)
    if output_dir.exists() or output_dir.is_symlink():
        raise PublicationError("Portrait output must be a fresh directory")
    output_dir.mkdir(parents=True)
    opener = build_opener(_PublicRedirect())
    for talk in public["presentations"]:
        urls = ledger.get("media", {}).get(talk["id"], [])
        for index, url in enumerate(urls):
            try:
                parts = urlsplit(url)
                if (
                    parts.scheme != "https"
                    or parts.hostname != "codahosted.io"
                    or parts.username
                    or parts.password
                    or not parts.path.startswith(f"/docs/{public_document}/blobs/")
                ):
                    raise PublicationError("Portrait is not bound to the approved public document")
                with opener.open(
                    Request(url, headers={"User-Agent": "Symposium-public-portrait-export"}),
                    timeout=30,
                ) as response:
                    payload = response.read(MAX_MEDIA_BYTES + 1)
                content = sanitize_portrait(payload)
                digest = hashlib.sha256(content).hexdigest()
                relative = f"assets/portraits/{digest}.jpg"
                path = output_dir / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    if path.read_bytes() != content:
                        raise PublicationError("Portrait digest collision")
                else:
                    with path.open("xb") as stream:
                        stream.write(content)
                talk["pictures"].append(
                    {
                        "path": relative,
                        "sha256": digest,
                        "alt": talk["presenter"] + " — submitted presenter image",
                    }
                )
            except Exception as exc:
                ledger.setdefault("warnings", []).append(
                    {
                        "kind": "portrait",
                        "public_id": talk["id"],
                        "attachment_index": index,
                        "reason": type(exc).__name__,
                        "source_url_sha256": hashlib.sha256(url.encode()).hexdigest(),
                    }
                )
    result = validate_bundle(public)
    from .models import content_hash

    ledger["public_sha256"] = content_hash(result)
    ledger["portrait_count"] = sum(len(talk["pictures"]) for talk in result["presentations"])
    return result, ledger
