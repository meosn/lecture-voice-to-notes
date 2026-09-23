"""
Configuration settings for the Lecture Notes AI application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Provider settings
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "ollama")  # ollama, openai, groq
DEFAULT_TRANSCRIPTION_PROVIDER = os.getenv("DEFAULT_TRANSCRIPTION_PROVIDER", "local")  # local, openai, groq

# Audio settings
MAX_FILE_SIZE_MB = 25
SUPPORTED_FORMATS = ['.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpga', '.webm']
AUDIO_SAMPLE_RATE = 16000  # Hz for Whisper

# Whisper settings
WHISPER_MODEL = os.getenv("LOCAL_WHISPER_MODEL", "medium")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE") or None  # None enables language auto-detection
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "qwen2.5vl:7b")

# Model configurations for different providers
PROVIDER_MODELS = {
    "openai": {
        "llm": "gpt-3.5-turbo",
        "whisper": "whisper-1"
    },
    "groq": {
        "llm": "llama-3.3-70b-versatile",
        "whisper": "whisper-large-v3"
    },
    "ollama": {
        "llm": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        "whisper": None
    },
    "local": {
        "llm": None,
        "whisper": WHISPER_MODEL
    }
}

# GPT settings (fallback to older config)
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
MAX_TOKENS = 2000
TEMPERATURE = 0.7

# Note generation settings
NOTE_STYLE = "structured"  # Options: "structured", "bullet", "detailed"

# Quiz settings
DEFAULT_QUIZ_QUESTIONS = 10
QUIZ_TYPES = ["multiple_choice", "true_false", "short_answer"]

# Flashcard settings
DEFAULT_FLASHCARD_COUNT = 15

# Export settings
EXPORT_FORMATS = ["txt", "md", "pdf", "docx"]

# Prompts directory
PROMPTS_DIR = BASE_DIR / "prompts"
PROMPTS_DIR.mkdir(exist_ok=True)
