"""Tests for the io.readers module (ReportReader)."""

import pandas as pd
import pytest

from symposium.io.readers import ReportReader


def test_read_markdown(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("# Title\nbody")
    assert ReportReader.read_markdown(p) == "# Title\nbody"


def test_read_markdown_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ReportReader.read_markdown(tmp_path / "missing.md")


def test_read_json(tmp_path):
    p = tmp_path / "a.json"
    p.write_text('{"k": "v", "n": 1}')
    assert ReportReader.read_json(p) == {"k": "v", "n": 1}


def test_read_csv(tmp_path):
    p = tmp_path / "a.csv"
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_csv(p, index=False)
    df = ReportReader.read_csv(p)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]


def test_read_catechism(tmp_path):
    p = tmp_path / "cat.md"
    p.write_text("template body")
    assert ReportReader.read_catechism(p) == "template body"


def test_read_domain_knowledge(tmp_path):
    p = tmp_path / "domain.md"
    p.write_text("domain knowledge")
    assert ReportReader.read_domain_knowledge(p) == "domain knowledge"


def test_read_system_prompt(tmp_path):
    p = tmp_path / "sys.md"
    p.write_text("you are helpful")
    assert ReportReader.read_system_prompt(p) == "you are helpful"


def test_list_files_non_recursive(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.md").write_text("x")
    (tmp_path / "sub" / "b.md").write_text("x")
    files = ReportReader.list_files_in_directory(tmp_path, "*.md", recursive=False)
    names = [f.name for f in files]
    assert "a.md" in names
    assert "b.md" not in names  # b.md is one level down


def test_list_files_recursive(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.md").write_text("x")
    (tmp_path / "sub" / "b.md").write_text("x")
    files = ReportReader.list_files_in_directory(tmp_path, "*.md", recursive=True)
    assert {f.name for f in files} == {"a.md", "b.md"}


def test_list_files_missing_dir_returns_empty(tmp_path):
    assert ReportReader.list_files_in_directory(tmp_path / "nope", "*.md") == []
