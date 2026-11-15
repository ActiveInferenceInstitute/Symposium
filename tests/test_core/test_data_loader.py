"""Tests for data loader module."""

import pandas as pd
import pytest

from symposium.core.data_loader import DataLoader


class TestDataLoader:
    """Tests for DataLoader class."""

    def test_load_csv(self, sample_csv_file):
        """Test loading CSV file."""
        df = DataLoader.load_csv(sample_csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_load_csv_not_found(self, temp_dir):
        """Test loading non-existent CSV raises error."""
        with pytest.raises(FileNotFoundError):
            DataLoader.load_csv(temp_dir / "nonexistent.csv")

    def test_load_json(self, sample_json_file):
        """Test loading JSON file."""
        data = DataLoader.load_json(sample_json_file)
        assert isinstance(data, dict)
        assert data["key"] == "value"

    def test_load_json_not_found(self, temp_dir):
        """Test loading non-existent JSON raises error."""
        with pytest.raises(FileNotFoundError):
            DataLoader.load_json(temp_dir / "nonexistent.json")

    @pytest.mark.parametrize("content", ["[]", "null", "42", "true", '"text"'])
    def test_load_json_rejects_non_object(self, tmp_path, content):
        path = tmp_path / "input.json"
        path.write_text(content, encoding="utf-8")

        with pytest.raises(ValueError, match="JSON object") as error:
            DataLoader.load_json(path)
        assert str(path) in str(error.value)

    def test_load_markdown(self, sample_markdown_file):
        """Test loading markdown file."""
        content = DataLoader.load_markdown(sample_markdown_file)
        assert isinstance(content, str)
        assert "Test Markdown" in content

    def test_truncate_dataframe(self):
        """Test truncating DataFrame."""
        df = pd.DataFrame({"col": range(100)})
        truncated = DataLoader.truncate_dataframe(df, 10)
        assert len(truncated) == 10

    def test_estimate_token_count(self):
        """Test token count estimation."""
        text = "This is a test sentence with ten words in it."
        tokens = DataLoader.estimate_token_count(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_truncate_to_tokens(self):
        """Test truncating text to token limit."""
        text = " ".join(["word"] * 1000)
        truncated = DataLoader.truncate_to_tokens(text, 100)
        assert len(truncated) < len(text)
        assert DataLoader.estimate_token_count(truncated) <= 100

    def test_load_presenter_data(self, temp_dir):
        """Test loading presenter data structure."""
        # Create presenter directory structure
        presenter_dir = temp_dir / "Test_Presenter"
        presenter_dir.mkdir()

        # Create mock CSV files
        topics_df = pd.DataFrame({"topic": ["topic1"], "count": [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-20240101.csv", index=False)

        works_df = pd.DataFrame(
            {"title": ["Work 1"], "publication_year": [2023], "cited_by_count": [10]}
        )
        works_df.to_csv(presenter_dir / "works-20240101.csv", index=False)

        # Load data
        presenters = DataLoader.load_presenter_data(temp_dir)

        assert "Test_Presenter" in presenters
        assert "topics" in presenters["Test_Presenter"]
        assert "works" in presenters["Test_Presenter"]


@pytest.mark.parametrize("as_string", [False, True])
def test_public_participant_loader_accepts_path_and_string(tmp_path, as_string):
    from symposium.core import load_participant_data

    csv_path = tmp_path / "participants.csv"
    csv_path.write_text(
        "share_publicly,name,background\nYes,Allowed,Research\nNo,Withheld,Private\n",
        encoding="utf-8",
    )
    result = load_participant_data(str(csv_path) if as_string else csv_path)
    assert set(result) == {"Allowed"}
    assert result["Allowed"]["background"] == "Research"
    assert result == DataLoader.load_participant_data(csv_path)
