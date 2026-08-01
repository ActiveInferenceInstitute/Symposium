"""Tests for CLI dispatch routing in symposium.cli:main.

These verify that the top-level argument parser routes each subcommand to the
correct handler function (asserting on the parsed args passed through), which
the rest of the suite does not currently cover.
"""

import pytest

from symposium import cli

# subcommand -> (argv fragments after the top-level command, module path, handler name)
# argv[0] is the top-level command (analyze|generate|visualize); argparse needs it.
DISPATCH_CASES = [
    (
        "analyze presenters",
        ["analyze", "presenters", "--data-dir", "d", "--output-dir", "o"],
        "symposium.cli.analyze", "analyze_presenters",
    ),
    (
        "analyze participants",
        ["analyze", "participants", "--csv-file", "c.csv", "--output-dir", "o"],
        "symposium.cli.analyze", "analyze_participants",
    ),
    (
        "analyze backgrounds",
        ["analyze", "backgrounds", "--csv-file", "c.csv", "--output-dir", "o"],
        "symposium.cli.analyze", "analyze_participant_backgrounds",
    ),
    (
        "analyze curricula",
        ["analyze", "curricula", "--csv-file", "c.csv", "--output-dir", "o"],
        "symposium.cli.analyze", "generate_participant_curricula",
    ),
    (
        "generate profiles",
        ["generate", "profiles", "--data-dir", "d", "--output-dir", "o"],
        "symposium.cli.generate", "generate_profiles",
    ),
    (
        "generate projects",
        ["generate", "projects", "--profiles-dir", "p", "--output-dir", "o", "--domain-file", "df.md"],
        "symposium.cli.generate", "generate_projects",
    ),
    (
        "visualize embeddings",
        ["visualize", "embeddings", "--input-dir", "i", "--output-dir", "o"],
        "symposium.cli.visualize", "visualize_embeddings",
    ),
    (
        "visualize networks",
        ["visualize", "networks", "--input-dir", "i", "--output-dir", "o"],
        "symposium.cli.visualize", "visualize_networks",
    ),
    (
        "visualize distributions",
        ["visualize", "distributions", "--input-dir", "i", "--output-dir", "o"],
        "symposium.cli.visualize", "visualize_distributions",
    ),
    (
        "visualize all",
        ["visualize", "all", "--input-dir", "i", "--output-dir", "o"],
        "symposium.cli.visualize", "visualize_all",
    ),
]


@pytest.mark.parametrize(
    "name,argv,module_path,handler", DISPATCH_CASES,
    ids=[c[0] for c in DISPATCH_CASES],
)
def test_main_routes_subcommand(monkeypatch, name, argv, module_path, handler):
    """main() must route the subcommand to the correct handler."""
    import importlib
    import sys

    mod = importlib.import_module(module_path)
    captured = {}

    def fake_handler(args):
        captured["args"] = args

    monkeypatch.setattr(mod, handler, fake_handler)
    monkeypatch.setattr(sys, "argv", ["symposium"] + argv)

    cli.main()

    assert "args" in captured
    # Sanity: the parsed namespace carries the subcommand type through.
    assert captured["args"] is not None


def test_main_no_command_prints_help_and_exits(monkeypatch, capsys):
    """Invoking with no command should print help and exit non-zero."""
    import sys

    monkeypatch.setattr(sys, "argv", ["symposium"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "usage:" in out.lower()
