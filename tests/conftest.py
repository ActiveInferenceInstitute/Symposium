"""Test configuration and fixtures for symposium package tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pandas as pd
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmp_dir = Path(tempfile.mkdtemp())
    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = Mock()
    client.get_response = Mock(return_value="Mock API response")
    return client


@pytest.fixture
def sample_presenter_data():
    """Create sample presenter data."""
    return {
        'name': 'Test Presenter',
        'topics': pd.DataFrame({
            'topic': ['Active Inference', 'Free Energy Principle'],
            'count': [10, 8]
        }),
        'works': pd.DataFrame({
            'title': ['Paper 1', 'Paper 2'],
            'publication_year': [2023, 2022],
            'cited_by_count': [50, 30]
        })
    }


@pytest.fixture
def sample_participant_data():
    """Create sample participant data."""
    return {
        'name': 'Test Participant',
        'background': 'Computer Science PhD student',
        'interests': 'Active Inference, Machine Learning',
        'experience': 'Intermediate'
    }


@pytest.fixture
def sample_config():
    """Create sample configuration."""
    return {
        'api': {
            'provider': 'perplexity',
            'perplexity': {
                'model': 'llama-3.1-sonar-large-128k-online',
                'temperature': 0.7,
                'max_tokens': 2000
            }
        },
        'data': {
            'max_rows_per_file': 10,
            'max_prompt_tokens': 12000
        }
    }


@pytest.fixture
def sample_csv_file(temp_dir):
    """Create a sample CSV file."""
    csv_path = temp_dir / "test.csv"
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_participant_csv_file(temp_dir):
    """Create a sample participant CSV file in the expected format."""
    csv_path = temp_dir / "participants.csv"
    df = pd.DataFrame({
        'Name': ['Test Participant 1', 'Test Participant 2'],
        'Affiliations': ['University A', 'University B'],
        'Background': ['PhD in Computer Science', 'MSc in Mathematics'],
        'Active Inference Application': ['Research', 'Teaching'],
        'Learning Needs': ['Advanced topics', 'Practical applications'],
        'Pragmatic Value': ['Understanding theory', 'Implementation']
    })
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file."""
    import json
    json_path = temp_dir / "test.json"
    data = {'key': 'value', 'list': [1, 2, 3]}
    with open(json_path, 'w') as f:
        json.dump(data, f)
    return json_path


@pytest.fixture
def sample_markdown_file(temp_dir):
    """Create a sample markdown file."""
    md_path = temp_dir / "test.md"
    content = "# Test Markdown\n\nThis is a test."
    with open(md_path, 'w') as f:
        f.write(content)
    return md_path

