"""Private operator transport and optimistic, append-only integration receipts.

Transport credentials and raw source snapshots never belong in the public repository.
Receipt application is read-before-write, not a server-side atomic compare-and-swap.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .models import PublicationError, canonical_bytes, content_hash

MAX_BYTES = 16 * 1024 * 1024
FIELDS = {
    "presentations": {"presenter", "title", "abstract", "contribution_type", "pictures"},
    "participants": {
        "share_publicly",
        "name",
        "affiliations",
        "orcid",
        "background",
        "pragmatic_value",
        "epistemic_value",
        "active_inference_application",
        "challenges",
        "learning_needs",
        "future_impact",
    },
    "sessions": {"title", "start_utc", "end_utc", "presenter", "kind"},
}
URI = re.compile(r"superhuman://docs/([A-Za-z0-9_-]+)/tables/([A-Za-z0-9_-]+)")
PAGE_URI = re.compile(r"superhuman://docs/[A-Za-z0-9_-]+/pages/[A-Za-z0-9_-]+")


class Transport(Protocol):
    def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


def _checked(result: object) -> dict[str, Any]:
    if (
        not isinstance(result, dict)
        or result.get("isError")
        or result.get("error")
        or result.get("success") is False
    ):
        raise PublicationError("Transport returned an unsuccessful response")
    if len(canonical_bytes(result)) > MAX_BYTES:
        raise PublicationError("Transport response exceeds the size limit")
    return result


class InstituteOSTransport:
    """Invoke the installed InstituteOS SDK without adding it as a dependency."""

    def __init__(self, root: Path, timeout: float = 90):
        self.root = root.resolve()
        self.timeout = timeout
        if not 0 < timeout <= 300:
            raise PublicationError("Transport timeout must be within 300 seconds")

    def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in {"table_columns_read", "table_rows_read", "content_read", "content_modify"}:
            raise PublicationError("Tool is outside the bridge allowlist")
        payload = canonical_bytes({"name": name, "arguments": arguments})
        if len(payload) > MAX_BYTES:
            raise PublicationError("Transport request exceeds the size limit")
        volume = next((p for p in self.root.parents if p.name == "GitVault" and p.is_mount()), None)
        interpreter = self.root / ".venv/bin/python"
        if (
            volume is None
            or not interpreter.is_file()
            or not (self.root / "src/instituteos/_superhuman.py").is_file()
        ):
            raise PublicationError("InstituteOS root or external interpreter is unavailable")
        if not os.environ.get("SUPERHUMAN_DOCS_MCP_TOKEN", "").strip():
            raise PublicationError("SUPERHUMAN_DOCS_MCP_TOKEN is required")
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        env.update(
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONPATH=str(self.root / "src"),
            BRIDGE_VOLUME=str(volume),
        )
        for key in ("TMPDIR", "UV_CACHE_DIR"):
            if not env.get(key) or not Path(env[key]).resolve().is_relative_to(volume):
                raise PublicationError(
                    "Transport requires external temporary and cache directories"
                )
        script = """import asyncio,json,os,sys,contextlib
from pathlib import Path
volume=Path(os.environ["BRIDGE_VOLUME"])
if not all(Path(p).resolve().is_relative_to(volume) for p in (sys.prefix,sys.base_prefix)):
    sys.exit(20)
try:
    request=json.loads(sys.stdin.buffer.read(16777217))
    with open(os.devnull,"w") as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        from instituteos._superhuman import call_tool
        result=asyncio.run(call_tool(os.environ["SUPERHUMAN_DOCS_MCP_TOKEN"],request["name"],request["arguments"]))
    encoded=json.dumps(result,allow_nan=False).encode()
    if len(encoded)>16777216: sys.exit(21)
    sys.stdout.buffer.write(encoded)
except Exception:
    sys.exit(22)
"""
        try:
            run = subprocess.run(
                [str(interpreter), "-B", "-c", script],
                input=payload,
                capture_output=True,
                cwd=self.root,
                env=env,
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise PublicationError(
                "InstituteOS transport failed or timed out; outcome may be unknown"
            ) from None
        if run.returncode:
            raise PublicationError("InstituteOS transport failed; outcome may be unknown")
        try:
            return _checked(json.loads(run.stdout))
        except (ValueError, UnicodeError):
            raise PublicationError("InstituteOS transport returned an invalid response") from None


def validate_mapping(config: object) -> dict[str, Any]:
    if (
        not isinstance(config, dict)
        or set(config) != {"schema_version", "organizer_document", "public_document", "sources"}
        or type(config["schema_version"]) is not int
        or config["schema_version"] != 1
    ):
        raise PublicationError("Invalid bridge mapping schema")
    for key in ("organizer_document", "public_document"):
        if not isinstance(config[key], str) or not re.fullmatch(r"[A-Za-z0-9_-]+", config[key]):
            raise PublicationError("Invalid document identifier")
    if config["organizer_document"] == config["public_document"]:
        raise PublicationError("Organizer and public documents must be distinct")
    sources = config["sources"]
    if not isinstance(sources, dict) or set(sources) != set(FIELDS):
        raise PublicationError("All three source mappings are required")
    uris = set()
    for kind, fields in FIELDS.items():
        source = sources[kind]
        if not isinstance(source, dict) or set(source) != {"uri", "fields"}:
            raise PublicationError("Unexpected source mapping fields")
        match = URI.fullmatch(source["uri"]) if isinstance(source["uri"], str) else None
        expected = config["organizer_document" if kind == "participants" else "public_document"]
        if not match or match[1] != expected or source["uri"] in uris:
            raise PublicationError("Source violates document separation")
        uris.add(source["uri"])
        mapping = source["fields"]
        if (
            not isinstance(mapping, dict)
            or set(mapping) != fields
            or any(
                not isinstance(v, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", v)
                for v in mapping.values()
            )
            or len(set(mapping.values())) != len(fields)
        ):
            raise PublicationError("Source field mapping must be complete, unique, and allowlisted")
    return json.loads(canonical_bytes(config))


def pull_snapshot(
    config: dict[str, Any], transport: Transport, *, public_root: Path, workspace: Path
) -> dict[str, Any]:
    config = validate_mapping(config)
    workspace = workspace.resolve()
    if workspace.is_relative_to(public_root.resolve()):
        raise PublicationError("Private workspace cannot be inside the public repository")
    snapshot: dict[str, Any] = {
        "schema_version": 1,
        "mapping": config,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "tables": {},
    }
    for kind, source in config["sources"].items():
        schema = _checked(transport.invoke("table_columns_read", {"uri": source["uri"]}))
        columns = schema.get("columns")
        if not isinstance(columns, list) or any(
            not isinstance(c, dict) or not isinstance(c.get("columnId"), str) for c in columns
        ):
            raise PublicationError("Invalid source column schema")
        ids = [c["columnId"] for c in columns]
        selected = list(source["fields"].values())
        if len(set(ids)) != len(ids) or not set(selected).issubset(ids):
            raise PublicationError("Source columns are missing or ambiguous")
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        total = None
        for _ in range(1000):
            result = _checked(
                transport.invoke(
                    "table_rows_read",
                    {
                        "uri": source["uri"],
                        "columnsToInclude": selected,
                        "rowLimit": 100,
                        "rowOffset": len(rows),
                    },
                )
            )
            batch, count, more = result.get("rows"), result.get("totalRows"), result.get("hasMore")
            if (
                not isinstance(batch, list)
                or type(count) is not int
                or count < 0
                or type(more) is not bool
                or len(batch) > 100
                or (total is not None and count != total)
            ):
                raise PublicationError("Invalid or inconsistent source pagination")
            total = count
            for row in batch:
                if (
                    not isinstance(row, dict)
                    or not isinstance(row.get("rowId"), str)
                    or not row["rowId"]
                    or row["rowId"] in seen
                    or not isinstance(row.get("values"), dict)
                    or set(row["values"]) != set(selected)
                ):
                    raise PublicationError("Source row identity or projection is incomplete")
                if any(not isinstance(v, dict) or "value" not in v for v in row["values"].values()):
                    raise PublicationError("Source cell is missing its value")
                seen.add(row["rowId"])
                rows.append(row)
            if len(rows) > total or more != (len(rows) < total) or (more and not batch):
                raise PublicationError("Source pagination is truncated or inconsistent")
            if not more:
                break
        else:
            raise PublicationError("Source pagination exceeds the safety bound")
        snapshot["tables"][kind] = {"schema": schema, "rows": rows, "totalRows": total}
    encoded = canonical_bytes(snapshot)
    if len(encoded) > MAX_BYTES:
        raise PublicationError("Snapshot exceeds the size limit")
    workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = workspace / ("snapshot-" + uuid.uuid4().hex + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(encoded)
    return snapshot


def canonical_content(text: str) -> str:
    """Ignore transport block wrappers and blank layout lines, preserving prose."""
    text = re.sub(r'</?block(?:\s+id="[^"]*")?\s*>', "", text)
    # Docs turns bare HTTPS URLs into links with the exact same displayed URL.
    # A backreference deliberately preserves every differing label or destination.
    text = re.sub(r"(?<![!\\])\[(https://[^\s\[\]()]+)\]\(\1\)", r"\1", text)
    return "\n".join(line.rstrip() for line in text.splitlines() if line.strip()).strip()


def prepare_receipt(
    page_uri: str, baseline_content: str, receipt_markdown: str, public_manifest_hash: str
) -> dict[str, Any]:
    if not isinstance(page_uri, str) or not PAGE_URI.fullmatch(page_uri):
        raise PublicationError("Receipt target must be a dedicated integration page URI")
    if (
        not isinstance(baseline_content, str)
        or not isinstance(receipt_markdown, str)
        or not receipt_markdown.strip()
        or len(baseline_content.encode()) > MAX_BYTES
        or len(receipt_markdown.encode()) > 100000
    ):
        raise PublicationError("Receipt and baseline must be bounded text")
    if not isinstance(public_manifest_hash, str) or not re.fullmatch(
        r"[a-f0-9]{64}", public_manifest_hash
    ):
        raise PublicationError("Receipt requires a public manifest SHA-256")
    if "Symposium synchronization receipt:" in receipt_markdown or re.search(
        r"</?block\b", receipt_markdown
    ):
        raise PublicationError("Receipt contains reserved markers or wrappers")
    body = canonical_content(receipt_markdown)
    receipt_id = content_hash(
        {"receipt_markdown": body, "public_manifest_hash": public_manifest_hash}
    )
    return {
        "schema_version": 1,
        "target_page_uri": page_uri,
        "expected_sha256": content_hash(canonical_content(baseline_content)),
        "receipt_markdown": body,
        "public_manifest_hash": public_manifest_hash,
        "receipt_id": receipt_id,
        "marker": "Symposium synchronization receipt: " + receipt_id,
    }


def read_page_content(transport: Transport, page_uri: str) -> str:
    """Verify server windows, probing every slot when blank slots lack wrappers."""
    if not PAGE_URI.fullmatch(page_uri):
        raise PublicationError("Invalid integration page URI")
    chunks: list[str] = []
    offset = 0
    total: int | None = None
    size = 0
    calls = 0
    seen: set[str] = set()
    wrapper = re.compile(r'<block\s+id="([^"]*)"\s*>(.*?)</block\s*>', re.S)

    def read_window(start: int, limit: int) -> tuple[str, list[tuple[str, str]], int]:
        nonlocal total, size, calls
        if calls >= 1000:
            raise PublicationError("Integration-page read call budget exceeded")
        calls += 1
        result = _checked(
            transport.invoke(
                "content_read",
                {
                    "uri": page_uri,
                    "contentTypesToInclude": ["markdown"],
                    "markdownBlockLimit": limit,
                    "markdownBlockOffset": start,
                },
            )
        )
        content, count, more = (
            result.get("content"),
            result.get("totalBlocks"),
            result.get("hasMore"),
        )
        if (
            not isinstance(content, str)
            or type(count) is not int
            or count < 0
            or type(more) is not bool
            or (total is not None and count != total)
        ):
            raise PublicationError("Invalid integration-page pagination")
        total = count
        if start > count:
            raise PublicationError("Integration-page window exceeds total blocks")
        span = min(limit, count - start)
        if more != (start + span < count):
            raise PublicationError("Integration-page pagination is truncated or inconsistent")
        size += len(content.encode())
        if size > MAX_BYTES:
            raise PublicationError("Integration-page reads exceed the byte limit")
        records = wrapper.findall(content)
        if len(records) > span or wrapper.sub("", content).strip():
            raise PublicationError("Integration-page block coverage is incomplete")
        return content, records, span

    while True:
        content, records, span = read_window(offset, 100)
        if len(records) < span:
            # Docs counts blank canvas slots in totalBlocks but emits no wrapper.
            # Reconcile all singleton slots against the bulk response so omitted
            # nonempty blocks cannot be mistaken for those explicit empty slots.
            verified: list[tuple[str, str]] = []
            for slot in range(offset, offset + span):
                _, singleton, _ = read_window(slot, 1)
                verified.extend(singleton)
            if records != verified:
                raise PublicationError("Integration-page bulk response omitted or changed blocks")
        for identifier, _ in records:
            if identifier:
                if identifier in seen:
                    raise PublicationError("Integration-page contains duplicate block identifiers")
                seen.add(identifier)
        chunks.append(content)
        offset += span
        if offset == total:
            return "\n\n".join(chunks)


def apply_receipt(
    plan: dict[str, Any], transport: Transport, *, apply: bool = False
) -> dict[str, Any]:
    """Append once after optimistic conflict checking; never retry unknown outcomes."""
    if apply is not True:
        raise PublicationError("Receipt mutation requires explicit apply")
    fields = {
        "schema_version",
        "target_page_uri",
        "expected_sha256",
        "receipt_markdown",
        "public_manifest_hash",
        "receipt_id",
        "marker",
    }
    if (
        not isinstance(plan, dict)
        or set(plan) != fields
        or type(plan["schema_version"]) is not int
        or plan["schema_version"] != 1
    ):
        raise PublicationError("Invalid receipt plan")
    rebuilt = prepare_receipt(
        plan["target_page_uri"], "", plan["receipt_markdown"], plan["public_manifest_hash"]
    )
    if (
        any(rebuilt[key] != plan[key] for key in fields - {"expected_sha256"})
        or not isinstance(plan["expected_sha256"], str)
        or not re.fullmatch(r"[a-f0-9]{64}", plan["expected_sha256"])
    ):
        raise PublicationError("Receipt plan integrity check failed")
    before = canonical_content(read_page_content(transport, plan["target_page_uri"]))
    addition = canonical_content(plan["marker"] + "\n\n" + plan["receipt_markdown"])
    if plan["marker"] in before:
        if before.count(plan["marker"]) != 1 or not re.search(
            re.escape(addition) + r"(?:\n|$)", before
        ):
            raise PublicationError("Existing receipt marker has conflicting content")
        return {
            "status": "noop",
            "receipt_id": plan["receipt_id"],
            "readback_verified": True,
            "content_sha256": content_hash(before),
        }
    if content_hash(before) != plan["expected_sha256"]:
        raise PublicationError("Integration page changed since preparation; no receipt appended")
    _checked(
        transport.invoke(
            "content_modify",
            {
                "uri": plan["target_page_uri"],
                "operations": [
                    {
                        "operation": "insert_element",
                        "blockType": "markdown",
                        "content": plan["marker"] + "\n\n" + plan["receipt_markdown"],
                    }
                ],
            },
        )
    )
    after = canonical_content(read_page_content(transport, plan["target_page_uri"]))
    expected = canonical_content(before + "\n\n" + addition)
    if after != expected or after.count(plan["marker"]) != 1:
        raise PublicationError("Receipt readback verification failed; do not blindly retry")
    return {
        "status": "applied",
        "receipt_id": plan["receipt_id"],
        "readback_verified": True,
        "content_sha256": content_hash(after),
    }
