"""Offline catalog boundaries and actual CLI credential nondisclosure."""

import copy
import json
import os
import subprocess
import sys

import pytest

from symposium.organizing.ecosystem import (
    capability_report,
    catalog_markdown,
    load_catalog,
    validate_catalog,
)
from symposium.organizing.models import PublicationError


def sample():
    return {
        "schema_version": 1,
        "reviewed_on": "2026-10-27",
        "repositories": [
            {
                "id": "sample",
                "name": "Synthetic fixture",
                "repository_url": "https://github.com/example/sample",
                "role": "resource",
                "summary": "Fixture only",
                "use_for": "Tests",
                "handoff": "Read manually",
                "evidence_url": "https://github.com/example/sample/blob/" + "a" * 40 + "/README.md",
                "commit": "a" * 40,
                "checked_on": "2026-10-27",
            }
        ],
        "workflows": [
            {
                "id": "local",
                "title": "Local workflow",
                "summary": "Offline",
                "commands": ["symposium organize methods"],
                "repository_ids": ["sample"],
                "credential_ids": [],
                "docs_url": "https://github.com/example/sample",
            }
        ],
    }


def test_roundtrip_real_file(tmp_path):
    payload = sample()
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(payload))
    result = load_catalog(path)
    assert result == payload
    assert "Pinned evidence" in catalog_markdown(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("repository_url", "http://github.com/example/sample"),
        ("repository_url", "https://github.com@example.org/example/sample"),
        ("repository_url", "https://github.com/example/sample?token=secret"),
        ("repository_url", "https://github.com/example/sample#private"),
        ("repository_url", "https://github.com/example/sample/%2e%2e/private"),
        ("repository_url", "https://github.com/example/sample/../private"),
        ("evidence_url", "https://github.com/example/other/blob/" + "a" * 40 + "/README.md"),
        ("evidence_url", "https://github.com/example/sample/blob/main/README.md"),
        ("commit", "a" * 39),
        ("checked_on", "2026-10-28"),
        ("checked_on", "2026-02-30"),
        ("role", "automatic-adapter"),
        ("id", "private/id"),
        ("name", "<script>"),
        ("summary", "secret=hidden"),
        ("summary", "x" * 2001),
        ("summary", "line\nbreak"),
    ],
)
def test_repository_rejects_adversarial_values(field, value):
    payload = sample()
    payload["repositories"][0][field] = value
    with pytest.raises(PublicationError):
        validate_catalog(payload)


@pytest.mark.parametrize(
    "mutation",
    [
        "root",
        "version",
        "repository-field",
        "workflow-field",
        "repository-ref",
        "credential-ref",
        "duplicate-repo",
        "duplicate-workflow",
        "duplicate-ref",
        "bad-list",
        "bad-command",
    ],
)
def test_schema_and_references_fail_closed(mutation):
    payload = sample()
    if mutation == "root":
        payload["unknown"] = "private"
    elif mutation == "version":
        payload["schema_version"] = True
    elif mutation == "repository-field":
        payload["repositories"][0]["token"] = "private"
    elif mutation == "workflow-field":
        del payload["workflows"][0]["docs_url"]
    elif mutation == "repository-ref":
        payload["workflows"][0]["repository_ids"] = ["absent"]
    elif mutation == "credential-ref":
        payload["workflows"][0]["credential_ids"] = ["coda"]
    elif mutation == "duplicate-repo":
        payload["repositories"].append(copy.deepcopy(payload["repositories"][0]))
    elif mutation == "duplicate-workflow":
        payload["workflows"].append(copy.deepcopy(payload["workflows"][0]))
    elif mutation == "duplicate-ref":
        payload["workflows"][0]["repository_ids"] = ["sample", "sample"]
    elif mutation == "bad-list":
        payload["repositories"] = "bad"
    elif mutation == "bad-command":
        payload["workflows"][0]["commands"] = ["curl private"]
    with pytest.raises(PublicationError):
        validate_catalog(payload)


@pytest.mark.parametrize(
    "raw", [b"{", b"\xff", b" " * 131073, b'{"schema_version":1,"schema_version":1}']
)
def test_invalid_file_rejected(tmp_path, raw):
    path = tmp_path / "catalog.json"
    path.write_bytes(raw)
    with pytest.raises(PublicationError):
        load_catalog(path)


@pytest.mark.parametrize("check_env", [False, True])
def test_cli_never_discloses_secrets_or_loads_dotenv(tmp_path, check_env):
    sentinel = "SYNTHETIC_SECRET_NEVER_PRINT_0123456789"
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = sentinel
    env["PERPLEXITY_API_KEY"] = "   "
    env.pop("SUPERHUMAN_DOCS_MCP_TOKEN", None)
    (tmp_path / ".env").write_text("SUPERHUMAN_DOCS_MCP_TOKEN=" + sentinel)
    command = [sys.executable, "-m", "symposium", "organize", "capabilities"]
    if check_env:
        command.append("--check-env")
    result = subprocess.run(
        command, cwd=tmp_path, env=env, text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert sentinel not in result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["environment_checked"] is check_env
    assert [row["status"] for row in report["credentials"]] == (
        ["configured", "missing", "missing"] if check_env else ["not-checked"] * 3
    )
    assert "does not validate authentication" in report["assurance"]


def test_bundled_catalog_and_cli_formats():
    catalog = load_catalog()
    assert catalog["repositories"] and catalog["workflows"]
    for format_name in ("json", "markdown"):
        result = subprocess.run(
            [sys.executable, "-m", "symposium", "organize", "methods", "--format", format_name],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        if format_name == "json":
            assert json.loads(result.stdout) == catalog
        else:
            assert result.stdout == catalog_markdown(catalog)


def test_metadata_default_is_not_checked():
    assert all(item["status"] == "not-checked" for item in capability_report()["credentials"])
