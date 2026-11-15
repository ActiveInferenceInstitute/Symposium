"""Check every package module with explicitly qualified third-party declarations."""

from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def verify_versions(expected: dict[str, str]) -> dict[str, str]:
    actual = {name: metadata.version(name) for name in expected}
    mismatches = {
        name: {"expected": version, "actual": actual[name]}
        for name, version in expected.items()
        if actual[name] != version
    }
    if mismatches:
        raise ValueError("Unqualified typing runtime: " + json.dumps(mismatches, sort_keys=True))
    return actual


def project_stub(spec: dict[str, Any], destination: Path) -> tuple[str, str]:
    source = Path(metadata.distribution(spec["distribution"]).locate_file(spec["path"]))
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError(f"Unqualified upstream declaration bytes: {source}")
    text = raw.decode("utf-8")
    for correction in spec["corrections"]:
        if text.count(correction["old"]) != correction["count"]:
            raise ValueError(f"Upstream declaration contract changed: {source}")
        text = text.replace(correction["old"], correction["new"])
    destination.write_text(text, encoding="utf-8")
    return str(source), str(destination)


def main() -> int:
    manifest = json.loads((ROOT / "typings/bindings.json").read_text(encoding="utf-8"))
    try:
        versions = verify_versions(manifest["versions"])
        with tempfile.TemporaryDirectory(prefix="symposium-types-") as directory:
            temporary = Path(directory)
            command = [
                sys.executable,
                "-B",
                "-m",
                "mypy",
                "--config-file",
                str(ROOT / "pyproject.toml"),
                "--show-error-codes",
                "--cache-dir",
                str(temporary / "cache"),
            ]
            for index, spec in enumerate(manifest["projections"]):
                source, shadow = project_stub(spec, temporary / f"upstream-{index}.pyi")
                command.extend(["--shadow-file", source, shadow])
            command.append(str(ROOT / "src"))
            environment = os.environ.copy()
            environment["MYPYPATH"] = str(ROOT / "typings")
            print(
                "Qualified typing dependencies: " + json.dumps(versions, sort_keys=True), flush=True
            )
            return subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode
    except (metadata.PackageNotFoundError, OSError, ValueError) as error:
        print(f"Typing qualification refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
