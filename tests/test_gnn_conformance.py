"""Fail-closed behaviour of scripts/gnn_conformance.py without the GNN package.

The real parser lives in an isolated gate environment, so these tests inject minimal
stand-ins for the ``gnn`` modules the script imports lazily.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "gnn_conformance.py"
PINNED_VERSION = json.loads((ROOT / ".github" / "gnn-pin.json").read_text(encoding="utf-8"))[
    "tag"
].removeprefix("v")


@pytest.fixture
def conformance():
    spec = importlib.util.spec_from_file_location("gnn_conformance_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_fake_gnn(
    monkeypatch: pytest.MonkeyPatch, outcome: object, *, version: str = PINNED_VERSION
) -> list[dict]:
    syntax_calls: list[dict] = []

    class FakeChecker:
        def validate_gnn_files(self, model_dir, output_dir):
            return outcome

    def validate_gnn_syntax(text, **kwargs):
        syntax_calls.append(kwargs)
        return True, []

    def parse_gnn_formal(path):
        return types.SimpleNamespace(parse_errors=[])

    gnn = types.ModuleType("gnn")
    gnn.__version__ = version
    modules = {
        "gnn": gnn,
        "gnn.parsers": types.ModuleType("gnn.parsers"),
        "gnn.parsers.basic": types.SimpleNamespace(
            parse_gnn_formal=parse_gnn_formal, validate_gnn_syntax=validate_gnn_syntax
        ),
        "gnn.type_checker": types.SimpleNamespace(GNNTypeChecker=FakeChecker),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    return syntax_calls


# 2 is the sentinel the original ``not`` check let through; 1 is truthy and equal to
# True, so only an identity check rejects it. Both are covered.
@pytest.mark.parametrize("outcome", [2, 1, False, None, 0])
def test_type_checker_non_true_outcome_fails(conformance, monkeypatch, tmp_path, outcome):
    _install_fake_gnn(monkeypatch, outcome)
    sketch = tmp_path / "a.gnn.md"
    sketch.write_text("# model\n", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(SystemExit) as excinfo:
        conformance.type_check([sketch], out)
    assert f"returned {outcome!r}" in str(excinfo.value)


def test_type_checker_true_passes(conformance, monkeypatch, tmp_path):
    _install_fake_gnn(monkeypatch, True)
    sketch = tmp_path / "a.gnn.md"
    sketch.write_text("# model\n", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    conformance.type_check([sketch], out)


def test_syntax_check_treats_text_as_content(conformance, monkeypatch, tmp_path):
    calls = _install_fake_gnn(monkeypatch, True)
    sketch = tmp_path / "a.gnn.md"
    sketch.write_text("# model\n", encoding="utf-8")
    conformance.check_parsed(sketch)
    assert calls == [{"is_content": True}]


def _patch_exemplar_download(conformance, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Serve synthetic exemplar content in place of the network download."""
    downloads: list[str] = []

    def urlretrieve(url, target):
        downloads.append(url)
        Path(target).write_text("# exemplar\n", encoding="utf-8")

    request = types.SimpleNamespace(urlretrieve=urlretrieve)
    monkeypatch.setattr(conformance, "urllib", types.SimpleNamespace(request=request))
    return downloads


def test_main_labels_repository_content_receipt(conformance, monkeypatch, tmp_path, capsys):
    _install_fake_gnn(monkeypatch, True)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    (tmp_path / "one.gnn.md").write_text("# model\n", encoding="utf-8")
    (tmp_path / "two.gnn.md").write_text("# model\n", encoding="utf-8")

    assert conformance.main() == 0

    receipt = json.loads(capsys.readouterr().out)
    assert (receipt["source"], receipt["result"]) == ("repository", "repository-content-passed")
    assert receipt["models"] == 2
    assert receipt["gnn-version"] == PINNED_VERSION


def test_main_labels_pinned_exemplar_baseline_receipt(conformance, monkeypatch, tmp_path, capsys):
    _install_fake_gnn(monkeypatch, True)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    downloads = _patch_exemplar_download(conformance, monkeypatch)

    assert conformance.main() == 0

    receipt = json.loads(capsys.readouterr().out)
    assert (receipt["source"], receipt["result"]) == (
        "pinned-exemplar",
        "pinned-exemplar-baseline-passed",
    )
    assert receipt["models"] == 1
    assert receipt["gnn-version"] == PINNED_VERSION
    assert len(downloads) == 1
    assert downloads[0].endswith(conformance.EXEMPLAR_PATH)
    assert conformance.load_pin()["revision"] in downloads[0]
