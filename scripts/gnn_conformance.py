"""Verify the pinned GNN importer and the repository's GNN sketches.

Reads ``.github/gnn-pin.json`` (schema ``gnn-importer-pin/v1``) and checks the
installed parser against that pin, so the pin file is the only place the revision
is written. When the repository has no ``*.gnn.md`` sketch it checks the pinned
upstream exemplar instead; that is a parser/pin baseline, not a claim that this
repository contains a model.

Run through ``./gate.sh gnn``, which creates the isolated parser environment.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = ROOT / ".github" / "gnn-pin.json"
EXEMPLAR_PATH = "input/gnn_files/basics/static_perception.md"
REQUIRED_FIELDS = ("schema", "repository", "revision", "tag")


def load_pin(path: Path = PIN_PATH) -> dict[str, str]:
    """Load and validate the pin file, refusing any other schema."""
    pin = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(pin, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    missing = [field for field in REQUIRED_FIELDS if not pin.get(field)]
    if missing:
        raise SystemExit(f"{path} is missing fields: {', '.join(missing)}")
    if pin["schema"] != "gnn-importer-pin/v1":
        raise SystemExit(f"{path} has unsupported schema {pin['schema']!r}")
    return pin


def check_parsed(path: Path) -> None:
    """Require a clean parse and clean syntax for one sketch."""
    from gnn.parsers.basic import parse_gnn_formal, validate_gnn_syntax

    parsed = parse_gnn_formal(path)
    if parsed is None or getattr(parsed, "parse_errors", None):
        raise SystemExit(f"{path} did not parse cleanly")
    valid, errors = validate_gnn_syntax(path.read_text(encoding="utf-8"), is_content=True)
    if not valid:
        raise SystemExit(f"{path} syntax errors: {errors!r}")


def type_check(models: list[Path], output_dir: Path) -> None:
    """Run the pinned type checker over the sketches copied into ``models``."""
    from gnn.type_checker import GNNTypeChecker

    model_dir = output_dir / "models"
    model_dir.mkdir()
    for index, sketch in enumerate(models):
        shutil.copy2(sketch, model_dir / f"{index:03d}_{sketch.name}")
    # validate_gnn_files returns True (every file valid), 2 (invalid files or no
    # files found) or False (hard failure); a bare ``not`` would let 2 through.
    outcome = GNNTypeChecker().validate_gnn_files(model_dir, output_dir)
    if outcome is not True:
        raise SystemExit(
            f"GNN type checker did not accept {len(models)} sketch(es) (returned {outcome!r})"
        )


def requirement(pin: dict[str, str]) -> str:
    """PEP 508 direct reference for the pinned revision (used for the install)."""
    return f"generalized-notation-notation @ git+https://github.com/{pin['repository']}.git@{pin['revision']}"


def main() -> int:
    if "--spec" in sys.argv[1:]:
        print(requirement(load_pin()))
        return 0

    import gnn

    pin = load_pin()
    expected_version = pin["tag"].removeprefix("v")
    if gnn.__version__ != expected_version:
        raise SystemExit(f"installed GNN {gnn.__version__!r} does not match pin tag {pin['tag']!r}")

    sketches = sorted(ROOT.rglob("*.gnn.md"))
    with tempfile.TemporaryDirectory(prefix="gnn-conformance-") as tmp:
        output_dir = Path(tmp)
        if sketches:
            for sketch in sketches:
                check_parsed(sketch)
            type_check(sketches, output_dir)
            source, checked = "repository", len(sketches)
        else:
            exemplar_url = (
                f"https://raw.githubusercontent.com/{pin['repository']}/"
                f"{pin['revision']}/{EXEMPLAR_PATH}"
            )
            exemplar = output_dir / Path(EXEMPLAR_PATH).name
            urllib.request.urlretrieve(exemplar_url, exemplar)
            check_parsed(exemplar)
            type_check([exemplar], output_dir)
            source, checked = "pinned-exemplar", 1

    result = (
        "repository-content-passed" if source == "repository" else "pinned-exemplar-baseline-passed"
    )

    print(
        json.dumps(
            {
                "gnn-version": gnn.__version__,
                "pin-revision": pin["revision"],
                "models": checked,
                "source": source,
                "result": result,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
