"""Tests for the analyze/generate CLI handler bodies.

These exercise the orchestration in ``cli/analyze.py`` and ``cli/generate.py``
(which the dispatch tests only route to, without executing). They mock the API
boundary (``APIClient.create``) — the repo explicitly endorses mocking — and then
assert on the real files the handlers write to disk.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


def _args(**kwargs):
    defaults = {
        "api_provider": None,
        "output_dir": "o",
        "log_level": "WARNING",
        "domain_file": None,
        "include_methods": False,
        "include_background_research": False,
        "include_curriculum": False,
        "include_column_summaries": False,
        "max_rows": 5,
        "catechism": "KarmaGAP",
        "catechisms_dir": None,
        "collaborators_file": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _presenter_dir(tmp_path, name="Test_Presenter"):
    d = tmp_path / name
    d.mkdir()
    (d / "openalex-group-by-20241103.csv").write_text(
        "topic,count\nActive Inference,12\nFree Energy,9\nBayesian,7\n"
    )
    (d / "works-20241103.csv").write_text(
        "title,publication_year,cited_by_count\nPaper A,2023,50\nPaper B,2022,30\n"
    )
    return d


def _participant_csv(tmp_path):
    p = tmp_path / "participants.csv"
    p.write_text(
        'Can we share this information publicly?,What is your name?,What is your email?,What are your affiliations?,What is your ORCID?,"What is your background & prior works? Feel free to provide as much information & links as you like.",What would be useful for you in the Symposium (pragmatic value)?,What would be interesting or informative for you to learn from the Symposium (epistemic value)?,"How are you applying Active Inference? What domain, stage?","What are the biggest hurdles or challenges facing Active Inference research and application?","What would help you learn and apply Active Inference? E.g. resource, tool, or community development.",How did you hear about the Symposium?,How could Active Inference applications make impact in 2026? (Think big!),Any other comments or questions?\n'
        'Yes,Alice,alice@x.edu,Uni,0000-0001-0000-0001,"PhD in neuroscience","practical","theory","Research, mid","implementation","mentorship","conference","impact","none"\n'
    )
    return p


def _profile_json(profile_dir):
    """Create a participant research profile JSON for the projects flow."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    f = profile_dir / "alice_research_profile.json"
    f.write_text(
        json.dumps(
            {
                "metadata": {"presenter": "Alice"},
                "content": "Alice researches active inference and machine learning.",
            }
        )
    )
    return f


def test_analyze_presenters_handler_writes_reports(tmp_path, monkeypatch):
    from symposium.cli import analyze

    _presenter_dir(tmp_path)  # creates <tmp>/Test_Presenter
    monkeypatch.setattr(
        analyze.APIClient,
        "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "analysis text"),
    )
    out = tmp_path / "out"
    analyze.analyze_presenters(_args(data_dir=str(tmp_path), output_dir=str(out)))

    report = out / "Test_Presenter" / "Test_Presenter_research_profile.md"
    assert report.exists()
    assert "analysis text" in report.read_text()


def test_analyze_participants_handler_writes_reports(tmp_path, monkeypatch):
    from symposium.cli import analyze

    csv_path = _participant_csv(tmp_path)
    monkeypatch.setattr(
        analyze.APIClient,
        "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "profile analysis"),
    )
    out = tmp_path / "out"
    analyze.analyze_participants(_args(csv_file=str(csv_path), output_dir=str(out)))

    report = out / "Alice" / "Alice_profile_analysis.md"
    assert report.exists()


def test_generate_profiles_handler_writes_reports(tmp_path, monkeypatch):
    from symposium.cli import generate

    _presenter_dir(tmp_path, "Test_Researcher")  # creates <tmp>/Test_Researcher
    monkeypatch.setattr(
        generate.APIClient,
        "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "profile"),
    )
    out = tmp_path / "out"
    generate.generate_profiles(
        _args(data_dir=str(tmp_path), output_dir=str(out), include_methods=True)
    )

    assert (out / "Test_Researcher" / "Test_Researcher_research_profile.md").exists()
    assert (out / "Test_Researcher" / "Test_Researcher_research_methods.md").exists()


def test_generate_projects_handler_writes_reports(tmp_path, monkeypatch):
    from symposium.cli import generate

    profiles_dir = tmp_path / "profiles"
    _profile_json(profiles_dir / "Alice")
    domain_file = tmp_path / "domain.md"
    domain_file.write_text("Active inference and cognitive science domain.")
    monkeypatch.setattr(
        generate.APIClient,
        "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "proposal text"),
    )
    out = tmp_path / "out"
    generate.generate_projects(
        _args(
            profiles_dir=str(profiles_dir),
            output_dir=str(out),
            domain_file=str(domain_file),
        )
    )

    # Proposal files are keyed by the participant name from the directory.
    assert (out / "Alice" / "Alice_project_proposal_KarmaGAP.md").exists()


def test_analyze_participant_backgrounds_handler(tmp_path, monkeypatch):
    from symposium.cli import analyze

    csv_path = _participant_csv(tmp_path)
    monkeypatch.setattr(
        analyze.APIClient,
        "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "background research"),
    )
    out = tmp_path / "out"
    analyze.analyze_participant_backgrounds(_args(csv_file=str(csv_path), output_dir=str(out)))

    assert not (out / "Alice" / "Alice_profile_analysis.md").exists()
    assert (out / "Alice" / "Alice_background_research.md").exists()


def test_generate_participant_curricula_handler(tmp_path, monkeypatch):
    from symposium.cli import analyze

    csv_path = _participant_csv(tmp_path)
    monkeypatch.setattr(
        analyze.APIClient,
        "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "curriculum"),
    )
    out = tmp_path / "out"
    analyze.generate_participant_curricula(_args(csv_file=str(csv_path), output_dir=str(out)))

    assert not (out / "Alice" / "Alice_profile_analysis.md").exists()
    assert (out / "Alice" / "Alice_curriculum.md").exists()


@pytest.mark.parametrize(
    "handler_name",
    [
        "analyze_presenters",
        "analyze_participants",
        "analyze_participant_backgrounds",
        "generate_participant_curricula",
        "generate_profiles",
        "generate_projects",
    ],
)
def test_handlers_honor_selected_config_and_forced_provider(
    tmp_path, monkeypatch, offline_api_requests, handler_name
):
    from symposium.cli import analyze, generate

    data = tmp_path / "presenters"
    data.mkdir()
    _presenter_dir(data, "Alice")
    profiles = tmp_path / "profiles"
    _profile_json(profiles / "Alice")
    csv_path = _participant_csv(tmp_path)
    domain = tmp_path / "domain.md"
    domain.write_text("Synthetic domain")
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "KarmaGAPGrants.md").write_text("Synthetic questions")
    selected = tmp_path / "selected.json"
    selected.write_text(
        json.dumps(
            {
                "api": {
                    "provider": "openrouter",
                    "openrouter": {"api_key": "file-router", "model": "selected-router"},
                    "perplexity": {"api_key": "file-perplexity", "model": "selected-perplexity"},
                }
            }
        )
    )
    (tmp_path / "config.json").write_text('{"api":{"provider":"invalid"}}')
    monkeypatch.setenv("OPENROUTER_API_KEY", "environment-router")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "environment-perplexity")
    output = tmp_path / "reports"
    args = _args(
        config=str(selected),
        data_dir=str(data),
        csv_file=str(csv_path),
        profiles_dir=str(profiles),
        domain_file=str(domain),
        catechisms_dir=str(templates),
        output_dir=str(output),
    )
    module = generate if handler_name in ("generate_profiles", "generate_projects") else analyze
    getattr(module, handler_name)(args)
    (request,) = offline_api_requests
    forced = handler_name == "analyze_participant_backgrounds"
    assert request.url.host == ("api.perplexity.ai" if forced else "openrouter.ai")
    key = "environment-perplexity" if forced else "environment-router"
    model = "selected-perplexity" if forced else "selected-router"
    assert request.headers["Authorization"] == f"Bearer {key}"
    assert json.loads(request.content)["model"] == model
    (report,) = output.rglob("*.json")
    assert json.loads(report.read_text())["content"] == "Offline provider response"


def test_combined_participant_background_uses_perplexity(tmp_path, offline_api_requests):
    from symposium.cli import analyze

    selected = tmp_path / "selected.json"
    selected.write_text(
        json.dumps(
            {
                "api": {
                    "provider": "openrouter",
                    "openrouter": {"api_key": "offline-router"},
                    "perplexity": {"api_key": "offline-perplexity"},
                }
            }
        )
    )
    output = tmp_path / "reports"
    analyze.analyze_participants(
        _args(
            config=str(selected),
            csv_file=str(_participant_csv(tmp_path)),
            output_dir=str(output),
            include_background_research=True,
        )
    )
    assert [request.url.host for request in offline_api_requests] == [
        "openrouter.ai",
        "api.perplexity.ai",
    ]
    for kind in ("profile_analysis", "background_research"):
        report = output / "Alice" / f"Alice_{kind}.json"
        assert json.loads(report.read_text())["content"] == "Offline provider response"


@pytest.mark.parametrize("flow", ["presenters", "profiles", "projects"])
@pytest.mark.parametrize("failure", ["payment", "persistence", "empty"])
def test_real_cli_exit_rejects_incomplete_work_and_preserves_files(tmp_path, flow, failure):
    data = tmp_path / "inputs"
    data.mkdir()
    if failure != "empty":
        for name in ("Alice", "Bob"):
            if flow == "projects":
                _profile_json(data / name)
            else:
                _presenter_dir(data, name)
    output = tmp_path / "reports"
    if flow == "projects":
        domain = tmp_path / "domain.md"
        domain.write_text("Synthetic domain")
        (tmp_path / "KarmaGAPGrants.md").write_text("Synthetic questions")
        arguments = [
            "generate",
            "projects",
            "--profiles-dir",
            str(data),
            "--domain-file",
            str(domain),
            "--catechisms-dir",
            str(tmp_path),
        ]
    else:
        arguments = [
            "analyze" if flow == "presenters" else "generate",
            flow,
            "--data-dir",
            str(data),
        ]
    arguments.extend(["--output-dir", str(output)])
    script = """
import runpy
import sys
from types import SimpleNamespace
from symposium.core.api import APIClient, PaymentRequiredError
from symposium.io.writers import ReportWriter

failure = sys.argv.pop(1)
calls = 0
writes = 0

def response(*args, **kwargs):
    global calls
    calls += 1
    if failure == "payment" and calls == 2:
        raise PaymentRequiredError("Cannot generate without credits", "openrouter")
    return "Persisted offline response"

APIClient.create = staticmethod(lambda **kwargs: SimpleNamespace(get_response=response))
original_save = ReportWriter.save_json_report

def save_json(*args, **kwargs):
    global writes
    writes += 1
    if failure == "persistence" and writes == 2:
        raise OSError("Synthetic storage failure")
    return original_save(*args, **kwargs)

ReportWriter.save_json_report = staticmethod(save_json)
sys.argv[0] = "symposium"
runpy.run_module("symposium", run_name="__main__")
"""
    environment = dict(os.environ)
    for key in (
        "API_PROVIDER",
        "PERPLEXITY_API_KEY",
        "OPENROUTER_API_KEY",
        "SYMPOSIUM_YEAR",
        "SYMPOSIUM_DATA_DIR",
        "SYMPOSIUM_OUTPUTS_DIR",
    ):
        environment.pop(key, None)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    result = subprocess.run(
        [sys.executable, "-c", script, failure, *arguments],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    reports = list(output.rglob("*.json"))
    markdown = list(output.rglob("*.md"))
    if failure == "empty":
        assert reports == markdown == []
    else:
        assert len(reports) == 1
        assert json.loads(reports[0].read_text())["content"] == "Persisted offline response"
        assert "Persisted offline response" in reports[0].with_suffix(".md").read_text()
        assert len(markdown) == (2 if failure == "persistence" else 1)
