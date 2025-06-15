# Multi-Agent Instagram Content Generation System
# Based on the Towards Data Science article: "Agentic AI 103: Building Multi-Agent Teams"

import os
from textwrap import dedent
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

# Core imports for the multi-agent system
from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env file

class InstagramContentGenerator:
    """
    A multi-agent system for generating Instagram content about wine and fine foods.
    
    This system uses two specialized agents:
    1. Writer Agent: Creates engaging Instagram captions with SEO optimization
    2. Illustrator Agent: Creates image generation prompts based on the content
    
    The agents work together through a Team coordinator to produce complete
    Instagram posts with accompanying image generation prompts.
    """
    
    def __init__(self, gemini_api_key: str, output_dir: str = "./output"):
        """
        Initialize the Instagram Content Generator.
        
        Args:
            gemini_api_key: API key for Google Gemini LLM
            output_dir: Directory to save generated content files
        """
        self.gemini_api_key = gemini_api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize the agents
        self.writer_agent = self._create_writer_agent()
        self.illustrator_agent = self._create_illustrator_agent()
        self.content_team = self._create_content_team()
    
    def _create_writer_agent(self) -> Agent:
        """
        Create the Writer agent specialized in Instagram content creation.
        
        This agent is designed as a digital marketing expert with deep knowledge
        in wine, cheese, and gourmet foods. It focuses on creating engaging,
        SEO-friendly Instagram captions.
        
        Returns:
            Agent: Configured writer agent
        """
        return Agent(
            name="Writer",
            role=dedent("""\
                You are an experienced digital marketer who specializes in Instagram posts.
                You know how to write an engaging, SEO-friendly post.
                You know all about wine, cheese, and gourmet foods found in grocery stores.
                You are also a wine sommelier who knows how to make recommendations.
                """),
            description=dedent("""\
                Write clear, engaging content using a neutral to fun and conversational tone.
                Write an Instagram caption about the requested {topic}.
                Write a short call to action at the end of the message.
                Add 5 hashtags to the caption.
                If you encounter a character encoding error, remove the character before sending your response to the Coordinator.
                """),
            tools=[DuckDuckGoTools()],
            add_name_to_instructions=True,
            expected_output=dedent("Caption for Instagram about the {topic}."),
            model=Gemini(
                id="gemini-2.0-flash-lite", 
                api_key=self.gemini_api_key
            ),
            exponential_backoff=True,
            delay_between_retries=2
        )
    
    def _create_illustrator_agent(self) -> Agent:
        """
        Create the Illustrator agent specialized in image prompt generation.
        
        This agent takes the content created by the Writer and generates
        detailed prompts for image generation tools.
        
        Returns:
            Agent: Configured illustrator agent
        """
        return Agent(
            name="Illustrator",
            role="You are an illustrator who specializes in pictures of wines, cheeses, and fine foods found in grocery stores.",
            description=dedent("""\
                Based on the caption created by Marketer, create a prompt to generate an engaging photo about the requested {topic}.
                If you encounter a character encoding error, remove the character before sending your response to the Coordinator.
                """),
            expected_output="Prompt to generate a picture.",
            add_name_to_instructions=True,
            model=Gemini(
                id="gemini-2.0-flash", 
                api_key=self.gemini_api_key
            ),
            exponential_backoff=True,
            delay_between_retries=2
        )
    
    def _create_content_team(self) -> Team:
        """
        Create the coordinating team that manages the multi-agent workflow.
        
        The team uses 'coordinate' mode to manage the sequential workflow:
        1. Writer creates the Instagram caption
        2. Illustrator creates the image generation prompt
        3. Results are compiled into a structured output
        
        Returns:
            Team: Configured team coordinator
        """
        return Team(
            name="Instagram Team",
            mode="coordinate",
            members=[self.writer_agent, self.illustrator_agent],
            instructions=dedent("""\
                You are a team of content writers working together to create engaging Instagram posts.
                First, you ask the 'Writer' to create a caption for the requested {topic}.
                Next, you ask the 'Illustrator' to create a prompt to generate an engaging illustration for the requested {topic}.
                Do not use emojis in the caption.
                If you encounter a character encoding error, remove the character before saving the file.
                Use the following template to generate the output:
                - Post
                - Prompt to generate an illustration
                """),
            model=Gemini(
                id="gemini-2.0-flash", 
                api_key=self.gemini_api_key
            ),
            tools=[FileTools(base_dir=self.output_dir)],
            expected_output="A text named 'post.txt' with the content of the Instagram post and the prompt to generate a picture.",
            share_member_interactions=True,
            markdown=True,
            monitoring=True
        )
    
    def generate_content(self, topic: str, save_to_file: bool = True) -> dict:
        """
        Generate Instagram content for a given topic.
        
        Args:
            topic: The topic for the Instagram post (should be related to wine/food)
            save_to_file: Whether to save the output to a file
            
        Returns:
            dict: Generated content with post and image prompt
        """
        print(f"🚀 Generating Instagram content for topic: {topic}")
        print("📝 Writer agent is researching and creating caption...")
        print("🎨 Illustrator agent is creating image prompt...")
        
        # Generate the content using the team
        response = self.content_team.print_response(topic)
        
        if save_to_file:
            self._save_content_history(topic, response)
        
        return {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "content": response
        }
    
    def _save_content_history(self, topic: str, content: str):
        """
        Save content generation history to a JSON file.
        
        Args:
            topic: The topic that was generated
            content: The generated content
        """
        history_file = self.output_dir / "content_history.json"
        
        # Load existing history or create new
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new entry
        history.append({
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "content": content
        })
        
        # Save updated history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def get_content_history(self) -> list:
        """
        Retrieve the history of generated content.
        
        Returns:
            list: List of previously generated content entries
        """
        history_file = self.output_dir / "content_history.json"
        
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

def setup_environment():
    """
    Setup the environment and validate required dependencies.
    
    Returns:
        str: The Gemini API key from environment variables
    """
    # Check for required API keyworking
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(api_key)
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    print("✅ Environment setup complete!")
    print("🤖 Multi-Agent Instagram Content Generator ready!")
    return api_key

def main():
    """
    Main function demonstrating the usage of the Instagram Content Generator.
    """
    try:
        # Setup environment
        api_key = setup_environment()
        
        # Initialize the content generator
        generator = InstagramContentGenerator(api_key)
        
        # Example topics for wine and fine foods
        example_topics = [
            "Sparkling Water and suggestion of food to accompany",
            "Pairing Italian Chianti with aged cheese",
            "Summer rosé wine and fresh seafood combinations",
            "Artisanal chocolate and wine pairings",
            "French brie and wine selection guide"
        ]
        
        print("\n🍷 Instagram Content Generator - Wine & Fine Foods Edition")
        print("=" * 60)
        
        # Interactive mode
        while True:
            print("\nOptions:")
            print("1. Generate content for custom topic")
            print("2. Use example topics")
            print("3. View content history")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == "1":
                topic = input("Enter your topic (wine/food related): ").strip()
                if topic:
                    result = generator.generate_content(topic)
                    print(f"\n✅ Content generated successfully!")
                    print(f"📁 Check the '{generator.output_dir}' folder for saved files.")
                else:
                    print("❌ Please enter a valid topic.")
            
            elif choice == "2":
                print("\nExample topics:")
                for i, topic in enumerate(example_topics, 1):
                    print(f"{i}. {topic}")
                
                try:
                    topic_choice = int(input("Select a topic (1-5): ")) - 1
                    if 0 <= topic_choice < len(example_topics):
                        selected_topic = example_topics[topic_choice]
                        result = generator.generate_content(selected_topic)
                        print(f"\n✅ Content generated for: {selected_topic}")
                        print(f"📁 Check the '{generator.output_dir}' folder for saved files.")
                    else:
                        print("❌ Invalid selection.")
                except ValueError:
                    print("❌ Please enter a valid number.")
            
            elif choice == "3":
                history = generator.get_content_history()
                if history:
                    print(f"\n📋 Content History ({len(history)} entries):")
                    for i, entry in enumerate(history[-5:], 1):  # Show last 5 entries
                        print(f"{i}. {entry['timestamp'][:19]} - {entry['topic']}")
                else:
                    print("\n📋 No content history found.")
            
            elif choice == "4":
                print("👋 Goodbye! Thanks for using the Instagram Content Generator!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-4.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Generator stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   - Set GEMINI_API_KEY in your environment")
        print("   - Installed required packages: pip install agno duckduckgo-search google-genai")

if __name__ == "__main__":
    main()

# Installation and Setup Instructions:
"""
1. Install required packages:
   pip install agno duckduckgo-search google-genai

2. Create a .env file with your API keys:
   GEMINI_API_KEY="your_gemini_api_key_here"
   
3. Run the script:
   python instagram_content_generator.py

4. The system will:
   - Create specialized agents (Writer and Illustrator)
   - Coordinate their work through a Team
   - Generate Instagram posts with image prompts
   - Save outputs to files in the ./output directory

5. Example usage:
   - Topic: "Sparkling Water and suggestion of food to accompany"
   - Output: Instagram caption + image generation prompt
   - Saved to: ./output/post.txt and content_history.json
"""