"""Operator commands for private intake, public staging, and synchronization receipts."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from symposium.organizing.artifacts import (
    ArtifactError,
    render_abstract_book,
    stage_abstract_book,
    write_dossiers,
)
from symposium.organizing.bridge import (
    InstituteOSTransport,
    apply_receipt,
    prepare_receipt,
    pull_snapshot,
)
from symposium.organizing.models import (
    MAX_BUNDLE_BYTES,
    PublicationError,
    canonical_bytes,
    content_hash,
    load_bundle,
)
from symposium.organizing.projection import project_snapshot
from symposium.organizing.publication import (
    stage_public,
    verify_public_tree,
    write_artifact_index,
    write_calendar,
    write_participant_briefs,
)
from symposium.organizing.review import readiness, review_update


def add_organize_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "organize", help="Private organizing and approved public exports"
    )
    commands = parser.add_subparsers(dest="subcommand", required=True)
    specifications = {
        "pull": ("mapping", "instituteos-root", "workspace", "public-root"),
        "project": ("snapshot", "event", "resources", "workspace", "public-root"),
        "dossiers": ("bundle", "output-dir", "public-root"),
        "book": ("bundle", "workspace", "public-root"),
        "calendar": ("bundle", "output", "public-root"),
        "participant-briefs": ("bundle", "output-dir", "public-root"),
        "artifact-index": ("bundle", "artifacts-dir", "public-root"),
        "stage-public": ("bundle", "snapshot", "ledger", "output-dir", "public-root"),
        "site": ("public-dir", "output-dir"),
        "check-public": ("public-dir",),
        "readiness": ("public-dir",),
        "review-update": ("previous-public-dir", "candidate-public-dir", "output", "public-root"),
        "receipt-prepare": ("request", "output", "public-root"),
        "receipt-apply": ("plan", "instituteos-root", "output", "public-root"),
    }
    children = {}
    for name, options in specifications.items():
        child = commands.add_parser(name)
        children[name] = child
        for option in options:
            child.add_argument("--" + option, required=True, type=Path)
    children["readiness"].add_argument(
        "--require-complete",
        action="store_true",
        help="Fail when presentations are absent or abstracts/session titles are pending; source freshness is not checked",
    )
    children[
        "review-update"
    ].description = (
        "Compare two verified public trees; save an exclusive private report without publishing."
    )
    children["project"].add_argument(
        "--portraits",
        action="store_true",
        help="Fetch approved program portraits into the private workspace",
    )
    children["book"].add_argument(
        "--render",
        action="store_true",
        help="Run the native template renderer; default only stages sources",
    )
    children["book"].add_argument("--template-root", type=Path)
    children["book"].add_argument("--timeout", type=int, default=600)
    children["stage-public"].add_argument("--assets-dir", type=Path)
    children["stage-public"].add_argument("--artifacts-dir", type=Path)
    children["stage-public"].add_argument("--max-age-seconds", type=int, default=3600)
    for command in ("stage-public", "receipt-apply"):
        children[command].add_argument(
            "--apply", action="store_true", help="Explicitly execute the prepared mutation"
        )
    children[
        "receipt-prepare"
    ].description = "Read a private JSON request with page_uri, baseline_content, receipt_markdown, public_manifest_hash; write an exclusive private plan."


def _private(path: Path, public_root: Path) -> Path:
    resolved = path.resolve()
    repository = Path(__file__).resolve().parents[3]
    if any(resolved.is_relative_to(root.resolve()) for root in (public_root, repository)):
        raise PublicationError(
            "Private inputs and workspaces must be outside the public repository"
        )
    return resolved


def _json(path: Path) -> Any:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BUNDLE_BYTES + 1)
    if len(raw) > MAX_BUNDLE_BYTES:
        raise PublicationError("Input JSON exceeds its byte limit")
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError):
        raise PublicationError("Input must be valid UTF-8 JSON") from None


def _write_private(path: Path, value: object) -> None:
    raw = canonical_bytes(value)
    if len(raw) > MAX_BUNDLE_BYTES:
        raise PublicationError("Output JSON exceeds its byte limit")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)


def _fresh(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise PublicationError("Output already exists; use a new destination")


def run_organize(args: argparse.Namespace) -> int:
    """Execute one bounded command; never echo private records or provider errors."""
    try:
        _run(args)
    except PublicationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ArtifactError:
        print(
            "ERROR: Native rendering failed; inspect retained private workspace evidence.",
            file=sys.stderr,
        )
        return 1
    except (OSError, ValueError, TypeError, KeyError):
        print(
            "ERROR: Invalid input or filesystem operation failed; no success claimed.",
            file=sys.stderr,
        )
        return 1
    return 0


def _run(args: argparse.Namespace) -> None:
    command = args.subcommand
    if command == "readiness":
        report = readiness(args.public_dir)
        print(canonical_bytes(report).decode(), end="")
        if args.require_complete and not report["content_complete"]:
            raise PublicationError(
                "Public content remains incomplete; inspect pending items in the report"
            )
        return
    if command == "review-update":
        output = _private(args.output, args.public_root)
        if any(
            output.is_relative_to(root.resolve())
            for root in (args.previous_public_dir, args.candidate_public_dir)
        ):
            raise PublicationError("Review output must be outside both public trees")
        _fresh(output)
        _write_private(output, review_update(args.previous_public_dir, args.candidate_public_dir))
        print("Private review report saved; no publication performed.")
        return
    if command in {"check-public", "site"}:
        bundle = verify_public_tree(args.public_dir)
        if command == "site":
            if args.output_dir.resolve().is_relative_to(args.public_dir.resolve()):
                raise PublicationError("Site output must be outside the verified publication tree")
            from symposium.organizing.site import build_site

            build_site(
                bundle, args.output_dir, assets_dir=args.public_dir, artifacts_dir=args.public_dir
            )
            print("Site built from verified public tree.")
        else:
            print("Public tree verified: " + content_hash(bundle))
        return

    boundary = args.public_root
    if command == "pull":
        mapping = _json(_private(args.mapping, boundary))
        snapshot = pull_snapshot(
            mapping,
            InstituteOSTransport(args.instituteos_root),
            public_root=boundary,
            workspace=_private(args.workspace, boundary),
        )
        print("Private snapshot saved: " + content_hash(snapshot))
        return
    if command == "project":
        workspace = _private(args.workspace, boundary)
        _fresh(workspace)
        snapshot = _json(_private(args.snapshot, boundary))
        bundle, ledger = project_snapshot(
            snapshot,
            _json(_private(args.event, boundary)),
            _json(_private(args.resources, boundary)),
        )
        workspace.mkdir(parents=True, mode=0o700)
        if args.portraits:
            from symposium.organizing.media import attach_public_portraits

            bundle, ledger = attach_public_portraits(
                bundle,
                ledger,
                workspace / "portraits",
                public_document=snapshot["mapping"]["public_document"],
            )
        _write_private(workspace / "program.json", bundle)
        _write_private(workspace / "approval-ledger.json", ledger)
        print(
            f"Projection saved privately; {len(ledger.get('warnings', []))} warnings recorded in approval-ledger.json."
        )
        return
    if command == "receipt-prepare":
        request = _json(_private(args.request, boundary))
        if not isinstance(request, dict) or set(request) != {
            "page_uri",
            "baseline_content",
            "receipt_markdown",
            "public_manifest_hash",
        }:
            raise PublicationError("Receipt request requires exactly the four documented fields")
        output = _private(args.output, boundary)
        _fresh(output)
        _write_private(output, prepare_receipt(**request))
        print("Private receipt plan prepared; no remote mutation.")
        return
    if command == "receipt-apply":
        output = _private(args.output, boundary)
        _fresh(output)
        plan = _json(_private(args.plan, boundary))
        # Create the evidence parent before the remote mutation, so a missing parent
        # cannot turn an otherwise verified write into an avoidable local failure.
        output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        result = apply_receipt(plan, InstituteOSTransport(args.instituteos_root), apply=args.apply)
        try:
            _write_private(output, result)
        except OSError:
            raise PublicationError(
                "Receipt readback succeeded but local evidence save failed; inspect the page before any retry"
            ) from None
        print("Receipt " + result["status"] + "; readback verified and private result saved.")
        return

    bundle = load_bundle(args.bundle)
    if command == "stage-public":
        snapshot = _json(_private(args.snapshot, boundary))
        ledger = _json(_private(args.ledger, boundary))
        stage_public(
            bundle,
            snapshot,
            ledger,
            args.output_dir,
            assets_dir=args.assets_dir,
            artifacts_dir=args.artifacts_dir,
            apply=args.apply,
            max_age_seconds=args.max_age_seconds,
        )
        print(
            "Approved public tree staged; verified bundle: "
            + content_hash(verify_public_tree(args.output_dir))
        )
    elif command == "book":
        workspace = _private(args.workspace, boundary)
        if args.render:
            if args.template_root is None:
                raise PublicationError("Native book rendering requires --template-root")
            render_abstract_book(bundle, workspace, args.template_root, timeout=args.timeout)
            print("Native abstract book rendered; evidence retained in private workspace.")
        else:
            if args.template_root is not None:
                raise PublicationError("--template-root requires --render")
            stage_abstract_book(bundle, workspace)
            print("Abstract book sources staged privately; no native render performed.")
    elif command == "dossiers":
        files = write_dossiers(bundle, _private(args.output_dir, boundary))
        print(f"Wrote {len(files)} public-content dossier files in private staging.")
    elif command == "participant-briefs":
        files = write_participant_briefs(bundle, _private(args.output_dir, boundary))
        print(f"Wrote {len(files)} public-content participant briefs in private staging.")
    elif command == "calendar":
        output = _private(args.output, boundary)
        output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        write_calendar(bundle, output)
        print("Public-content calendar staged privately; no invitations sent.")
    elif command == "artifact-index":
        write_artifact_index(bundle, _private(args.artifacts_dir, boundary))
        print("Artifact index bound to validated bundle.")
    else:
        raise PublicationError("Unknown organizing command")
