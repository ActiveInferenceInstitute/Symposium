"""Fail-closed behaviour of scripts/gnn_conformance.py without the GNN package.

The real parser lives in an isolated gate environment, so these tests inject minimal
stand-ins for the ``gnn`` modules the script imports lazily.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "gnn_conformance.py"


@pytest.fixture
def conformance():
    spec = importlib.util.spec_from_file_location("gnn_conformance_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_fake_gnn(monkeypatch: pytest.MonkeyPatch, outcome: object) -> list[dict]:
    syntax_calls: list[dict] = []

    class FakeChecker:
        def validate_gnn_files(self, model_dir, output_dir):
            return outcome

    def validate_gnn_syntax(text, **kwargs):
        syntax_calls.append(kwargs)
        return True, []

    def parse_gnn_formal(path):
        return types.SimpleNamespace(parse_errors=[])

    modules = {
        "gnn": types.ModuleType("gnn"),
        "gnn.parsers": types.ModuleType("gnn.parsers"),
        "gnn.parsers.basic": types.SimpleNamespace(
            parse_gnn_formal=parse_gnn_formal, validate_gnn_syntax=validate_gnn_syntax
        ),
        "gnn.type_checker": types.SimpleNamespace(GNNTypeChecker=FakeChecker),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    return syntax_calls


@pytest.mark.parametrize("outcome", [2, False, None, 0])
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
