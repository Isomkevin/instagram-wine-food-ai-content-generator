import pytest
from app import PromptInterface

def test_prompt_interface_initialization(prompt_interface):
    """Test that the prompt interface is initialized correctly."""
    assert prompt_interface.generator is not None
    assert isinstance(prompt_interface.session_context, dict)

def test_prompt_parsing(prompt_interface, sample_prompt):
    """Test that the prompt interface correctly parses natural language instructions."""
    result = prompt_interface.process_prompt(sample_prompt)
    
    assert isinstance(result, dict)
    assert "topic" in result
    assert "style" in result
    assert "requirements" in result

def test_topic_extraction(prompt_interface, sample_prompt):
    """Test that the topic is correctly extracted from the prompt."""
    result = prompt_interface.process_prompt(sample_prompt)
    
    assert "Italian Chianti wine" in result["topic"]

def test_style_extraction(prompt_interface, sample_prompt):
    """Test that the style preferences are correctly extracted."""
    result = prompt_interface.process_prompt(sample_prompt)
    
    assert "casual" in result["style"].lower()
    assert "educational" in result["style"].lower()

def test_requirements_extraction(prompt_interface, sample_prompt):
    """Test that specific requirements are correctly extracted."""
    result = prompt_interface.process_prompt(sample_prompt)
    
    assert "food pairing" in str(result["requirements"]).lower()
    assert "call to action" in str(result["requirements"]).lower()

def test_empty_prompt_handling(prompt_interface):
    """Test that empty prompts are handled gracefully."""
    with pytest.raises(ValueError):
        prompt_interface.process_prompt("")

def test_invalid_prompt_handling(prompt_interface):
    """Test that invalid prompts are handled gracefully."""
    with pytest.raises(ValueError):
        prompt_interface.process_prompt("Invalid prompt without topic")

def test_prompt_with_special_characters(prompt_interface):
    """Test that prompts with special characters are handled correctly."""
    special_prompt = """
    Create a post about Château Margaux 2015
    Include price range (€€€)
    Add food pairing suggestions
    END
    """
    
    result = prompt_interface.process_prompt(special_prompt)
    
    assert "Château Margaux" in result["topic"]
    assert "price" in str(result["requirements"]).lower() 