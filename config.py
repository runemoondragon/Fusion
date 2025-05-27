from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Model configurations with defaults
    MODEL = os.getenv('MODEL', "claude-3-5-sonnet-20241022")  # For Claude
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")       # Default for OpenAI
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest") # Default for Gemini

    MAX_TOKENS = 8000
    MAX_CONVERSATION_TOKENS = 200000  # Maximum tokens per conversation

    # Paths
    BASE_DIR = Path(__file__).parent
    TOOLS_DIR = BASE_DIR / "tools"
    PROMPTS_DIR = BASE_DIR / "prompts"
    GENERATED_FILES_DIR = BASE_DIR / "generated_files" # Added for tool outputs

    # Assistant Configuration
    ENABLE_THINKING = True
    SHOW_TOOL_USAGE = True
    SHOW_TOKEN_USAGE = True
    DEFAULT_TEMPERATURE = 0.7
