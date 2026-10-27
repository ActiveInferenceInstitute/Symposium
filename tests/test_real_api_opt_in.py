"""Exercise real-api opt-in using local sentinel tests without provider calls."""

import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest


@pytest.mark.parametrize(
    ("options", "runs_live_probe"),
    [((), False), (("-m", "real_api"), False), (("--run-real-api",), True)],
)
def test_real_api_requires_explicit_opt_in(tmp_path, options, runs_live_probe):
    repository = Path(__file__).resolve().parents[1]
    marker = tmp_path / "live-probe-ran"
    probe = tmp_path / "test_local_probe.py"
    probe.write_text(
        "from pathlib import Path\nimport pytest\n"
        "@pytest.mark.real_api\n"
        "def test_live_probe():\n"
        f"    Path({str(marker)!r}).write_text('local only')\n"
        "def test_ordinary():\n    assert 2 + 2 == 4\n"
    )
    config = tmp_path / "pytest.ini"
    config.write_text("[pytest]\nmarkers = real_api: explicitly enabled provider tests\n")
    report = tmp_path / "result.xml"
    env = {
        **os.environ,
        "PYTHONPATH": str(repository),
        "PERPLEXITY_API_KEY": "synthetic-unused-key",
        "OPENROUTER_API_KEY": "synthetic-unused-key",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--noconftest",
            "-p",
            "tests.conftest",
            "-c",
            str(config),
            "-o",
            f"cache_dir={tmp_path / 'cache'}",
            f"--junitxml={report}",
            *options,
            str(probe),
        ],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert marker.exists() is runs_live_probe
    cases = ElementTree.parse(report).findall(".//testcase")
    live = next(case for case in cases if case.attrib["name"] == "test_live_probe")
    assert (live.find("skipped") is None) is runs_live_probe
    if "-m" not in options:
        assert any(case.attrib["name"] == "test_ordinary" for case in cases)
