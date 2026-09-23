"""
Speech-to-text transcription module with multiple provider support
"""

from pathlib import Path
from typing import Optional
from config import WHISPER_MODEL, WHISPER_LANGUAGE
from src.ai_provider import TranscriptionProvider


class Transcriber:
    """Transcribe audio files to text using multiple providers"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai", model: str = None):
        """
        Initialize transcriber with provider
        
        Args:
            api_key: API key for the provider (if required)
            provider: Provider type (openai, groq, local)
            model: Model to use (optional, uses provider default if not specified)
        """
        # Use provider-specific defaults if model not specified
        from config import PROVIDER_MODELS
        
        if not model:
            provider_config = PROVIDER_MODELS.get(provider, {})
            model = provider_config.get("whisper")
        
        self.provider = TranscriptionProvider(
            provider_type=provider,
            api_key=api_key,
            model=model
        )
        self.language = WHISPER_LANGUAGE
    
    def transcribe(self, audio_path: str, language: str = None) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to the audio file
            language: Language code (optional, default from config)
            
        Returns:
            Transcribed text
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            return self.provider.transcribe(
                str(audio_path),
                language=language if language is not None else self.language
            )
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")

    def transcribe_detailed(self, audio_path: str, language: str = None) -> dict:
        """Transcribe audio and include detected language metadata when available."""
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            return self.provider.transcribe_detailed(
                str(audio_path),
                language=language if language is not None else self.language
            )
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
    
    def transcribe_with_timestamps(self, audio_path: str) -> dict:
        """
        Transcribe audio with timestamps
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with transcription and timestamps
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            segments = self.provider.transcribe_with_timestamps(str(audio_path))
            return {"segments": segments}
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
    
    def transcribe_segments(self, audio_path: str) -> dict:
        """
        Transcribe audio with segment-level timestamps
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with transcription segments
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            segments = self.provider.transcribe_with_timestamps(str(audio_path))
            return {"segments": segments}
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
    
    def transcribe_chunks(self, audio_paths: list) -> str:
        """
        Transcribe multiple audio chunks and combine
        
        Args:
            audio_paths: List of paths to audio chunks
            
        Returns:
            Combined transcription
        """
        transcriptions = []
        
        for audio_path in audio_paths:
            try:
                transcript = self.transcribe(audio_path)
                transcriptions.append(transcript)
            except Exception as e:
                print(f"Warning: Failed to transcribe {audio_path}: {str(e)}")
                continue
        
        return " ".join(transcriptions)
