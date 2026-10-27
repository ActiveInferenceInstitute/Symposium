"""Offline edition administration commands."""

import argparse
from pathlib import Path

from symposium.core.config import Config
from symposium.core.edition import Edition, init_edition, validate_edition


def add_edition_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register edition commands alongside existing command groups."""
    parser = subparsers.add_parser("edition", help="Initialize and validate symposium editions")
    commands = parser.add_subparsers(dest="subcommand", required=True)
    for command in ("init", "validate"):
        child = commands.add_parser(command)
        child.add_argument("--year", type=int, default=None)
        child.add_argument("--data-dir", default=None)
        child.add_argument("--output-dir", default=None)
        if command == "validate":
            child.add_argument("--require-data", action="store_true")


def run_edition(args: argparse.Namespace) -> int:
    """Print bounded readiness diagnostics and return a process status."""
    try:
        config_file = getattr(args, "config", None)
        config = Config(config_file=Path(config_file) if config_file else None)
        edition = Edition(
            year=args.year if args.year is not None else config.get("edition.year"),
            data_dir=args.data_dir if args.data_dir is not None else config.get_path("data_dir"),
            outputs_dir=args.output_dir
            if args.output_dir is not None
            else config.get_path("outputs_dir"),
        )
        if args.subcommand == "init":
            created = init_edition(edition)
            print(
                f"Edition {edition.year}: "
                + ("initialized" if created else "already initialized; no files changed")
            )
            print(f"Inputs: {edition.input_dir}; outputs: {edition.output_dir}")
            return 0
        report = validate_edition(edition, require_data=args.require_data)
        print(
            f"Edition {edition.year}: {report.participants} public participants, {report.presenters} complete presenters"
        )
        for warning in report.warnings:
            print(f"WARNING: {warning}")
        for error in report.errors:
            print(f"ERROR: {error}")
        return 0 if report.valid else 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
