import pytest
import json
from pathlib import Path
from app import InstagramContentGenerator

def test_output_directory_creation(content_generator, test_output_dir):
    """Test that the output directory is created if it doesn't exist."""
    assert test_output_dir.exists()
    assert test_output_dir.is_dir()

def test_post_file_generation(content_generator, sample_topic, test_output_dir):
    """Test that post files are generated with correct format."""
    content_generator.generate_content(sample_topic)
    
    post_file = test_output_dir / "post.txt"
    assert post_file.exists()
    
    content = post_file.read_text()
    assert "- Post" in content
    assert "- Prompt to generate an illustration" in content

def test_content_history_file_generation(content_generator, sample_topic, test_output_dir):
    """Test that content history is saved in JSON format."""
    content_generator.generate_content(sample_topic)
    
    history_file = test_output_dir / "content_history.json"
    assert history_file.exists()
    
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    assert isinstance(history, list)
    assert len(history) > 0
    assert all(isinstance(entry, dict) for entry in history)

def test_content_history_format(content_generator, sample_topic):
    """Test that content history entries have the correct format."""
    content_generator.generate_content(sample_topic)
    history = content_generator.get_content_history()
    
    latest_entry = history[-1]
    assert "timestamp" in latest_entry
    assert "topic" in latest_entry
    assert "content" in latest_entry
    assert latest_entry["topic"] == sample_topic

def test_multiple_content_generation(content_generator, test_output_dir):
    """Test that multiple content generations are handled correctly."""
    topics = ["Wine 1", "Wine 2", "Wine 3"]
    
    for topic in topics:
        content_generator.generate_content(topic)
    
    history_file = test_output_dir / "content_history.json"
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    assert len(history) == len(topics)
    assert all(entry["topic"] in topics for entry in history)

def test_file_encoding_handling(content_generator, test_output_dir):
    """Test that special characters are handled correctly in file output."""
    special_topic = "Château Margaux 2015 (€€€)"
    content_generator.generate_content(special_topic)
    
    post_file = test_output_dir / "post.txt"
    content = post_file.read_text(encoding='utf-8')
    
    assert "Château" in content
    assert "€€€" in content

def test_output_file_permissions(content_generator, sample_topic, test_output_dir):
    """Test that output files have correct permissions."""
    content_generator.generate_content(sample_topic)
    
    post_file = test_output_dir / "post.txt"
    history_file = test_output_dir / "content_history.json"
    
    assert post_file.stat().st_mode & 0o777 == 0o644
    assert history_file.stat().st_mode & 0o777 == 0o644 