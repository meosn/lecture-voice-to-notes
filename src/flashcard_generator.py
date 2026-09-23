"""
Flashcard generation module using multiple AI providers
"""

from typing import Optional
from pathlib import Path
from config import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE, PROMPTS_DIR, DEFAULT_FLASHCARD_COUNT
from src.ai_provider import AIProvider
from src.json_utils import extract_json


class FlashcardGenerator:
    """Generate flashcards from lecture transcriptions"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai", model: str = None):
        """
        Initialize flashcard generator with provider
        
        Args:
            api_key: API key for the provider (if required)
            provider: Provider type (openai, groq, ollama, huggingface)
            model: Model to use (optional, uses default)
        """
        self.provider = AIProvider(
            provider_type=provider,
            api_key=api_key,
            model=model or DEFAULT_MODEL
        )
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE
    
    def generate_flashcards(self, transcription: str, num_cards: int = None) -> str:
        """
        Generate flashcards from transcription
        
        Args:
            transcription: Lecture transcription text
            num_cards: Number of flashcards (default from config)
            
        Returns:
            Flashcards in formatted text
        """
        num_cards = num_cards or DEFAULT_FLASHCARD_COUNT
        prompt = self._get_flashcard_prompt(num_cards)
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Create flashcards from this lecture:\n\n{transcription}"}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=self.temperature
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Flashcard generation error: {str(e)}")

    def generate_interactive_flashcards(self, transcription: str, num_cards: int = None, language: str = None, difficulty: str = "medium") -> list:
        """Generate machine-readable flashcards for the interactive UI."""
        num_cards = num_cards or DEFAULT_FLASHCARD_COUNT
        language_instruction = language or "the same language as the lecture transcription"
        prompt = f"""Create {num_cards} {difficulty} study flashcards in {language_instruction}.
Return only valid JSON, no markdown. The JSON must be an array.
Each item must have:
- front: concise question, term, or concept
- back: clear answer or explanation
- topic: short topic label
Use the lecture content only.
Create a fresh set of cards that helps the student practice from a different angle."""

        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=self.temperature
            )
            return extract_json(response)
        except Exception as e:
            raise Exception(f"Interactive flashcard generation error: {str(e)}")
    
    def generate_term_definition_cards(self, transcription: str, num_cards: int = 15) -> str:
        """
        Generate term/definition flashcards
        
        Args:
            transcription: Lecture transcription text
            num_cards: Number of flashcards
            
        Returns:
            Term/definition flashcards
        """
        prompt = f"""Create {num_cards} flashcards for important terms and definitions from the lecture.

Format:
Card [number]
Front: [Term or concept]
Back: [Clear definition or explanation]

---

Focus on key vocabulary, concepts, and terminology."""
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Term flashcard generation error: {str(e)}")
    
    def generate_qa_cards(self, transcription: str, num_cards: int = 15) -> str:
        """
        Generate question/answer flashcards
        
        Args:
            transcription: Lecture transcription text
            num_cards: Number of flashcards
            
        Returns:
            Q&A flashcards
        """
        prompt = f"""Create {num_cards} question/answer flashcards from the lecture content.

Format:
Card [number]
Front: [Question]
Back: [Concise answer]

---

Create questions that test understanding of key concepts."""
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Q&A flashcard generation error: {str(e)}")
    
    def generate_concept_cards(self, transcription: str, num_cards: int = 10) -> str:
        """
        Generate concept explanation flashcards
        
        Args:
            transcription: Lecture transcription text
            num_cards: Number of flashcards
            
        Returns:
            Concept flashcards
        """
        prompt = f"""Create {num_cards} flashcards explaining key concepts from the lecture.

Format:
Card [number]
Front: [Concept name]
Back: [Explanation with example if relevant]

---

Focus on the most important concepts that need understanding."""
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Concept flashcard generation error: {str(e)}")
    
    def _get_flashcard_prompt(self, num_cards: int) -> str:
        """
        Load or create the flashcard generation prompt
        
        Returns:
            System prompt for flashcard generation
        """
        prompt_file = PROMPTS_DIR / "flashcard.txt"
        
        if prompt_file.exists():
            return prompt_file.read_text()
        
        # Default prompt
        default_prompt = f"""You are an expert at creating effective study flashcards for students.
Create {num_cards} flashcards from the lecture content. Include a mix of:
- Term definitions (40%)
- Question/answer pairs (30%)
- Concept explanations (30%)

Guidelines:
1. Front side: Keep it concise (one term, question, or concept)
2. Back side: Provide clear, complete answer (2-4 sentences max)
3. Cover all major topics from the lecture
4. Prioritize the most important and testable information
5. Use simple, direct language
6. Include examples when helpful
7. Make cards atomic (one idea per card)

Format:
# Study Flashcards

## Card 1
**Front:** [Term/Question/Concept]

**Back:** [Definition/Answer/Explanation]

---

## Card 2
**Front:** [Term/Question/Concept]

**Back:** [Definition/Answer/Explanation]

---

[Continue for all {num_cards} cards]

---

## Study Tips
- Review cards daily for best retention
- Focus on cards you find difficult
- Try to explain concepts in your own words"""
        
        # Save default prompt
        prompt_file.write_text(default_prompt)
        
        return default_prompt
