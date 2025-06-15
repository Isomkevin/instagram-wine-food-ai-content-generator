import pytest
from unittest.mock import Mock, patch
from app import InstagramContentGenerator

def test_writer_agent_creation(content_generator):
    """Test that the writer agent is created with correct configuration."""
    writer = content_generator.writer_agent
    
    assert writer.name == "Writer"
    assert "digital marketer" in writer.role.lower()
    assert "wine" in writer.role.lower()
    assert writer.model.id == "gemini-2.0-flash-lite"
    assert writer.exponential_backoff is True

def test_illustrator_agent_creation(content_generator):
    """Test that the illustrator agent is created with correct configuration."""
    illustrator = content_generator.illustrator_agent
    
    assert illustrator.name == "Illustrator"
    assert "illustrator" in illustrator.role.lower()
    assert "wine" in illustrator.role.lower()
    assert illustrator.model.id == "gemini-2.0-flash"
    assert illustrator.exponential_backoff is True

def test_content_team_creation(content_generator):
    """Test that the content team is created with correct configuration."""
    team = content_generator.content_team
    
    assert team.name == "Instagram Team"
    assert team.mode == "coordinate"
    assert len(team.members) == 2
    assert team.monitoring is True
    assert team.markdown is True

@patch('agno.agent.Agent')
def test_writer_agent_response(mock_agent, content_generator, sample_topic):
    """Test that the writer agent generates appropriate content."""
    # Mock the agent's response
    mock_agent.return_value.print_response.return_value = "Test caption #wine #food"
    
    response = content_generator.writer_agent.print_response(sample_topic)
    
    assert isinstance(response, str)
    assert len(response) > 0

@patch('agno.agent.Agent')
def test_illustrator_agent_response(mock_agent, content_generator, sample_topic):
    """Test that the illustrator agent generates appropriate prompts."""
    # Mock the agent's response
    mock_agent.return_value.print_response.return_value = "Test image prompt"
    
    response = content_generator.illustrator_agent.print_response(sample_topic)
    
    assert isinstance(response, str)
    assert len(response) > 0

def test_agent_error_handling(content_generator, sample_topic):
    """Test that agents handle errors gracefully."""
    with pytest.raises(Exception):
        # Test with invalid API key
        invalid_generator = InstagramContentGenerator(
            gemini_api_key="invalid_key",
            output_dir="./test_output"
        )
        invalid_generator.generate_content(sample_topic) 