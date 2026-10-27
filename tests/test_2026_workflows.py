"""Offline regression checks for the 2026 organizer workflows."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from symposium.analysis.participants import ParticipantAnalyzer
from symposium.core.api import PaymentRequiredError
from symposium.core.config import Config

ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    spec = importlib.util.spec_from_file_location("symposium_runner", ROOT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecordingProvider:
    def __init__(self, error=None):
        self.calls = []
        self.error = error

    def get_response(self, prompt, system_prompt=None, **kwargs):
        self.calls.append(prompt)
        if self.error:
            raise self.error
        return "Offline test response"


def registration(tmp_path):
    path = tmp_path / "participants.csv"
    path.write_text(
        "share_publicly,name,background,learning_needs\nYes,Test Person,Research,Mathematics\n",
        encoding="utf-8",
    )
    return path


def test_config_redaction_keeps_live_credentials(tmp_path):
    config = Config(load_env=False)
    config.set("api.perplexity.api_key", "test-credential")
    config.save(tmp_path / "config.json")
    assert config.get_api_key("perplexity") == "test-credential"
    assert (
        json.loads((tmp_path / "config.json").read_text())["api"]["perplexity"]["api_key"]
        == "***REDACTED***"
    )
    detached = config.to_dict()
    detached["api"]["perplexity"]["model"] = "changed"
    assert config.get("api.perplexity.model") == "sonar"


@pytest.mark.parametrize("value", ["not-a-year", "1999", "2101"])
def test_invalid_environment_year(monkeypatch, value):
    monkeypatch.setenv("SYMPOSIUM_YEAR", value)
    with pytest.raises(ValueError):
        Config(load_env=False)


def test_column_summary_payment_error_stops_immediately(tmp_path):
    provider = RecordingProvider(PaymentRequiredError("test payment failure", "openrouter"))
    with pytest.raises(PaymentRequiredError):
        ParticipantAnalyzer(provider).generate_column_summaries(
            registration(tmp_path), tmp_path / "summaries"
        )
    assert len(provider.calls) == 1


def test_background_only_does_not_generate_profile(tmp_path):
    provider = RecordingProvider()
    results = ParticipantAnalyzer(provider).analyze_all_participants(
        registration(tmp_path),
        tmp_path / "reports",
        include_background_research=True,
        include_profile=False,
    )
    assert list(results["Test Person"]) == ["background_research"]
    assert len(provider.calls) == 1
    assert not list((tmp_path / "reports").rglob("*profile_analysis*"))
    assert list((tmp_path / "reports").rglob("*background_research.md"))


def test_curriculum_only_does_not_generate_profile(tmp_path):
    provider = RecordingProvider()
    results = ParticipantAnalyzer(provider).analyze_all_participants(
        registration(tmp_path),
        tmp_path / "reports",
        include_curriculum=True,
        include_profile=False,
    )
    assert list(results["Test Person"]) == ["curriculum"]
    assert len(provider.calls) == 1


def test_runner_uses_edition_config_and_redacts_keys(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("SYMPOSIUM_YEAR", raising=False)
    monkeypatch.delenv("SYMPOSIUM_DATA_DIR", raising=False)
    monkeypatch.delenv("SYMPOSIUM_OUTPUTS_DIR", raising=False)
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "edition": {"year": 2025},
                "paths": {
                    "data_dir": str(tmp_path / "data"),
                    "outputs_dir": str(tmp_path / "outputs"),
                },
                "api": {"perplexity": {"api_key": "fixture-secret"}},
            }
        )
    )
    runner = load_runner().SymposiumRunner(config_file=config_file)
    assert runner.edition.year == 2025
    assert (
        runner.edition.participants_csv
        == tmp_path / "data/inputs/aif_2025/Public_Participant_Information.csv"
    )
    assert runner.edition.output_dir == tmp_path / "outputs/2025_symposium"
    assert not (tmp_path / "outputs").exists()
    runner.show_config_details()
    assert "fixture-secret" not in capsys.readouterr().out
    assert load_runner().SymposiumRunner(year=2026, config_file=config_file).edition.year == 2026


def test_runner_import_has_no_filesystem_or_cwd_side_effects(tmp_path):
    code = "import importlib.util,os; from pathlib import Path; before=Path.cwd(); spec=importlib.util.spec_from_file_location('runner',os.environ['RUNNER_PATH']); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert Path.cwd()==before; assert not list(before.iterdir())"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env={**os.environ, "RUNNER_PATH": str(ROOT / "run.py")},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("year", [2025, 2026])
def test_runner_real_startup_and_exit(tmp_path, year):
    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "paths": {
                    "data_dir": str(tmp_path / "data"),
                    "outputs_dir": str(tmp_path / "outputs"),
                }
            }
        )
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "run.py"), "--year", str(year), "--config", str(cfg)],
        input="9\n",
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert f"SYMPOSIUM {year}" in result.stdout
    assert not (tmp_path / "outputs").exists()


def test_runner_rejects_invalid_year():
    result = subprocess.run(
        [sys.executable, str(ROOT / "run.py"), "--year", "1999"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_versions_agree():
    from importlib.metadata import version

    import symposium

    assert symposium.__version__ == version("symposium")
    assert f'version = "{symposium.__version__}"' in (ROOT / "pyproject.toml").read_text()


@pytest.mark.parametrize(
    "handler_name",
    ["analyze_participants", "analyze_participant_backgrounds", "generate_participant_curricula"],
)
def test_cli_reports_batch_failure(tmp_path, monkeypatch, handler_name):
    from argparse import Namespace

    from symposium.cli import analyze

    provider = RecordingProvider(PaymentRequiredError("test payment failure", "openrouter"))
    monkeypatch.setattr(analyze.APIClient, "create", lambda **kwargs: provider)
    args = Namespace(
        csv_file=str(registration(tmp_path)),
        output_dir=str(tmp_path / "out"),
        api_provider="openrouter",
        include_background_research=False,
        include_curriculum=False,
        include_column_summaries=False,
    )
    with pytest.raises(RuntimeError, match="processing incomplete"):
        getattr(analyze, handler_name)(args)
    assert len(provider.calls) == 1


def test_empty_registrations_fail_before_client_creation(tmp_path, monkeypatch):
    from argparse import Namespace

    from symposium.cli import analyze

    path = tmp_path / "empty.csv"
    path.write_text("name,share_publicly\n")

    def unexpected_client(**kwargs):
        raise AssertionError("Client must not be created for an empty registration")

    monkeypatch.setattr(analyze.APIClient, "create", unexpected_client)
    with pytest.raises(ValueError, match="No eligible"):
        analyze.analyze_participants(Namespace(csv_file=str(path)))


def test_perplexity_payment_failure_is_fatal_over_local_http():
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    from openai import OpenAI

    from symposium.core.api import PerplexityProvider

    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append(self.path)
            body = b'{"error":{"message":"Offline payment test"}}'
            self.send_response(402)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        provider = PerplexityProvider("test-key")
        provider.client.close()
        provider.client = OpenAI(
            api_key="test-key", base_url=f"http://127.0.0.1:{server.server_port}", max_retries=0
        )
        try:
            with pytest.raises(PaymentRequiredError) as exc:
                provider.get_response("Offline test prompt")
            assert exc.value.provider == "perplexity"
            assert requests == ["/chat/completions"]
        finally:
            provider.client.close()
            server.shutdown()
            thread.join(timeout=5)
        assert not thread.is_alive()


@pytest.mark.parametrize("content", ["{broken", "[]", "null"])
def test_explicit_invalid_config_is_rejected(tmp_path, content):
    path = tmp_path / "invalid.json"
    path.write_text(content)
    with pytest.raises(ValueError):
        Config(config_file=path, load_env=False)


def test_explicit_missing_config_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        Config(config_file=tmp_path / "missing.json", load_env=False)
    with pytest.raises(FileNotFoundError):
        load_runner().SymposiumRunner(config_file=tmp_path / "missing.json")


def test_cli_bad_config_does_not_create_edition(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "symposium",
            "--config",
            str(tmp_path / "missing.json"),
            "edition",
            "init",
            "--data-dir",
            str(tmp_path / "data"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert not (tmp_path / "data").exists()
    assert "Traceback" not in result.stderr


def test_openrouter_uses_configured_generation_parameters():
    from types import SimpleNamespace

    from symposium.core.api import OpenRouterProvider

    requests = []

    def create(**kwargs):
        requests.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Offline response"))]
        )

    provider = OpenRouterProvider("test-key", model="test-model", temperature=0.2, max_tokens=123)
    provider.client.close()
    provider.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    assert provider.get_response("Offline prompt") == "Offline response"
    assert requests[0]["model"] == "test-model"
    assert requests[0]["temperature"] == 0.2
    assert requests[0]["max_tokens"] == 123
    provider.get_response("Offline prompt", temperature=0.1, max_tokens=50)
    assert requests[1]["temperature"] == 0.1
    assert requests[1]["max_tokens"] == 50
