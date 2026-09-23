"""
AI Provider abstraction layer for multiple LLM services
Supports: OpenAI, Groq, Ollama, and Hugging Face
"""

from typing import Optional, Dict, Any
import os


class AIProvider:
    """Abstract base for AI providers"""
    
    def __init__(self, provider_type: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize AI provider
        
        Args:
            provider_type: Type of provider (openai, groq, ollama, huggingface)
            api_key: API key for the provider (if required)
            **kwargs: Additional provider-specific parameters
        """
        self.provider_type = provider_type.lower()
        self.api_key = api_key
        self.client = None
        self.model = kwargs.get('model')
        self._initialize_client(**kwargs)
    
    def _initialize_client(self, **kwargs):
        """Initialize the specific provider client"""
        
        if self.provider_type == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model = self.model or "gpt-3.5-turbo"
            
        elif self.provider_type == "groq":
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.model = self.model or "llama-3.3-70b-versatile"

        elif self.provider_type == "ollama":
            import ollama
            from config import OLLAMA_HOST
            self.client = ollama.Client(host=kwargs.get("host") or OLLAMA_HOST)
            self.model = self.model or "llama3.1:8b"
            
        else:
            raise ValueError(f"Unsupported provider type: {self.provider_type}. Supported: ollama, openai, groq")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using the AI provider
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Generated text response
        """
        try:
            if self.provider_type == "ollama":
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                )
                return response["response"]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"Text generation error ({self.provider_type}): {str(e)}")
    
    def chat_completion(self, messages: list, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Generated response
        """
        try:
            if self.provider_type == "ollama":
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                )
                return response["message"]["content"]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"Chat completion error ({self.provider_type}): {str(e)}")


class TranscriptionProvider:
    """Handle audio transcription with multiple providers"""
    
    def __init__(self, provider_type: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize transcription provider
        
        Args:
            provider_type: Type of provider (openai, groq, local)
            api_key: API key for the provider (if required)
            **kwargs: Additional provider-specific parameters
        """
        self.provider_type = provider_type.lower()
        self.api_key = api_key
        self.client = None
        self.model = kwargs.get('model')
        self._initialize_client(**kwargs)
    
    def _initialize_client(self, **kwargs):
        """Initialize the specific transcription client"""
        
        if self.provider_type == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model = self.model or "whisper-1"
            
        elif self.provider_type == "groq":
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.model = self.model or "whisper-large-v3"

        elif self.provider_type == "local":
            from faster_whisper import WhisperModel
            self.model = self.model or "medium"
            self.client = WhisperModel(
                self.model,
                device=kwargs.get("device") or "auto",
                compute_type=kwargs.get("compute_type") or "int8",
            )
            
        else:
            raise ValueError(f"Unsupported transcription provider: {self.provider_type}. Supported: local, openai, groq")
    
    def transcribe(self, audio_path: str, language: str = None) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional)
            
        Returns:
            Transcribed text
        """
        try:
            if self.provider_type == "local":
                segments, _ = self.client.transcribe(
                    audio_path,
                    language=language,
                    vad_filter=True,
                )
                return " ".join(segment.text.strip() for segment in segments).strip()

            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language
                )
            return transcription.text
                
        except Exception as e:
            raise Exception(f"Transcription error ({self.provider_type}): {str(e)}")

    def transcribe_detailed(self, audio_path: str, language: str = None) -> dict:
        """Transcribe audio and return text plus detected language when available."""
        try:
            if self.provider_type == "local":
                segments, info = self.client.transcribe(
                    audio_path,
                    language=language,
                    vad_filter=True,
                )
                text = " ".join(segment.text.strip() for segment in segments).strip()
                return {
                    "text": text,
                    "language": getattr(info, "language", None),
                    "language_probability": getattr(info, "language_probability", None),
                }

            text = self.transcribe(audio_path, language=language)
            return {"text": text, "language": language, "language_probability": None}
        except Exception as e:
            raise Exception(f"Detailed transcription error ({self.provider_type}): {str(e)}")
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = None) -> list:
        """
        Transcribe with timestamps
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional)
            
        Returns:
            List of segments with timestamps and text
        """
        try:
            if self.provider_type == "local":
                segments, _ = self.client.transcribe(
                    audio_path,
                    language=language,
                    vad_filter=True,
                )
                return [
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                    }
                    for segment in segments
                ]

            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            segments = []
            if hasattr(transcription, 'segments'):
                for seg in transcription.segments:
                    segments.append({
                        'start': seg.start,
                        'end': seg.end,
                        'text': seg.text
                    })
            return segments
                
        except Exception as e:
            raise Exception(f"Timestamp transcription error ({self.provider_type}): {str(e)}")


# Provider configurations and models
PROVIDER_CONFIGS = {
    "openai": {
        "name": "OpenAI",
        "requires_api_key": True,
        "llm_models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
        "whisper_models": ["whisper-1"],
        "free": False
    },
    "groq": {
        "name": "Groq",
        "requires_api_key": True,
        "llm_models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        "whisper_models": ["whisper-large-v3"],
        "free": True
    },
    "ollama": {
        "name": "Ollama (Local)",
        "requires_api_key": False,
        "llm_models": ["llama3.1:8b"],
        "whisper_models": [],
        "free": True
    },
    "local": {
        "name": "Faster-Whisper (Local)",
        "requires_api_key": False,
        "llm_models": [],
        "whisper_models": ["medium", "small", "base"],
        "free": True
    }
}


def get_available_providers():
    """Get list of available provider types"""
    return list(PROVIDER_CONFIGS.keys())


def get_provider_info(provider_type: str) -> Dict[str, Any]:
    """Get information about a specific provider"""
    return PROVIDER_CONFIGS.get(provider_type.lower(), {})
