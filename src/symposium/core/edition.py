"""Offline edition paths, safe scaffolding, and readiness validation."""

import csv
import ctypes
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from symposium.core.participant_schema import load_participants, participant_headers


class EditionError(ValueError):
    """Edition input is invalid or conflicts with existing paths."""


@dataclass(frozen=True, slots=True)
class Edition:
    """Paths belonging to one symposium year."""

    year: int = 2026
    data_dir: Path = Path("data")
    outputs_dir: Path = Path("outputs")

    def __post_init__(self) -> None:
        if type(self.year) is not int or not 2000 <= self.year <= 2100:
            raise EditionError("Edition year must be an integer between 2000 and 2100")
        object.__setattr__(self, "data_dir", Path(self.data_dir))
        object.__setattr__(self, "outputs_dir", Path(self.outputs_dir))

    @property
    def input_dir(self) -> Path:
        return self.data_dir / "inputs" / f"aif_{self.year}"

    @property
    def participants_csv(self) -> Path:
        return self.input_dir / "Public_Participant_Information.csv"

    @property
    def presenters_dir(self) -> Path:
        return self.input_dir / "presenters"

    @property
    def output_dir(self) -> Path:
        return self.outputs_dir / f"{self.year}_symposium"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Counts and actionable diagnostics without personal records."""

    participants: int
    presenters: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


def _publish_directory(source: Path, destination: Path) -> None:
    """Atomically publish without replacing even an empty existing directory."""
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        result = rename(os.fsencode(source), os.fsencode(destination), 4)
    elif sys.platform.startswith("linux"):
        rename = libc.renameat2
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        result = rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    else:
        raise EditionError("Atomic edition initialization requires macOS or Linux")
    if result:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def init_edition(edition: Edition) -> bool:
    """Publish a complete empty scaffold once; never modify an existing edition."""
    if edition.output_dir.is_symlink() or (
        edition.output_dir.exists() and not edition.output_dir.is_dir()
    ):
        raise EditionError("Edition output path conflicts with a file or symbolic link")
    for ancestor in edition.output_dir.parents:
        if ancestor.is_symlink() or (ancestor.exists() and not ancestor.is_dir()):
            raise EditionError("Edition output parent must be a real directory")
    target = edition.input_dir
    if target.exists() or target.is_symlink():
        if target.is_symlink() or not target.is_dir():
            raise EditionError("Edition input path must be a real directory")
        report = validate_edition(edition)
        required = [
            target / "presenters/README.md",
            target / "templates/works-example.csv",
            target / "templates/openalex-group-by-example.csv",
        ]
        if report.errors or not all(path.is_file() for path in required):
            raise EditionError(
                "Existing edition conflicts with scaffold; no files changed. "
                + "; ".join(report.errors)
            )
        return False
    for ancestor in target.parents:
        if ancestor.is_symlink() or (ancestor.exists() and not ancestor.is_dir()):
            raise EditionError("Edition input parent must be a real directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".aif_{edition.year}-", dir=target.parent
    ) as temporary:
        stage = Path(temporary) / "edition"
        stage.mkdir()
        (stage / "presenters").mkdir()
        (stage / "templates").mkdir()
        with (stage / "Public_Participant_Information.csv").open(
            "w", encoding="utf-8", newline=""
        ) as stream:
            csv.writer(stream).writerow(participant_headers(edition.year))
        (stage / "presenters/README.md").write_text(
            "# Presenter inputs\n\nAwaiting confirmed presenter data. Create one folder per presenter, using their name "
            "(spaces, Unicode letters, hyphens and underscores are supported). Each folder needs exactly one "
            "`works-*.csv` and one `openalex-group-by-*.csv`. Copy header-only templates from `../templates/` "
            "and populate them with verified data. Empty template rows do not count as presenter data.\n",
            encoding="utf-8",
        )
        (stage / "templates/works-example.csv").write_text(
            "title,publication_year,cited_by_count\n", encoding="utf-8"
        )
        (stage / "templates/openalex-group-by-example.csv").write_text(
            "topic,count\n", encoding="utf-8"
        )
        (stage / "schedule.json").write_text('{"events": []}\n', encoding="utf-8")
        _publish_directory(stage, target)
    return True


def _csv_rows(path: Path, *, topics: bool = False) -> int:
    """Validate canonical CSVs and historical OpenAlex topic exports."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        headers = next(reader, [])
        if topics and headers and headers[0].strip() == "Primary Topic Id":
            headers = next(reader, [])
        normalized = [header.strip().casefold() for header in headers]
        required = {"title", "publication_year", "cited_by_count"}
        if topics:
            required = {"count"}
            if not {"topic", "name", "display_name"}.intersection(normalized):
                raise EditionError("Topic CSV needs topic (or name/display_name) and count columns")
        if not required.issubset(normalized):
            raise EditionError(
                "CSV missing columns: " + ", ".join(sorted(required - set(normalized)))
            )
        nonempty = [header for header in normalized if header]
        if len(nonempty) != len(set(nonempty)):
            raise EditionError("CSV has duplicate headers")
        count = 0
        for index, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(headers):
                raise EditionError(f"CSV row {index} has incorrect column count")
            values = dict(zip(normalized, row))
            label = (
                next(
                    (
                        values[key].strip()
                        for key in ("topic", "name", "display_name")
                        if key in values
                    ),
                    "",
                )
                if topics
                else values["title"].strip()
            )
            if not label:
                raise EditionError(f"CSV row {index} has an empty title/topic")
            numeric = ("count",) if topics else ("publication_year", "cited_by_count")
            if any(not re.fullmatch(r"[0-9]+", values[key].strip()) for key in numeric):
                raise EditionError(f"CSV row {index} requires nonnegative integer counts/year")
            count += 1
        return count


def validate_edition(edition: Edition, *, require_data: bool = False) -> ValidationResult:
    """Validate readiness locally without making API calls or exposing records."""
    errors: list[str] = []
    warnings: list[str] = []
    participants = 0
    presenters = 0
    try:
        participants = len(load_participants(edition.participants_csv))
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(f"Participant CSV: {exc}")
    if not edition.presenters_dir.is_dir():
        errors.append("Missing presenters directory")
    else:
        folders = sorted(edition.presenters_dir.iterdir())
        safe_names: set[str] = set()
        from symposium.io.writers import ReportWriter

        for folder in folders:
            if folder.name == "README.md" and folder.is_file():
                continue
            if not folder.is_dir() or folder.is_symlink():
                errors.append("Presenters directory contains an unexpected file or symbolic link")
                continue
            safe = ReportWriter.sanitize_filename(folder.name).casefold()
            if (
                not safe
                or folder.name.strip() != folder.name
                or any(
                    not (character.isalnum() or character in " _-'.") for character in folder.name
                )
            ):
                errors.append(
                    "Presenter folder has an invalid name; use a person name with spaces, hyphens or underscores"
                )
                continue
            if safe in safe_names:
                errors.append("Presenter folder names collide after filename sanitization")
                continue
            safe_names.add(safe)
            works = list(folder.glob("works-*.csv"))
            topics = list(folder.glob("openalex-group-by-*.csv"))
            if len(works) != 1 or len(topics) != 1:
                errors.append(
                    "Incomplete presenter folder: expected exactly one works-*.csv and one openalex-group-by-*.csv"
                )
                continue
            try:
                if not _csv_rows(works[0]) or not _csv_rows(topics[0], topics=True):
                    errors.append(
                        "Incomplete presenter folder: works and topic CSVs must contain data rows"
                    )
                    continue
            except (OSError, ValueError, UnicodeError, csv.Error) as exc:
                errors.append(f"Presenter CSV: {exc}")
                continue
            presenters += 1
    if not participants:
        warnings.append("Awaiting public participant data (0 consenting participants)")
    if not presenters:
        warnings.append("Awaiting presenter data (0 complete presenters)")
    if require_data and (not participants or not presenters):
        errors.append(
            "--require-data needs at least one public participant and one complete presenter"
        )
    return ValidationResult(participants, presenters, tuple(errors), tuple(warnings))
