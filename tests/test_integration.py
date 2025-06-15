import pytest
from pathlib import Path
from unittest.mock import patch
from app import InstagramContentGenerator

@patch('agno.team.Team')
def test_team_coordination(mock_team, content_generator, sample_topic):
    """Test that the team coordinates between writer and illustrator agents."""
    # Mock team response
    mock_team.return_value.print_response.return_value = """
    - Post
    Test caption about wine
    #wine #food
    
    - Prompt to generate an illustration
    Test image prompt
    """
    
    result = content_generator.generate_content(sample_topic)
    
    assert isinstance(result, dict)
    assert "topic" in result
    assert "timestamp" in result
    assert "content" in result
    assert result["topic"] == sample_topic

def test_content_generation_workflow(content_generator, sample_topic, test_output_dir):
    """Test the complete content generation workflow."""
    result = content_generator.generate_content(sample_topic)
    
    # Check output files
    post_file = test_output_dir / "post.txt"
    history_file = test_output_dir / "content_history.json"
    
    assert post_file.exists()
    assert history_file.exists()
    
    # Verify content history
    history = content_generator.get_content_history()
    assert isinstance(history, list)
    assert len(history) > 0
    assert history[-1]["topic"] == sample_topic

@patch('agno.team.Team')
def test_team_error_handling(mock_team, content_generator, sample_topic):
    """Test that the team handles errors gracefully."""
    # Mock team to raise an exception
    mock_team.return_value.print_response.side_effect = Exception("Test error")
    
    with pytest.raises(Exception):
        content_generator.generate_content(sample_topic)

def test_content_history_management(content_generator, sample_topic, test_output_dir):
    """Test content history management functionality."""
    # Generate multiple pieces of content
    topics = ["Wine 1", "Wine 2", "Wine 3"]
    for topic in topics:
        content_generator.generate_content(topic)
    
    # Get history
    history = content_generator.get_content_history()
    
    assert len(history) == len(topics)
    assert all(entry["topic"] in topics for entry in history)
    assert all("timestamp" in entry for entry in history)
    assert all("content" in entry for entry in history) 