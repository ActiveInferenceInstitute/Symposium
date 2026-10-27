"""Offline organizing CLI scenarios using real private/public filesystem trees."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from symposium.cli.organize import add_organize_parser, run_organize
from symposium.organizing.bridge import FIELDS
from symposium.organizing.models import canonical_bytes


def invoke(*arguments):
    parser = argparse.ArgumentParser()
    add_organize_parser(parser.add_subparsers(dest="command"))
    return run_organize(parser.parse_args(["organize", *map(str, arguments)]))


@pytest.fixture
def private_inputs(tmp_path):
    private = tmp_path / "private"
    private.mkdir()
    public = tmp_path / "public"
    public.mkdir()
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
            "title": "Synthetic Talk",
            "abstract": "Complete synthetic abstract.",
            "contribution_type": "Talk",
            "pictures": [],
        },
        "participants": {"share_publicly": "Yes", "name": "Synthetic Participant"},
        "sessions": {
            "title": "Synthetic Talk",
            "presenter": "Synthetic Presenter",
            "kind": "Talk",
            "start_utc": "2026-11-01T12:00:00Z",
            "end_utc": "2026-11-01T13:00:00Z",
        },
    }
    snapshot = {
        "schema_version": 1,
        "mapping": mapping,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "tables": {
            kind: {
                "schema": [],
                "totalRows": 1,
                "rows": [
                    {
                        "rowId": "synthetic-private-row",
                        "values": {
                            "c-" + key: {"value": values[kind].get(key, "")} for key in fields
                        },
                    }
                ],
            }
            for kind, fields in FIELDS.items()
        },
    }
    for name, value in (
        ("snapshot", snapshot),
        ("event", event),
        ("resources", []),
        ("mapping", mapping),
    ):
        (private / (name + ".json")).write_bytes(canonical_bytes(value))
    return private, public


def project(private, public, destination="project", *extra):
    return invoke(
        "project",
        "--snapshot",
        private / "snapshot.json",
        "--event",
        private / "event.json",
        "--resources",
        private / "resources.json",
        "--workspace",
        private / destination,
        "--public-root",
        public,
        *extra,
    )


def test_complete_offline_cli_workflow(private_inputs):
    private, public = private_inputs
    assert project(private, public) == 0
    workspace = private / "project"
    bundle = workspace / "program.json"
    ledger = workspace / "approval-ledger.json"
    assert bundle.stat().st_mode & 0o777 == 0o600
    assert ledger.stat().st_mode & 0o777 == 0o600
    artifacts = private / "artifacts"
    artifacts.mkdir()
    for command, destination in (
        ("dossiers", artifacts / "dossiers"),
        ("participant-briefs", artifacts / "participants"),
    ):
        assert (
            invoke(
                command, "--bundle", bundle, "--output-dir", destination, "--public-root", public
            )
            == 0
        )
        assert list(destination.glob("*.md"))
    assert (
        invoke(
            "calendar",
            "--bundle",
            bundle,
            "--output",
            artifacts / "program.ics",
            "--public-root",
            public,
        )
        == 0
    )
    assert "BEGIN:VEVENT" in (artifacts / "program.ics").read_text()
    assert (
        invoke("book", "--bundle", bundle, "--workspace", private / "book", "--public-root", public)
        == 0
    )
    assert list((private / "book/projects").glob("*/manuscript/*.md"))
    assert (
        invoke(
            "artifact-index",
            "--bundle",
            bundle,
            "--artifacts-dir",
            artifacts,
            "--public-root",
            public,
        )
        == 0
    )
    assert (artifacts / "artifact_index.json").is_file()
    stage_args = [
        "stage-public",
        "--bundle",
        bundle,
        "--snapshot",
        private / "snapshot.json",
        "--ledger",
        ledger,
        "--output-dir",
        public / "edition",
        "--public-root",
        public,
        "--artifacts-dir",
        artifacts,
    ]
    assert invoke(*stage_args) == 1
    assert not (public / "edition").exists()
    assert invoke(*stage_args, "--apply") == 0
    assert invoke("check-public", "--public-dir", public / "edition") == 0
    assert invoke("site", "--public-dir", public / "edition", "--output-dir", public / "site") == 0
    assert "Complete synthetic abstract." in (public / "site/index.html").read_text()
    assert not list((public / "edition").rglob("*ledger*"))
    for path in (public / "edition").rglob("*"):
        if path.is_file():
            assert b"synthetic-private" not in path.read_bytes()
    (public / "edition/program.json").write_text("{}")
    assert invoke("check-public", "--public-dir", public / "edition") == 1
    assert (
        invoke("site", "--public-dir", public / "edition", "--output-dir", public / "rejected-site")
        == 1
    )
    assert not (public / "rejected-site").exists()


def test_private_workspace_symlink_and_existing_refusals(private_inputs):
    private, public = private_inputs
    assert project(private, public) == 0
    original = (private / "project/program.json").read_bytes()
    assert project(private, public) == 1
    assert (private / "project/program.json").read_bytes() == original
    (private / "public-link").symlink_to(public, target_is_directory=True)
    assert project(private, public, "public-link/new") == 1
    assert not (public / "new").exists()
    (public / "snapshot.json").write_bytes((private / "snapshot.json").read_bytes())
    assert (
        invoke(
            "project",
            "--snapshot",
            public / "snapshot.json",
            "--event",
            private / "event.json",
            "--resources",
            private / "resources.json",
            "--workspace",
            private / "refused",
            "--public-root",
            public,
        )
        == 1
    )
    assert not (private / "refused").exists()


def test_empty_portrait_projection_and_native_prerequisites(private_inputs):
    private, public = private_inputs
    assert project(private, public, "project", "--portraits") == 0
    assert (private / "project/portraits").is_dir()
    bundle = private / "project/program.json"
    assert (
        invoke(
            "book",
            "--bundle",
            bundle,
            "--workspace",
            private / "book",
            "--public-root",
            public,
            "--render",
        )
        == 1
    )
    assert not (private / "book").exists()
    assert (
        invoke(
            "book",
            "--bundle",
            bundle,
            "--workspace",
            private / "book",
            "--public-root",
            public,
            "--template-root",
            private / "missing",
        )
        == 1
    )
    assert not (private / "book").exists()


def test_receipt_prepare_and_missing_apply_never_calls_transport(private_inputs, capsys):
    private, public = private_inputs
    request = {
        "page_uri": "superhuman://docs/synthetic-private/pages/integration",
        "baseline_content": "Baseline",
        "receipt_markdown": "Synthetic approved receipt",
        "public_manifest_hash": "a" * 64,
    }
    source = private / "receipt-request.json"
    source.write_bytes(canonical_bytes(request))
    plan = private / "plan.json"
    assert (
        invoke("receipt-prepare", "--request", source, "--output", plan, "--public-root", public)
        == 0
    )
    assert plan.stat().st_mode & 0o777 == 0o600
    assert json.loads(plan.read_text())["target_page_uri"] == request["page_uri"]
    assert (
        invoke(
            "receipt-apply",
            "--plan",
            plan,
            "--instituteos-root",
            private / "missing",
            "--output",
            private / "result.json",
            "--public-root",
            public,
        )
        == 1
    )
    assert not (private / "result.json").exists()
    assert "explicit apply" in capsys.readouterr().err
    assert (
        invoke("receipt-prepare", "--request", source, "--output", plan, "--public-root", public)
        == 1
    )


def test_pull_invalid_root_and_invalid_json_fail_without_snapshot(private_inputs, capsys):
    private, public = private_inputs
    assert (
        invoke(
            "pull",
            "--mapping",
            private / "mapping.json",
            "--instituteos-root",
            private / "missing",
            "--workspace",
            private / "pull",
            "--public-root",
            public,
        )
        == 1
    )
    assert not (private / "pull").exists()
    (private / "snapshot.json").write_text("Not JSON: synthetic-secret")
    assert project(private, public) == 1
    assert "synthetic-secret" not in capsys.readouterr().err


def test_real_cli_entrypoint_help_and_failure(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    prefix = [sys.executable, "-B", "-c", "from symposium.cli import main; main()"]
    help_run = subprocess.run(
        [*prefix, "organize", "--help"], capture_output=True, text=True, env=env, check=False
    )
    assert help_run.returncode == 0
    assert all(
        name in help_run.stdout for name in ("project", "receipt-apply", "site", "stage-public")
    )
    bad_run = subprocess.run(
        [*prefix, "organize", "check-public", "--public-dir", str(tmp_path / "missing")],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert bad_run.returncode == 1 and "ERROR:" in bad_run.stderr
    assert "Traceback" not in bad_run.stderr


def test_cli_synthetic_sdk_pull_and_receipt_apply(private_inputs):
    private, public = private_inputs
    root = private / "synthetic-sdk"
    package = root / "src/instituteos"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (root / "mapping.json").write_bytes((private / "mapping.json").read_bytes())
    (root / "page.md").write_text("Baseline")
    (package / "_superhuman.py").write_text("""import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
async def call_tool(token, name, args):
    print(token)
    if name == "table_columns_read":
        mapping = json.loads((ROOT / "mapping.json").read_text())
        source = next(s for s in mapping["sources"].values() if s["uri"] == args["uri"])
        return {"columns": [{"columnId": value} for value in source["fields"].values()]}
    if name == "table_rows_read":
        return {"rows": [], "totalRows": 0, "hasMore": False}
    page = ROOT / "page.md"
    if name == "content_read":
        lines = page.read_text().splitlines()
        return {"content": "\\n".join(f'<block id="cl-{i}">{line}</block>' for i,line in enumerate(lines)), "totalBlocks": len(lines), "hasMore": False}
    if name == "content_modify":
        page.write_text(page.read_text() + "\\n\\n" + args["operations"][0]["content"])
        return {"success": True}
    raise ValueError("Unsupported synthetic tool")
""")
    binary = root / ".venv/bin/python"
    binary.parent.mkdir(parents=True)
    binary.symlink_to(sys.executable)
    env = os.environ.copy()
    env["SUPERHUMAN_DOCS_MCP_TOKEN"] = "synthetic-cli-secret"
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    prefix = [sys.executable, "-B", "-c", "from symposium.cli import main; main()", "organize"]
    pull = subprocess.run(
        [
            *prefix,
            "pull",
            "--mapping",
            str(private / "mapping.json"),
            "--instituteos-root",
            str(root),
            "--workspace",
            str(private / "pulled"),
            "--public-root",
            str(public),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    # Hosted CI has no mounted GitVault. It must prove the real CLI refuses
    # that unsupported runtime; full pull/apply is exercised on the SSD host.
    if not any(parent.name == "GitVault" and parent.is_mount() for parent in root.parents):
        assert pull.returncode == 1
        assert "InstituteOS root or external interpreter is unavailable" in pull.stderr
        assert "synthetic-cli-secret" not in pull.stdout + pull.stderr
        assert not (private / "pulled").exists()
        assert (root / "page.md").read_text() == "Baseline"
        return
    assert pull.returncode == 0, pull.stdout + pull.stderr
    snapshots = list((private / "pulled").glob("snapshot-*.json"))
    assert len(snapshots) == 1
    assert all(
        table["totalRows"] == 0 for table in json.loads(snapshots[0].read_text())["tables"].values()
    )
    request = private / "request.json"
    request.write_bytes(
        canonical_bytes(
            {
                "page_uri": "superhuman://docs/synthetic-private/pages/integration",
                "baseline_content": "Baseline",
                "receipt_markdown": "Approved synthetic synchronization",
                "public_manifest_hash": "a" * 64,
            }
        )
    )
    plan = private / "plan.json"
    assert (
        invoke("receipt-prepare", "--request", request, "--output", plan, "--public-root", public)
        == 0
    )
    outputs = [pull.stdout + pull.stderr]
    for index, expected in enumerate(("applied", "noop")):
        output = private / f"receipt-result-{index}.json"
        run = subprocess.run(
            [
                *prefix,
                "receipt-apply",
                "--plan",
                str(plan),
                "--instituteos-root",
                str(root),
                "--output",
                str(output),
                "--public-root",
                str(public),
                "--apply",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert run.returncode == 0, run.stdout + run.stderr
        result = json.loads(output.read_text())
        assert result["status"] == expected and result["readback_verified"] is True
        assert output.stat().st_mode & 0o777 == 0o600
        outputs.append(run.stdout + run.stderr)
    assert (root / "page.md").read_text().count("Symposium synchronization receipt:") == 1
    assert all("synthetic-cli-secret" not in output for output in outputs)
