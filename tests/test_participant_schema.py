"""Real-file participant schema regression scenarios."""

import csv

import pytest

from symposium.core.data_loader import DataLoader
from symposium.core.participant_schema import ParticipantSchemaError, participant_headers


def write_csv(path, headers, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)
    return path


@pytest.mark.parametrize("year", [2025, 2026, 2030])
def test_full_survey_roundtrip_preserves_text(tmp_path, year):
    headers = participant_headers(year)
    path = write_csv(
        tmp_path / "participants.csv",
        headers,
        [
            [
                "yes",
                "Test Person",
                "",
                "001",
                "0000-0001",
                "NA",
                "",
                "",
                "",
                "",
                "",
                "",
                "future",
                "",
            ]
        ],
    )
    participants = DataLoader.load_participant_data(path)
    assert len(headers) == 14
    assert f"impact in {year + 1}?" in headers[12]
    assert participants["Test Person"]["orcid"] == "0000-0001"
    assert participants["Test Person"]["affiliations"] == "001"
    assert participants["Test Person"]["background"] == ""
    assert participants["Test Person"]["future_impact"] == "future"
    assert participants["Test Person"]["row_index"] == 0


@pytest.mark.parametrize("consent", ["yes", "Y", "True", "1"])
def test_short_headers_bom_and_public_consent(tmp_path, consent):
    path = write_csv(
        tmp_path / "participants.csv",
        ["\ufeff Name ", " share_publicly ", "Background", "Affiliations"],
        [[" Test ", consent, "text", "001"], ["Private", "no", "secret", ""], ["", "yes", "", ""]],
    )
    participants = DataLoader.load_participant_data(path)
    assert list(participants) == ["Test"]
    assert participants["Test"]["email"] == ""
    assert participants["Test"]["affiliations"] == "001"


@pytest.mark.parametrize(
    "headers,rows,reason",
    [
        (["name"], [["Test"]], "Missing required"),
        (["share_publicly"], [["yes"]], "Missing required"),
        (["name", "Name", "share_publicly"], [], "ambiguous"),
        (
            [
                "name",
                "share_publicly",
                "future_impact",
                "How could Active Inference applications make impact in 2032? (Think big!)",
            ],
            [],
            "ambiguous",
        ),
        (["name", "share_publicly"], [["Test", "yes", "extra"]], "expected 2"),
        (["name", "share_publicly"], [["Test"]], "expected 2"),
        (["name", "share_publicly"], [["Test", "yes"], ["test", "yes"]], "duplicate public"),
        (["name", "share_publicly"], [["A B", "yes"], ["A_B", "yes"]], "filename collision"),
        (["name", "share_publicly"], [["!!!", "yes"]], "no safe filename"),
    ],
)
def test_rejects_unsafe_schema_without_personal_records(tmp_path, headers, rows, reason):
    path = write_csv(tmp_path / "participants.csv", headers, rows)
    with pytest.raises(ParticipantSchemaError, match=reason):
        DataLoader.load_participant_data(path)


def test_unrecognized_consent_is_excluded_before_duplicate_check(tmp_path):
    path = write_csv(
        tmp_path / "participants.csv",
        ["name", "share_publicly"],
        [["Test", "yes"], ["Test", "maybe"], ["Test", "1.0"]],
    )
    assert len(DataLoader.load_participant_data(path)) == 1


def test_unclosed_quote_is_rejected(tmp_path):
    path = tmp_path / "participants.csv"
    path.write_text('name,share_publicly\n"Test,yes\n')
    with pytest.raises(ParticipantSchemaError, match="Malformed"):
        DataLoader.load_participant_data(path)


def test_legacy_none_comments_remain_empty(tmp_path):
    path = write_csv(
        tmp_path / "participants.csv",
        ["name", "share_publicly", "comments"],
        [["Test", "yes", "None"]],
    )
    assert DataLoader.load_participant_data(path)["Test"]["comments"] == ""


@pytest.mark.parametrize("marker", ["None", "NaN", "NA", "N/A", "NULL", "null", "<NA>"])
def test_legacy_null_markers_are_consistent_for_optional_fields(tmp_path, marker):
    path = write_csv(
        tmp_path / "participants.csv",
        ["name", "share_publicly", "background", "affiliations", "comments"],
        [["Test", "yes", marker, marker, marker]],
    )
    participant = DataLoader.load_participant_data(path)["Test"]
    assert participant["background"] == participant["affiliations"] == participant["comments"] == ""
