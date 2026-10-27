"""Curated, offline integration methods and presence-only credential metadata.

Catalog validation establishes structure and pinned provenance, not current repository
availability, scientific suitability, authentication, or authorization.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from importlib.resources import files
from pathlib import Path
from typing import Final, Literal, TypedDict

from symposium.organizing.models import PublicationError


class Repository(TypedDict):
    id: str
    name: str
    repository_url: str
    role: Literal["code-integration", "manual-handoff", "resource"]
    summary: str
    use_for: str
    handoff: str
    evidence_url: str
    commit: str
    checked_on: str


class Workflow(TypedDict):
    id: str
    title: str
    summary: str
    commands: list[str]
    repository_ids: list[str]
    credential_ids: list[str]
    docs_url: str


class Catalog(TypedDict):
    schema_version: int
    reviewed_on: str
    repositories: list[Repository]
    workflows: list[Workflow]


class Credential(TypedDict):
    id: str
    environment_variable: str
    purpose: str
    status: Literal["not-checked", "configured", "missing"]


class CapabilityReport(TypedDict):
    schema_version: int
    environment_checked: bool
    assurance: str
    keyless: list[str]
    credentials: list[Credential]


_CREDENTIALS: Final = (
    ("openrouter", "OPENROUTER_API_KEY", "Optional paid OpenRouter analysis and generation"),
    ("perplexity", "PERPLEXITY_API_KEY", "Optional paid Perplexity analysis and generation"),
    (
        "instituteos-docs",
        "SUPERHUMAN_DOCS_MCP_TOKEN",
        "Private document bridge; requires separately installed InstituteOS SDK and a Docs token with MCP access enabled",
    ),
)
_MAX_BYTES: Final = 131072


def capability_report(check_env: bool = False) -> CapabilityReport:
    """Return metadata; opt-in presence reads never return credential values."""
    credentials: list[Credential] = []
    for identifier, variable, purpose in _CREDENTIALS:
        status: Literal["not-checked", "configured", "missing"] = "not-checked"
        if check_env:
            status = "configured" if os.environ.get(variable, "").strip() else "missing"
        credentials.append(
            Credential(id=identifier, environment_variable=variable, purpose=purpose, status=status)
        )
    return CapabilityReport(
        schema_version=1,
        environment_checked=check_env,
        assurance="Presence only; does not validate authentication, authorization, balance, or SDK availability. No .env loading or network calls. OpenAlex API keys are not consumed by these workflows.",
        keyless=[
            "Public snapshot projection",
            "Dossiers",
            "Calendar",
            "Static site",
            "Search",
            "Method catalog",
            "Native Template local renderer (separate installation required)",
        ],
        credentials=credentials,
    )


def _record(value: object, keys: set[str], location: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise PublicationError(f"Catalog {location}: unexpected or missing fields")
    return {key: value[key] for key in keys}


def _text(value: object, location: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 2000 or value != value.strip():
        raise PublicationError(f"Catalog {location}: expected bounded nonempty text")
    if any(ord(char) < 32 or ord(char) == 127 for char in value) or any(
        char in value for char in "<>`\\"
    ):
        raise PublicationError(f"Catalog {location}: unsupported text characters")
    if re.search(
        r"(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,}|Bearer\s|(?:token|password|secret|api_key)\s*=)",
        value,
        re.I,
    ):
        raise PublicationError(f"Catalog {location}: credential-like text forbidden")
    return value


def _identifier(value: object, location: str) -> str:
    text = _text(value, location)
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", text):
        raise PublicationError(f"Catalog {location}: invalid identifier")
    return text


def _date(value: object, location: str) -> str:
    text = _text(value, location)
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        raise PublicationError(f"Catalog {location}: invalid date") from None
    if parsed.isoformat() != text:
        raise PublicationError(f"Catalog {location}: expected YYYY-MM-DD")
    return text


def _url(value: object, location: str) -> str:
    text = _text(value, location)
    if not re.fullmatch(
        r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./-]+)?", text
    ) or any(segment in {".", ".."} for segment in text.split("/")):
        raise PublicationError(f"Catalog {location}: expected plain HTTPS GitHub URL")
    return text


def _list(value: object, location: str) -> list[object]:
    if not isinstance(value, list) or len(value) > 100:
        raise PublicationError(f"Catalog {location}: expected bounded list")
    return list(value)


def _unique(values: list[str], location: str) -> list[str]:
    if len(values) != len(set(values)):
        raise PublicationError(f"Catalog {location}: duplicate identifiers")
    return values


def validate_catalog(value: object) -> Catalog:
    """Parse an exact-schema JSON value into normalized catalog records."""
    root = _record(value, {"schema_version", "reviewed_on", "repositories", "workflows"}, "root")
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise PublicationError("Catalog schema_version: expected integer 1")
    reviewed_on = _date(root["reviewed_on"], "reviewed_on")
    repositories: list[Repository] = []
    for item in _list(root["repositories"], "repositories"):
        row = _record(item, set(Repository.__annotations__), "repository")
        identifier = _identifier(row["id"], "repository.id")
        url = _url(row["repository_url"], "repository_url")
        if len(url.split("/")) != 5:
            raise PublicationError("Catalog repository_url: expected repository root")
        role = row["role"]
        if role not in ("code-integration", "manual-handoff", "resource"):
            raise PublicationError("Catalog role: invalid integration role")
        commit = _text(row["commit"], "commit")
        evidence = _url(row["evidence_url"], "evidence_url")
        if not re.fullmatch(r"[0-9a-f]{40}", commit) or not evidence.startswith(
            f"{url}/blob/{commit}/"
        ):
            raise PublicationError("Catalog evidence_url: must bind repository and exact commit")
        checked_on = _date(row["checked_on"], "checked_on")
        if checked_on > reviewed_on:
            raise PublicationError("Catalog checked_on: later than reviewed_on")
        # Explicit branches preserve the literal role type at the JSON boundary.
        normalized_role: Literal["code-integration", "manual-handoff", "resource"] = "resource"
        if role == "code-integration":
            normalized_role = "code-integration"
        elif role == "manual-handoff":
            normalized_role = "manual-handoff"
        repositories.append(
            Repository(
                id=identifier,
                name=_text(row["name"], "name"),
                repository_url=url,
                role=normalized_role,
                summary=_text(row["summary"], "summary"),
                use_for=_text(row["use_for"], "use_for"),
                handoff=_text(row["handoff"], "handoff"),
                evidence_url=evidence,
                commit=commit,
                checked_on=checked_on,
            )
        )
    repository_ids = set(_unique([row["id"] for row in repositories], "repositories"))
    credential_ids = {row[0] for row in _CREDENTIALS}
    workflows: list[Workflow] = []
    for item in _list(root["workflows"], "workflows"):
        row = _record(item, set(Workflow.__annotations__), "workflow")
        repos = _unique(
            [
                _identifier(item, "repository_ids")
                for item in _list(row["repository_ids"], "repository_ids")
            ],
            "repository_ids",
        )
        creds = _unique(
            [
                _identifier(item, "credential_ids")
                for item in _list(row["credential_ids"], "credential_ids")
            ],
            "credential_ids",
        )
        if not set(repos) <= repository_ids or not set(creds) <= credential_ids:
            raise PublicationError("Catalog workflow: unknown repository or credential reference")
        commands = [_text(item, "commands") for item in _list(row["commands"], "commands")]
        if any(not command.startswith("symposium ") for command in commands):
            raise PublicationError("Catalog commands: expected Symposium CLI examples")
        workflows.append(
            Workflow(
                id=_identifier(row["id"], "workflow.id"),
                title=_text(row["title"], "title"),
                summary=_text(row["summary"], "summary"),
                commands=commands,
                repository_ids=repos,
                credential_ids=creds,
                docs_url=_url(row["docs_url"], "docs_url"),
            )
        )
    _unique([row["id"] for row in workflows], "workflows")
    return Catalog(
        schema_version=1, reviewed_on=reviewed_on, repositories=repositories, workflows=workflows
    )


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise PublicationError("Catalog JSON: duplicate fields")
        result[key] = value
    return result


def load_catalog(path: Path | None = None) -> Catalog:
    """Read the bundled catalog or a bounded file without network/environment access."""
    source = (
        path
        if path is not None
        else files("symposium.organizing").joinpath("resources/ecosystem.json")
    )
    with source.open("rb") as stream:
        raw = stream.read(_MAX_BYTES + 1)
    if len(raw) > _MAX_BYTES:
        raise PublicationError("Catalog JSON: byte limit exceeded")
    try:
        value: object = json.loads(raw, object_pairs_hook=_pairs)
    except (ValueError, UnicodeError):
        raise PublicationError("Catalog JSON: invalid UTF-8 JSON") from None
    return validate_catalog(value)


def _markdown(text: str) -> str:
    return re.sub(r"([\\*_[\]#!|])", r"\\\1", text)


def catalog_markdown(catalog: Catalog) -> str:
    """Render validated metadata as escaped Markdown with pinned source links."""
    lines = [
        "# Integration methods",
        "",
        f"Reviewed: {catalog['reviewed_on']}. Offline metadata; no live availability or authentication checks.",
        "",
    ]
    for repository in catalog["repositories"]:
        lines.extend(
            [
                f"## {_markdown(repository['name'])}",
                "",
                f"Role: {repository['role']}",
                "",
                _markdown(repository["summary"]),
                "",
                "Use for: " + _markdown(repository["use_for"]),
                "",
                "Handoff: " + _markdown(repository["handoff"]),
                "",
                f"[Repository]({repository['repository_url']}) · [Pinned evidence]({repository['evidence_url']})",
                "",
            ]
        )
    for workflow in catalog["workflows"]:
        lines.extend(
            [
                f"## {_markdown(workflow['title'])}",
                "",
                _markdown(workflow["summary"]),
                "",
                "Credentials: " + (", ".join(workflow["credential_ids"]) or "none"),
                "",
            ]
        )
        lines.extend(f"- `uv run {command}`" for command in workflow["commands"])
        lines.extend(["", f"[Documentation]({workflow['docs_url']})", ""])
    return "\n".join(lines)
