"""Synthetic filesystem transports exercise custody and receipt failure boundaries."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from symposium.organizing.bridge import (
    FIELDS,
    InstituteOSTransport,
    apply_receipt,
    canonical_content,
    prepare_receipt,
    pull_snapshot,
    read_page_content,
    validate_mapping,
)
from symposium.organizing.models import PublicationError


def mapping():
    return {
        "schema_version": 1,
        "organizer_document": "synthetic-private",
        "public_document": "synthetic-public",
        "sources": {
            kind: {
                "uri": f"superhuman://docs/synthetic-{'private' if kind == 'participants' else 'public'}/tables/{kind}",
                "fields": {key: "c-" + key for key in sorted(fields)},
            }
            for kind, fields in FIELDS.items()
        },
    }


class FileTables:
    def __init__(self, path, fault=None):
        self.path = path
        self.fault = fault
        self.calls = []
        path.write_text(json.dumps(mapping()))

    def invoke(self, name, arguments):
        self.calls.append((name, arguments))
        config = json.loads(self.path.read_text())
        source = next(s for s in config["sources"].values() if s["uri"] == arguments["uri"])
        ids = list(source["fields"].values())
        if name == "table_columns_read":
            columns = [{"columnId": key, "name": key} for key in ids]
            if self.fault == "schema":
                columns.pop()
            return {"columns": columns}
        assert name == "table_rows_read"
        assert set(arguments["columnsToInclude"]) == set(ids)
        offset = arguments["rowOffset"]
        rows = [
            {"rowId": f"row-{index}", "values": {key: {"value": "synthetic"} for key in ids}}
            for index in range(offset, min(offset + 100, 101))
        ]
        total = 102 if self.fault == "total" and offset else 101
        if self.fault == "duplicate" and offset:
            rows[0]["rowId"] = "row-0"
        if self.fault == "omitted":
            rows[0]["values"].pop(ids[0])
        if self.fault == "extra":
            rows[0]["values"]["email"] = {"value": "synthetic-private"}
        return {
            "rows": rows,
            "totalRows": total,
            "hasMore": False if self.fault == "truncated" else offset == 0,
        }


def test_mapping_is_closed_and_copied():
    original = mapping()
    assert validate_mapping(original) == original
    validated = validate_mapping(original)
    validated["sources"]["sessions"]["fields"]["title"] = "changed"
    assert original != validated


@pytest.mark.parametrize(
    "fault",
    ["extra", "missing", "reuse", "document", "same_document", "schema_version", "duplicate_uri"],
)
def test_mapping_rejects_unsafe_shapes(fault):
    config = mapping()
    fields = config["sources"]["participants"]["fields"]
    if fault == "extra":
        fields["email"] = "private-email"
    elif fault == "missing":
        fields.pop("share_publicly")
    elif fault == "reuse":
        fields["name"] = fields["share_publicly"]
    elif fault == "document":
        config["sources"]["sessions"]["uri"] = "superhuman://docs/synthetic-private/tables/sessions"
    elif fault == "same_document":
        config["public_document"] = config["organizer_document"]
    elif fault == "duplicate_uri":
        config["sources"]["sessions"]["uri"] = config["sources"]["presentations"]["uri"]
    else:
        config["schema_version"] = True
    with pytest.raises(PublicationError):
        validate_mapping(config)


def test_pull_complete_pagination_private_file_and_no_overwrite(tmp_path):
    public = tmp_path / "public"
    public.mkdir()
    workspace = tmp_path / "private"
    transport = FileTables(tmp_path / "source.json")
    snapshot = pull_snapshot(mapping(), transport, public_root=public, workspace=workspace)
    assert all(len(table["rows"]) == 101 for table in snapshot["tables"].values())
    assert len(transport.calls) == 9
    files = list(workspace.glob("*.json"))
    assert len(files) == 1 and files[0].stat().st_mode & 0o777 == 0o600
    before = files[0].read_bytes()
    assert json.loads(before) == snapshot
    pull_snapshot(mapping(), transport, public_root=public, workspace=workspace)
    assert len(list(workspace.glob("*.json"))) == 2
    assert files[0].read_bytes() == before
    assert not list(public.iterdir())


@pytest.mark.parametrize("fault", ["schema", "total", "duplicate", "omitted", "extra", "truncated"])
def test_pull_rejects_bad_source_without_snapshot(tmp_path, fault):
    workspace = tmp_path / "private"
    with pytest.raises(PublicationError):
        pull_snapshot(
            mapping(),
            FileTables(tmp_path / "source.json", fault),
            public_root=tmp_path / "public",
            workspace=workspace,
        )
    assert not workspace.exists()


def test_pull_rejects_public_and_symlink_workspace(tmp_path):
    public = tmp_path / "public"
    public.mkdir()
    link = tmp_path / "link"
    link.symlink_to(public, target_is_directory=True)
    transport = FileTables(tmp_path / "source.json")
    for workspace in (public, public / "private", link / "private"):
        with pytest.raises(PublicationError, match="public repository"):
            pull_snapshot(mapping(), transport, public_root=public, workspace=workspace)
    assert transport.calls == []


class FilePage:
    def __init__(self, path, text="Baseline", fault=None):
        self.path = path
        path.write_text(text)
        self.fault = fault
        self.writes = 0

    def invoke(self, name, arguments):
        if name == "content_read":
            lines = self.path.read_text().splitlines()
            offset = arguments["markdownBlockOffset"]
            return {
                "content": "\n\n".join(
                    f'<block id="cl-{i}">{line}</block>'
                    for i, line in enumerate(lines[offset : offset + 100], start=offset)
                ),
                "totalBlocks": len(lines),
                "hasMore": offset + 100 < len(lines),
            }
        assert name == "content_modify"
        (operation,) = arguments["operations"]
        assert set(operation) == {"operation", "blockType", "content"}
        assert operation["operation"] == "insert_element" and operation["blockType"] == "markdown"
        self.writes += 1
        self.path.write_text(
            self.path.read_text()
            + "\n\n"
            + ("corrupted" if self.fault == "corrupt" else operation["content"])
        )
        if self.fault == "unknown":
            raise PublicationError("Synthetic unknown outcome")
        return {"success": True}


def receipt(page):
    return prepare_receipt(
        "superhuman://docs/synthetic-private/pages/integration",
        page.path.read_text(),
        "Public bundle synchronized.\nManifest verified.",
        "a" * 64,
    )


def test_receipt_requires_apply_then_applies_and_is_idempotent(tmp_path):
    page = FilePage(tmp_path / "page.md")
    plan = receipt(page)
    with pytest.raises(PublicationError, match="explicit apply"):
        apply_receipt(plan, page)
    assert page.writes == 0
    assert apply_receipt(plan, page, apply=True)["status"] == "applied"
    assert apply_receipt(plan, page, apply=True)["status"] == "noop"
    assert page.writes == 1
    assert page.path.read_text().count(plan["marker"]) == 1


def test_receipt_baseline_conflict_and_tampering_never_mutate(tmp_path):
    page = FilePage(tmp_path / "page.md")
    plan = receipt(page)
    changed = copy.deepcopy(plan)
    changed["receipt_markdown"] = "Tampered"
    with pytest.raises(PublicationError, match="integrity"):
        apply_receipt(changed, page, apply=True)
    page.path.write_text("Human edit")
    with pytest.raises(PublicationError, match="changed since"):
        apply_receipt(plan, page, apply=True)
    assert page.writes == 0


@pytest.mark.parametrize("fault", ["corrupt", "unknown"])
def test_receipt_unknown_or_bad_readback_is_not_retried(tmp_path, fault):
    page = FilePage(tmp_path / "page.md", fault=fault)
    with pytest.raises(PublicationError):
        apply_receipt(receipt(page), page, apply=True)
    assert page.writes == 1


def test_receipt_conflicting_marker_refuses(tmp_path):
    page = FilePage(tmp_path / "page.md")
    plan = receipt(page)
    page.path.write_text(plan["marker"] + "\nWrong body")
    with pytest.raises(PublicationError, match="conflicting"):
        apply_receipt(plan, page, apply=True)
    assert page.writes == 0


def test_read_page_paginates_and_normalizes_wrappers(tmp_path):
    text = "\n".join(f"Line {i}" for i in range(205))
    page = FilePage(tmp_path / "page.md", text)
    assert (
        canonical_content(
            read_page_content(page, "superhuman://docs/synthetic-private/pages/integration")
        )
        == text
    )


def test_transport_missing_root_and_denied_tool(tmp_path):
    transport = InstituteOSTransport(tmp_path / "absent")
    with pytest.raises(PublicationError, match="allowlist"):
        transport.invoke("table_rows_modify", {})
    with pytest.raises(PublicationError, match="unavailable"):
        transport.invoke("content_read", {})


def test_transport_real_subprocess_synthetic_adapter(tmp_path):
    root = tmp_path / "instituteos"
    package = root / "src/instituteos"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "_superhuman.py").write_text(
        'import os\nasync def call_tool(token,name,args):\n    print(token)\n    if args.get("fail"): raise ValueError(token)\n    return {"name":name,"arguments":args}\n'
    )
    binary = root / ".venv/bin/python"
    binary.parent.mkdir(parents=True)
    binary.symlink_to(sys.executable)
    script = 'from pathlib import Path\nfrom symposium.organizing.bridge import InstituteOSTransport\nimport sys\ntry:\n print(InstituteOSTransport(Path(sys.argv[1])).invoke("content_read", {"fail":sys.argv[2]=="fail"}))\nexcept Exception as exc:\n print(str(exc))\n sys.exit(1)\n'
    env = os.environ.copy()
    env["SUPERHUMAN_DOCS_MCP_TOKEN"] = "synthetic-secret-never-echo"
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    on_vault = any(parent.name == "GitVault" and parent.is_mount() for parent in root.parents)
    for mode, expected in (("ok", 0), ("fail", 1)):
        run = subprocess.run(
            [sys.executable, "-B", "-c", script, str(root), mode],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        # The real external-storage guard precedes SDK authentication. On
        # hosted runners it must reject both operations without leaking secrets.
        if not on_vault:
            assert run.returncode == 1
            assert "root or external interpreter is unavailable" in run.stdout
        else:
            assert run.returncode == expected, run.stdout + run.stderr
        assert "synthetic-secret-never-echo" not in run.stdout + run.stderr
    env.pop("SUPERHUMAN_DOCS_MCP_TOKEN")
    run = subprocess.run(
        [sys.executable, "-B", "-c", script, str(root), "ok"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert run.returncode == 1
    assert (
        "is required" if on_vault else "root or external interpreter is unavailable"
    ) in run.stdout


class BrokenPage(FilePage):
    def invoke(self, name, arguments):
        result = super().invoke(name, arguments)
        if name == "content_read":
            result["hasMore"] = True
        return result


def test_page_truncation_fails_before_mutation(tmp_path):
    page = BrokenPage(tmp_path / "page.md")
    with pytest.raises(PublicationError, match="pagination"):
        apply_receipt(receipt(page), page, apply=True)
    assert page.writes == 0


def test_receipt_partial_body_match_is_not_idempotency(tmp_path):
    page = FilePage(tmp_path / "page.md")
    plan = receipt(page)
    page.path.write_text(plan["marker"] + "\n" + plan["receipt_markdown"] + " CHANGED")
    with pytest.raises(PublicationError, match="conflicting"):
        apply_receipt(plan, page, apply=True)
    assert page.writes == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("target_page_uri", "bad-uri"),
        ("public_manifest_hash", "bad-hash"),
        ("receipt_markdown", ""),
        ("receipt_markdown", '<block id="fake">reserved</block>'),
    ],
)
def test_receipt_invalid_preparation_inputs(tmp_path, field, value):
    inputs = {
        "page_uri": "superhuman://docs/synthetic-private/pages/integration",
        "baseline_content": "",
        "receipt_markdown": "Approved receipt",
        "public_manifest_hash": "a" * 64,
    }
    inputs["page_uri" if field == "target_page_uri" else field] = value
    with pytest.raises(PublicationError):
        prepare_receipt(**inputs)


class EmptyCanvas(FilePage):
    def __init__(self, path, count=1, more=False):
        super().__init__(path, "")
        self.count = count
        self.more = more

    def invoke(self, name, arguments):
        if name == "content_read" and not self.path.read_text():
            return {"content": "", "totalBlocks": self.count, "hasMore": self.more}
        return super().invoke(name, arguments)


@pytest.mark.parametrize("count", [0, 1])
def test_empty_canvas_live_response_shape_allows_verified_append(tmp_path, count):
    page = EmptyCanvas(tmp_path / "empty-page.md", count=count)
    uri = "superhuman://docs/synthetic-private/pages/integration"
    assert read_page_content(page, uri) == ""
    plan = receipt(page)
    assert apply_receipt(plan, page, apply=True)["status"] == "applied"
    assert apply_receipt(plan, page, apply=True)["status"] == "noop"
    assert page.writes == 1


@pytest.mark.parametrize("count,more", [(2, False), (1, True)])
def test_empty_canvas_does_not_relax_missing_block_coverage(tmp_path, count, more):
    page = EmptyCanvas(tmp_path / "empty-page.md", count=count, more=more)
    with pytest.raises(PublicationError):
        apply_receipt(receipt(page), page, apply=True)
    assert page.writes == 0


class AutolinkPage(FilePage):
    def __init__(self, path, destination="https://example.org/guide"):
        super().__init__(path)
        self.destination = destination

    def invoke(self, name, arguments):
        result = super().invoke(name, arguments)
        if name == "content_read" and self.writes:
            result["content"] = result["content"].replace(
                "https://example.org/guide",
                f"[https://example.org/guide]({self.destination})",
            )
        return result


def test_identical_https_autolink_readback_and_noop(tmp_path):
    page = AutolinkPage(tmp_path / "page.md")
    plan = prepare_receipt(
        "superhuman://docs/synthetic-private/pages/integration",
        "Baseline",
        "Guide: https://example.org/guide",
        "a" * 64,
    )
    assert plan["receipt_markdown"] == "Guide: https://example.org/guide"
    original_id = plan["receipt_id"]
    assert apply_receipt(plan, page, apply=True)["status"] == "applied"
    assert apply_receipt(plan, page, apply=True)["status"] == "noop"
    assert page.writes == 1 and plan["receipt_id"] == original_id


def test_changed_autolink_destination_fails_readback_without_retry(tmp_path):
    page = AutolinkPage(tmp_path / "page.md", "https://example.org/changed")
    plan = prepare_receipt(
        "superhuman://docs/synthetic-private/pages/integration",
        "Baseline",
        "Guide: https://example.org/guide",
        "a" * 64,
    )
    with pytest.raises(PublicationError, match="readback verification failed"):
        apply_receipt(plan, page, apply=True)
    assert page.writes == 1
    with pytest.raises(PublicationError, match="conflicting content"):
        apply_receipt(plan, page, apply=True)
    assert page.writes == 1


@pytest.mark.parametrize(
    "text",
    [
        "[Guide](https://example.org/guide)",
        "[https://example.org/guide](https://example.org/changed)",
        "[https://example.org/guide](https://example.org/guide?changed=1)",
        "[http://example.org/guide](http://example.org/guide)",
        "![https://example.org/guide](https://example.org/guide)",
    ],
)
def test_canonical_content_preserves_nonidentity_links(text):
    assert canonical_content(text) == text


class FileSlots:
    """Synthetic server windows include metadata-counted unrendered empty slots."""

    def __init__(self, path, slots, fault=None):
        self.path = path
        path.write_text(json.dumps(slots))
        self.fault = fault
        self.calls = []
        self.writes = 0

    def invoke(self, name, arguments):
        slots = json.loads(self.path.read_text())
        if name == "content_modify":
            self.writes += 1
            slots.extend(
                line for line in arguments["operations"][0]["content"].splitlines() if line.strip()
            )
            self.path.write_text(json.dumps(slots))
            return {"success": True}
        assert name == "content_read"
        offset, limit = arguments["markdownBlockOffset"], arguments["markdownBlockLimit"]
        self.calls.append((offset, limit))
        records = [
            (index, value)
            for index, value in enumerate(slots[offset : offset + limit], start=offset)
            if value is not None
        ]
        if self.fault == "missing_bulk" and limit > 1 and records:
            records.pop()
        content = "\n\n".join(
            f'<block id="cl-{0 if self.fault == "duplicate" else index}">{value}</block>'
            for index, value in records
        )
        if self.fault == "unwrapped" and limit == 1 and not content:
            content = "Unwrapped hidden text"
        return {
            "content": content,
            "totalBlocks": len(slots) + (1 if self.fault == "changed_total" and limit == 1 else 0),
            "hasMore": False
            if self.fault == "wrong_more" and limit == 1
            else offset + limit < len(slots),
        }


def test_metadata_empty_slot_exact_live_contract_apply_and_noop(tmp_path):
    page = FileSlots(tmp_path / "slots.json", [None])
    plan = prepare_receipt(
        "superhuman://docs/synthetic-private/pages/integration",
        "",
        "## Receipt\n\nGuide: https://example.org/guide",
        "a" * 64,
    )
    assert apply_receipt(plan, page, apply=True)["status"] == "applied"
    assert len(json.loads(page.path.read_text())) == 4
    assert apply_receipt(plan, page, apply=True)["status"] == "noop"
    assert page.writes == 1
    assert all((index, 1) in page.calls for index in range(4))


def test_sparse_server_windows_advance_by_requested_span(tmp_path):
    slots = [None if index in {0, 99, 100, 204} else f"Slot {index}" for index in range(205)]
    page = FileSlots(tmp_path / "slots.json", slots)
    result = read_page_content(page, "superhuman://docs/synthetic-private/pages/integration")
    assert canonical_content(result) == "\n".join(value for value in slots if value is not None)
    assert [offset for offset, limit in page.calls if limit == 100] == [0, 100, 200]
    assert len(page.calls) == 208


@pytest.mark.parametrize(
    "fault", ["missing_bulk", "duplicate", "changed_total", "wrong_more", "unwrapped"]
)
def test_gap_verification_rejects_truncation_duplicates_and_inconsistency(tmp_path, fault):
    page = FileSlots(tmp_path / "slots.json", [None, "First", "Second"], fault=fault)
    plan = prepare_receipt(
        "superhuman://docs/synthetic-private/pages/integration",
        "First\nSecond",
        "Receipt",
        "a" * 64,
    )
    with pytest.raises(PublicationError):
        apply_receipt(plan, page, apply=True)
    assert page.writes == 0


def test_sparse_page_call_budget_is_bounded(tmp_path):
    page = FileSlots(tmp_path / "slots.json", [None] * 1001)
    with pytest.raises(PublicationError, match="call budget"):
        read_page_content(page, "superhuman://docs/synthetic-private/pages/integration")
    assert len(page.calls) == 1000
