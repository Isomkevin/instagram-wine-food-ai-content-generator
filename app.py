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
    # Check for required API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    print("✅ Environment setup complete!")
    print("🤖 Multi-Agent Instagram Content Generator ready!")
    return api_key

class PromptInterface:
    """
    Advanced prompt interface for receiving detailed instructions and prompts.
    """
    
    def __init__(self, generator: InstagramContentGenerator):
        self.generator = generator
        self.session_context = {}
    
    def process_prompt(self, prompt: str) -> dict:
        """
        Process a natural language prompt and extract instructions.
        
        Args:
            prompt: Natural language instruction/prompt
            
        Returns:
            dict: Processed instruction with extracted parameters
        """
        # Parse the prompt for specific instructions
        parsed_instruction = self._parse_instruction(prompt)
        
        # Generate content based on parsed instruction
        result = self.generator.generate_content(
            topic=parsed_instruction['topic'],
            save_to_file=parsed_instruction.get('save_file', True)
        )
        
        return {
            'original_prompt': prompt,
            'parsed_instruction': parsed_instruction,
            'generated_content': result
        }
    
    def _parse_instruction(self, prompt: str) -> dict:
        """
        Parse natural language instructions into structured format.
        
        Args:
            prompt: Raw instruction text
            
        Returns:
            dict: Structured instruction parameters
        """
        prompt_lower = prompt.lower()
        
        # Extract topic (main content focus)
        topic = self._extract_topic(prompt)
        
        # Extract style preferences
        style = self._extract_style(prompt_lower)
        
        # Extract special requirements
        requirements = self._extract_requirements(prompt_lower)
        
        return {
            'topic': topic,
            'style': style,
            'requirements': requirements,
            'save_file': 'no save' not in prompt_lower and 'don\'t save' not in prompt_lower
        }
    
    def _extract_topic(self, prompt: str) -> str:
        """Extract the main topic from the prompt."""
        # Remove common instruction words to isolate the topic
        instruction_words = [
            'create', 'generate', 'write', 'make', 'build', 'post', 'about',
            'for', 'instagram', 'content', 'caption', 'image', 'prompt'
        ]
        
        words = prompt.split()
        topic_words = []
        
        for word in words:
            if word.lower() not in instruction_words:
                topic_words.append(word)
        
        # If no specific topic found, use the full prompt
        if not topic_words:
            return prompt
        
        return ' '.join(topic_words)
    
    def _extract_style(self, prompt_lower: str) -> str:
        """Extract style preferences from the prompt."""
        style_keywords = {
            'casual': ['casual', 'relaxed', 'laid-back', 'informal'],
            'professional': ['professional', 'formal', 'business', 'corporate'],
            'fun': ['fun', 'playful', 'energetic', 'vibrant', 'exciting'],
            'elegant': ['elegant', 'sophisticated', 'classy', 'refined'],
            'educational': ['educational', 'informative', 'teaching', 'learning']
        }
        
        for style, keywords in style_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return style
        
        return 'conversational'  # default style
    
    def _extract_requirements(self, prompt_lower: str) -> list:
        """Extract special requirements from the prompt."""
        requirements = []
        
        requirement_patterns = {
            'no_emojis': ['no emoji', 'without emoji', 'no emojis'],
            'include_cta': ['call to action', 'cta', 'include cta'],
            'short_format': ['short', 'brief', 'concise', 'quick'],
            'long_format': ['detailed', 'long', 'comprehensive', 'in-depth'],
            'hashtags': ['hashtag', 'tags', '#'],
            'story_format': ['story', 'narrative', 'storytelling']
        }
        
        for req, patterns in requirement_patterns.items():
            if any(pattern in prompt_lower for pattern in patterns):
                requirements.append(req)
        
        return requirements

def get_multiline_input(prompt_text: str) -> str:
    """
    Get multiline input from user with clear instructions.
    
    Args:
        prompt_text: The prompt to display to the user
        
    Returns:
        str: The complete user input
    """
    print(f"\n{prompt_text}")
    print("💡 Tips:")
    print("   - Be specific about your topic (wine, cheese, food pairings, etc.)")
    print("   - Mention style preferences (casual, professional, fun, elegant)")
    print("   - Add special requirements (no emojis, include CTA, short format)")
    print("   - Type 'END' on a new line when finished")
    print("   - Type 'CANCEL' to go back")
    print("-" * 50)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            elif line.strip().upper() == 'CANCEL':
                return None
            lines.append(line)
        except KeyboardInterrupt:
            return None
    
    return '\n'.join(lines).strip()

def main():
    """
    Main function with enhanced prompt interface for receiving instructions.
    """
    try:
        # Setup environment
        api_key = setup_environment()
        
        # Initialize the content generator and prompt interface
        generator = InstagramContentGenerator(api_key)
        prompt_interface = PromptInterface(generator)
        
        print("\n🍷 Instagram Content Generator - Advanced Prompt Interface")
        print("=" * 65)
        print("🤖 I can understand natural language instructions!")
        print("📝 Tell me what kind of Instagram content you want to create.")
        
        # Interactive mode
        while True:
            print("\n" + "="*50)
            print("📋 MAIN MENU")
            print("="*50)
            print("1. 💬 Natural Language Prompt (Advanced)")
            print("2. 🎯 Quick Topic Entry")
            print("3. 📖 Example Prompts & Instructions")
            print("4. 📊 View Content History")
            print("5. ❓ Help & Instructions")
            print("6. 🚪 Exit")
            
            choice = input("\n👉 Select an option (1-6): ").strip()
            
            if choice == "1":
                # Advanced natural language prompt
                user_prompt = get_multiline_input(
                    "🗣️  NATURAL LANGUAGE PROMPT MODE\n"
                    "Tell me exactly what you want - I'll understand your instructions:"
                )
                
                if user_prompt:
                    print("\n🔄 Processing your instruction...")
                    print(f"📝 Your prompt: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
                    
                    try:
                        result = prompt_interface.process_prompt(user_prompt)
                        print(f"\n✅ Content generated successfully!")
                        print(f"🎯 Interpreted topic: {result['parsed_instruction']['topic']}")
                        print(f"🎨 Style: {result['parsed_instruction']['style']}")
                        if result['parsed_instruction']['requirements']:
                            print(f"📋 Requirements: {', '.join(result['parsed_instruction']['requirements'])}")
                        print(f"📁 Check the '{generator.output_dir}' folder for saved files.")
                    except Exception as e:
                        print(f"❌ Error processing prompt: {e}")
                else:
                    print("❌ Prompt cancelled or empty.")
            
            elif choice == "2":
                # Quick topic entry
                topic = input("\n🎯 Enter your topic (wine/food related): ").strip()
                if topic:
                    try:
                        result = generator.generate_content(topic)
                        print(f"\n✅ Content generated successfully!")
                        print(f"📁 Check the '{generator.output_dir}' folder for saved files.")
                    except Exception as e:
                        print(f"❌ Error generating content: {e}")
                else:
                    print("❌ Please enter a valid topic.")
            
            elif choice == "3":
                # Example prompts
                print("\n📖 EXAMPLE PROMPTS & INSTRUCTIONS")
                print("-" * 40)
                examples = [
                    {
                        "prompt": "Create a fun and casual Instagram post about pairing Italian Chianti with aged cheese. Make it educational but keep it light and include a call to action.",
                        "explanation": "This specifies topic, style (fun/casual), tone (educational but light), and includes CTA requirement."
                    },
                    {
                        "prompt": "Write an elegant and sophisticated post about summer rosé wines. Focus on French varieties and include food pairing suggestions. No emojis please.",
                        "explanation": "Specifies style (elegant), region focus, content type, and formatting preference."
                    },
                    {
                        "prompt": "Generate a short and concise post about artisanal chocolate and wine pairings for beginners. Make it approachable and include hashtags.",
                        "explanation": "Specifies length (short), audience (beginners), tone (approachable), and hashtag requirement."
                    }
                ]
                
                for i, example in enumerate(examples, 1):
                    print(f"\n{i}. EXAMPLE PROMPT:")
                    print(f"   '{example['prompt']}'")
                    print(f"   💡 Why this works: {example['explanation']}")
                
                input("\n⏎ Press Enter to continue...")
            
            elif choice == "4":
                # Content history
                history = generator.get_content_history()
                if history:
                    print(f"\n📊 CONTENT HISTORY ({len(history)} entries)")
                    print("-" * 40)
                    for i, entry in enumerate(history[-10:], 1):  # Show last 10 entries
                        print(f"{i:2d}. {entry['timestamp'][:19]} - {entry['topic'][:50]}{'...' if len(entry['topic']) > 50 else ''}")
                else:
                    print("\n📊 No content history found.")
                
                input("\n⏎ Press Enter to continue...")
            
            elif choice == "5":
                # Help and instructions
                print("\n❓ HELP & INSTRUCTIONS")
                print("=" * 30)
                print("\n🎯 HOW TO USE THE NATURAL LANGUAGE PROMPT:")
                print("   • Be specific about your topic (wine types, food items, pairings)")
                print("   • Mention your preferred style: casual, professional, fun, elegant")
                print("   • Add special requirements: no emojis, include CTA, short/long format")
                print("   • Specify your target audience: beginners, experts, general audience")
                
                print("\n📝 PROMPT STRUCTURE EXAMPLES:")
                print("   'Create a [STYLE] post about [TOPIC] for [AUDIENCE] with [REQUIREMENTS]'")
                print("   'Write [LENGTH] content about [TOPIC] that is [TONE] and includes [ELEMENTS]'")
                
                print("\n🎨 AVAILABLE STYLES:")
                print("   • Casual/Relaxed • Professional/Formal • Fun/Playful")
                print("   • Elegant/Sophisticated • Educational/Informative")
                
                print("\n📋 SPECIAL REQUIREMENTS:")
                print("   • No emojis • Include call-to-action • Short/Brief format")
                print("   • Long/Detailed format • Include hashtags • Story format")
                
                input("\n⏎ Press Enter to continue...")
            
            elif choice == "6":
                print("\n👋 Thank you for using the Instagram Content Generator!")
                print("🍷 Keep creating amazing wine and food content!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-6.")
    
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