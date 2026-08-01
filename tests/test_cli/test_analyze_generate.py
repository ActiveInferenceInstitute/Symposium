"""Tests for the analyze/generate CLI handler bodies.

These exercise the orchestration in ``cli/analyze.py`` and ``cli/generate.py``
(which the dispatch tests only route to, without executing). They mock the API
boundary (``APIClient.create``) — the repo explicitly endorses mocking — and then
assert on the real files the handlers write to disk.
"""

import argparse
import json
from unittest.mock import Mock


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
        "Can we share this information publicly?,What is your name?,What is your email?,What are your affiliations?,What is your ORCID?,\"What is your background & prior works? Feel free to provide as much information & links as you like.\",What would be useful for you in the Symposium (pragmatic value)?,What would be interesting or informative for you to learn from the Symposium (epistemic value)?,\"How are you applying Active Inference? What domain, stage?\",\"What are the biggest hurdles or challenges facing Active Inference research and application?\",\"What would help you learn and apply Active Inference? E.g. resource, tool, or community development.\",How did you hear about the Symposium?,How could Active Inference applications make impact in 2026? (Think big!),Any other comments or questions?\n"
        "Yes,Alice,alice@x.edu,Uni,0000-0001-0000-0001,\"PhD in neuroscience\",\"practical\",\"theory\",\"Research, mid\",\"implementation\",\"mentorship\",\"conference\",\"impact\",\"none\"\n"
    )
    return p


def _profile_json(profile_dir):
    """Create a participant research profile JSON for the projects flow."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    f = profile_dir / "alice_research_profile.json"
    f.write_text(json.dumps({
        "metadata": {"presenter": "Alice"},
        "content": "Alice researches active inference and machine learning.",
    }))
    return f


def test_analyze_presenters_handler_writes_reports(tmp_path, monkeypatch):
    from symposium.cli import analyze

    _presenter_dir(tmp_path)  # creates <tmp>/Test_Presenter
    monkeypatch.setattr(
        analyze.APIClient, "create",
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
        analyze.APIClient, "create",
        lambda *a, **k: Mock(get_response=lambda *a, **k: "profile analysis"),
    )
    out = tmp_path / "out"
    analyze.analyze_participants(
        _args(csv_file=str(csv_path), output_dir=str(out))
    )

    report = out / "Alice" / "Alice_profile_analysis.md"
    assert report.exists()


def test_generate_profiles_handler_writes_reports(tmp_path, monkeypatch):
    from symposium.cli import generate

    _presenter_dir(tmp_path, "Test_Researcher")  # creates <tmp>/Test_Researcher
    monkeypatch.setattr(
        generate.APIClient, "create",
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
        generate.APIClient, "create",
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
