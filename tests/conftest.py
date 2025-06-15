import os
import pytest
from pathlib import Path
import sys

# Add the project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import InstagramContentGenerator, PromptInterface

@pytest.fixture
def test_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    return tmp_path / "test_output"

@pytest.fixture
def mock_gemini_api_key():
    """Mock Gemini API key for testing."""
    return "test_api_key"

@pytest.fixture
def content_generator(test_output_dir, mock_gemini_api_key):
    """Create an instance of InstagramContentGenerator for testing."""
    return InstagramContentGenerator(
        gemini_api_key=mock_gemini_api_key,
        output_dir=str(test_output_dir)
    )

@pytest.fixture
def prompt_interface(content_generator):
    """Create an instance of PromptInterface for testing."""
    return PromptInterface(content_generator)

@pytest.fixture
def sample_topic():
    """Sample topic for testing."""
    return "Italian Chianti wine"

@pytest.fixture
def sample_prompt():
    """Sample natural language prompt for testing."""
    return """
    Create a fun post about Italian Chianti wine
    Make it educational but casual
    Include food pairing suggestions
    Add a call to action
    END
    """ 