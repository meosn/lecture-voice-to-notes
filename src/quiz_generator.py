"""
Quiz generation module using multiple AI providers
"""

from typing import Optional
from pathlib import Path
from config import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE, PROMPTS_DIR, DEFAULT_QUIZ_QUESTIONS
from src.ai_provider import AIProvider
from src.json_utils import extract_json


class QuizGenerator:
    """Generate quiz questions from lecture transcriptions"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai", model: str = None):
        """
        Initialize quiz generator with provider
        
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
    
    def generate_quiz(self, transcription: str, num_questions: int = None) -> str:
        """
        Generate a complete quiz from transcription
        
        Args:
            transcription: Lecture transcription text
            num_questions: Number of questions (default from config)
            
        Returns:
            Quiz in formatted text
        """
        num_questions = num_questions or DEFAULT_QUIZ_QUESTIONS
        prompt = self._get_quiz_prompt(num_questions)
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Create a quiz from this lecture:\n\n{transcription}"}
                ],
                max_tokens=self.max_tokens * 2,
                temperature=self.temperature
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Quiz generation error: {str(e)}")

    def generate_interactive_quiz(self, transcription: str, num_questions: int = None, language: str = None, difficulty: str = "medium") -> list:
        """Generate machine-readable quiz questions for the interactive UI."""
        num_questions = num_questions or DEFAULT_QUIZ_QUESTIONS
        language_instruction = language or "the same language as the lecture transcription"
        prompt = f"""Create {num_questions} {difficulty} quiz questions in {language_instruction}.
Return only valid JSON, no markdown. The JSON must be an array.
Each item must have:
- type: "multiple_choice" or "short_answer"
- question: string
- options: array of 4 strings for multiple_choice, empty array for short_answer
- correct_answer: exact correct option text or model short answer
- explanation: brief explanation
Use mostly multiple_choice questions and include a few short_answer questions.
Create a fresh set of questions, not the most obvious first-pass set."""

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
            raise Exception(f"Interactive quiz generation error: {str(e)}")
    
    def generate_mcq(self, transcription: str, num_questions: int = 10) -> str:
        """
        Generate multiple choice questions
        
        Args:
            transcription: Lecture transcription text
            num_questions: Number of questions
            
        Returns:
            MCQ quiz
        """
        prompt = f"""You are an expert at creating multiple choice questions for students.
Create {num_questions} multiple choice questions based on the lecture content.

Format each question as:
Q[number]: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]
Explanation: [Brief explanation]

Mix difficulty levels and cover different topics from the lecture."""
        
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
            raise Exception(f"MCQ generation error: {str(e)}")
    
    def generate_true_false(self, transcription: str, num_questions: int = 10) -> str:
        """
        Generate true/false questions
        
        Args:
            transcription: Lecture transcription text
            num_questions: Number of questions
            
        Returns:
            True/False quiz
        """
        prompt = f"""Create {num_questions} true/false questions from the lecture.

Format:
Q[number]: [Statement]
Answer: [True/False]
Explanation: [Why the answer is correct]

Include both true and false statements."""
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"True/False generation error: {str(e)}")
    
    def generate_short_answer(self, transcription: str, num_questions: int = 5) -> str:
        """
        Generate short answer questions
        
        Args:
            transcription: Lecture transcription text
            num_questions: Number of questions
            
        Returns:
            Short answer quiz
        """
        prompt = f"""Create {num_questions} short answer questions from the lecture.

Format:
Q[number]: [Question]
Model Answer: [Concise answer with key points]

Focus on testing understanding of key concepts."""
        
        try:
            response = self.provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Short answer generation error: {str(e)}")
    
    def _get_quiz_prompt(self, num_questions: int) -> str:
        """
        Load or create the quiz generation prompt
        
        Returns:
            System prompt for quiz generation
        """
        prompt_file = PROMPTS_DIR / "quiz.txt"
        
        if prompt_file.exists():
            return prompt_file.read_text()
        
        # Default prompt
        default_prompt = f"""You are an expert educator creating quiz questions for students.
Create {num_questions} questions from the lecture content. Mix different question types:
- Multiple Choice (60%)
- True/False (20%)
- Short Answer (20%)

Guidelines:
1. Cover all major topics from the lecture
2. Mix difficulty levels (easy, medium, hard)
3. Test both knowledge recall and understanding
4. Ensure questions are clear and unambiguous
5. Provide correct answers and brief explanations
6. Make distractors (wrong answers) plausible

Format:
# Practice Quiz

## Multiple Choice Questions

Q1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

**Correct Answer:** [Letter]
**Explanation:** [Why this is correct]

---

## True/False Questions

Q[n]: [Statement]

**Answer:** [True/False]
**Explanation:** [Brief explanation]

---

## Short Answer Questions

Q[n]: [Question]

**Model Answer:** [Expected answer with key points]

---

## Answer Key
[Summary of all correct answers]"""
        
        # Save default prompt
        prompt_file.write_text(default_prompt)
        
        return default_prompt
